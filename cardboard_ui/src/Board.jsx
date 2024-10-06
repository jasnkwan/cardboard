/**
 * Board.js
 */
import React from 'react';
import { useEffect, useState } from 'react'
import Column from '@/Column';

//import Plot from 'react-plotly.js'; // Example Plotly component
import axios from 'axios';

import './Board.css';

const Board = () => {

  const [board, setBoard] = useState([]);

  useEffect(() => {

    /*
    // fetch the card data from flask server
    const getCards = async () => {
        
        try {
            const res = await axios.get("http://127.0.0.1:5000/cards");
            setCards(res.data);
            console.log("cards: ", res.data)
        } catch(error) {
            console.error(error)
        }
    }
    getCards();
    */

    // fetch the card data from flask server
    const getBoard = async () => {
    
        try {
            const res = await axios.get("http://127.0.0.1:5000/board");
            
            console.log("board: ", res.data.board);
            console.log("columns: ", res.data.board.columns);
            
            setBoard(res.data.board);

        } catch(error) {
            console.error(error)
        }
    }
    getBoard();
    
  }, [])



  return (
    <div className="cardboard">
        
        {board && board.columns && board.columns.map((column, index) => (
            <Column key={index} {...column} />
        ))}
        
        {/*
        {cards.map((cardData, index) => (            
            <DataCard key={index} {...cardData} />
        ))}
        */}
    </div>
  )
};

export default Board;
