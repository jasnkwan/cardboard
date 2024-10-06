// src/components/DataCard.js
import React from 'react';
import { useState, useEffect, useRef } from 'react'
import Card from './Card';
import './DataCard.css';
import axios from 'axios';

const DataCard = ({ title, type, url, groups }) => {

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
                    console.log("url=" + url);
                    // Create a WebSocket connection to the Python server
                    socket.current = new WebSocket(url);

                    // Event listener when the connection is opened
                    socket.current.addEventListener('open', function (event) {
                        console.log('Connected to WebSocket server');
                    });

                    // Event listener for messages received from the server
                    socket.current.addEventListener('message', function (event) {
                        const o = JSON.parse(event.data)
                        //console.log('Message from server: event.data.value=' + o.value);
                        
                        //setData(event.data)
                        setTimestamp(o.value)
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
        <Card title={title} type={type} url={url}>
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
            <div className="card-time">{timestamp}</div>
        </Card>
    );
};

export default DataCard;
