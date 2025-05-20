import React, { useState, useEffect } from 'react';

/**
 * Futuristic Systems Dashboard Component
 * Displays project metrics and statistics in a visually appealing way
 */
const SystemsDashboard = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hoveredSystem, setHoveredSystem] = useState(null);
  
  // Sample system metrics - replace with your actual data
  const systemMetrics = {
    totalSystems: 6,
    activeProjects: 4,
    completedProjects: 2,
    systemsByCategory: [
      { name: 'Web Dev', count: 3, percentage: 50, color: '#00c2cb' },
      { name: 'Data Science', count: 2, percentage: 33, color: '#ff7b73' },
      { name: 'DevOps', count: 1, percentage: 17, color: '#ffb563' }
    ],
    latestSystem: {
      name: 'AI-Powered Data Analysis Platform',
      completion: 85,
      date: '2025-05-01',
      category: 'Data Science'
    },
    systems: [
      { 
        id: 1, 
        name: 'AI-Powered Data Analysis Platform', 
        category: 'Data Science',
        completion: 85,
        status: 'active',
        technologies: ['Python', 'Django', 'TensorFlow', 'PostgreSQL', 'Docker'],
        lastUpdated: '2025-05-01',
        slug: 'ai-data-analysis'
      },
      { 
        id: 2, 
        name: 'Tech Portfolio with Futuristic UI', 
        category: 'Web Dev',
        completion: 95,
        status: 'active',
        technologies: ['Django', 'React', 'Tailwind CSS', 'JavaScript'],
        lastUpdated: '2025-04-28',
        slug: 'tech-portfolio'
      },
      { 
        id: 3, 
        name: 'Automated CI/CD Pipeline', 
        category: 'DevOps',
        completion: 100,
        status: 'completed',
        technologies: ['GitHub Actions', 'Docker', 'AWS', 'Python'],
        lastUpdated: '2025-04-15',
        slug: 'cicd-pipeline'
      },
      { 
        id: 4, 
        name: 'RESTful API Service', 
        category: 'Web Dev',
        completion: 100,
        status: 'completed',
        technologies: ['Django REST Framework', 'PostgreSQL', 'Swagger', 'JWT'],
        lastUpdated: '2025-03-30',
        slug: 'restful-api'
      }
    ]
  };
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoaded(true);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Format date like "MAY 1, 2025"
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).toUpperCase();
  };
  
  // Calculate avg progress
  const avgCompletion = systemMetrics.systems.reduce(
    (sum, system) => sum + system.completion, 0
  ) / systemMetrics.systems.length;
  
  return (
    <div className="w-full">
      {/* Loading overlay */}
      <div 
        className={`fixed inset-0 z-50 bg-gray-900 bg-opacity-90 flex flex-col items-center justify-center transition-opacity duration-500 ${
          isLoaded ? 'opacity-0 pointer-events-none' : 'opacity-100'
        }`}
      >
        <div className="w-24 h-24 relative">
          <div className="absolute inset-0 rounded-full border-2 border-teal-400 opacity-20"></div>
          <div className="absolute inset-3 rounded-full border-2 border-teal-400 opacity-40"></div>
          <div className="absolute inset-6 rounded-full border-2 border-teal-400 opacity-60"></div>
          <div className="absolute inset-9 rounded-full bg-teal-400 opacity-80 animate-ping"></div>
        </div>
        <div className="mt-6 text-teal-400 uppercase tracking-wider">
          <span>INITIALIZING SYSTEMS</span>
          <span className="inline-block ml-1 w-6">
            <span className="animate-pulse">.</span>
            <span className="animate-pulse" style={{ animationDelay: '0.3s' }}>.</span>
            <span className="animate-pulse" style={{ animationDelay: '0.6s' }}>.</span>
          </span>
        </div>
      </div>
      
      {/* Main Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Status Overview - Left Column */}
        <div className="lg:col-span-1">
          <div className="bg-gray-900 bg-opacity-40 border border-teal-500 border-opacity-20 rounded overflow-hidden backdrop-filter backdrop-blur-sm mb-6">
            <div className="bg-gray-900 bg-opacity-50 px-4 py-3 border-b border-teal-500 border-opacity-20">
              <div className="text-teal-400 uppercase tracking-wider text-sm font-medium flex items-center">
                <div className="w-2 h-2 rounded-full bg-teal-400 mr-2 animate-pulse"></div>
                <span>SYSTEM_STATUS</span>
              </div>
            </div>
            
            <div className="p-4">
              {/* Large circular progress indicator */}
              <div className="flex justify-center mb-6">
                <div className="relative w-40 h-40">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle 
                      cx="80" 
                      cy="80" 
                      r="70" 
                      fill="none" 
                      stroke="rgba(0, 194, 203, 0.1)" 
                      strokeWidth="8" 
                    />
                    <circle 
                      cx="80" 
                      cy="80" 
                      r="70" 
                      fill="none" 
                      stroke="rgba(0, 194, 203, 0.8)" 
                      strokeWidth="8" 
                      strokeDasharray="440" 
                      strokeDashoffset={440 - (440 * avgCompletion / 100)}
                      strokeLinecap="round"
                      style={{ 
                        transition: 'stroke-dashoffset 1.5s ease',
                        filter: 'drop-shadow(0 0 6px rgba(0, 194, 203, 0.5))'
                      }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="text-4xl font-medium text-white">{Math.round(avgCompletion)}%</div>
                    <div className="text-xs text-teal-400 uppercase tracking-wider mt-1">COMPLETION</div>
                  </div>
                </div>
              </div>
              
              {/* Status metrics grid */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-900 bg-opacity-50 p-3 rounded border border-teal-500 border-opacity-10 text-center">
                  <div className="text-3xl font-medium text-white mb-1">{systemMetrics.totalSystems}</div>
                  <div className="text-xs text-teal-400 uppercase tracking-wider">TOTAL_SYSTEMS</div>
                </div>
                <div className="bg-gray-900 bg-opacity-50 p-3 rounded border border-teal-500 border-opacity-10 text-center">
                  <div className="text-3xl font-medium text-white mb-1">{systemMetrics.activeProjects}</div>
                  <div className="text-xs text-teal-400 uppercase tracking-wider">ACTIVE_SYSTEMS</div>
                </div>
                <div className="bg-gray-900 bg-opacity-50 p-3 rounded border border-teal-500 border-opacity-10 text-center">
                  <div className="text-3xl font-medium text-white mb-1">{systemMetrics.completedProjects}</div>
                  <div className="text-xs text-teal-400 uppercase tracking-wider">COMPLETED</div>
                </div>
                <div className="bg-gray-900 bg-opacity-50 p-3 rounded border border-teal-500 border-opacity-10 text-center">
                  <div className="text-3xl font-medium text-white mb-1">12</div>
                  <div className="text-xs text-teal-400 uppercase tracking-wider">TECHNOLOGIES</div>
                </div>
              </div>
              
              {/* Latest system */}
              <div className="mb-4">
                <div className="text-sm uppercase tracking-wider mb-2 text-white text-opacity-80">LATEST_SYSTEM_UPDATE</div>
                <div className="bg-gray-900 bg-opacity-50 p-3 rounded border border-teal-500 border-opacity-10">
                  <div className="text-white font-medium mb-2">{systemMetrics.latestSystem.name}</div>
                  <div className="flex justify-between items-center">
                    <div className="text-xs text-teal-400">{formatDate(systemMetrics.latestSystem.date)}</div>
                    <div className="text-xs text-white text-opacity-70">{systemMetrics.latestSystem.category}</div>
                  </div>
                  <div className="mt-2 h-1 bg-gray-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-teal-400"
                      style={{ 
                        width: `${systemMetrics.latestSystem.completion}%`,
                        transition: 'width 1s ease'
                      }}
                    ></div>
                  </div>
                  <div className="text-right text-xs text-white text-opacity-70 mt-1">
                    {systemMetrics.latestSystem.completion}% COMPLETE
                  </div>
                </div>
              </div>
              
              {/* Category distribution */}
              <div>
                <div className="text-sm uppercase tracking-wider mb-2 text-white text-opacity-80">SYSTEM_CATEGORIES</div>
                {systemMetrics.systemsByCategory.map((category, index) => (
                  <div key={index} className="mb-3">
                    <div className="flex justify-between text-xs mb-1">
                      <div className="text-white text-opacity-90">{category.name}</div>
                      <div className="text-teal-400">{category.percentage}%</div>
                    </div>
                    <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full"
                        style={{ 
                          width: `${category.percentage}%`,
                          backgroundColor: category.color,
                          transition: 'width 1s ease'
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* Main Systems Overview - Center and Right Columns */}
        <div className="lg:col-span-2">
          <div className="bg-gray-900 bg-opacity-40 border border-teal-500 border-opacity-20 rounded overflow-hidden backdrop-filter backdrop-blur-sm">
            <div className="bg-gray-900 bg-opacity-50 px-4 py-3 border-b border-teal-500 border-opacity-20 flex justify-between items-center">
              <div className="text-teal-400 uppercase tracking-wider text-sm font-medium flex items-center">
                <div className="w-2 h-2 rounded-full bg-teal-400 mr-2 animate-pulse"></div>
                <span>ACTIVE_SYSTEMS_OVERVIEW</span>
              </div>
              <a 
                href="/systems" 
                className="text-xs text-teal-400 hover:underline flex items-center"
              >
                VIEW_ALL
                <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </a>
            </div>
            
            <div className="p-4">
              <div className="grid grid-cols-1 gap-4">
                {systemMetrics.systems.map((system) => (
                  <div 
                    key={system.id}
                    className="bg-gray-900 bg-opacity-50 rounded border border-teal-500 border-opacity-10 p-4 transition-all duration-300 hover:border-opacity-30 hover:shadow-lg"
                    onMouseEnter={() => setHoveredSystem(system.id)}
                    onMouseLeave={() => setHoveredSystem(null)}
                  >
                    <div className="flex justify-between mb-3">
                      <div>
                        <div className="flex items-center mb-1">
                          <div className={`w-2 h-2 rounded-full mr-2 ${
                            system.status === 'active' ? 'bg-teal-400 animate-pulse' : 'bg-green-400'
                          }`}></div>
                          <h3 className="text-white font-medium">{system.name}</h3>
                        </div>
                        <div className="text-xs text-white text-opacity-70">
                          <span className="uppercase">{system.category}</span>
                          <span className="mx-2">•</span>
                          <span>Last Updated: {formatDate(system.lastUpdated)}</span>
                        </div>
                      </div>
                      <div className="text-xs text-white text-opacity-60 font-mono">
                        SYS_ID: {system.id.toString().padStart(3, '0')}
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="mb-2">
                      <div className="flex justify-between text-xs mb-1">
                        <div className="text-white text-opacity-70">COMPLETION</div>
                        <div className="text-teal-400">{system.completion}%</div>
                      </div>
                      <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-teal-400 rounded-full"
                          style={{ 
                            width: `${system.completion}%`,
                            transition: 'width 1s ease',
                            boxShadow: hoveredSystem === system.id ? '0 0 8px rgba(0, 194, 203, 0.5)' : 'none'
                          }}
                        ></div>
                      </div>
                    </div>
                    
                    {/* Technologies */}
                    <div className="flex flex-wrap gap-2 mt-3">
                      {system.technologies.map((tech, techIndex) => (
                        <span 
                          key={techIndex}
                          className="text-xs px-2 py-1 bg-gray-900 bg-opacity-70 text-teal-300 text-opacity-80 rounded-sm"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                    
                    {/* Action Button */}
                    <div className="mt-3 text-right">
                      <a 
                        href={`/systems/${system.slug}`}
                        className="inline-flex items-center px-3 py-1 bg-gray-800 bg-opacity-60 border border-teal-500 border-opacity-30 rounded text-xs text-teal-400 transition-all duration-300 hover:bg-opacity-80 hover:border-opacity-50"
                      >
                        <span>ACCESS_SYSTEM</span>
                        <svg className="w-3 h-3 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                      </a>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* System Resources Utilization */}
              <div className="mt-6">
                <div className="text-sm uppercase tracking-wider mb-3 text-white text-opacity-80">SYSTEM_RESOURCES</div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-900 bg-opacity-50 p-3 rounded border border-teal-500 border-opacity-10">
                    <div className="flex justify-between items-center mb-2">
                      <div className="text-xs text-white text-opacity-80">CPU_UTILIZATION</div>
                      <div className="text-xs text-teal-400">35%</div>
                    </div>
                    <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-teal-400 rounded-full"
                        style={{ width: '35%', transition: 'width 1s ease' }}
                      ></div>
                    </div>
                  </div>
                  <div className="bg-gray-900 bg-opacity-50 p-3 rounded border border-teal-500 border-opacity-10">
                    <div className="flex justify-between items-center mb-2">
                      <div className="text-xs text-white text-opacity-80">MEMORY_USAGE</div>
                      <div className="text-xs text-teal-400">47%</div>
                    </div>
                    <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-teal-400 rounded-full"
                        style={{ width: '47%', transition: 'width 1s ease' }}
                      ></div>
                    </div>
                  </div>
                  <div className="bg-gray-900 bg-opacity-50 p-3 rounded border border-teal-500 border-opacity-10">
                    <div className="flex justify-between items-center mb-2">
                      <div className="text-xs text-white text-opacity-80">DATABASE_LOAD</div>
                      <div className="text-xs text-teal-400">23%</div>
                    </div>
                    <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-teal-400 rounded-full"
                        style={{ width: '23%', transition: 'width 1s ease' }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemsDashboard;