// src/components/HashScroll.tsx
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export default function HashScroll({ offset = 80 }:{offset?:number}){
  const { hash } = useLocation()
  useEffect(()=>{
    if(!hash) return
    const id = hash.replace('#','')
    const el = document.getElementById(id)
    if(!el) return
    const rect = el.getBoundingClientRect()
    const top = rect.top + window.scrollY - offset
    window.scrollTo({ top, behavior: 'smooth' })
  }, [hash, offset])
  return null
}
