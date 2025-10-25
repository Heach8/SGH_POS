import React from 'react'

export default function GiftCards({auth}){
  const [cardNumber,setCardNumber]=React.useState('9845-2211-7788')
  const [initBal,setInitBal]=React.useState('500')
  const [reloadAmt,setReloadAmt]=React.useState('100')
  const [balanceRes,setBalanceRes]=React.useState(null)
  const api = async (path, body)=>{
    const res = await fetch(window.API_BASE+path,{method:'POST',headers:{'Authorization':'Bearer '+auth.token,'Content-Type':'application/json'},body:JSON.stringify(body)})
    return res.json()
  }
  return <div className="grid md:grid-cols-2 gap-6">
    <div className="bg-white p-4 rounded-xl shadow">
      <h2 className="font-semibold mb-2">Create Gift Card</h2>
      <input className="border rounded p-2 w-full mb-2" placeholder="Card Number" value={cardNumber} onChange={e=>setCardNumber(e.target.value)} />
      <input className="border rounded p-2 w-full mb-2" placeholder="Initial Balance" value={initBal} onChange={e=>setInitBal(e.target.value)} />
      <button className="w-full bg-black text-white rounded p-2" onClick={async()=>{const r=await api('/giftcards/create',{card_number:cardNumber, initial_balance:parseFloat(initBal||'0')}); alert(JSON.stringify(r))}}>Create</button>
    </div>

    <div className="bg-white p-4 rounded-xl shadow">
      <h2 className="font-semibold mb-2">Reload & Balance</h2>
      <input className="border rounded p-2 w-full mb-2" placeholder="Card Number" value={cardNumber} onChange={e=>setCardNumber(e.target.value)} />
      <div className="flex gap-2">
        <input className="border rounded p-2 w-full mb-2" placeholder="Reload Amount" value={reloadAmt} onChange={e=>setReloadAmt(e.target.value)} />
        <button className="border rounded px-3" onClick={async()=>{const r=await api('/giftcards/reload',{card_number:cardNumber, amount:parseFloat(reloadAmt||'0')}); alert(JSON.stringify(r))}}>Reload</button>
      </div>
      <button className="w-full border rounded p-2" onClick={async()=>{const r=await api('/giftcards/balance',{card_number:cardNumber}); setBalanceRes(r)}}>Check Balance</button>
      <pre className="bg-gray-50 p-2 rounded text-xs h-40 overflow-auto">{balanceRes?JSON.stringify(balanceRes,null,2):''}</pre>
    </div>
  </div>
}