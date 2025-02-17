//import React from 'react';
import { useState, useEffect, useRef } from 'react'
import Card from './Card';
import axios from 'axios';

import './FormCard.css';

const FormCard = ({ title, type, url, groups, cardboard_server }) => {

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
                let server = cardboard_server         
                if(!server) {
                    server = "http://127.0.0.1:5000"
                }    
                const req = server + "/start?card=" + title + "&type=" + type + "&url=" + encodeURIComponent(url);   
                const startRes = await axios.get(req);
                console.log("start res=" + JSON.stringify(startRes.data))
                startSocket()
                
            } catch(e) {
                console.error("FormCard.startCard(): Error: " + e);
            }
        }

        const stopCard = async() => {
            try {
                let server = cardboard_server         
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



    const handleSliderChange = (e) => {
        const el = e.target
        const label = el.name
        const val = el.value

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


    const handleButtonPressed = (e) => {
        const el = e.target;
        const label = el.name;
        const val = 1;
        console.log("handleButtonPressed: el=" + label + ", value=" + val);

        if(socket.current) {
            socket.current.send(JSON.stringify({"card": title, "button": label, "value": 1}))
        }
    }


    const handleButtonReleased = (e) => {
        const el = e.target;
        const label = el.name;
        const val = 0;
        console.log("handleButtonReleased: el=" + label + ", value=" + val);

        if(socket.current) {
            socket.current.send(JSON.stringify({"card": title, "button": label, "value": 0}))
        }
    }

    const updateSliderBackground = (e) => {
        let slider = e.target;
        const value = slider.value;
        const percentage = (value - 50.) * 2.;
        const r = 4.0; // matches half the thumb width/height. 
        
        //const cutColor = tailwindConfig.theme.extend.colors.sky(900);
        //const boostColor = tailwindConfig.theme.extend.colors.sky(900);
        const cutColor = "#14648C";
        const boostColor = "#14648C";

        if(value >= 50) {
            const x = value - (r)*percentage/100.;
            slider.style.background = `linear-gradient(to right, transparent 0%, transparent 50%, ${boostColor} 50%, ${boostColor} ${x}%, transparent ${x}%, transparent 100%)`;
        } else {
            const x = value - (r)*percentage/100.;
            slider.style.background = `linear-gradient(to right, transparent 0%, transparent ${x}%, ${cutColor} ${x}%, ${cutColor} 50%, transparent 50%, transparent 100%)`;
        }
        
      }

    const sliderClasses = "range range-xs [--range-shdw:transparent] h-[16px] bg-base-100 rangethumb"
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
                            <input className={sliderClasses} type="range" min={item.input.minValue} max={item.input.maxValue} step={item.input.step} name={item.label} label={item.label} defaultValue={item.input.defaultValue} onChange={handleSliderChange}/>
                        }
                        {item.input.type == "button" &&
                            <button className="btn btn-primary btn-sm rounded-md text-white" onMouseDown={handleButtonPressed} onMouseUp={handleButtonReleased}>{item.label}</button>
                        }
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