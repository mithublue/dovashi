export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export type Provider = 'gemini' | 'openai'

export interface TextConversionResult {
  translation: string
  transcript: string
  segments: Array<{
    transcript: string
    translation: string
  }>
}

export async function convertAudio(
  file: File,
  options: { target_lang: string; provider: Provider; source_lang?: string }
): Promise<Blob> {
  const form = new FormData()
  form.append('file', file)
  form.append('target_lang', options.target_lang)
  form.append('provider', options.provider)
  if (options.source_lang) form.append('source_lang', options.source_lang)

  const res = await fetch(`${API_BASE}/api/convert`, {
    method: 'POST',
    body: form,
  })

  if (!res.ok) {
    let msg = 'Conversion failed'
    try {
      const j = await res.json()
      msg = j.detail || JSON.stringify(j)
    } catch {
      // ignore
    }
    throw new Error(msg)
  }

  return await res.blob()
}

export async function getProviders(): Promise<Provider[]> {
  const res = await fetch(`${API_BASE}/api/providers`)
  if (!res.ok) return ['gemini', 'openai']
  const j = await res.json()
  return j.providers || ['gemini', 'openai']
}

export async function convertAudioToText(
  file: File,
  options: { target_lang: string; provider: Provider; source_lang?: string }
): Promise<TextConversionResult> {
  const form = new FormData()
  form.append('file', file)
  form.append('target_lang', options.target_lang)
  form.append('provider', options.provider)
  if (options.source_lang) form.append('source_lang', options.source_lang)

  const res = await fetch(`${API_BASE}/api/convert-text`, {
    method: 'POST',
    body: form,
  })

  if (!res.ok) {
    let msg = 'Conversion failed'
    try {
      const j = await res.json()
      msg = j.detail || JSON.stringify(j)
    } catch {
      // ignore
    }
    throw new Error(msg)
  }

  return await res.json()
}
