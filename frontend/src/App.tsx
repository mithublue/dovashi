import React, { useEffect, useMemo, useState } from 'react'
import { Download, Loader2, Sparkles, FileText } from 'lucide-react'
import Recorder from './components/Recorder'
import FileUploader from './components/FileUploader'
import ProviderToggle from './components/ProviderToggle'
import LanguageSelect from './components/LanguageSelect'
import { convertAudio, convertAudioToText, getProviders, type Provider, type TextConversionResult } from './api'

export default function App() {
  const [provider, setProvider] = useState<Provider>('gemini')
  const [providers, setProviders] = useState<Provider[]>(['gemini', 'openai'])
  const [targetLang, setTargetLang] = useState('en')
  const [sourceLang, setSourceLang] = useState('')
  const [inputFile, setInputFile] = useState<File | null>(null)
  const [inputUrl, setInputUrl] = useState<string | null>(null)
  const [outUrl, setOutUrl] = useState<string | null>(null)
  const [textResult, setTextResult] = useState<TextConversionResult | null>(null)
  const [busyAction, setBusyAction] = useState<'speech' | 'text' | null>(null)
  const [speechError, setSpeechError] = useState<string | null>(null)
  const [textError, setTextError] = useState<string | null>(null)

  useEffect(() => {
    getProviders().then(setProviders).catch(() => {})
  }, [])

  useEffect(() => {
    if (!inputFile) return
    const url = URL.createObjectURL(inputFile)
    setInputUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [inputFile])

  useEffect(() => {
    setOutUrl(null)
    setTextResult(null)
    setSpeechError(null)
    setTextError(null)
  }, [inputFile])

  const canConvert = useMemo(() => !!inputFile && !!targetLang && !!provider, [inputFile, targetLang, provider])

  const onConvert = async () => {
    if (!inputFile) return
    setBusyAction('speech')
    setSpeechError(null)
    setOutUrl(null)
    setTextResult(null)
    try {
      const blob = await convertAudio(inputFile, {
        target_lang: targetLang,
        provider,
        source_lang: sourceLang || undefined,
      })
      const url = URL.createObjectURL(blob)
      setOutUrl(url)
    } catch (e: any) {
      setSpeechError(e?.message || 'Conversion failed')
    } finally {
      setBusyAction(null)
    }
  }

  const onConvertText = async () => {
    if (!inputFile) return
    setBusyAction('text')
    setTextError(null)
    setTextResult(null)
    try {
      const result = await convertAudioToText(inputFile, {
        target_lang: targetLang,
        provider,
        source_lang: sourceLang || undefined,
      })
      setTextResult(result)
    } catch (e: any) {
      setTextError(e?.message || 'Conversion failed')
    } finally {
      setBusyAction(null)
    }
  }

  return (
    <div className="container-prose py-8 space-y-6">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent to-accent2 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-black" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Dovashi</h1>
            <p className="text-xs text-white/60">Perplexity-inspired speech-to-speech (Gemini / GPT)</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <ProviderToggle value={provider} onChange={setProvider} />
        </div>
      </header>

      {/* Input Section */}
      <section className="grid md:grid-cols-2 gap-6">
        <div className="card p-6 space-y-4">
          <h2 className="font-medium">1. Provide audio</h2>
          <Recorder onRecorded={setInputFile} />
          <div className="text-center text-xs text-white/50">or</div>
          <FileUploader onFile={setInputFile} />
          {inputUrl && (
            <div className="mt-2">
              <audio controls src={inputUrl} className="w-full" />
              <p className="text-xs text-white/60 mt-1">Input preview</p>
            </div>
          )}
        </div>

        <div className="card p-6 space-y-4">
          <h2 className="font-medium">2. Choose languages</h2>
          <LanguageSelect label="Target language" value={targetLang} onChange={setTargetLang} allowCustom />
          <div className="space-y-1">
            <label className="text-xs text-white/60">Source language (optional)</label>
            <input className="input" placeholder="e.g. bn (Bangla)" value={sourceLang} onChange={(e) => setSourceLang(e.target.value)} />
            <p className="text-[11px] text-white/50">Leave blank for auto-detect.</p>
          </div>
          <div className="grid gap-2">
            <button
              className="btn btn-accent w-full justify-center disabled:opacity-60"
              onClick={onConvert}
              disabled={!canConvert || busyAction === 'speech'}
            >
              {busyAction === 'speech' ? (<><Loader2 className="w-4 h-4 animate-spin" /> Converting...</>) : 'Convert to speech'}
            </button>
            <button
              className="btn btn-primary w-full justify-center disabled:opacity-60"
              onClick={onConvertText}
              disabled={!canConvert || busyAction === 'text'}
            >
              {busyAction === 'text' ? (<><Loader2 className="w-4 h-4 animate-spin" /> Converting...</>) : (<><FileText className="w-4 h-4" /> Convert to text</>)}
            </button>
          </div>
          {speechError && <p className="text-sm text-red-400">{speechError}</p>}
          {textError && <p className="text-sm text-red-400">{textError}</p>}
        </div>
      </section>

      {/* Output Section */}
      <section className="card p-6 space-y-4">
        <h2 className="font-medium">3. Result</h2>
        {outUrl ? (
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
            <audio controls src={outUrl} className="w-full" />
            <a className="btn btn-primary" href={outUrl} download="converted.wav">
              <Download className="w-4 h-4" /> Download
            </a>
          </div>
        ) : (
          <p className="text-white/60 text-sm">Your converted audio will appear here.</p>
        )}

        {textResult && (
          <div className="space-y-3">
            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-white/80 mb-2">Translated text ({targetLang})</h3>
              <p className="text-sm text-white/90 whitespace-pre-wrap leading-relaxed">{textResult.translation || 'No translation detected.'}</p>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-white/80 mb-2">Original transcript</h3>
              <p className="text-sm text-white/80 whitespace-pre-wrap leading-relaxed">{textResult.transcript || 'No transcript detected.'}</p>
            </div>
            {textResult.segments.length > 1 && (
              <div className="bg-white/5 border border-white/10 rounded-lg p-4 space-y-2 max-h-60 overflow-auto">
                <h4 className="text-xs font-semibold text-white/60 uppercase tracking-wide">Segments</h4>
                {textResult.segments.map((seg, idx) => (
                  <div key={idx} className="text-xs text-white/70">
                    <p className="font-medium text-white/80">Segment {idx + 1}</p>
                    <p><span className="text-white/50">Transcript:</span> {seg.transcript || '—'}</p>
                    <p><span className="text-white/50">Translation:</span> {seg.translation || '—'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      {/* Footer note */}
      <p className="text-center text-xs text-white/50">Pauses are preserved using VAD-based segmentation on the backend.</p>
    </div>
  )
}
