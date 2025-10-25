import React from 'react'

export default function Sales({auth}){
  const [products,setProducts]=React.useState([])
  const [cart,setCart]=React.useState([])
  const [pricing,setPricing]=React.useState(null)
  const [payments,setPayments]=React.useState([])
  const [payType,setPayType]=React.useState('Cash')
  const [payAmount,setPayAmount]=React.useState('')
  const [payRef,setPayRef]=React.useState('')
  const [result,setResult]=React.useState(null)

  const api = async (path, options={})=>{
    const res = await fetch(window.API_BASE+path, {headers:{'Authorization':'Bearer '+auth.token,'Content-Type':'application/json'}, ...options})
    return res.json()
  }

  React.useEffect(()=>{ (async()=>{
    setProducts(await api('/products'))
  })() },[])

  const add = (p)=> setCart(v=>[...v,{product_id:p.id, brand:p.brand, name:p.name, unit_price:parseFloat(p.list_price), qty:1}])
  const price = async()=> setPricing(await api('/cart/price',{method:'POST', body:JSON.stringify(cart)}))
  const addPayment = ()=> { setPayments(v=>[...v,{type:payType, amount:parseFloat(payAmount||'0'), reference:payRef}]); setPayAmount(''); setPayRef('') }
  const submit = async()=>{
    const body={store_id: auth.user?.store_id||'STR-001', salesperson_id: String(auth.user?.id||'EMP-LOCAL'), cart, payments}
    const r = await api('/sales',{method:'POST', body:JSON.stringify(body)}); setResult(r)
  }

  return <div className="grid md:grid-cols-2 gap-6">
    <div className="bg-white p-4 rounded-xl shadow">
      <h2 className="font-semibold mb-2">Products</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {products.map(p=>(
          <div key={p.id} className="border rounded-lg p-3">
            <div className="font-medium">{p.name}</div>
            <div className="text-sm text-gray-600">{p.brand}</div>
            <div className="text-sm">{p.list_price}</div>
            <button className="mt-2 w-full border rounded p-2" onClick={()=>add(p)}>Add</button>
          </div>
        ))}
      </div>
    </div>

    <div className="bg-white p-4 rounded-xl shadow">
      <h2 className="font-semibold mb-2">Cart</h2>
      <pre className="bg-gray-50 p-2 rounded text-xs h-40 overflow-auto">{JSON.stringify(cart,null,2)}</pre>
      <button className="mt-2 w-full bg-black text-white rounded p-2" onClick={price}>Price (apply campaigns)</button>
      <pre className="bg-gray-50 p-2 rounded text-xs h-28 overflow-auto">{pricing?JSON.stringify(pricing,null,2):''}</pre>
    </div>

    <div className="bg-white p-4 rounded-xl shadow">
      <h2 className="font-semibold mb-2">Payments</h2>
      <select className="border rounded p-2 w-full mb-2" value={payType} onChange={e=>setPayType(e.target.value)}>
        <option>Cash</option><option>CreditCard</option><option>BankTransfer</option><option>GiftCard</option>
      </select>
      <input className="border rounded p-2 w-full mb-2" placeholder="Amount" value={payAmount} onChange={e=>setPayAmount(e.target.value)}/>
      <input className="border rounded p-2 w-full mb-2" placeholder="Reference (card # for GiftCard)" value={payRef} onChange={e=>setPayRef(e.target.value)}/>
      <button className="w-full border rounded p-2" onClick={addPayment}>Add Payment</button>
      <pre className="bg-gray-50 p-2 rounded text-xs h-28 overflow-auto">{JSON.stringify(payments,null,2)}</pre>
      <button className="mt-2 w-full bg-emerald-600 text-white rounded p-2" onClick={submit}>Submit Sale</button>
      <pre className="bg-gray-50 p-2 rounded text-xs h-40 overflow-auto">{result?JSON.stringify(result,null,2):''}</pre>
    </div>
  </div>
}