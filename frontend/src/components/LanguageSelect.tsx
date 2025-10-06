import React from 'react'

interface Props {
  label?: string
  value: string
  onChange: (v: string) => void
  allowCustom?: boolean
}

const COMMON_LANGS = [
  { code: 'en', name: 'English' },
  { code: 'bn', name: 'Bangla' },
  { code: 'hi', name: 'Hindi' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'ar', name: 'Arabic' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ja', name: 'Japanese' },
]

export default function LanguageSelect({ label, value, onChange, allowCustom }: Props) {
  return (
    <div className="space-y-1">
      {label && <label className="text-xs text-white/60">{label}</label>}
      <div className="flex gap-2">
        <select
          className="input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          {COMMON_LANGS.map((l) => (
            <option key={l.code} value={l.code}>{l.name}</option>
          ))}
        </select>
        {allowCustom && (
          <input
            className="input"
            placeholder="or type language code (e.g. en, bn)"
            value={value}
            onChange={(e) => onChange(e.target.value)}
          />
        )}
      </div>
    </div>
  )
}
