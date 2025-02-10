import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Board from './Board.jsx'
import './index.css'

createRoot(document.getElementById('cardboard-root')).render(
  <StrictMode>
    <Board flask_server={flask_server}/>
  </StrictMode>,
)
