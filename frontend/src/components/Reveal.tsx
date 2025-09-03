import React, { useRef } from 'react'
import { motion, useInView, useScroll, useTransform } from 'framer-motion'

export function Reveal({ children, delay = 0 }:{
  children: React.ReactNode, delay?: number
}) {
  const ref = useRef<HTMLDivElement | null>(null)
  const inView = useInView(ref, { once: true, margin: '0px 0px -120px 0px' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={inView ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.6, ease: 'easeOut', delay }}
    >
      {children}
    </motion.div>
  )
}

export function ParallaxY({
  children,
  move = [0, -40],
}:{
  children: React.ReactNode
  move?: [number, number]
}) {
  const ref = useRef<HTMLDivElement | null>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end','end start'] })
  const y = useTransform(scrollYProgress, [0, 1], move)
  return (
    <motion.div ref={ref} style={{ y }}>
      {children}
    </motion.div>
  )
}
