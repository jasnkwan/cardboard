/**
 * Board.js
 */
import React from 'react';
import { useEffect, useState } from 'react';
import Column from '@/Column';

import axios from 'axios';

import './Board.css';

const Board = () => {

    const [board, setBoard] = useState([]);

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
        <div className="cardboard">        
            {board && board.columns && board.columns.map((column, index) => (
                <Column key={index} {...column} />
            ))}
        </div>        
    )
};

export default Board;
