/**
 * Board.js
 */
//import React from 'react';
import { useEffect, useState } from 'react';
import Column from './Column';

import axios from 'axios';

import './index.css'
import './Board.css';

const Board = ({cardboard_server}) => {

    const [board, setBoard] = useState([]);

    useEffect(() => {

        // fetch the card data from flask server
        const getBoard = async () => {
            try {
                let server = cardboard_server         
                if(!server) {
                    server = "http://127.0.0.1:5000"
                }    
                const req = server + "/board"            
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
                <Column key={index} cardboard_server={cardboard_server} {...column} />
            ))}
        </div>        
    )
};

export default Board;
