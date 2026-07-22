import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <Routes>
      <Route path="/" element={<div className="p-8 text-center text-lg font-semibold">EquipTracker</div>} />
    </Routes>
  )
}

export default App
