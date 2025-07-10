## 🎯 **What This Gives You**

**1. Flexible Template Tag**: `{% dashboard_panel %}` that intelligently wraps content with minimal configuration needed

**2. Multiple Panel Styles**:
- `dashboard` - Standard panels with prominent headers
- `grid` - Grid layout for related systems/components  
- `activity` - Timeline-style for recent activity feeds
- `component` - Component grid for tech stacks, dependencies
- `chart` - Chart containers with interactive controls
- `alert` - Alert/notification panels with dismissal
- `metric` - Large metric displays with counters
- `status` - Status displays with health indicators

**3. Smart Color System**: Uses AURA color palette (teal, purple, coral, lavender, mint, yellow, navy, gunmetal)

**4. Auto-Detection**: Automatically extracts titles from wrapped content (looks for h1-h6 tags)

**5. Interactive JavaScript**: Real-time updates, animations, hover effects, and chart controls

## 🚀 **Usage Examples**

```html
{% load systems_tags %}

<!-- Simple system health with auto-detected title -->
{% dashboard_panel style="dashboard" color="mint" %}
    <h3>System Health Overview</h3>
    <div class="health-metrics">...</div>
{% enddashboard_panel %}

<!-- Activity feed -->
{% dashboard_panel style="activity" color="lavender" %}
    <h4>Recent Activity</h4>
    {% for activity in recent_activities %}...{% endfor %}
{% enddashboard_panel %}

<!-- Technology stack -->
{% dashboard_panel style="component" color="coral" %}
    <h4>Tech Stack</h4>
    {% for tech in technologies %}...{% endfor %}
{% enddashboard_panel %}
```

## 🎨 **Key Features**

- **Glass-morphism styling** that fits AURA theme
- **Responsive design** with mobile-first approach
- **Accessibility support** with proper ARIA attributes
- **Animation system** with entrance effects and interactions
- **Real-time updates** for metrics and status
- **Interactive controls** for charts and dismissible alerts
- **Auto-layout adjustment** when panels are added/removed

## 🔧 **Integration Steps**

1. **Add the template tag** to `projects/templatetags/systems_tags.py`
2. **Create the component template** at `projects/templates/projects/components/dashboard_panel.html`
3. **Add the JavaScript** to `static/projects/js/dashboard_panels.js`
4. **Include in your templates**:
   ```html
   {% load systems_tags %}
   <script src="{% static 'projects/js/dashboard_panels.js' %}"></script>
   ```

This system gives a flexible way to wrap content in dashboard panels with minimal configuration, while getting maximum visual impact and functionality. The tag intelligently handles most styling automatically while letting you specify the important bits (style and color).

<!-- Usage Examples for Dashboard Panel Template Tag -->

<!-- Load the template tags -->
{% load systems_tags %}

<!-- Example 1: Basic System Health Dashboard -->
{% dashboard_panel style="dashboard" color="mint" %}
    <h3>System Health Overview</h3>
    <div class="health-metrics">
        <div class="metric-item">
            <span class="metric-label">CPU Usage</span>
            <span class="metric-value">45%</span>
            <div class="metric-bar">
                <div class="metric-fill" style="width: 45%"></div>
            </div>
        </div>
        <div class="metric-item">
            <span class="metric-label">Memory</span>
            <span class="metric-value">67%</span>
            <div class="metric-bar">
                <div class="metric-fill" style="width: 67%"></div>
            </div>
        </div>
        <div class="metric-item">
            <span class="metric-label">Disk Space</span>
            <span class="metric-value">23%</span>
            <div class="metric-bar">
                <div class="metric-fill" style="width: 23%"></div>
            </div>
        </div>
    </div>
{% enddashboard_panel %}

<!-- Example 2: Recent Activity Feed -->
{% dashboard_panel style="activity" color="lavender" %}
    <h4>Recent System Activity</h4>
    {% for activity in recent_activities %}
    <div class="activity-item">
        <div class="activity-timestamp">{{ activity.timestamp|timesince }} ago</div>
        <div class="activity-description">{{ activity.description }}</div>
        <div class="activity-system">{{ activity.system.name }}</div>
    </div>
    {% endfor %}
{% enddashboard_panel %}

<!-- Example 3: Technology Stack Component Grid -->
{% dashboard_panel style="component" color="coral" %}
    <h4>Technology Stack</h4>
    {% for tech in system.technologies.all %}
    <div class="tech-component">
        <div class="tech-icon">
            {% if tech.icon %}
                <img src="{{ tech.icon.url }}" alt="{{ tech.name }}">
            {% else %}
                <span class="material-icons">code</span>
            {% endif %}
        </div>
        <div class="tech-name">{{ tech.name }}</div>
        <div class="tech-version">v{{ tech.version }}</div>
    </div>
    {% endfor %}
{% enddashboard_panel %}

<!-- Example 4: Performance Chart -->
{% dashboard_panel style="chart" color="teal" chart_type="line" %}
    <h4>Performance Trends</h4>
    <canvas id="performance-chart" width="400" height="200"></canvas>
    <script>
        // Chart.js initialization would go here
        initializePerformanceChart('performance-chart', {{ chart_data|safe }});
    </script>
{% enddashboard_panel %}

<!-- Example 5: System Alerts -->
{% dashboard_panel style="alert" color="yellow" level="warning" dismissible="true" %}
    <strong>Memory Usage High</strong>
    <p>System memory usage has exceeded 80%. Consider optimizing or scaling resources.</p>
    <div class="alert-actions">
        <button class="btn btn-sm btn-primary">View Details</button>
        <button class="btn btn-sm btn-secondary">Dismiss</button>
    </div>
{% enddashboard_panel %}

<!-- Example 6: Key Metrics Display -->
{% dashboard_panel style="metric" color="purple" precision="1" %}
    <div class="metric-grid">
        <div class="metric-large">
            <div class="metric-number" data-target="{{ system.uptime_percentage }}">0</div>
            <div class="metric-unit">%</div>
            <div class="metric-label">Uptime</div>
        </div>
        <div class="metric-small">
            <div class="metric-number" data-target="{{ system.response_time }}">0</div>
            <div class="metric-unit">ms</div>
            <div class="metric-label">Response Time</div>
        </div>
        <div class="metric-small">
            <div class="metric-number" data-target="{{ system.active_connections }}">0</div>
            <div class="metric-unit"></div>
            <div class="metric-label">Active Connections</div>
        </div>
    </div>
{% enddashboard_panel %}

<!-- Example 7: System Status -->
{% dashboard_panel style="status" color="mint" %}
    <div class="status-overview">
        <div class="status-main">
            <h4>{{ system.name }}</h4>
            <div class="status-badge status-{{ system.status|lower }}">
                {{ system.get_status_display }}
            </div>
        </div>
        <div class="status-details">
            <div class="status-item">
                <span class="status-label">Last Check:</span>
                <span class="status-value">{{ system.last_health_check|timesince }} ago</span>
            </div>
            <div class="status-item">
                <span class="status-label">Version:</span>
                <span class="status-value">{{ system.version }}</span>
            </div>
        </div>
    </div>
{% enddashboard_panel %}

<!-- Example 8: Grid Layout for Related Systems -->
{% dashboard_panel style="grid" color="navy" %}
    <h4>Related Systems</h4>
    {% for related_system in system.get_related_systems %}
    <div class="system-card">
        <div class="system-header">
            <h5>{{ related_system.name }}</h5>
            <span class="system-status status-{{ related_system.status|lower }}"></span>
        </div>
        <p class="system-description">{{ related_system.description|truncatewords:10 }}</p>
        <div class="system-meta">
            <span class="system-type">{{ related_system.get_system_type_display }}</span>
            <span class="system-priority">{{ related_system.get_priority_display }}</span>
        </div>
    </div>
    {% endfor %}
{% enddashboard_panel %}

<!-- Example 9: Auto-title Detection (no explicit title needed) -->
{% dashboard_panel style="dashboard" color="gunmetal" %}
    <h3>Dependencies Overview</h3>
    <div class="dependencies-list">
        {% for dependency in system.dependencies.all %}
        <div class="dependency-item">
            <div class="dependency-icon">
                <span class="material-icons">{{ dependency.get_icon }}</span>
            </div>
            <div class="dependency-info">
                <div class="dependency-name">{{ dependency.name }}</div>
                <div class="dependency-version">{{ dependency.version }}</div>
                <div class="dependency-status status-{{ dependency.status|lower }}">
                    {{ dependency.get_status_display }}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
{% enddashboard_panel %}

<!-- Example 10: Complex Dashboard with Multiple Metrics -->
{% dashboard_panel style="dashboard" color="teal" title="System Overview" subtitle="Real-time monitoring dashboard" icon="dashboard" %}
    <div class="dashboard-grid">
        <div class="dashboard-section">
            <h5>Performance Metrics</h5>
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons">speed</span>
                    </div>
                    <div class="metric-data">
                        <div class="metric-value">{{ system.avg_response_time }}ms</div>
                        <div class="metric-label">Avg Response</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons">memory</span>
                    </div>
                    <div class="metric-data">
                        <div class="metric-value">{{ system.memory_usage }}%</div>
                        <div class="metric-label">Memory Usage</div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons">storage</span>
                    </div>
                    <div class="metric-data">
                        <div class="metric-value">{{ system.cpu_usage }}%</div>
                        <div class="metric-label">CPU Usage</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="dashboard-section">
            <h5>System Health</h5>
            <div class="health-indicators">
                <div class="health-item">
                    <div class="health-dot status-{{ system.database_status|lower }}"></div>
                    <span>Database</span>
                </div>
                <div class="health-item">
                    <div class="health-dot status-{{ system.api_status|lower }}"></div>
                    <span>API</span>
                </div>
                <div class="health-item">
                    <div class="health-dot status-{{ system.cache_status|lower }}"></div>
                    <span>Cache</span>
                </div>
            </div>
        </div>
    </div>
{% enddashboard_panel %}

<style>
/* Additional styles for the usage examples */

/* Health Metrics */
.health-metrics {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.metric-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.metric-label {
    flex: 0 0 120px;
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
}

.metric-value {
    flex: 0 0 60px;
    font-weight: 600;
    color: var(--color-text);
    text-align: right;
}

.metric-bar {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.metric-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--panel-accent), rgba(var(--panel-accent-rgb), 0.7));
    border-radius: 4px;
    transition: width 0.3s ease;
}

/* Activity Items */
.activity-item {
    padding: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--border-radius-sm);
    border-left: 3px solid var(--panel-accent);
}

.activity-timestamp {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-xs);
}

.activity-description {
    font-size: var(--font-size-sm);
    color: var(--color-text);
    margin-bottom: var(--spacing-xs);
}

.activity-system {
    font-size: var(--font-size-xs);
    color: var(--panel-accent);
    font-weight: 500;
}

/* Technology Components */
.tech-component {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--border-radius-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.2s ease;
}

.tech-component:hover {
    background: rgba(var(--panel-accent-rgb), 0.1);
    border-color: var(--panel-accent);
    transform: translateY(-2px);
}

.tech-icon {
    width: 40px;
    height: 40px;
    margin-bottom: var(--spacing-sm);
    display: flex;
    align-items: center;
    justify-content: center;
}

.tech-icon img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.tech-icon .material-icons {
    font-size: 32px;
    color: var(--panel-accent);
}

.tech-name {
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: var(--spacing-xs);
}

.tech-version {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
}

/* Alert Actions */
.alert-actions {
    margin-top: var(--spacing-md);
    display: flex;
    gap: var(--spacing-sm);
}

/* Metric Grid */
.metric-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: var(--spacing-lg);
    align-items: center;
    text-align: center;
}

.metric-large .metric-number {
    font-size: 3rem;
    font-weight: 700;
    color: var(--panel-accent);
    line-height: 1;
}

.metric-small .metric-number {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text);
    line-height: 1;
}

.metric-unit {
    font-size: 1rem;
    color: var(--color-text-secondary);
    margin-left: var(--spacing-xs);
}

.metric-label {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin-top: var(--spacing-xs);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Status Badges */
.status-badge {
    display: inline-flex;
    align-items: center;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-badge.status-online,
.status-badge.status-active,
.status-badge.status-healthy {
    background: rgba(76, 175, 80, 0.2);
    color: #4caf50;
}

.status-badge.status-offline,
.status-badge.status-error,
.status-badge.status-down {
    background: rgba(244, 67, 54, 0.2);
    color: #f44336;
}

.status-badge.status-maintenance,
.status-badge.status-warning {
    background: rgba(255, 193, 7, 0.2);
    color: #ffc107;
}

.status-badge.status-unknown,
.status-badge.status-pending {
    background: rgba(158, 158, 158, 0.2);
    color: #9e9e9e;
}

/* Status Overview */
.status-overview {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: var(--spacing-lg);
}

.status-details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--spacing-md);
}

.status-label {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
}

.status-value {
    font-size: var(--font-size-sm);
    color: var(--color-text);
    font-weight: 500;
}

/* System Cards */
.system-card {
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--border-radius-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.2s ease;
}

.system-card:hover {
    background: rgba(var(--panel-accent-rgb), 0.1);
    border-color: var(--panel-accent);
}

.system-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);
}

.system-header h5 {
    margin: 0;
    font-size: var(--font-size-md);
    color: var(--color-text);
}

.system-status {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.system-description {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-sm);
    line-height: 1.4;
}

.system-meta {
    display: flex;
    gap: var(--spacing-sm);
    font-size: var(--font-size-xs);
}

.system-type,
.system-priority {
    padding: var(--spacing-xs);
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius-xs);
    color: var(--color-text-secondary);
}

/* Dependencies */
.dependencies-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.dependency-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-sm);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--border-radius-sm);
    transition: all 0.2s ease;
}

.dependency-item:hover {
    background: rgba(var(--panel-accent-rgb), 0.1);
}

.dependency-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: rgba(var(--panel-accent-rgb), 0.2);
    border-radius: var(--border-radius-sm);
    color: var(--panel-accent);
}

.dependency-info {
    flex: 1;
}

.dependency-name {
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: var(--spacing-xs);
}

.dependency-version {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
}

.dependency-status {
    font-size: var(--font-size-xs);
    margin-top: var(--spacing-xs);
}

/* Dashboard Grid */
.dashboard-grid {
    display: grid;
    gap: var(--spacing-xl);
    grid-template-columns: 1fr;
}

.dashboard-section h5 {
    margin: 0 0 var(--spacing-md) 0;
    font-size: var(--font-size-md);
    color: var(--color-text);
    padding-bottom: var(--spacing-sm);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: var(--spacing-md);
}

.metric-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: var(--spacing-md);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--border-radius-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.2s ease;
}

.metric-card:hover {
    background: rgba(var(--panel-accent-rgb), 0.1);
    border-color: var(--panel-accent);
    transform: translateY(-2px);
}

.metric-card .metric-icon {
    margin-bottom: var(--spacing-sm);
    color: var(--panel-accent);
}

.metric-card .metric-data {
    text-align: center;
}

.metric-card .metric-value {
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: var(--spacing-xs);
}

.metric-card .metric-label {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Health Indicators */
.health-indicators {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.health-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--font-size-sm);
    color: var(--color-text);
}

.health-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.health-dot.status-online,
.health-dot.status-healthy {
    background: #4caf50;
}

.health-dot.status-offline,
.health-dot.status-error {
    background: #f44336;
}

.health-dot.status-warning {
    background: #ffc107;
}

.health-dot.status-unknown {
    background: #9e9e9e;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .metric-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
    }
    
    .metrics-row {
        grid-template-columns: 1fr;
    }
    
    .status-overview {
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .dashboard-grid {
        gap: var(--spacing-lg);
    }
}
</style>