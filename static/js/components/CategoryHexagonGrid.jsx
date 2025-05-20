import React, { useState, useEffect } from 'react';

/**
 * Futuristic Hexagonal Category Grid Component
 * Displays categories in a hexagonal grid with hover effects
 */
const CategoryHexagonGrid = () => {
  const [hoverCategory, setHoverCategory] = useState(null);
  
  // Sample category data - replace with your actual categories
  const categories = [
    { id: 'python', name: 'Python', code: 'PY', color: '#00c2cb', count: 12 },
    { id: 'data', name: 'Data Analysis', code: 'DA', color: '#3a89c9', count: 8 },
    { id: 'web', name: 'Web Dev', code: 'WD', color: '#ff7b73', count: 10 },
    { id: 'ai', name: 'AI & ML', code: 'AI', color: '#ffb563', count: 6 },
    { id: 'devops', name: 'DevOps', code: 'DO', color: '#78c2ff', count: 5 },
    { id: 'db', name: 'Databases', code: 'DB', color: '#00e676', count: 7 }
  ];
  
  // Animate hexagons on load
  useEffect(() => {
    const hexagons = document.querySelectorAll('.category-hexagon');
    hexagons.forEach((hexagon, index) => {
      setTimeout(() => {
        hexagon.classList.add('animate-in');
      }, index * 100);
    });
  }, []);
  
  return (
    <div className="w-full">
      <div className="mb-4 text-center">
        <h3 className="text-teal-400 text-lg font-medium uppercase tracking-wider">SYSTEM_CATEGORIES</h3>
        <p className="text-white text-opacity-70 text-sm">Select a category to filter systems</p>
      </div>
      
      <div className="flex flex-wrap justify-center gap-4 lg:gap-6 p-2">
        {categories.map((category, index) => (
          <div 
            key={category.id}
            className="flex flex-col items-center relative"
            onMouseEnter={() => setHoverCategory(category.id)}
            onMouseLeave={() => setHoverCategory(null)}
          >
            {/* Connection lines between hexagons */}
            {index > 0 && (
              <div 
                className="absolute h-px bg-gradient-to-r from-transparent via-teal-400 to-transparent opacity-30"
                style={{ 
                  width: '150%', 
                  top: '50%', 
                  left: '-75%',
                  transform: 'rotate(' + (index * 60) % 180 + 'deg)'
                }}
              ></div>
            )}
            
            {/* Main Hexagon */}
            <div 
              className={`category-hexagon relative h-24 w-24 transition-all duration-500 transform opacity-0 scale-90 cursor-pointer ${
                hoverCategory === category.id ? 'scale-110' : 'hover:scale-105'
              }`}
            >
              {/* Outer Border */}
              <div 
                className="absolute inset-0" 
                style={{ 
                  clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                  background: `linear-gradient(135deg, ${category.color}40, transparent)`,
                  border: `1px solid ${category.color}80`
                }}
              >
                {/* Inner Background */}
                <div 
                  className="absolute inset-1 bg-gray-900 bg-opacity-80"
                  style={{ 
                    clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                  }}
                ></div>
              </div>
              
              {/* Content */}
              <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
                <div 
                  className="text-2xl font-bold mb-1"
                  style={{ color: category.color }}
                >{category.code}</div>
                <div className="text-xs text-white text-opacity-90">{category.name}</div>
                <div 
                  className="mt-1 text-xs opacity-80"
                  style={{ color: category.color }}
                >({category.count})</div>
              </div>
              
              {/* Animated Pulsing Effect */}
              {hoverCategory === category.id && (
                <div 
                  className="absolute inset-0 animate-pulse opacity-30" 
                  style={{ 
                    clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
                    background: `${category.color}40`,
                  }}
                ></div>
              )}
              
              {/* Corner Accents */}
              <div className="absolute w-2 h-2 border-t border-l top-6 left-2 border-teal-400 opacity-60"></div>
              <div className="absolute w-2 h-2 border-t border-r top-6 right-2 border-teal-400 opacity-60"></div>
              <div className="absolute w-2 h-2 border-b border-l bottom-6 left-2 border-teal-400 opacity-60"></div>
              <div className="absolute w-2 h-2 border-b border-r bottom-6 right-2 border-teal-400 opacity-60"></div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Central Connecting Node */}
      <div className="flex justify-center mt-4">
        <div className="relative w-12 h-12 rounded-full bg-gray-900 border border-teal-400 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border border-teal-400 opacity-20 animate-ping"></div>
          <div className="text-teal-400 text-xs">CORE</div>
          
          {/* Connection lines to categories */}
          {categories.map((_, index) => (
            <div 
              key={`line-${index}`}
              className="absolute w-16 h-px bg-gradient-to-r from-teal-400 to-transparent opacity-30"
              style={{ 
                transformOrigin: 'left center',
                transform: `rotate(${index * (360 / categories.length)}deg)` 
              }}
            ></div>
          ))}
        </div>
      </div>
      
      <style jsx>{`
        .category-hexagon.animate-in {
          animation: hexagonIn 0.6s forwards cubic-bezier(0.19, 1, 0.22, 1);
        }
        
        @keyframes hexagonIn {
          0% {
            opacity: 0;
            transform: scale(0.9) translateY(20px);
          }
          100% {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default CategoryHexagonGrid;