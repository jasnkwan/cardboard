/**
 * Board.js
 */
import React from 'react';
import { useEffect, useState } from 'react';
import Column from '@/Column';

import { ThemeProvider, createTheme } from '@mui/material/styles';

import axios from 'axios';

import './Board.css';

const Board = () => {

  const [board, setBoard] = useState([]);

  let theme = createTheme({
    "palette": {
      "primary": {
        "light": "#BAE6FD",
        "main": "#14648C",
        "dark": "#082F49",
        "contrastText": "#fff"
      },
      "secondary": {
        "light": "#ff7961",
        "main": "#f44336",
        "dark": "#ba000d",
        "contrastText": "#000"
      }
    }
  });

  useEffect(() => {

    // fetch the card data from flask server
    const getBoard = async () => {
        try {
            const req = CARDBOARD_SERVER + "/board"            
            const res = await axios.get(req, {
                headers: {
                  'Access-Control-Allow-Origin': '*',
                  // Other headers as needed
                }
            });

            setBoard(res.data.board);

        } catch(error) {
            console.error(error)
        }
    }
    getBoard();        
    
    return () => {
        console.log("Board will unmount");
    }

  }, [])



  return (
    <ThemeProvider theme={theme}>
    <div className="cardboard">        
        {board && board.columns && board.columns.map((column, index) => (
            <Column key={index} {...column} />
        ))}
    </div>
    </ThemeProvider>
  )
};

export default Board;
