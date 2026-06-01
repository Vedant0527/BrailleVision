import { useState, useEffect, useCallback, useRef } from 'react'
import ParticleBackground from './ParticleBackground'

/** Maps on-screen tokens to phrasing TTS can pronounce naturally (UI text unchanged). */
const PHONETIC_MAP = {
  JIHIND: 'Jai Hind',
  JAIHIND: 'Jai Hind',
  INDIA: 'India',
  SCIOBRAILLE: 'Sigh oh Braille',
  VISUALLYIMPAIR: 'Visually Impaired',
  GREATPROJECT: 'Great Project',
}

function formatTextForSpeech(rawText) {
  if (!rawText?.trim()) return ''
  return rawText
    .split(/\s+/)
    .map((word) => {
      const key = word.replace(/[^A-Za-z]/g, '').toUpperCase()
      return key && PHONETIC_MAP[key] ? PHONETIC_MAP[key] : word
    })
    .join(' ')
}

function SpeakerIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className="w-6 h-6"
      aria-hidden="true"
    >
      <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
    </svg>
  )
}

// Native React Typewriter Component to completely bypass layout/CSS collapse bugs
function ReactTypewriter({ text }) {
  const [displayedText, setDisplayedText] = useState('')

  useEffect(() => {
    setDisplayedText('')
    if (!text) return

    let i = 0
    const interval = setInterval(() => {
      setDisplayedText((prev) => prev + text.charAt(i))
      i++
      if (i >= text.length) {
        clearInterval(interval)
      }
    }, 75) // Dictates smooth typewriter character delay speeds

    return () => clearInterval(interval)
  }, [text])

  return (
    <span className="text-white border-r-4 border-cyan-400 pr-1 animate-pulse font-black uppercase tracking-tight">
      {displayedText}
    </span>
  )
}

export default function App() {
  const [previewUrl, setPreviewUrl] = useState(null)
  const [apiData, setApiData] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)

  /** Pin utterance so Chromium GC cannot collect it mid-playback */
  const utteranceRef = useRef(null)

  const translatedText = apiData?.data?.translated_text?.trim() ?? ''

  const cancelSpeech = useCallback(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return
    window.speechSynthesis.cancel()
    utteranceRef.current = null
    window._activeUtterance = null
  }, [])

  const pickEnglishVoice = useCallback(() => {
    try {
      const voices = window.speechSynthesis?.getVoices() ?? []
      if (!voices.length) return null
      return (
        voices.find((v) => v.lang === 'en-US') ||
        voices.find((v) => v.lang.startsWith('en')) ||
        null
      )
    } catch {
      return null
    }
  }, [])

  const doSpeak = useCallback(
    (text) => {
      const synth = window.speechSynthesis
      if (!text?.trim() || !synth) return

      synth.cancel()

      const utterance = new SpeechSynthesisUtterance(text.trim())
      utterance.rate = 0.95
      utterance.pitch = 1
      utterance.volume = 1

      const voice = pickEnglishVoice()
      if (voice) {
        utterance.voice = voice
      }

      utterance.onstart = () => console.log('📣 TTS Speech started successfully!')
      utterance.onerror = (e) =>
        console.error('❌ TTS Speech error event:', e.error)
      utterance.onend = () => {
        if (utteranceRef.current === utterance) utteranceRef.current = null
        if (window._activeUtterance === utterance) window._activeUtterance = null
      }

      utteranceRef.current = utterance
      window._activeUtterance = utterance

      synth.speak(utterance)
      if (synth.paused) synth.resume()
    },
    [pickEnglishVoice]
  )

  const speakText = useCallback(
    (text) => {
      if (!text?.trim() || typeof window === 'undefined' || !window.speechSynthesis) {
        console.warn('TTS unavailable or empty text')
        return
      }

      const speechText = formatTextForSpeech(text)
      const run = () => setTimeout(() => doSpeak(speechText), 50)

      const voices = window.speechSynthesis.getVoices()
      if (voices.length === 0) {
        const onVoices = () => {
          window.speechSynthesis.removeEventListener('voiceschanged', onVoices)
          console.log(
            'TTS voices loaded:',
            window.speechSynthesis.getVoices().length
          )
          run()
        }
        window.speechSynthesis.addEventListener('voiceschanged', onVoices)
        window.speechSynthesis.getVoices()
        return
      }

      run()
    },
    [doSpeak]
  )

  const handleReplaySpeech = useCallback(() => {
    if (translatedText) speakText(translatedText)
  }, [translatedText, speakText])

  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return
    const warm = () => {
      const n = window.speechSynthesis.getVoices().length
      if (n > 0) console.log('TTS voices preloaded:', n)
    }
    warm()
    window.speechSynthesis.addEventListener('voiceschanged', warm)
    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', warm)
      cancelSpeech()
    }
  }, [cancelSpeech])

  useEffect(() => {
    if (!translatedText || isProcessing) return
    speakText(translatedText)
  }, [translatedText, isProcessing, speakText])

  const handleFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    cancelSpeech()
    setApiData(null)
    setPreviewUrl(URL.createObjectURL(file))
    setIsProcessing(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/translate', {
        method: 'POST',
        body: formData,
      })
      const jsonResult = await response.json()
      setApiData(jsonResult)
    } catch (err) {
      console.error("API Error:", err)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-black text-white font-sans p-6 md:p-12 relative z-0 selection:bg-cyan-500 selection:text-white">
      
      {/* THE 3D BACKGROUND ENGINE */}
      <ParticleBackground />

      {/* 1. Header */}
      <header className="flex flex-col items-center justify-center mb-24 mt-8">
        <h1 className="text-6xl sm:text-7xl md:text-[8.5rem] font-thin tracking-[1.1em] ml-[1.1em] leading-none text-center select-none text-white drop-shadow-md">
          VISION
        </h1>
        <p className="mt-6 text-[0.65rem] sm:text-xs font-bold tracking-[0.5em] text-cyan-400 uppercase text-center">
          The Architecture of Accessibility
        </p>
      </header>

      {/* 2. Main Grid */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20">
        
        {/* LEFT COLUMN: Image Ingestion */}
        <section className="space-y-4">
          <div className="text-[0.7rem] font-bold tracking-[0.3em] text-gray-400">[ INGESTION HUB ]</div>
          
          <label className="block relative overflow-hidden bg-[#0a0a0a] border-2 border-white p-4 shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] hover:shadow-[12px_12px_0px_0px_rgba(255,255,255,1)] hover:-translate-y-0.5 transition-all duration-300 cursor-pointer group bg-opacity-80 backdrop-blur-sm">
            <input 
              type="file" 
              className="hidden"
              onChange={handleFileChange}
              accept="image/png, image/jpeg"
            />
            
            {previewUrl ? (
              <div className="w-full h-72 relative flex items-center justify-center bg-[#111] overflow-hidden border border-gray-800">
                  <img src={previewUrl} alt="Uploaded Braille" className="max-w-full max-h-full object-contain grayscale invert opacity-90 transition-all duration-500 group-hover:invert-0 group-hover:opacity-100" />
                  
                  {/* The AI Scanning Laser */}
                  {isProcessing && (
                    <div className="absolute left-0 right-0 h-1 bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,1)] animate-scanner z-10" />
                  )}
              </div>
            ) : (
              <div className="h-72 flex flex-col items-center justify-center bg-[#050505] border-2 border-dashed border-gray-700 gap-3 hover:border-cyan-500 transition-colors">
                <span className="text-3xl text-gray-600 group-hover:text-cyan-400 transition-colors">📥</span>
                <p className="font-bold tracking-[0.25em] text-gray-500 text-[0.75rem] group-hover:text-cyan-400 transition-colors">MOUNT MATRIX FILE</p>
              </div>
            )}
          </label>
        </section>

        {/* RIGHT COLUMN: Output Data */}
        <section className="space-y-4 perspective-1000">
          <div className="text-[0.7rem] font-bold tracking-[0.3em] text-gray-400">[ DECRYPTION NODE ]</div>
          
          <div className="bg-[#0a0a0a] border-2 border-white p-8 md:p-10 shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] min-h-[355px] flex flex-col justify-center transition-transform duration-500 hover:rotate-x-2 hover:-rotate-y-2 preserve-3d bg-opacity-80 backdrop-blur-sm">
            
            {isProcessing && (
              <div className="space-y-6 text-center py-8 transform translate-z-12">
                <div className="w-12 h-0.5 bg-cyan-400 mx-auto animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
                <p className="font-bold tracking-[0.3em] text-[0.7rem] text-cyan-400 animate-pulse">
                  EXECUTING SPATIAL LOCALIZATION...
                </p>
              </div>
            )}

            {apiData && apiData.data && !isProcessing && (
              <div className="space-y-10 transform translate-z-12">
                <div>
                  <span className="text-[0.65rem] font-bold tracking-[0.25em] text-gray-500 uppercase block mb-4">
                    Class (A) Translation:
                  </span>
                  
                  <div className="flex flex-wrap items-start gap-4 border-b-2 border-gray-700 pb-4">
                    <h2 className="text-4xl md:text-5xl font-black leading-tight text-white flex-1 min-w-0">
                      <ReactTypewriter text={apiData.data.translated_text} />
                    </h2>
                    <button
                      type="button"
                      onClick={handleReplaySpeech}
                      aria-label="Read translation aloud again"
                      title="Read aloud"
                      className="shrink-0 flex items-center justify-center w-14 h-14 border-2 border-cyan-400 text-cyan-400 bg-black hover:bg-cyan-400 hover:text-black focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black transition-colors duration-200 shadow-[4px_4px_0px_0px_rgba(34,211,238,1)] hover:shadow-[6px_6px_0px_0px_rgba(34,211,238,1)]"
                    >
                      <SpeakerIcon />
                    </button>
                  </div>
                </div>

                <div className="flex justify-between items-center text-xs font-bold tracking-widest text-gray-500 pt-2 border-t border-gray-800 mt-4">
                  <span>LATENCY: <span className="text-cyan-400">{apiData.metrics.latency_ms}ms</span></span>
                  <span>TOKENS: <span className="text-white">{apiData.metrics.token_count}</span></span>
                </div>
              </div>
            )}

            {!previewUrl && !isProcessing && !apiData && (
              <div className="text-center py-12 space-y-2 transform translate-z-12">
                <p className="text-[0.75rem] font-bold tracking-[0.3em] text-gray-600">SYSTEM STANDBY</p>
                <p className="text-[0.65rem] font-medium tracking-wider text-gray-700">AWAITING INPUT PROTOCOL</p>
              </div>
            )}

          </div>
        </section>
      </main>
    </div>
  )
}