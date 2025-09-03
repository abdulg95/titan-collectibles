import { useEffect, useState, Suspense } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment } from '@react-three/drei'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import * as THREE from 'three'

type CardDTO = { id:string; owned:boolean; ownedByMe:boolean; serial_no:number; template:{ version:'regular'|'diamond'; glb_url:string; athlete:{ full_name:string; dob:string|null; sport:string; nationality:string; handedness?:string|null; world_ranking?:number|null; best_world_ranking?:number|null; intl_debut_year?:number|null; }}}

function Model({ url }:{ url:string }){
  const [g,setG] = useState<THREE.Group|null>(null)
  useEffect(()=>{ new GLTFLoader().load(url, (res)=>setG(res.scene)) },[url])
  return g ? <primitive object={g}/> : null
}

export default function CardView(){
  const { cardId } = useParams()
  const [sp] = useSearchParams()
  const [data,setData] = useState<CardDTO|null>(null)

  useEffect(()=>{ (async()=>{
    const r = await fetch(`/api/cards/${cardId}`, { credentials:'include' })
    const j = await r.json(); setData(j)
  })() },[cardId])

  async function claim(){
    const r = await fetch(`/api/cards/${cardId}/claim`, { method:'POST', credentials:'include' })
    if(r.ok) location.reload(); else alert('Unable to claim')
  }

  if(!data) return <p style={{padding:24}}>Loading…</p>
  const wantClaim = sp.get('claim')==='1' && !data.owned

  return (
    <div style={{display:'grid', gridTemplateColumns:'1fr 380px', gap:24, padding:24}}>
      <div style={{height:'70vh', background:'#111'}}>
        <Canvas camera={{fov:60, position:[0,0.6,1.2]}}>
          <ambientLight/>
          <Suspense fallback={null}>
            <Model url={data.template.glb_url}/>
            <Environment preset='city'/>
          </Suspense>
          <OrbitControls enablePan enableRotate enableZoom/>
        </Canvas>
      </div>
      <aside>
        <h2>{data.template.athlete.full_name} — {data.template.version.toUpperCase()} #{data.serial_no}</h2>
        <ul>
          {data.template.athlete.dob && <li>DOB: {new Date(data.template.athlete.dob).toLocaleDateString()}</li>}
          <li>Sport: {data.template.athlete.sport}</li>
          <li>Nationality: {data.template.athlete.nationality}</li>
          {data.template.athlete.handedness && <li>Handedness: {data.template.athlete.handedness}</li>}
          {data.template.athlete.world_ranking!=null && <li>World Ranking: {data.template.athlete.world_ranking}</li>}
          {data.template.athlete.best_world_ranking!=null && <li>Best Ranking: {data.template.athlete.best_world_ranking}</li>}
          {data.template.athlete.intl_debut_year && <li>International Debut: {data.template.athlete.intl_debut_year}</li>}
        </ul>
        {!data.owned && wantClaim && <button onClick={claim}>Add to my collection</button>}
        {data.owned && !data.ownedByMe && <div>Already owned by another collector</div>}
      </aside>
    </div>
  )
}
