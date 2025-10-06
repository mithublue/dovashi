import React from 'react'
import type { Provider } from '../api'

interface Props {
  value: Provider
  onChange: (p: Provider) => void
}

export default function ProviderToggle({ value, onChange }: Props) {
  const options: Provider[] = ['gemini', 'openai']
  return (
    <div className="inline-flex bg-white/5 border border-white/10 rounded-lg overflow-hidden">
      {options.map((opt) => (
        <button
          key={opt}
          className={`px-3 py-1.5 text-sm capitalize ${value === opt ? 'bg-white/15 text-white' : 'text-white/70 hover:bg-white/10'}`}
          onClick={() => onChange(opt)}
        >
          {opt}
        </button>
      ))}
    </div>
  )
}
