// src/components/DataCard.js
//import React from 'react';
import { useState, useEffect, useRef } from 'react'
import Card from './Card';
import axios from 'axios';

import './Card.css';
import './DataCard.css';


const DataCard = ({ title, type, url, groups, flask_server }) => {

    const [data, setData] = useState(groups);
    const [timestamp, setTimestamp] = useState("");

    const socket = useRef(null);
    const timer = useRef(null);
    
    useEffect(() => {

        const startSocket = async () => {
            if(socket.current != null && (socket.current.readyState == WebSocket.OPEN || socket.current.readyState == WebSocket.CONNECTING)) {
                console.log("Socket already connected.");
                return;
            }
            console.log("Starting client socket...")
            // start the socket client
            try {
                
                // Create a WebSocket connection to the Python server
                socket.current = new WebSocket(url);

                // Event listener when the connection is opened
                socket.current.addEventListener('open', function (event) {
                    console.log('Connected to WebSocket server: ' + url);
                });

                // Event listener for messages received from the server
                socket.current.addEventListener('message', function (event) {
                    const o = JSON.parse(event.data)
                    //console.log(title + ': Message from server: label=' + o.label + ', value=' + o.value);
                    
                    //setData(event.data)
                    if(o.label == "Current time") {
                        setTimestamp(o.value)
                    }
                });

                // Event listener for errors
                socket.current.addEventListener('error', function (event) {
                    console.error('WebSocket error: ', event);
                    socket.current.close();
                });

                // Event listener for when the connection is closed
                socket.current.addEventListener('close', function (event) {
                    console.log('WebSocket connection closed');
                    socket.current = null;
                });
                
            } catch(e) {
                console.error("Error: " + e);
                if(socket.current) {
                    socket.current.close();
                    socket.current = null;
                }
            }
        }
 
        const startCard = async() => {
            try {  
                let server = flask_server         
                if(!server) {
                    server = "http://127.0.0.1:5000"
                }     
                const req = server + "/start?card=" + title + "&type=" + type + "&url=" + encodeURIComponent(url);           
                const startRes = await axios.get(req);
                console.log("start res=" + JSON.stringify(startRes.data))
                startSocket()
                
            } catch(e) {
                console.error("DataCard.startCard(): Error: " + e);
            }
        }

        const stopCard = async() => {
            try {
                let server = flask_server         
                if(!server) {
                    server = "http://127.0.0.1:5000"
                }    
                const req = server + "/stop?card=" + title;
                const stopRes = await axios.get(req);
                console.log("stop res=" + JSON.stringify(stopRes.data));
                if(socket.current) {
                    socket.current.close();
                    socket.current = null;
                }
            } catch(e) {
                console.error("DataCard.stopCard(): Error: " + e);
            }
        }
        
        startCard();

        const checkSocket = () => {
            if(socket.current == null) {
                console.log("Socket is null, trying to restart...");
                startSocket()
            } else if(socket.current.readyState == WebSocket.CLOSED) {
                console.log("Socket is closed, trying to restart...");
                startSocket()
            }            
        }
        timer.current = setInterval(checkSocket, 1000);

        return () => {
            // unmounting, cleanup refs
            if(timer.current) {
                clearInterval(timer.current);
            }
            if(socket.current) {
                socket.current.close();
            }
        }

    }, []);


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
