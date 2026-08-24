"use client"
import { useSession } from "@/hooks/useSession"
import { Sidebar } from "@/components/ui/Sidebar"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { motion } from "framer-motion"

export default function Home() {
  const { session, setDocumentLoaded, clearDocument } = useSession()

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-brain-bg">
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{ background: "radial-gradient(ellipse at 20% 50%, rgba(74,158,255,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(167,139,250,0.06) 0%, transparent 60%)" }}
      />
      <Sidebar session={session} onDocumentLoaded={setDocumentLoaded} onClear={clearDocument} />
      <motion.div
        className="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="px-6 py-4 border-b border-brain-border glass-strong shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-sm font-semibold text-brain-text truncate">
                {session.loaded ? session.name : "No document loaded"}
              </h1>
              <p className="text-xs text-brain-muted">
                {session.loaded
                  ? session.chunks.toLocaleString() + " chunks indexed in Pinecone"
                  : "Upload a document from the sidebar to begin"}
              </p>
            </div>
            {session.loaded && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-brain-card border border-brain-border shrink-0">
                <div className="w-1.5 h-1.5 rounded-full bg-brain-success animate-pulse" />
                <span className="text-xs text-brain-muted">Ready</span>
              </div>
            )}
          </div>
        </div>
        <ChatInterface session={session} />
      </motion.div>
    </main>
  )
}
