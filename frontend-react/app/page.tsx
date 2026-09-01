"use client"
import { useState } from "react"
import { useSession } from "@/hooks/useSession"
import { Sidebar } from "@/components/ui/Sidebar"
import { ChatInterface } from "@/components/chat/ChatInterface"
import { motion, AnimatePresence } from "framer-motion"
import { Menu } from "lucide-react"

export default function Home() {
  const { session, setDocumentLoaded, clearDocument } = useSession()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-brain-bg">
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{ background: "radial-gradient(ellipse at 20% 50%, rgba(74,158,255,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(167,139,250,0.06) 0%, transparent 60%)" }}
      />

      <div className="hidden md:flex">
        <Sidebar session={session} onDocumentLoaded={setDocumentLoaded} onClear={clearDocument} />
      </div>

      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              className="fixed inset-0 bg-black/60 z-40 md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
            />
            <motion.div
              className="fixed left-0 top-0 h-full z-50 md:hidden"
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            >
              <Sidebar
                session={session}
                onDocumentLoaded={(name, chunks) => { setDocumentLoaded(name, chunks); setSidebarOpen(false) }}
                onClear={() => { clearDocument(); setSidebarOpen(false) }}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <motion.div
        className="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="px-4 md:px-6 py-3 md:py-4 border-b border-brain-border glass-strong shrink-0">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <button
                className="md:hidden p-2 rounded-lg text-brain-muted hover:text-brain-text hover:bg-brain-card transition-colors shrink-0"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu size={18} />
              </button>
              <div className="min-w-0">
                <h1 className="text-sm font-semibold text-brain-text truncate">
                  {session.loaded ? session.name : "Document Brain"}
                </h1>
                <p className="text-xs text-brain-muted truncate">
                  {session.loaded
                    ? session.chunks.toLocaleString() + " chunks indexed"
                    : "Upload a document to begin"}
                </p>
              </div>
            </div>
            {session.loaded && (
              <div className="flex items-center gap-1.5 px-2 md:px-3 py-1.5 rounded-full bg-brain-card border border-brain-border shrink-0">
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
