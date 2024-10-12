import React from 'react';
import { useState, useEffect, useRef } from 'react'
import Card from './Card';
import axios from 'axios';
import Button from '@mui/material/Button';
import Slider from '@mui/material/Slider';

import './FormCard.css';

const FormCard = ({ title, type, url, groups }) => {

    const [sliderValues, setSliderValues] = useState({})

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
                    //console.log(title + ': Message from server: event.data.value=' + o.value);
                    
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
                const startRes = await axios.get("http://127.0.0.1:5000/start?card="+title+"&type="+type+"&url="+encodeURIComponent(url));
                console.log("start res=" + JSON.stringify(startRes.data))
                startSocket()
                
            } catch(e) {
                console.error("FormCard.startCard(): Error: " + e);
            }
        }

        const stopCard = async() => {
            try {
                const stopRes = await axios.get("http://127.0.0.1:5000/stop?card="+title);
                console.log("stop res=" + JSON.stringify(stopRes.data));
                if(socket.current) {
                    socket.current.close();
                    socket.current = null;
                }
            } catch(e) {
                console.error("FormCard.stopCard(): Error: " + e);
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



    const handleSliderChange = (e, val) => {
        const el = e.target
        const label = el.name

        console.log("handleSliderChange: el=" + label + ", value=" + val)

        setSliderValues((prevValues) => ({
            ...prevValues,   // Keep other slider values unchanged
            [label]: val,    // Update the current slider's value
        }));

        // send the slider value to the server socket
        if(socket.current) {
            socket.current.send(JSON.stringify({"card": title, "slider": label, "value": val}))
        }
    };


    const handleButtonPressed = (e, val) => {
        const el = e.target;
        const label = el.name;
        console.log("handleButtonPressed: el=" + label + ", value=" + val);

        if(socket.current) {
            socket.current.send(JSON.stringify({"card": title, "button": label, "value": 1}))
        }
    }


    const handleButtonReleased = (e, val) => {
        const el = e.target;
        const label = el.name;
        console.log("handleButtonReleased: el=" + label + ", value=" + val);

        if(socket.current) {
            socket.current.send(JSON.stringify({"card": title, "button": label, "value": 0}))
        }
    }


    return (
        <Card title={title} type={type} url={url}>
            {data.map((group, index) => (
                <div key={index} className="form-card-group">
                <div className="form-card-group-label">{group.label}</div>
                <div className="form-card-group-items">
                    {group.items.map((item, idx) => (
                    <div key={idx} className="form-card-group-item">
                        {item.input.type == "slider" && <div className="form-card-group-item-header">
                            <div className="form-card-group-item-label">{item.label}</div>
                            <div className="form-card-group-item-value">{sliderValues[item.label] || item.input.defaultValue}</div>
                        </div>}
                        {item.input.type == "slider" && 
                            <Slider defaultValue={item.input.defaultValue} 
                                    min={item.input.minValue} 
                                    max={item.input.maxValue} 
                                    step={item.input.step} 
                                    onChange={handleSliderChange}
                                    size="normal"
                                    name={item.label}      
                                    label={item.label}                              
                                    sx={{
                                        '& .MuiSlider-thumb': {
                                            width: 12, // Customize thumb width
                                            height: 12, // Customize thumb height
                                        },
                                        margin: 0,
                                        padding: 0,
                                    }}
                            />}
                        {item.input.type == "button" &&
                            <Button name={item.label}
                                    label={item.label}
                                    variant="contained"
                                    size="small"
                                    onMouseDown={handleButtonPressed}
                                    onMouseUp={handleButtonReleased}
                                    style={{ fontSize: '.7em' }}>
                                {item.label}
                            </Button>}
                    </div>
                    ))}
                </div>
                </div>
            ))}
            <div className="card-time">{timestamp}</div>
        </Card>
    )
};

export default FormCard;