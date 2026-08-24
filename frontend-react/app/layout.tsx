import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Document Brain - Intelligent Document Q&A",
  description: "Ask questions about any document with AI-powered source citations",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
