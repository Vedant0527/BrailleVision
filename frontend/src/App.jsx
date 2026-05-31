import { useState } from 'react'

export default function App() {
  const [previewUrl, setPreviewUrl] = useState(null)
  const [apiData, setApiData] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Reset state for new upload
    setApiData(null)
    setPreviewUrl(URL.createObjectURL(file))
    setIsProcessing(true)

    // Send to your working FastAPI endpoint
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://127.0.0.1:8000/translate/', {
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
    <div className="min-h-screen bg-[#FAFAFA] text-black font-sans p-6 md:p-12">
      
      {/* 1. Massive Architectural Header */}
      <header className="flex flex-col items-center justify-center mb-24 mt-8">
        <h1 className="text-6xl sm:text-7xl md:text-[8.5rem] font-thin tracking-[1.1em] ml-[1.1em] leading-none text-center select-none text-black">
          VISION
        </h1>
        <p className="mt-6 text-[0.65rem] sm:text-xs font-bold tracking-[0.5em] text-gray-400 uppercase text-center">
          The Architecture of Accessibility
        </p>
      </header>

      {/* 2. Main Two-Column Grid */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20">
        
        {/* LEFT COLUMN: Image Ingestion */}
        <section className="space-y-4">
          <div className="text-[0.7rem] font-bold tracking-[0.3em] text-gray-500">[ INGESTION HUB ]</div>
          
          <div className="relative overflow-hidden bg-white border-2 border-black p-4 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-0.5 transition-all duration-300">
            <input 
              type="file" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
              onChange={handleFileChange}
              accept="image/png, image/jpeg"
            />
            
            {previewUrl ? (
              <img src={previewUrl} alt="Uploaded Braille" className="w-full h-auto object-cover grayscale border border-gray-200" />
            ) : (
              <div className="h-72 flex flex-col items-center justify-center bg-[#F9F9F9] border-2 border-dashed border-gray-300 gap-3">
                <span className="text-3xl text-gray-400">📥</span>
                <p className="font-bold tracking-[0.25em] text-gray-400 text-[0.75rem]">MOUNT MATRIX FILE</p>
              </div>
            )}
          </div>
        </section>

        {/* RIGHT COLUMN: Output Data */}
        <section className="space-y-4">
          <div className="text-[0.7rem] font-bold tracking-[0.3em] text-gray-500">[ DECRYPTION NODE ]</div>
          
          <div className="bg-white border-2 border-black p-8 md:p-10 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] min-h-[310px] flex flex-col justify-center transition-all duration-300">
            
            {/* Loading State */}
            {isProcessing && (
              <div className="space-y-6 text-center py-8">
                <div className="w-12 h-0.5 bg-black mx-auto animate-pulse" />
                <p className="font-bold tracking-[0.3em] text-[0.7rem] text-black animate-pulse">
                  EXECUTING SPATIAL LOCALIZATION...
                </p>
              </div>
            )}

            {/* Success State (Matches your FastAPI JSON variables) */}
            {apiData && !isProcessing && (
              <div className="space-y-8 animate-fade-in">
                <div>
                  <span className="text-[0.65rem] font-bold tracking-[0.25em] text-gray-400 uppercase block mb-3">
                    Class (A) Translation:
                  </span>
                  <h2 className="text-5xl md:text-6xl font-black tracking-tight border-b-4 border-black pb-6 break-words uppercase text-black">
                    {apiData.translated_text}
                  </h2>
                </div>

                {/* Metrics */}
                <div className="flex justify-between items-center text-xs font-bold tracking-widest text-gray-600 pt-4">
                  <span>LATENCY: {apiData.latency_ms}ms</span>
                  <span>TOKENS: {apiData.detected_tokens}</span>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!previewUrl && !isProcessing && !apiData && (
              <div className="text-center py-12 space-y-2">
                <p className="text-[0.75rem] font-bold tracking-[0.3em] text-gray-300">SYSTEM STANDBY</p>
                <p className="text-[0.65rem] font-medium tracking-wider text-gray-300">AWAITING INPUT PROTOCOL</p>
              </div>
            )}

          </div>
        </section>

      </main>
    </div>
  )
}