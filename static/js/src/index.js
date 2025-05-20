import React from 'react';
import ReactDOM from 'react-dom';
import TechRadarVisualization from './components/TechRadarVisualization';

// Find all React mount points in your Django templates
document.addEventListener('DOMContentLoaded', () => {
  const techRadarContainers = document.querySelectorAll('.tech-radar-container');
  
  techRadarContainers.forEach(container => {
    // Get data attributes from the container (data passed from Django)
    const skillsData = JSON.parse(container.dataset.skills || '{}');
    
    ReactDOM.render(
      <TechRadarVisualization skills={skillsData} />,
      container
    );
  });
});