/**
 * Board.js
 */
import React from 'react';
import { useEffect, useState } from 'react';
import Column from '@/Column';

import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

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

            const res = await axios.get("http://127.0.0.1:5000/board",             {
                headers: {
                  'Access-Control-Allow-Origin': '*',
                  // Other headers as needed
                }
            });
                        
            //if(res.data.board.palette) {
              //theme = createTheme({"palette": res.data.board.palette})
            //}

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
