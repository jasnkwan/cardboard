// src/components/DataCard.js
import React from 'react';
import { useState, useEffect, useRef } from 'react'
import Card from './Card';
import './DataCard.css'; // Assuming additional styles specific to DataCard
import axios from 'axios';

const DataCard = ({ title, type, port, groups }) => {

    const [data, setData] = useState(groups);
    const [timestamp, setTimestamp] = useState("")
    const socket = useRef(null)

    useEffect(() => {
 
        // start the socket server
        const startSocket = async () => {
            try {
                //const res = await axios.get("/api/start?card=" + title);
                //if(res.data) {
                    //console.log("res: " + res.data);

                    // Create a WebSocket connection to the Python server
                    socket.current = new WebSocket('ws://127.0.0.1:' + port);

                    // Event listener when the connection is opened
                    socket.current.addEventListener('open', function (event) {
                        console.log('Connected to WebSocket server');
                    });

                    // Event listener for messages received from the server
                    socket.current.addEventListener('message', function (event) {
                        //console.log('Message from server: ', event.data);
                        //document.getElementById('time').innerText = `Server Time: ${event.data}`;
                        //setData(event.data)
                        setTimestamp(event.data)
                    });

                    // Event listener for errors
                    socket.current.addEventListener('error', function (event) {
                        console.error('WebSocket error: ', event);
                    });

                    // Event listener for when the connection is closed
                    socket.current.addEventListener('close', function (event) {
                        console.log('WebSocket connection closed');
                    });
                //}
            } catch(e) {
                console.log("Error: " + e);
            }
        }
        startSocket();
        
    }, [socket]);


    return (
        <Card title={title} type={type} port={port}>
            <div className="card-time">{timestamp}</div>
            <div>Groups:</div>
            {data.map((group, index) => (
                <div key={index} className="card-group">
                <div className="card-group-label">{group.label}</div>
                
                <div className="card-group-items">
                    {group.items.map((item, idx) => (
                    <div key={idx} className="card-group-item">
                        <div className="card-group-item-label">{item.label}</div>
                        <div className="card-group-item-value">{item.value}</div>
                    </div>
                    ))}
                </div>
                </div>
            ))}
        </Card>
    );
};

export default DataCard;
