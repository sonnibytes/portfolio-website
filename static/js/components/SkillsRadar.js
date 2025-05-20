import { useState, useEffect } from 'react';

/**
 * Futuristic Skills Radar Chart Component
 */
const SkillsRadar = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [hoveredSkill, setHoveredSkill] = useState(null);
  
  // Sample skills data - replace with your actual skills
  const skills = [
    { name: 'Python', level: 95, category: 'languages' },
    { name: 'Django', level: 90, category: 'frameworks' },
    { name: 'JavaScript', level: 75, category: 'languages' },
    { name: 'SQL', level: 85, category: 'languages' },
    { name: 'React', level: 65, category: 'frameworks' },
    { name: 'Docker', level: 80, category: 'tools' },
    { name: 'AWS', level: 75, category: 'tools' },
    { name: 'Git', level: 90, category: 'tools' },
    { name: 'Data Analysis', level: 85, category: 'domains' },
    { name: 'Machine Learning', level: 70, category: 'domains' },
    { name: 'API Design', level: 85, category: 'domains' }
  ];
  
  // Filter skills based on selected category
  const filteredSkills = selectedCategory === 'all' 
    ? skills 
    : skills.filter(skill => skill.category === selectedCategory);
  
  // Categories for the filter
  const categories = [
    { id: 'all', name: 'ALL SKILLS' },
    { id: 'languages', name: 'LANGUAGES' },
    { id: 'frameworks', name: 'FRAMEWORKS' },
    { id: 'tools', name: 'TOOLS' },
    { id: 'domains', name: 'DOMAINS' }
  ];
  
  // Calculate positions for radar chart
  const getSkillCoordinates = (skills) => {
    const totalSkills = skills.length;
    const radius = 120;
    const centerX = 150;
    const centerY = 150;
    
    return skills.map((skill, index) => {
      const angle = (Math.PI * 2 * index) / totalSkills - Math.PI / 2;
      const skillRadius = (skill.level / 100) * radius;
      
      return {
        ...skill,
        x: centerX + skillRadius * Math.cos(angle),
        y: centerY + skillRadius * Math.sin(angle),
        labelX: centerX + (radius + 20) * Math.cos(angle),
        labelY: centerY + (radius + 20) * Math.sin(angle),
        angle
      };
    });
  };
  
  const skillsWithCoordinates = getSkillCoordinates(filteredSkills);
  
  // Generate polygon points for the radar shape
  const polygonPoints = skillsWithCoordinates
    .map(skill => `${skill.x},${skill.y}`)
    .join(' ');
  
  // Generate circular rings
  const rings = [0.25, 0.5, 0.75, 1].map(ratio => {
    const ringRadius = 120 * ratio;
    return { ratio, radius: ringRadius };
  });
  
  // Animate entrance when category changes
  useEffect(() => {
    const timer = setTimeout(() => {
      document.querySelectorAll('.skill-node').forEach((node, i) => {
        node.style.transition = `transform 0.5s ease ${i * 0.05}s, opacity 0.5s ease ${i * 0.05}s`;
        node.style.transform = 'scale(1)';
        node.style.opacity = '1';
      });
      
      document.querySelector('.skill-polygon').style.opacity = '0.6';
    }, 100);
    
    return () => clearTimeout(timer);
  }, [selectedCategory]);
  
  return (
    <div className="flex flex-col items-center">
      <div className="mb-6 flex flex-wrap justify-center gap-2">
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`text-xs px-3 py-1 border border-opacity-30 rounded ${
              selectedCategory === category.id
                ? 'bg-teal-500 bg-opacity-20 border-teal-400'
                : 'border-teal-600 bg-opacity-0 hover:bg-teal-500 hover:bg-opacity-10'
            } transition-all duration-300`}
          >
            {category.name}
          </button>
        ))}
      </div>
      
      <div className="relative w-80 h-80">
        {/* Background circular rings */}
        <svg className="absolute inset-0" width="300" height="300">
          <circle cx="150" cy="150" r="140" fill="none" stroke="rgba(0, 194, 203, 0.03)" strokeWidth="1" />
          
          {rings.map((ring, i) => (
            <circle 
              key={i}
              cx="150" 
              cy="150" 
              r={ring.radius} 
              fill="none" 
              stroke="rgba(0, 194, 203, 0.1)" 
              strokeWidth="1" 
              strokeDasharray={ring.ratio === 1 ? "none" : "2,4"}
            />
          ))}
          
          {/* Axis lines for each skill */}
          {skillsWithCoordinates.map((skill, i) => (
            <line 
              key={`axis-${i}`}
              x1="150" 
              y1="150" 
              x2={150 + 120 * Math.cos(skill.angle)} 
              y2={150 + 120 * Math.sin(skill.angle)} 
              stroke="rgba(0, 194, 203, 0.2)" 
              strokeWidth="1" 
              strokeDasharray="2,2" 
            />
          ))}
          
          {/* Skill level polygon */}
          <polygon 
            className="skill-polygon"
            points={polygonPoints} 
            fill="rgba(0, 194, 203, 0.15)" 
            stroke="rgba(0, 194, 203, 0.8)" 
            strokeWidth="2"
            style={{ 
              opacity: 0, 
              transition: 'opacity 0.8s ease-in-out',
              filter: 'drop-shadow(0 0 8px rgba(0, 194, 203, 0.5))'
            }}
          />
        </svg>
        
        {/* Skill nodes */}
        {skillsWithCoordinates.map((skill, i) => (
          <div 
            key={`node-${i}`}
            className="skill-node absolute w-3 h-3 rounded-full bg-teal-400 shadow-lg transform -translate-x-1.5 -translate-y-1.5 cursor-pointer transition-all duration-300"
            style={{ 
              left: skill.x,
              top: skill.y,
              transform: 'scale(0)', 
              opacity: 0,
              boxShadow: '0 0 10px rgba(0, 194, 203, 0.8)',
              zIndex: hoveredSkill === i ? 10 : 5
            }}
            onMouseEnter={() => setHoveredSkill(i)}
            onMouseLeave={() => setHoveredSkill(null)}
          >
            {hoveredSkill === i && (
              <div className="absolute left-4 top-0 transform -translate-y-1/2 bg-gray-900 bg-opacity-90 border border-teal-500 py-1 px-3 rounded whitespace-nowrap z-20">
                <div className="text-teal-400 text-sm font-medium">{skill.name}</div>
                <div className="text-white text-xs font-medium">{skill.level}%</div>
              </div>
            )}
          </div>
        ))}
        
        {/* Skill labels */}
        {skillsWithCoordinates.map((skill, i) => (
          <div 
            key={`label-${i}`}
            className="absolute text-xs text-teal-400 text-opacity-90 transform -translate-x-1/2 -translate-y-1/2 transition-opacity duration-300"
            style={{ 
              left: skill.labelX, 
              top: skill.labelY,
              opacity: 0.8,
              textShadow: '0 0 5px rgba(0, 194, 203, 0.3)'
            }}
          >
            {skill.name}
          </div>
        ))}
        
        {/* Center point */}
        <div className="absolute left-1/2 top-1/2 w-4 h-4 bg-teal-500 bg-opacity-20 border border-teal-400 rounded-full transform -translate-x-1/2 -translate-y-1/2">
          <div className="absolute inset-0 bg-teal-400 rounded-full animate-ping opacity-30"></div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="mt-6 text-center text-xs text-white text-opacity-70">
        <div className="mb-1">SKILL PROFICIENCY RADAR</div>
        <div className="flex items-center justify-center space-x-6">
          {rings.map((ring, i) => (
            <div key={i} className="flex items-center">
              <div className="w-2 h-2 rounded-full bg-teal-400 mr-1 opacity-60"></div>
              <span>{ring.ratio * 100}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SkillsRadar;