"use client"
import { motion } from "framer-motion"

export function Logo({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizes = {
    sm: { icon: 28, text: "text-lg" },
    md: { icon: 36, text: "text-2xl" },
    lg: { icon: 48, text: "text-4xl" },
  }
  const s = sizes[size]

  return (
    <motion.div
      className="flex items-center gap-3"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <motion.div
        className="relative flex items-center justify-center rounded-xl bg-gradient-to-br from-brain-accent-dim to-brain-card"
        style={{ width: s.icon, height: s.icon }}
        whileHover={{ scale: 1.05 }}
        transition={{ type: "spring", stiffness: 400 }}
      >
        <svg width={s.icon * 0.6} height={s.icon * 0.6} viewBox="0 0 24 24" fill="none">
          <path d="M12 2C8.5 2 6 4.5 6 7.5C6 9 6.5 10.5 7.5 11.5C6.5 12 6 13 6 14C6 16 7.5 17.5 9.5 17.5H10V20C10 21.1 10.9 22 12 22C13.1 22 14 21.1 14 20V17.5H14.5C16.5 17.5 18 16 18 14C18 13 17.5 12 16.5 11.5C17.5 10.5 18 9 18 7.5C18 4.5 15.5 2 12 2Z" fill="#4a9eff" opacity="0.9"/>
          <circle cx="10" cy="8" r="1.5" fill="white" opacity="0.8"/>
          <circle cx="14" cy="8" r="1.5" fill="white" opacity="0.8"/>
          <path d="M10 11H14" stroke="white" strokeWidth="1.5" strokeLinecap="round" opacity="0.6"/>
        </svg>
        <motion.div
          className="absolute inset-0 rounded-xl"
          style={{ background: "radial-gradient(circle at 50% 0%, rgba(74,158,255,0.3), transparent 70%)" }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 3, repeat: Infinity }}
        />
      </motion.div>
      <div>
        <span className={"font-bold " + s.text + " text-gradient"}>Document</span>
        <span className={"font-light " + s.text + " text-brain-text"}> Brain</span>
      </div>
    </motion.div>
  )
}
