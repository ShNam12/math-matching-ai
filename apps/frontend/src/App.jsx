import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import SemanticSearch from './pages/SemanticSearch.jsx'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <SemanticSearch />
    </>
  )
}

export default App
