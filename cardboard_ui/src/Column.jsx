/**
 * Column.jsx
 * Column layout card container
 */

import React from "react";
import DataCard from '@/DataCard';
import FormCard from '@/FormCard';
import PlotCard from '@/PlotCard';

import "./Column.css"

const Column = ({ cards }) => {
    return (
        <div className="column">
            {cards.map((card, index) => (
                card.type=="Data" && <DataCard key={index} {...card} /> ||
                card.type=="Form" && <FormCard key={index} {...card} /> ||
                card.type=="Plot" && <PlotCard key={index} {...card} />
            ))}
        </div>
    );
};

export default Column; 