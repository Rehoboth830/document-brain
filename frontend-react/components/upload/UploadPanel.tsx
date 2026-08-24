"use client"
import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, Link, FileText, CheckCircle, Loader2, X, Globe } from "lucide-react"
import { uploadFile, uploadUrl, clearSession, getSessionId } from "@/lib/api"
import { DocumentState } from "@/types"

interface UploadPanelProps {
  session: DocumentState
  onDocumentLoaded: (name: string, chunks: number) => void
  onClear: () => void
}

export function UploadPanel({ session, onDocumentLoaded, onClear }: UploadPanelProps) {
  const [mode, setMode] = useState<"file" | "url">("file")
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [urlInput, setUrlInput] = useState("")
  const [error, setError] = useState("")
  const [progress, setProgress] = useState(0)

  const handleFile = useCallback(async (file: File) => {
    if (!file) return
    setIsLoading(true)
    setError("")
    setProgress(0)
    const interval = setInterval(() => setProgress(p => Math.min(p + 2, 90)), 200)
    try {
      const result = await uploadFile(file)
      clearInterval(interval)
      setProgress(100)
      setTimeout(() => {
        onDocumentLoaded(file.name, result.chunks_stored)
        setProgress(0)
      }, 500)
    } catch (e: any) {
      clearInterval(interval)
      setError(e.response?.data?.detail || "Upload failed. Is the API running?")
      setProgress(0)
    } finally {
      setIsLoading(false)
    }
  }, [onDocumentLoaded])

  const handleUrl = async () => {
    if (!urlInput.trim()) return
    setIsLoading(true)
    setError("")
    setProgress(0)
    const interval = setInterval(() => setProgress(p => Math.min(p + 1, 85)), 300)
    try {
      const result = await uploadUrl(urlInput.trim())
      clearInterval(interval)
      setProgress(100)
      setTimeout(() => {
        onDocumentLoaded(urlInput.trim().slice(0, 40) + "...", result.chunks_stored)
        setUrlInput("")
        setProgress(0)
      }, 500)
    } catch (e: any) {
      clearInterval(interval)
      setError(e.response?.data?.detail || "Failed to fetch URL")
      setProgress(0)
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = async () => {
    try { await clearSession() } catch {}
    onClear()
  }

  if (session.loaded) {
    return (
      <motion.div
        className="glass rounded-2xl p-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <CheckCircle className="text-brain-success shrink-0" size={16} />
            <div className="min-w-0">
              <p className="text-xs text-brain-muted">Document loaded</p>
              <p className="text-sm font-medium text-brain-text truncate">{session.name}</p>
              <p className="text-xs text-brain-accent">{session.chunks.toLocaleString()} chunks indexed</p>
            </div>
          </div>
          <button
            onClick={handleClear}
            className="shrink-0 p-1.5 rounded-lg hover:bg-brain-border transition-colors text-brain-muted hover:text-brain-error"
          >
            <X size={14} />
          </button>
        </div>
      </motion.div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex rounded-xl overflow-hidden border border-brain-border">
        {(["file", "url"] as const).map((id) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            className={"flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium transition-all " + (mode === id ? "bg-brain-accent text-white" : "bg-brain-card text-brain-muted hover:text-brain-text")}
          >
            {id === "file" ? <FileText size={14} /> : <Globe size={14} />}
            {id === "file" ? "File" : "URL"}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {mode === "file" ? (
          <motion.div key="file" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }}>
            <label
              className={"relative flex flex-col items-center justify-center gap-3 p-6 rounded-2xl border-2 border-dashed cursor-pointer transition-all " + (isDragging ? "border-brain-accent bg-brain-accent-dim" : "border-brain-border hover:border-brain-accent hover:bg-brain-card")}
              onDragOver={e => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={e => { e.preventDefault(); setIsDragging(false); const file = e.dataTransfer.files[0]; if (file) handleFile(file) }}
            >
              <input type="file" className="hidden" accept=".pdf,.docx,.doc" onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f) }} disabled={isLoading} />
              {isLoading ? <Loader2 className="text-brain-accent animate-spin" size={28} /> : <Upload className="text-brain-accent" size={28} />}
              <div className="text-center">
                <p className="text-sm font-medium text-brain-text">{isLoading ? "Processing..." : "Drop file or click to upload"}</p>
                <p className="text-xs text-brain-muted mt-1">PDF, DOCX supported</p>
              </div>
              {progress > 0 && (
                <div className="w-full bg-brain-border rounded-full h-1.5">
                  <motion.div className="bg-brain-accent h-1.5 rounded-full" initial={{ width: 0 }} animate={{ width: progress + "%" }} transition={{ ease: "easeOut" }} />
                </div>
              )}
            </label>
          </motion.div>
        ) : (
          <motion.div key="url" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} className="space-y-2">
            <input
              type="url"
              value={urlInput}
              onChange={e => setUrlInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleUrl()}
              placeholder="https://example.com/article"
              className="w-full px-3 py-2.5 rounded-xl bg-brain-card border border-brain-border text-brain-text text-sm placeholder:text-brain-muted focus:outline-none focus:border-brain-accent transition-colors"
              disabled={isLoading}
            />
            <button
              onClick={handleUrl}
              disabled={isLoading || !urlInput.trim()}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-brain-accent text-white text-sm font-medium hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? <Loader2 size={14} className="animate-spin" /> : <Link size={14} />}
              {isLoading ? "Loading..." : "Load URL"}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-brain-error bg-red-950/30 border border-red-900/30 rounded-lg px-3 py-2">
          {error}
        </motion.p>
      )}
    </div>
  )
}
