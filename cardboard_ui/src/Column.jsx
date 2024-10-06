/**
 * Column.jsx
 * Column layout card container
 */

import React from "react";
import Card from "@/Card";
import DataCard from '@/DataCard';
import PlotCard from '@/PlotCard';

import "./Column.css"

const Column = ({ cards }) => {
    return (
        <div className="column">
            {cards.map((card, index) => (
                <DataCard key={index} {...card} />
            ))}
        </div>
    );
};

export default Column; 