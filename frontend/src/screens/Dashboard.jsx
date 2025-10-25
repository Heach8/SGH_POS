import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

export default function Dashboard({auth}){
  const [month,setMonth]=React.useState(new Date().toISOString().slice(0,7))
  const [data,setData]=React.useState([])
  const [loading,setLoading]=React.useState(false)

  const load = async()=>{
    setLoading(true)
    const res = await fetch(window.API_BASE+`/targets/summary?month=${month}`,{headers:{'Authorization':'Bearer '+auth.token}})
    const js = await res.json()
    setData(js.items||[])
    setLoading(false)
  }
  React.useEffect(()=>{ load() },[])

  const storeRows = data.filter(d=>d.type==='store').map(d=>({name:d.target_id, Target:d.target_amount, Actual:d.actual_amount}))

  return <div className="grid gap-4">
    <div className="bg-white rounded-xl p-4 shadow">
      <div className="flex justify-between items-center mb-3">
        <h2 className="font-semibold">Store Targets</h2>
        <input className="border p-2 rounded" type="month" value={month} onChange={e=>setMonth(e.target.value)} />
        <button className="border rounded px-3 py-2" onClick={load}>Refresh</button>
      </div>
      <div style={{width:'100%', height:320}}>
        <ResponsiveContainer>
          <BarChart data={storeRows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" /><YAxis />
            <Tooltip />
            <Bar dataKey="Target" />
            <Bar dataKey="Actual" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  </div>
}