import React, { useState, useEffect } from 'react';

/**
 * Futuristic DataLog Timeline Component
 * Displays blog posts in a vertical timeline with tech-inspired styling
 */
const DataLogTimeline = () => {
  const [selectedTag, setSelectedTag] = useState(null);
  const [animatedIndex, setAnimatedIndex] = useState(-1);
  
  // Sample blog posts data - replace with your actual posts
  const posts = [
    {
      id: 1,
      title: "Building Efficient Data Pipelines",
      date: "2025-05-10",
      excerpt: "A comprehensive guide to designing and implementing efficient data pipelines using Python, Apache Airflow, and related technologies.",
      tags: ["Python", "Data Engineering", "Airflow"],
      slug: "building-data-pipelines"
    },
    {
      id: 2,
      title: "Django ORM Optimization Techniques",
      date: "2025-05-05",
      excerpt: "Advanced strategies for optimizing Django ORM queries to improve performance in large-scale applications.",
      tags: ["Django", "Performance", "Database"],
      slug: "django-orm-optimization"
    },
    {
      id: 3,
      title: "Machine Learning Model Deployment",
      date: "2025-04-28",
      excerpt: "Best practices for deploying machine learning models in production using containerization and CI/CD pipelines.",
      tags: ["Machine Learning", "DevOps", "Docker"],
      slug: "ml-model-deployment"
    },
    {
      id: 4,
      title: "RESTful API Design Principles",
      date: "2025-04-15",
      excerpt: "A deep dive into RESTful API design principles and best practices for creating robust, scalable APIs.",
      tags: ["API", "REST", "Web Development"],
      slug: "restful-api-design"
    },
    {
      id: 5,
      title: "Python Concurrency Explained",
      date: "2025-04-05",
      excerpt: "Understanding Python's concurrency models including threading, multiprocessing, and asynchronous programming.",
      tags: ["Python", "Concurrency", "Performance"],
      slug: "python-concurrency"
    }
  ];
  
  // Extract all unique tags
  const allTags = [...new Set(posts.flatMap(post => post.tags))].sort();
  
  // Filter posts by selected tag
  const filteredPosts = selectedTag
    ? posts.filter(post => post.tags.includes(selectedTag))
    : posts;
  
  // Format date to "MAY 10, 2025" format
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    }).toUpperCase();
  };
  
  // Animate logs sequentially on load
  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      if (index < filteredPosts.length) {
        setAnimatedIndex(index);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 150);
    
    return () => clearInterval(interval);
  }, [filteredPosts]);
  
  // Reset animation when tag changes
  useEffect(() => {
    setAnimatedIndex(-1);
    setTimeout(() => {
      setAnimatedIndex(0);
    }, 100);
  }, [selectedTag]);
  
  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Tags Filter */}
      <div className="mb-6">
        <div className="text-center mb-3">
          <div className="text-teal-400 uppercase tracking-wider text-sm font-medium">LOG_TAGS</div>
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          <button
            className={`text-xs px-3 py-1 border border-opacity-30 rounded transition-all duration-300 ${
              selectedTag === null
                ? "bg-teal-500 bg-opacity-20 border-teal-400"
                : "border-teal-600 bg-opacity-0 hover:bg-teal-500 hover:bg-opacity-10"
            }`}
            onClick={() => setSelectedTag(null)}
          >
            ALL_LOGS
          </button>
          
          {allTags.map(tag => (
            <button
              key={tag}
              className={`text-xs px-3 py-1 border border-opacity-30 rounded transition-all duration-300 ${
                selectedTag === tag
                  ? "bg-teal-500 bg-opacity-20 border-teal-400"
                  : "border-teal-600 bg-opacity-0 hover:bg-teal-500 hover:bg-opacity-10"
              }`}
              onClick={() => setSelectedTag(tag)}
            >
              {tag.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
      
      {/* Timeline Header */}
      <div className="flex items-center mb-6">
        <div className="w-2 h-8 bg-teal-400 rounded-sm mr-4"></div>
        <div className="text-lg text-white uppercase tracking-wider">DATALOG_TIMELINE</div>
      </div>
      
      {/* Logs Counter */}
      <div className="flex items-center mb-6">
        <div className="bg-gray-900 bg-opacity-60 border border-teal-500 border-opacity-30 px-4 py-2 rounded">
          <span className="text-teal-400 font-medium">{filteredPosts.length}</span>
          <span className="text-white text-opacity-80 ml-2 text-sm">LOGS_FOUND</span>
        </div>
      </div>
      
      {/* Timeline */}
      <div className="relative">
        {/* Vertical timeline line */}
        <div className="absolute left-0 top-0 bottom-0 w-px bg-teal-500 bg-opacity-20"></div>
        
        {filteredPosts.map((post, index) => (
          <div 
            key={post.id}
            className={`relative pl-8 pb-10 transition-all duration-500 transform ${
              index <= animatedIndex ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-6"
            }`}
            style={{ transitionDelay: `${index * 0.1}s` }}
          >
            {/* Timeline node */}
            <div className="absolute left-0 top-0 transform -translate-x-1/2">
              <div className="w-6 h-6 rounded-full bg-gray-900 border border-teal-400 flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-teal-400"></div>
              </div>
            </div>
            
            {/* Log Card */}
            <div className="datalog-card bg-gray-900 bg-opacity-40 border border-teal-500 border-opacity-20 rounded overflow-hidden backdrop-filter backdrop-blur-sm">
              {/* Card Header */}
              <div className="flex justify-between items-center bg-gray-900 bg-opacity-60 px-4 py-3 border-b border-teal-500 border-opacity-20">
                <div className="flex items-center">
                  <div className="w-2 h-2 rounded-full bg-teal-400 mr-2 animate-pulse"></div>
                  <h3 className="text-white font-medium truncate mr-4">{post.title}</h3>
                </div>
                <div className="text-teal-400 text-xs">{formatDate(post.date)}</div>
              </div>
              
              {/* Card Content */}
              <div className="p-4">
                <p className="text-white text-opacity-80 text-sm mb-4">{post.excerpt}</p>
                
                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {post.tags.map(tag => (
                    <span 
                      key={tag}
                      className={`text-xs px-2 py-1 rounded-sm ${
                        selectedTag === tag
                          ? "bg-teal-500 bg-opacity-20 text-teal-400"
                          : "bg-gray-800 bg-opacity-70 text-teal-300 text-opacity-80"
                      }`}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                
                {/* Waveform Visualization */}
                <div className="h-8 relative mb-4 overflow-hidden">
                  <div className="absolute inset-0 flex items-center">
                    <div className="h-px bg-teal-500 bg-opacity-20 w-full"></div>
                  </div>
                  {Array.from({ length: 40 }).map((_, i) => {
                    const height = Math.sin(i * 0.5) * 12 + Math.random() * 5;
                    return (
                      <div
                        key={i}
                        className="absolute bottom-1/2 w-1 bg-teal-400 opacity-40 transform translate-y-px transition-all duration-1000"
                        style={{ 
                          height: `${Math.abs(height)}px`,
                          left: `${i * 2.5}%`,
                          animationDelay: `${i * 0.05}s`
                        }}
                      ></div>
                    );
                  })}
                </div>
                
                {/* Action Button */}
                <div className="flex justify-between items-center">
                  <a 
                    href={`/datalogs/${post.slug}`}
                    className="inline-flex items-center px-3 py-1 bg-gray-800 bg-opacity-60 border border-teal-500 border-opacity-30 rounded text-xs text-teal-400 transition-all duration-300 hover:bg-opacity-80 hover:border-opacity-50"
                  >
                    <span>ACCESS_LOG</span>
                    <svg className="w-3 h-3 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </a>
                  
                  <div className="text-xs text-white text-opacity-60">
                    <span className="font-mono">LOG_ID: </span>
                    <span>{post.id.toString().padStart(4, "0")}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Timeline end node */}
        <div className="absolute left-0 bottom-0 transform -translate-x-1/2">
          <div className="w-4 h-4 rounded-full bg-gray-900 border border-teal-400 flex items-center justify-center"></div>
        </div>
      </div>
      
      {/* Empty state */}
      {filteredPosts.length === 0 && (
        <div className="text-center py-12 px-4">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-800 bg-opacity-50 mb-4">
            <svg className="w-8 h-8 text-teal-400 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-white text-lg mb-2">NO_LOGS_FOUND</h3>
          <p className="text-white text-opacity-70 text-sm">No logs matching the selected filter were found in the database.</p>
          <button 
            onClick={() => setSelectedTag(null)}
            className="mt-4 px-4 py-2 bg-gray-800 bg-opacity-50 border border-teal-500 border-opacity-30 rounded text-sm text-teal-400"
          >
            RESET_FILTERS
          </button>
        </div>
      )}
    </div>
  );
};

export default DataLogTimeline;