import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import CVATest from './CVATest.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <CVATest />
  </StrictMode>,
)
