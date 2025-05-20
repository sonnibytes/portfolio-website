// TechRadarVisualization.jsx
// This could be used on your about page or projects page for an interactive visualization

import React, { useState, useEffect } from 'react';

const TechRadarVisualization = () => {
  const [activeCategory, setActiveCategory] = useState('all');
  const [hoveredSkill, setHoveredSkill] = useState(null);
  
  // Sample data - you would replace this with your actual skills data
  const skillsData = {
    languages: [
      { name: 'Python', proficiency: 95, description: 'Primary development language', years: 5 },
      { name: 'JavaScript', proficiency: 85, description: 'Frontend development', years: 4 },
      { name: 'SQL', proficiency: 90, description: 'Database queries', years: 5 },
      { name: 'HTML/CSS', proficiency: 88, description: 'Web markup and styling', years: 5 },
    ],
    frameworks: [
      { name: 'Django', proficiency: 92, description: 'Primary web framework', years: 4 },
      { name: 'Flask', proficiency: 85, description: 'Microservices and APIs', years: 3 },
      { name: 'React', proficiency: 80, description: 'Frontend interfaces', years: 3 },
      { name: 'Bootstrap', proficiency: 85, description: 'Responsive design', years: 4 },
    ],
    tools: [
      { name: 'Git', proficiency: 90, description: 'Version control', years: 5 },
      { name: 'Docker', proficiency: 82, description: 'Containerization', years: 3 },
      { name: 'AWS', proficiency: 78, description: 'Cloud deployment', years: 3 },
      { name: 'Jupyter', proficiency: 88, description: 'Data analysis', years: 4 },
    ],
    data: [
      { name: 'PostgreSQL', proficiency: 88, description: 'Relational database', years: 4 },
      { name: 'MongoDB', proficiency: 80, description: 'NoSQL database', years: 3 },
      { name: 'Pandas', proficiency: 92, description: 'Data manipulation', years: 4 },
      { name: 'NumPy', proficiency: 85, description: 'Scientific computing', years: 4 },
    ]
  };
  
  // Get all skills as a flat array
  const getAllSkills = () => {
    let allSkills = [];
    Object.keys(skillsData).forEach(category => {
      allSkills = [...allSkills, ...skillsData[category]];
    });
    return allSkills;
  };
  
  // Get skills to display based on active category
  const getSkillsToDisplay = () => {
    if (activeCategory === 'all') {
      return getAllSkills();
    }
    return skillsData[activeCategory] || [];
  };
  
  // Calculate positions for the radar chart
  const calculatePositions = (skills) => {
    const centerX = 250;
    const centerY = 250;
    const maxRadius = 200;
    
    return skills.map((skill, index) => {
      const angle = (index * 2 * Math.PI) / skills.length;
      const radius = (skill.proficiency / 100) * maxRadius;
      
      return {
        ...skill,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        angle
      };
    });
  };
  
  const skillsWithPositions = calculatePositions(getSkillsToDisplay());
  
  // Draw radar circles
  const renderRadarCircles = () => {
    const circles = [25, 50, 75, 100];
    const centerX = 250;
    const centerY = 250;
    const maxRadius = 200;
    
    return circles.map((percentage, index) => {
      const radius = (percentage / 100) * maxRadius;
      return (
        <circle
          key={`circle-${index}`}
          cx={centerX}
          cy={centerY}
          r={radius}
          fill="none"
          stroke="#00c2cb"
          strokeWidth="1"
          strokeOpacity="0.3"
        />
      );
    });
  };
  
  // Draw radar lines
  const renderRadarLines = () => {
    const skills = getSkillsToDisplay();
    const lines = [];
    const centerX = 250;
    const centerY = 250;
    const maxRadius = 200;
    
    for (let i = 0; i < skills.length; i++) {
      const angle = (i * 2 * Math.PI) / skills.length;
      const x = centerX + maxRadius * Math.cos(angle);
      const y = centerY + maxRadius * Math.sin(angle);
      
      lines.push(
        <line
          key={`line-${i}`}
          x1={centerX}
          y1={centerY}
          x2={x}
          y2={y}
          stroke="#00c2cb"
          strokeWidth="1"
          strokeOpacity="0.3"
        />
      );
    }
    
    return lines;
  };
  
  // Draw the polygon connecting the skill points
  const renderSkillPolygon = () => {
    if (skillsWithPositions.length < 3) return null;
    
    const points = skillsWithPositions.map(skill => `${skill.x},${skill.y}`).join(' ');
    
    return (
      <polygon
        points={points}
        fill="#ff7b73"
        fillOpacity="0.2"
        stroke="#ff7b73"
        strokeWidth="2"
      />
    );
  };
  
  // Draw skill points
  const renderSkillPoints = () => {
    return skillsWithPositions.map((skill, index) => (
      <g key={`skill-${index}`}>
        <circle
          cx={skill.x}
          cy={skill.y}
          r={hoveredSkill === skill.name ? 8 : 6}
          fill={hoveredSkill === skill.name ? "#ff7b73" : "#00c2cb"}
          onMouseEnter={() => setHoveredSkill(skill.name)}
          onMouseLeave={() => setHoveredSkill(null)}
        />
        <text
          x={skill.x + 15 * Math.cos(skill.angle)}
          y={skill.y + 15 * Math.sin(skill.angle)}
          fontSize="12"
          fill="#00c2cb"
          textAnchor="middle"
          dominantBaseline="middle"
        >
          {skill.name}
        </text>
      </g>
    ));
  };
  
  // Render skill details when hovering
  const renderSkillDetails = () => {
    if (!hoveredSkill) return null;
    
    const skill = getAllSkills().find(s => s.name === hoveredSkill);
    if (!skill) return null;
    
    return (
      <div className="absolute bottom-4 left-4 bg-primary border border-accent-teal p-4 w-64">
        <div className="text-accent-coral text-lg">{skill.name}</div>
        <div className="text-accent-teal text-sm">{skill.description}</div>
        <div className="mt-2 flex justify-between items-center">
          <div className="text-xs">PROFICIENCY: {skill.proficiency}%</div>
          <div className="text-xs">EXPERIENCE: {skill.years} YRS</div>
        </div>
        <div className="mt-2 bg-accent-teal bg-opacity-20 h-2">
          <div 
            className="bg-accent-coral h-full" 
            style={{ width: `${skill.proficiency}%` }}
          ></div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="tech-container relative" style={{ height: '600px' }}>
      <div className="tech-header">SKILL_RADAR</div>
      
      <div className="flex justify-center mb-4">
        <div className="flex space-x-4">
          <button 
            onClick={() => setActiveCategory('all')} 
            className={`text-xs px-3 py-1 border border-accent-teal ${activeCategory === 'all' ? 'bg-accent-teal bg-opacity-10' : ''}`}
          >
            ALL
          </button>
          {Object.keys(skillsData).map(category => (
            <button 
              key={category} 
              onClick={() => setActiveCategory(category)} 
              className={`text-xs px-3 py-1 border border-accent-teal ${activeCategory === category ? 'bg-accent-teal bg-opacity-10' : ''}`}
            >
              {category.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex justify-center">
        <svg width="500" height="500" viewBox="0 0 500 500">
          {/* Add a subtle glow effect around the center */}
          <radialGradient id="radar-glow" cx="50%" cy="50%" r="50%" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#00c2cb" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#051e3e" stopOpacity="0" />
          </radialGradient>
          <circle cx="250" cy="250" r="200" fill="url(#radar-glow)" />
          
          {/* Draw radar elements */}
          {renderRadarCircles()}
          {renderRadarLines()}
          {renderSkillPolygon()}
          {renderSkillPoints()}
          
          {/* Add percentage labels */}
          <text x="250" y="45" fill="#00c2cb" fontSize="10" textAnchor="middle">100%</text>
          <text x="250" y="95" fill="#00c2cb" fontSize="10" textAnchor="middle">75%</text>
          <text x="250" y="145" fill="#00c2cb" fontSize="10" textAnchor="middle">50%</text>
          <text x="250" y="195" fill="#00c2cb" fontSize="10" textAnchor="middle">25%</text>
          
          {/* Add center pulsing dot */}
          <circle cx="250" cy="250" r="6" fill="#ff7b73">
            <animate 
              attributeName="r" 
              values="4;8;4" 
              dur="2s" 
              repeatCount="indefinite" 
            />
            <animate 
              attributeName="opacity" 
              values="1;0.8;1" 
              dur="2s" 
              repeatCount="indefinite" 
            />
          </circle>
          
          {/* Add a scanning line animation */}
          <line 
            x1="250" 
            y1="250" 
            x2="450" 
            y2="250" 
            stroke="#00c2cb" 
            strokeWidth="2" 
            strokeOpacity="0.5"
          >
            <animateTransform 
              attributeName="transform" 
              type="rotate" 
              from="0 250 250" 
              to="360 250 250" 
              dur="8s" 
              repeatCount="indefinite" 
            />
          </line>
        </svg>
      </div>
      
      {renderSkillDetails()}
    </div>
  );
};

export default TechRadarVisualization;