/**
 * Column.jsx
 * Column layout card container
 */

//import React from "react";
import DataCard from './DataCard';
import FormCard from './FormCard';
import PlotCard from './PlotCard';

import "./Column.css"

const Column = ({ cards, grow, cardboard_server }) => {

    const classNames = grow==true ? "column grow-column" : "column";
    console.log("grow=" + grow + ", classNames=" + classNames)
    return (
        <div className={classNames}>
            {cards.map((card, index) => (
                card.type=="Data" && <DataCard key={index} cardboard_server={cardboard_server} {...card} /> ||
                card.type=="Form" && <FormCard key={index} cardboard_server={cardboard_server} {...card} /> ||
                card.type=="Plot" && <PlotCard key={index} cardboard_server={cardboard_server} {...card} />
            ))}
        </div>
    );
};

export default Column; 