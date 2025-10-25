import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom'
import './index.css'
import Dashboard from './screens/Dashboard.jsx'
import Sales from './screens/Sales.jsx'
import GiftCards from './screens/GiftCards.jsx'
import Stores from './screens/Stores.jsx'

function useAuth() {
  const [token, setToken] = React.useState(localStorage.getItem('token')||'')
  const [user, setUser] = React.useState(localStorage.getItem('user')?JSON.parse(localStorage.getItem('user')):null)
  const save = (t,u)=>{ setToken(t); setUser(u); localStorage.setItem('token',t); localStorage.setItem('user',JSON.stringify(u)) }
  const clear = ()=>{ setToken(''); setUser(null); localStorage.removeItem('token'); localStorage.removeItem('user') }
  return { token, user, save, clear }
}
const API = async (path, token, options={})=>{
  const res = await fetch(window.API_BASE+path, { headers: {'Authorization':'Bearer '+token, 'Content-Type':'application/json'}, ...options })
  return res.json()
}

function Login({onLogin}){
  const [email,setEmail]=React.useState('sales@retail.com')
  const [password,setPassword]=React.useState('Sales123!')
  const submit=async()=>{
    const res = await fetch(window.API_BASE+'/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})})
    const data = await res.json()
    if(data.token) onLogin(data.token,data.user); else alert(JSON.stringify(data))
  }
  return <div className="h-screen flex items-center justify-center">
    <div className="bg-white p-6 rounded-2xl shadow w-full max-w-sm">
      <h1 className="text-2xl font-bold mb-4">Sign in</h1>
      <input className="w-full border p-2 rounded mb-2" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email"/>
      <input className="w-full border p-2 rounded mb-2" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password"/>
      <button className="w-full bg-black text-white rounded p-2" onClick={submit}>Login</button>
    </div>
  </div>
}

function Shell({auth}){
  const nav = useNavigate()
  return <div className="min-h-screen">
    <header className="bg-white border-b">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="font-bold">Retail Sales v3</div>
        <nav className="flex gap-4 text-sm">
          <Link to="/">Dashboard</Link>
          <Link to="/sales">Sales</Link>
          <Link to="/giftcards">Gift Cards</Link>
          <Link to="/stores">Stores</Link>
        </nav>
        <div className="text-xs">{auth.user?.email} ({auth.user?.role}) <button className="ml-2 underline" onClick={()=>{auth.clear(); nav(0)}}>Logout</button></div>
      </div>
    </header>
    <main className="max-w-6xl mx-auto p-4">
      <Routes>
        <Route path="/" element={<Dashboard auth={auth}/>} />
        <Route path="/sales" element={<Sales auth={auth}/>} />
        <Route path="/giftcards" element={<GiftCards auth={auth}/>} />
        <Route path="/stores" element={<Stores auth={auth}/>} />
      </Routes>
    </main>
  </div>
}

function App(){
  const auth = useAuth()
  if(!auth.token) return <Login onLogin={auth.save}/>
  return <BrowserRouter><Shell auth={auth}/></BrowserRouter>
}

createRoot(document.getElementById('root')).render(<App/>)