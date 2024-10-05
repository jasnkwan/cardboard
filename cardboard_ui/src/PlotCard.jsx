// src/components/PlotCard.js
import React from 'react';
import Card from './Card';
import './PlotCard.css'; // Assuming additional styles specific to PlotCard

const PlotCard = ({ title, plotComponent }) => {
  return (
    <Card title={title}>
      <div className="plot-container">
        {plotComponent} {/* This could be a Plotly chart, for example */}
      </div>
    </Card>
  );
};

export default PlotCard;
