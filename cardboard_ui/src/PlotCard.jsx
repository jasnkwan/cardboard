// src/components/PlotCard.js
//import React from 'react';
import { useState, useEffect, useRef } from 'react'
import Card from './Card';
import axios from 'axios';
import Plot from 'react-plotly.js';

import './PlotCard.css'; // Assuming additional styles specific to PlotCard


const PlotCard = ({ title, type, url, plot_data, plot_layout, plot_opts, grow, flask_server }) => {

    const [data, setData] = useState(plot_data);
    const [timestamp, setTimestamp] = useState("");

    const socket = useRef(null);
    const timer = useRef(null);

    const classNames = grow==true ? "plot-container grow-plot-container" : "plot-container";
    console.log("grow=" + grow + ", classNames=" + classNames)

    // Fix the range for log scale
    if(plot_layout.xaxis.type && plot_layout.xaxis.type == "log" && plot_layout.xaxis.range) {
        console.log("Update log range")
        plot_layout.xaxis.range[0] = Math.log10(plot_layout.xaxis.range[0]);
        plot_layout.xaxis.range[1] = Math.log10(plot_layout.xaxis.range[1]);
    }

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
                    //console.log(title + ': Message from server: event.data.value=' + o.value);
                    
                    //setData(event.data)
                    setTimestamp(o.value)
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
                let provider = "cardboard.sockets.UDPSocketProvider"
                const req = server + "/start?card=" + title + "&type=" + type + "&url=" + encodeURIComponent(url) + "&provider=" + encodeURIComponent(provider);           
                const startRes = await axios.get(req);
                console.log("start res=" + JSON.stringify(startRes.data))
                startSocket()
                
            } catch(e) {
                console.error("PlotCard.startCard(): Error: " + e);
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
                console.error("PlotCard.stopCard(): Error: " + e);
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
        <Card title={title} style={{ }}>
        <div className="plot-container">
            <Plot data={[plot_data]} layout={plot_layout} config={plot_opts} style={{ width: "100%", height: "100%" }} />
        </div>
        </Card>
    );
};

export default PlotCard;
