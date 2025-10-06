import React, { useCallback, useRef, useState } from 'react'
import { UploadCloud } from 'lucide-react'

interface Props {
  onFile: (file: File) => void
}

export default function FileUploader({ onFile }: Props) {
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement | null>(null)

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if (f) onFile(f)
  }, [onFile])

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) onFile(f)
  }

  return (
    <div
      className={`card p-6 text-center cursor-pointer ${dragOver ? 'ring-2 ring-accent/60' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input ref={inputRef} type="file" accept="audio/*" className="hidden" onChange={onChange} />
      <div className="flex flex-col items-center gap-2">
        <UploadCloud className="w-8 h-8 text-white/70" />
        <p className="text-white/80">Drag & drop an audio file, or click to select</p>
        <p className="text-xs text-white/50">Supported: wav, mp3, m4a, webm, etc.</p>
      </div>
    </div>
  )
}
