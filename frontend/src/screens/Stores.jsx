import React from 'react'

export default function Stores({auth}){
  const [list,setList]=React.useState([])
  const [id,setId]=React.useState('STR-003')
  const [name,setName]=React.useState('Yeni Mağaza')
  const [region,setRegion]=React.useState('MARMARA')
  const load = async()=>{
    const res = await fetch(window.API_BASE+'/stores',{headers:{'Authorization':'Bearer '+auth.token}})
    setList(await res.json())
  }
  const add = async()=>{
    const res = await fetch(window.API_BASE+'/stores',{method:'POST',headers:{'Authorization':'Bearer '+auth.token,'Content-Type':'application/json'},
      body: JSON.stringify({id,name,region,is_active:true})})
    const js = await res.json(); if(js.ok){ load() } else { alert(JSON.stringify(js)) }
  }
  React.useEffect(()=>{ load() },[])

  return <div className="grid gap-4">
    <div className="bg-white p-4 rounded-xl shadow">
      <h2 className="font-semibold mb-2">Add Store (admin)</h2>
      <div className="grid md:grid-cols-3 gap-2">
        <input className="border rounded p-2" value={id} onChange={e=>setId(e.target.value)} placeholder="StoreID"/>
        <input className="border rounded p-2" value={name} onChange={e=>setName(e.target.value)} placeholder="Store Name"/>
        <input className="border rounded p-2" value={region} onChange={e=>setRegion(e.target.value)} placeholder="Region"/>
      </div>
      <button className="mt-2 bg-black text-white rounded px-3 py-2" onClick={add}>Add</button>
    </div>

    <div className="bg-white p-4 rounded-xl shadow">
      <h2 className="font-semibold mb-2">Stores</h2>
      <pre className="bg-gray-50 p-2 rounded text-xs">{JSON.stringify(list,null,2)}</pre>
    </div>
  </div>
}