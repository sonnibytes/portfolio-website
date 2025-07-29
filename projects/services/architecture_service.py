import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots
import numpy as np
from django.utils.html import format_html

from ..models import ArchitectureComponent, ArchitectureConnection

class ArchitectureDiagramService:
    """
    Service for generating interactive 3D architecture diagrams using Plotly.
    Integrates with SystemModule and ArchitectureComponent models.
    """

    def __init__(self, system_module):
        self.system = system_module
        self.components = system_module.architecture_components.all().order_by('display_order')
        self.connections = []

        # Collect all connections
        for component in self.components:
            self.connections.extend(component.outgoing_connections.all())

    def generate_plotly_diagram(self):
        """
        Generate complete Plotly 3D architecture diagram.
        Returns HTML div ready for template embedding. 
        """
        if not self.components.exists():
            return self._generate_no_architecture_message()
        
        fig = go.Figure()

        # Add component nodes
        self._add_component_nodes(fig)

        # Add connection lines
        self._add_connection_lines(fig)

        # Apply AURA theme and layout
        self._apply_aura_theme(fig)

        # UPDATED CONFIG: Optimized to reduce canvas readback operations
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'{self.system.slug}_architecture',
                'height': 600,
                'width': 800,
                'scale': 2
            },
            # Performance optimizations to reduce the warning
            'responsive': True,
            'staticPlot': False,
            'plotlyServerURL': None,  # Disables cloud features that read canvas
            'showTips': False,        # Reduces DOM operations
            'doubleClick': 'reset',   # Cleaner interaction
            'editable': False,        # Prevents editing operations
            'scrollZoom': True,       # Better than pan for performance
        }

        graph_html = pyo.plot(
            fig,
            output_type='div',
            include_plotlyjs=True,
            config=config,
            # div_id=f'architecture-{self.system.slug}',
        )

        return graph_html
    
    def _add_component_nodes(self, fig):
        """Add 3D scatter points for architecture component."""

        for component in self.components:
            # Determine size based on importance
            size = component.size
            if component.is_core:
                size *= 1.5
            
            # Create hover text
            hover_text = component.get_hover_info()

            # Add component as 3D scatter point
            fig.add_trace(go.Scatter3d(
                x=[component.position_x],
                y=[component.position_y],
                z=[component.position_z],
                mode='markers+text',
                marker=dict(
                    size=size,
                    color=component.color,
                    opacity=0.8,
                    line=dict(width=2, color='white'),
                    # Add glow effect for core components
                    symbol='circle' if not component.is_core else 'diamond'
                ),
                text=[component.name],
                textposition='top center',
                textfont=dict(
                    size=10 if not component.is_core else 12,
                    color='white',
                    family='Courier New'
                ),
                name=component.name,
                hovertemplate=hover_text + "<extra></extra>",
                legendgroup=component.get_component_type_display(),
                legendgrouptitle={'text': component.get_component_type_display()}
            ))
    
    def _add_connection_lines(self, fig):
        """Add connection lines between components."""

        for connection in self.connections:
            from_pos = [
                connection.from_component.position_x,
                connection.from_component.position_y,
                connection.from_component.position_z,
            ]
            to_pos = [
                connection.to_component.position_x,
                connection.to_component.position_y,
                connection.to_component.position_z,
            ]

            # Create curved line for better visualization
            if connection.is_bidirectional:
                # For bidirectional, create a slight curve
                mid_x = (from_pos[0] + to_pos[0]) / 2
                mid_y = (from_pos[1] + to_pos[1]) / 2 + 0.3  # Slight curve
                mid_z = (from_pos[2] + to_pos[2]) / 2
                
                line_x = [from_pos[0], mid_x, to_pos[0], None]
                line_y = [from_pos[1], mid_y, to_pos[1], None]
                line_z = [from_pos[2], mid_z, to_pos[2], None]
            else:
                # Direct line
                line_x = [from_pos[0], to_pos[0], None]
                line_y = [from_pos[1], to_pos[1], None]
                line_z = [from_pos[2], to_pos[2], None]
            
            # Add connection line
            fig.add_trace(go.Scatter3d(
                x=line_x,
                y=line_y,
                z=line_z,
                mode='lines',
                line=dict(
                    color=connection.line_color,
                    width=connection.line_width * 2,  # Plotly uses different scale
                    # dash='dash' if connection.connection_type == 'dependency' else 'solid'
                ),
                showlegend=False,
                hovertemplate=(
                    f"<b>{connection.get_connection_type_display()}</b><br>"
                    f"{connection.from_component.name} → {connection.to_component.name}<br>"
                    f"{connection.label if connection.label else ''}"
                    "<extra></extra>"
                ),
                name=f"{connection.from_component.name} → {connection.to_component.name}"
            ))

    def _apply_aura_theme(self, fig):
        """Apply AURA design system theme to the diagram"""
        
        fig.update_layout(
            title={
                'text': f'{self.system.title.upper()} - SYSTEM ARCHITECTURE',
                'x': 0.5,
                'font': {
                    'size': 18,
                    'color': '#00ffff',
                    'family': 'Courier New, monospace'
                }
            },
            scene=dict(
                # AURA dark background
                bgcolor='rgba(10, 15, 28, 1)',
                
                # Grid styling
                xaxis=dict(
                    backgroundcolor='rgba(0, 0, 0, 0)',
                    gridcolor='rgba(0, 255, 255, 0.2)',
                    showbackground=True,
                    zerolinecolor='rgba(0, 255, 255, 0.4)',
                    title_font_color='#00ffff',
                    tickfont_color='#00ffff',
                    title='Component Layer'
                ),
                yaxis=dict(
                    backgroundcolor='rgba(0, 0, 0, 0)',
                    gridcolor='rgba(0, 255, 255, 0.2)',
                    showbackground=True,
                    zerolinecolor='rgba(0, 255, 255, 0.4)',
                    title_font_color='#00ffff',
                    tickfont_color='#00ffff',
                    title='Service Tier'
                ),
                zaxis=dict(
                    backgroundcolor='rgba(0, 0, 0, 0)',
                    gridcolor='rgba(0, 255, 255, 0.2)',
                    showbackground=True,
                    zerolinecolor='rgba(0, 255, 255, 0.4)',
                    title_font_color='#00ffff',
                    tickfont_color='#00ffff',
                    title='Data Flow'
                ),
                
                # Camera positioning
                camera=dict(
                    eye=dict(x=1.8, y=1.8, z=1.2),
                    center=dict(x=0, y=0, z=0),
                    up=dict(x=0, y=0, z=1)
                ),
                
                # Lighting
                aspectmode='cube'  # Keep proportions
            ),
            
            # Overall theme
            paper_bgcolor='rgba(10, 15, 28, 1)',
            plot_bgcolor='rgba(10, 15, 28, 1)',
            font=dict(
                color='#00ffff',
                family='Courier New, monospace',
                size=11
            ),
            
            # Legend styling
            showlegend=True,
            legend=dict(
                bgcolor='rgba(0, 0, 0, 0.7)',
                bordercolor='rgba(0, 255, 255, 0.5)',
                borderwidth=1,
                font=dict(color='#00ffff', size=10),
                x=0.02,
                y=0.98
            ),
            
            # Responsive sizing
            autosize=True,
            margin=dict(l=0, r=0, t=50, b=0)
        )
    
    def _generate_no_architecture_message(self):
        """Generate message when no architecture is defined"""
        return format_html(
            '<div class="glass-card p-4 text-center">'
            '<div class="text-lavender mb-2">'
            '<i class="fas fa-project-diagram fa-2x"></i>'
            '</div>'
            '<h4 class="text-white">Architecture Diagram</h4>'
            '<p class="text-muted">No architecture components defined for this system.</p>'
            '</div>'
        )
    
    @classmethod
    def create_default_architecture(cls, system_module, architecture_type='web_app'):
        """
        Create default architecture components for different project types.
        Useful for quick setup of common patterns.
        """

        # Clear existing components
        system_module.architecture_components.all().delete()

        if architecture_type == 'web_app':
            cls._create_web_app_architecture(system_module)
        elif architecture_type == 'api_service':
            cls._create_api_service_architecture(system_module)
        elif architecture_type == 'data_pipeline':
            cls._create_data_pipeline_architecture(system_module)
        elif architecture_type == 'ml_project':
            cls._create_ml_project_architecture(system_module)
    
    @staticmethod
    def _create_web_app_architecture(system):
        """Create default web app architecture"""
        
        # Frontend
        frontend = ArchitectureComponent.objects.create(
            system=system,
            name='Frontend Interface',
            component_type='frontend',
            position_x=0,
            position_y=0,
            position_z=0,
            color='#00ffff',
            size=20,
            is_core=True,
            description='User interface and main application logic'
        )

        # Backend API
        backend = ArchitectureComponent.objects.create(
            system=system,
            name='Backend API',
            component_type='backend',
            position_x=0,
            position_y=-2,
            position_z=1,
            color='#ffd23f',
            ssize=18,
            description='Server-side API and business logic'
        )

        # Database
        database = ArchitectureComponent.objects.create(
            system=system,
            name='Database',
            component_type='database',
            position_x=-2, position_y=-2, position_z=2,
            color='#4ecdc4',
            size=15,
            description='Data storage and persistence layer'
        )

        # Create connections
        ArchitectureConnection.objects.create(
            from_component=frontend,
            to_component=backend,
            connection_type='api_call',
            label='API Requests',
            is_bidirectional=True
        )
        
        ArchitectureConnection.objects.create(
            from_component=backend,
            to_component=database,
            connection_type='data_flow',
            label='Data Operations'
        )
    
    @staticmethod
    def _create_data_pipeline_architecture(system):
        """Create default data pipeline architecture (perfect for map-buddy)"""
        
        # Input Interface
        interface = ArchitectureComponent.objects.create(
            system=system,
            name='User Interface',
            component_type='frontend',
            position_x=0, position_y=0, position_z=0,
            color='#00ffff',
            size=18,
            is_core=True,
            description='Streamlit interface for data input and configuration'
        )
        
        # External APIs
        api1 = ArchitectureComponent.objects.create(
            system=system,
            name='External API 1',
            component_type='api',
            position_x=-3, position_y=2, position_z=-1,
            color='#ff6b35',
            size=15,
            description='Primary external data source'
        )
        
        api2 = ArchitectureComponent.objects.create(
            system=system,
            name='External API 2',
            component_type='api',
            position_x=3, position_y=2, position_z=-1,
            color='#4ecdc4',
            size=15,
            description='Secondary external data source'
        )
        
        # Data Processing
        processor = ArchitectureComponent.objects.create(
            system=system,
            name='Data Processing',
            component_type='processing',
            position_x=0, position_y=-2, position_z=1,
            color='#ffd23f',
            size=16,
            description='Data transformation and analysis engine'
        )
        
        # File I/O
        file_input = ArchitectureComponent.objects.create(
            system=system,
            name='File Input',
            component_type='file_io',
            position_x=-2, position_y=-1, position_z=2,
            color='#95e1d3',
            size=12,
            description='CSV file upload and parsing'
        )
        
        file_output = ArchitectureComponent.objects.create(
            system=system,
            name='File Output',
            component_type='file_io',
            position_x=2, position_y=-1, position_z=2,
            color='#3d5a80',
            size=12,
            description='Processed data export and download'
        )
        
        # Create connections
        connections = [
            (interface, api1, 'api_call', 'API Requests'),
            (interface, api2, 'api_call', 'API Requests'),
            (interface, processor, 'data_flow', 'Process Control'),
            (processor, file_input, 'file_transfer', 'Import Data'),
            (processor, file_output, 'file_transfer', 'Export Results'),
        ]
        
        for from_comp, to_comp, conn_type, label in connections:
            ArchitectureConnection.objects.create(
                from_component=from_comp,
                to_component=to_comp,
                connection_type=conn_type,
                label=label
            )
    
    @staticmethod
    def _create_api_service_architecture(system):
        """Create default api service architecture"""
        pass

    @staticmethod
    def _create_ml_project_architecture(system):
        """Create default ml project architecture"""
        pass