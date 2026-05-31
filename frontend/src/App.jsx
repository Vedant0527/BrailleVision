import { useState } from 'react'

export default function App() {
  const [previewUrl, setPreviewUrl] = useState(null)
  const [apiData, setApiData] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setApiData(null)
    setPreviewUrl(URL.createObjectURL(file))
    setIsProcessing(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      // UPDATED: Pointing to the new API route
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
    <div className="min-h-screen bg-[#FAFAFA] text-black font-sans p-6 md:p-12">
      
      {/* 1. Header */}
      <header className="flex flex-col items-center justify-center mb-24 mt-8">
        <h1 className="text-6xl sm:text-7xl md:text-[8.5rem] font-thin tracking-[1.1em] ml-[1.1em] leading-none text-center select-none text-black">
          VISION
        </h1>
        <p className="mt-6 text-[0.65rem] sm:text-xs font-bold tracking-[0.5em] text-gray-400 uppercase text-center">
          The Architecture of Accessibility
        </p>
      </header>

      {/* 2. Main Grid */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20">
        
        {/* LEFT COLUMN: Image Ingestion */}
        <section className="space-y-4">
          <div className="text-[0.7rem] font-bold tracking-[0.3em] text-gray-500">[ INGESTION HUB ]</div>
          
          <label className="block relative overflow-hidden bg-white border-2 border-black p-4 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-0.5 transition-all duration-300 cursor-pointer group">
            <input 
              type="file" 
              className="hidden"
              onChange={handleFileChange}
              accept="image/png, image/jpeg"
            />
            
            {previewUrl ? (
              <div className="w-full h-72 relative flex items-center justify-center bg-[#F9F9F9] overflow-hidden">
                  <img src={previewUrl} alt="Uploaded Braille" className="max-w-full max-h-full object-contain grayscale transition-all duration-500 group-hover:grayscale-0" />
                  
                  {/* The AI Scanning Laser */}
                  {isProcessing && (
                    <div className="absolute left-0 right-0 h-1 bg-black shadow-[0_0_15px_rgba(0,0,0,0.5)] animate-scanner z-10" />
                  )}
              </div>
            ) : (
              <div className="h-72 flex flex-col items-center justify-center bg-[#F9F9F9] border-2 border-dashed border-gray-300 gap-3">
                <span className="text-3xl text-gray-400">📥</span>
                <p className="font-bold tracking-[0.25em] text-gray-400 text-[0.75rem]">MOUNT MATRIX FILE</p>
              </div>
            )}
          </label>
        </section>

        {/* RIGHT COLUMN: Output Data */}
        <section className="space-y-4">
          <div className="text-[0.7rem] font-bold tracking-[0.3em] text-gray-500">[ DECRYPTION NODE ]</div>
          
          <div className="bg-white border-2 border-black p-8 md:p-10 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] min-h-[355px] flex flex-col justify-center transition-all duration-300">
            
            {isProcessing && (
              <div className="space-y-6 text-center py-8">
                <div className="w-12 h-0.5 bg-black mx-auto animate-pulse" />
                <p className="font-bold tracking-[0.3em] text-[0.7rem] text-black animate-pulse">
                  EXECUTING SPATIAL LOCALIZATION...
                </p>
              </div>
            )}

            {/* UPDATED: React now looks inside apiData.data and apiData.metrics */}
            {apiData && apiData.data && !isProcessing && (
              <div className="space-y-10 animate-fade-in">
                <div>
                  <span className="text-[0.65rem] font-bold tracking-[0.25em] text-gray-400 uppercase block mb-4">
                    Class (A) Translation:
                  </span>
                  <h2 className="text-4xl md:text-5xl font-black tracking-tight border-b-4 border-black pb-8 break-words uppercase text-black leading-tight">
                    {apiData.data.translated_text}
                  </h2>
                </div>

                <div className="flex justify-between items-center text-xs font-bold tracking-widest text-gray-600 pt-2">
                  <span>LATENCY: {apiData.metrics.latency_ms}ms</span>
                  <span>TOKENS: {apiData.metrics.token_count}</span>
                </div>
              </div>
            )}

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