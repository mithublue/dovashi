import React, { useEffect, useRef, useState } from 'react'
import { Circle, Square, Pause, Mic } from 'lucide-react'

interface Props {
  onRecorded: (file: File) => void
}

export default function Recorder({ onRecorded }: Props) {
  const [recording, setRecording] = useState(false)
  const [paused, setPaused] = useState(false)
  const [time, setTime] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current)
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  const startTimer = () => {
    if (timerRef.current) window.clearInterval(timerRef.current)
    setTime(0)
    timerRef.current = window.setInterval(() => setTime((t) => t + 1), 1000)
  }

  const stopTimer = () => {
    if (timerRef.current) window.clearInterval(timerRef.current)
    timerRef.current = null
  }

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm'
      const mr = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = mr
      chunksRef.current = []

      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      mr.onstop = () => {
        stopTimer()
        const blob = new Blob(chunksRef.current, { type: mr.mimeType })
        const file = new File([blob], `recording.${mr.mimeType.includes('webm') ? 'webm' : 'wav'}`, { type: mr.mimeType })
        onRecorded(file)
        setRecording(false)
        setPaused(false)
      }

      mr.start()
      startTimer()
      setRecording(true)
      setPaused(false)
    } catch (e) {
      console.error(e)
      alert('Microphone permission denied or recording failed.')
    }
  }

  const stop = () => {
    mediaRecorderRef.current?.stop()
    mediaRecorderRef.current?.stream.getTracks().forEach((t) => t.stop())
  }

  const pause = () => {
    if (!mediaRecorderRef.current) return
    if (!paused) {
      mediaRecorderRef.current.pause()
      stopTimer()
      setPaused(true)
    } else {
      mediaRecorderRef.current.resume()
      startTimer()
      setPaused(false)
    }
  }

  const fmt = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

  return (
    <div className="flex items-center gap-3">
      {!recording ? (
        <button onClick={start} className="btn btn-accent">
          <Mic className="w-4 h-4" /> Record
        </button>
      ) : (
        <>
          <span className="inline-flex items-center gap-2 text-white/80 text-sm">
            <Circle className="w-3 h-3 text-red-500 animate-pulse" /> {fmt(time)}
          </span>
          <button onClick={pause} className="btn btn-primary">
            <Pause className="w-4 h-4" /> {paused ? 'Resume' : 'Pause'}
          </button>
          <button onClick={stop} className="btn btn-primary">
            <Square className="w-4 h-4" /> Stop
          </button>
        </>
      )}
    </div>
  )
}
