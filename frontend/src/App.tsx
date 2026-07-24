import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<div className="p-8 text-center text-lg font-semibold">EquipTracker</div>} />
      </Routes>
      <Toaster richColors closeButton />
    </>
  )
}

export default App
