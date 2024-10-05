/**
 * Board.js
 */
import React from 'react';
import { useEffect, useState } from 'react'
import Card from '@/Card';
import DataCard from '@/DataCard';
import PlotCard from '@/PlotCard';
import Plot from 'react-plotly.js'; // Example Plotly component
import axios from 'axios';

const Board = () => {

  const [cards, setCards] = useState([]);

  useEffect(() => {
    /*
    console.log("Board")
    const socket = io("http://127.0.0.1:5000")
    
    socket.on("foo", function (data) {
      console.log("on foo: ", data)
    })
  
    socket.on("bar", function (data) {
      console.log("on bar: ", data)
    })

    const getCards = async () => {
      const res = await axios.get("http://127.0.0.1:5000/cards")
      if(res) {
        console.log("res.data=", res.data)
      }
    };
    getCards();
    */

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
    
  }, [])

  return (
    <div className="cardboard">
        {cards.map((cardData, index) => (            
            <DataCard key={index} {...cardData} />
        ))}
    </div>
  )

  /*
  const dataGroups = [
    {
      label: "Group 1",
      items: [
        { label: "Label 1", value: "Value 1" },
        { label: "Label 2", value: "Value 2" },
      ]
    },
    {
      label: "Group 2",
      items: [
        { label: "Label 3", value: "Value 3" },
        { label: "Label 4", value: "Value 4" },
      ]
    }
  ];

  return (
    <div>
      <h1>Dashboard</h1>

      <DataCard title="Data Card" groups={dataGroups} />
      <PlotCard title="Plot Card" plotComponent={<Plot data={[{x: [1, 2, 3], y: [2, 6, 3]}]} layout={{width: 320, height: 240, title: 'A Plot'}} />} />
    </div>
  );
  */
};

export default Board;
