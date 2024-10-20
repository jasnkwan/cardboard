import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Board from './Board.jsx'
import './index.css'

createRoot(document.getElementById('cardboard-root')).render(
  <StrictMode>
    <Board cardboard_server={cardboard_server}/>
  </StrictMode>,
)
