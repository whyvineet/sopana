import { Routes, Route } from 'react-router-dom'
import Navbar from '@/components/layout/Navbar'
import Landing from '@/pages/Landing'
import Conversation from '@/pages/Conversation'
import Profile from '@/pages/Profile'
import Path from '@/pages/Path'
import Dashboard from '@/pages/Dashboard'

function App() {
  return (
    <div className="min-h-screen bg-paper text-gray-900">
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/journey" element={<Conversation />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/path" element={<Path />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </div>
  )
}

export default App
