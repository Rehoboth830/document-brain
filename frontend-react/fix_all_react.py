import os

files = {}

files["components/chat/MessageBubble.tsx"] = """\
"use client"
import { motion, AnimatePresence } from "framer-motion"
import { useState } from "react"
import { ChevronDown, ChevronUp, FileText, Globe, ExternalLink } from "lucide-react"
import { Message, Citation } from "@/types"

interface CitationCardProps {
  citation: Citation
  index: number
}

export function CitationCard({ citation, index }: CitationCardProps) {
  const isUrl = citation.source_type === "url"
  const sourceName = citation.source.length > 45
    ? "..." + citation.source.slice(-42)
    : citation.source
  const relevance = Math.round(citation.similarity * 100)

  return (
    <div className="flex items-start gap-2 p-2.5 rounded-lg bg-brain-bg border border-brain-border hover:border-brain-accent/30 transition-colors">
      <div className="shrink-0 mt-0.5">
        {isUrl
          ? <Globe size={12} className="text-brain-accent" />
          : <FileText size={12} className="text-brain-accent" />}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs font-medium text-brain-accent">Source {index + 1}</span>
          <span className="text-xs text-brain-muted shrink-0">{relevance}% match</span>
        </div>
        <p className="text-xs text-brain-muted truncate mt-0.5">{sourceName}</p>
        <p className="text-xs text-brain-text">Page {citation.page_number}</p>
      </div>
      {isUrl && (
        <a
          href={citation.source}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 text-brain-muted hover:text-brain-accent transition-colors"
        >
          <ExternalLink size={11} />
        </a>
      )}
    </div>
  )
}

interface MessageBubbleProps {
  message: Message
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const [showCitations, setShowCitations] = useState(false)
  const isUser = message.role === "user"
  const hasCitations = message.citations && message.citations.length > 0

  if (isUser) {
    return (
      <motion.div
        className="flex justify-end"
        initial={{ opacity: 0, y: 10, x: 20 }}
        animate={{ opacity: 1, y: 0, x: 0 }}
        transition={{ type: "spring", stiffness: 300, damping: 25 }}
      >
        <div className="max-w-[80%] px-4 py-3 rounded-2xl rounded-tr-sm bg-gradient-to-br from-brain-accent-dim to-blue-900/40 border border-brain-accent/20 text-brain-text text-sm leading-relaxed">
          {message.content}
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      className="flex justify-start"
      initial={{ opacity: 0, y: 10, x: -20 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
    >
      <div className="max-w-[85%] space-y-2">
        <div className="px-4 py-3 rounded-2xl rounded-tl-sm glass border-l-2 border-brain-accent text-brain-text text-sm leading-relaxed">
          {message.isStreaming ? (
            <span>
              {message.content}
              <motion.span
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.5, repeat: Infinity }}
                className="inline-block w-0.5 h-4 bg-brain-accent ml-0.5 align-middle"
              />
            </span>
          ) : (
            message.content
          )}
        </div>

        {hasCitations && !message.isStreaming && (
          <div>
            <button
              onClick={() => setShowCitations(!showCitations)}
              className="flex items-center gap-1.5 text-xs text-brain-muted hover:text-brain-accent transition-colors px-1"
            >
              {showCitations ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              {message.citations!.length} {message.citations!.length > 1 ? "sources" : "source"}
            </button>

            <AnimatePresence>
              {showCitations && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2 space-y-1.5 overflow-hidden"
                >
                  {message.citations!.map((citation, i) => (
                    <CitationCard key={i} citation={citation} index={i} />
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.div>
  )
}
"""

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"Written: {path}")

print("All files written successfully")
