/**
 * Card.js
 * Base component for cards.  This will render a title and the content container
 */

import React from "react";
import "./Card.css"

const Card = ({ title, type, url, children }) => {

    return (
        <div className="card">
            <div className="card-title">{title}</div>
            <div className="card-type">{type}</div>
            <div className="card-url">{url}</div>
            <div className="card-content">
                {children} {/* Render custom content passed by extending components */}
            </div>
        </div>
    );
};
  
export default Card;
