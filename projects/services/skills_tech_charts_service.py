import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots
import plotly.io as pio
import numpy as np
from django.utils.html import format_html

class SkillsTechChartsService:
    """
    Service for generating interactive Skills & Technology analysis charts using Plotly.
    Integrates with SystemModule, SystemSkillGain, and Technology models.
    Follows the same pattern as ArchitectureDiagramService.
    """

    def __init__(self, system_module):
        self.system = system_module
        self.skill_gains = system_module.skill_gains.select_related('skill').all()
        self.technologies = system_module.technologies.all()

        # AURA theme colors for consistency
        self.aura_colors = {
            'primary': "#7c3aed",      # Purple
            'secondary': "#fb923c",    # Orange
            'accent': '#60a5fa',       # Blue
            'success': '#34d399',      # Green/Emerald
            'warning': '#fff59d',      # Yellow
            'mint': '#a5d6a7',         # Mint
            'background': '#0f172a',   # Dark background
            'text': '#e2e8f0',         # Light text
            'grid': 'rgba(148, 163, 184, 0.2)',  # Grid lines

            # AURA Colors w Alpha
            'primary_trans': 'rgba(124, 58, 237, 0.2)',  # Semi-transparent purple
            'secondary_trans': 'rgba(251, 146, 60, 0.2)',  # Semi-transparent orange
            'accent_trans': 'rgba(96, 165, 250, 0.2)',  # Semi-transparent blue
            'success_trans': 'rgba(52, 211, 153, 0.2)',  # Semi-transparent green/emerald
            'warning_trans': 'rgba(255, 245, 157, 0.2)',  # Semi-transparent yellow
            'mint_trans': 'rgba(165, 214, 167, 0.2)',  # Semi-transparent purple
        }

        self.theme = self.set_default_theme("plotly_dark")
        self.colorway = pio.templates[self.theme].layout.colorway
    
    def set_default_theme(self, theme="plotly_dark"):
        pio.templates.default = theme
        return theme

    
    # Helper to convert hex colors to rgba w transparency
    @staticmethod
    def hex_to_rgba(hex_color, alpha=0.2):
        hex_color = hex_color.strip('#')
        r, g, b = tuple(int(hex_color[i: i + 2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"
    
    def generate_skills_radar_chart(self):
        """
        Generate interactive skills radar chart using Plotly.
        Returns HTML div ready for template embedding.
        """
        if not self.skill_gains.exists():
            return self._generate_no_skills_message()
    
        fig = go.Figure()

        # Prepare data
        skills_data = []
        proficiency_data = []
        colors = []

        for skill_gain in self.skill_gains:
            skills_data.append(skill_gain.skill.name)
            proficiency_data.append(skill_gain.proficiency_gained)
            colors.append(getattr(skill_gain, 'color', self.aura_colors['accent']))
        
        # Add proficiency trace
        fig.add_trace(go.Scatterpolar(
            r=proficiency_data,
            theta=skills_data,
            fill='toself',
            name='Skill Proficiency',
            line=dict(color=self.aura_colors['primary'], width=3),
            fillcolor=f"rgba(124, 58, 237, 0.2)",  # Semi-transparent purple
            marker=dict(
                size=12,
                color=colors,
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>%{theta}</b><br>' +
                         'Proficiency: %{r}/5<br>' +
                         '<extra></extra>'
        ))

        # Apply AURA theme
        self._apply_radar_theme(fig, max_proficiency=5)

        # Convert to HTML w toggle button (may not need since skipping confidence)
        graph_html = self._create_chart_html(
            fig,
            f'skills-radar-{self.system.slug}'
        )

        return graph_html
    
    def generate_tech_donut_chart(self):
        """
        Generate interactive technology distribution donut chart using Plotly.
        Returns HTML div ready for template embedding.
        """
        if not self.technologies.exists():
            return self._generate_no_tech_message()
        
        fig = go.Figure()

        # Prepare data
        tech_names = []
        usage_counts = []
        mastery_levels = []
        # colors = []

        for tech in self.technologies:
            tech_names.append(tech.name)
            usage_counts.append(tech.systems.count())
            mastery_levels.append(self._get_mastery_numeric(tech))
            # colors.append(getattr(tech, 'color', self.aura_colors['secondary']))
        
        # Add usage trace (default)
        fig.add_trace(go.Pie(
            labels=tech_names,
            values=usage_counts,
            name="Technology Usage",
            marker=dict(
                colors=[self.hex_to_rgba(self.colorway[i % len(self.colorway)], 0.2) for i in range(len(tech_names))],
                line=dict(
                    color=[self.colorway[i % len(self.colorway)] for i in range(len(tech_names))], width=3)
            ),
            hole=0.6,  # Donut chart
            textposition="inside",
            textinfo="label+percent",
            textfont=dict(color='white', size=12),
            hovertemplate='<b>%{label}</b><br>' +
                         'Used in %{value} projects<br>' +
                         '%{percent}<br>' +
                         '<extra></extra>'
        ))

        # Add mastery trace (hidden by default)
        fig.add_trace(go.Pie(
            labels=tech_names,
            values=mastery_levels,
            name="Technology Mastery",
            marker=dict(
                colors=[self.hex_to_rgba(self.colorway[i % len(self.colorway)], 0.2) for i in range(len(tech_names))],
                line=dict(
                    color=[self.colorway[i % len(self.colorway)] for i in range(len(tech_names))], width=3)
            ),
            hole=0.6,  # donut chart
            textposition="inside",
            textinfo="label+percent",
            textfont=dict(color='white', size=12),
            visible=False,  # Hidden by default
            hovertemplate='<b>%{label}</b><br>' +
                         'Mastery Level: %{value}/4<br>' +
                         '%{percent}<br>' +
                         '<extra></extra>'
        ))

        # Plotly Theme
        # fig.update_layout(template="plotly_dark")

        # Apply AURA theme
        self._apply_donut_theme(fig)

        # Convert to HTML w toggle
        graph_html = self._create_chart_html(
            fig,
            f'tech-donut-{self.system.slug}',
            buttons=[
                {'label': 'Usage Count', 'method': 'update', 'args': [{'visible': [True, False]}]},
                {'label': 'Mastery Level', 'method': 'update', 'args': [{'visible': [False, True]}]}
            ]
        )

        return graph_html
    
    def generate_skill_tech_network(self):
        """
        Generate interactive skill-technology network diagram using Plotly.
        Shows relationships between skills and technologies.
        """
        if not self.skill_gains.exists() or not self.technologies.exists():
            return self._generate_no_network_message()

        fig = go.Figure()

        # Create network layout
        skill_positions = self._calculate_skill_positions()
        tech_positions = self._calculate_tech_positions()
        connections = self._find_skill_tech_connections()

        # Add connection lines
        for connection in connections:
            skill_pos = skill_positions[connection['skill_id']]
            tech_pos = tech_positions[connection['tech_id']]

            fig.add_trace(go.Scatter(
                x=[skill_pos['x'], tech_pos['x']],
                y=[skill_pos['y'], tech_pos['y']],
                mode='lines',
                line=dict(
                    color=f"rgba(124, 58, 237, {connection['strength'] * 0.3})",
                    width=connection['strength'] * 2
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add Skill nodes
        skill_x = [pos['x'] for pos in skill_positions.values()]
        skill_y = [pos['y'] for pos in skill_positions.values()]
        skill_names = [skill_gain.skill.name for skill_gain in self.skill_gains]
        skill_proficiency = [skill_gain.proficiency_gained for skill_gain in self.skill_gains]

        fig.add_trace(go.Scatter(
            x=skill_x,
            y=skill_y,
            mode='markers+text',
            marker=dict(
                size=[prof * 8 + 20 for prof in skill_proficiency],
                color=self.aura_colors['primary'],
                line=dict(color='white', width=2),
                symbol='hexagon-open',
            ),
            text=skill_names,
            textposition="middle center",
            textfont=dict(color='white', size=10),
            name='Skills',
            hovertemplate='<b>%{text}</b><br>' +
                         'Proficiency: %{customdata}/5<br>' +
                         '<extra></extra>',
            customdata=skill_proficiency
        ))

        # Add technology nodes
        tech_x = [pos['x'] for pos in tech_positions.values()]
        tech_y = [pos['y'] for pos in tech_positions.values()]
        tech_names = [tech.name for tech in self.technologies]
        tech_usage = [tech.systems.count() for tech in self.technologies]

        fig.add_trace(go.Scatter(
            x=tech_x,
            y=tech_y,
            mode='markers+text',
            marker=dict(
                size=[usage * 6 + 15 for usage in tech_usage],
                color=self.aura_colors['secondary'],
                line=dict(color='white', width=2)
            ),
            text=tech_names,
            textposition="middle center",
            textfont=dict(color='white', size=10),
            name='Technologies',
            hovertemplate='<b>%{text}</b><br>' +
                         'Used in %{customdata} projects<br>' +
                         '<extra></extra>',
            customdata=tech_usage
        ))

        # Apply network theme
        self._apply_network_theme(fig)

        # Convert to HTML
        graph_html = self._create_chart_html(fig, f'skill-tech-network-{self.system.slug}')

        return graph_html
    
    def generate_tech_sunburst(self):
        """
        Generate interactive technology distribution sunburst using Plotly.
        Returns HTML div ready for embedding.
        """
        if not self.technologies.exists():
            return self._generate_no_tech_message()
        
        fig = go.Figure()

        # Prepare the data
        tech_names = []
        categories = []
        usage_counts = []
        colors = []

        for tech in self.technologies:
            tech_names.append(tech.name)
            categories.append(tech.get_category_display())
            usage_counts.append(tech.systems.count())
            colors.append(getattr(tech, 'color', self.aura_colors['accent']))
        
        # Add Usage Trace
        fig.add_trace(go.Sunburst(
            labels=tech_names,
            parents=categories,
            values=usage_counts,
            level=self.system.title,
            name="Tech Usage by Category",
            marker=dict(
                colors=colors,
                line=dict(color='white', width=3)
            ),
            hovertemplate='<b>%{label}</b><br>' +
                         'Used in %{value} projects<br>' +
                         '%{parent}<br>' +
                         '<extra></extra>'
        ))

        # Apply AURA Theme
        # self._apply_donut_theme(fig)

        # Convert to HTML
        graph_html = self._create_chart_html(fig, f'tech-sunburst-{self.system.slug}')

        return graph_html
    
    def _apply_radar_theme(self, fig, max_proficiency=5):
        """Apply AURA theme to radar chart - Improved"""
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(15, 23, 42, 0.8)',
                radialaxis=dict(
                    visible=True,
                    range=[0, max_proficiency],
                    tickfont=dict(color=self.aura_colors['text'], size=10),
                    gridcolor=self.aura_colors['grid'],
                    linecolor=self.aura_colors['grid']
                ),
                angularaxis=dict(
                    tickfont=dict(color=self.aura_colors['text'], size=11),
                    linecolor=self.aura_colors['grid'],
                    gridcolor=self.aura_colors['grid']
                )
            ),
            paper_bgcolor='rgba(15, 23, 42, 0.9)',
            plot_bgcolor='rgba(15, 23, 42, 0.9)',
            font=dict(color=self.aura_colors['text']),
            # Enhanced
            legend=dict(
                x=0.02,
                y=0.95,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(15, 23, 42, 0.8)',
                bordercolor=self.aura_colors['grid'],
                borderwidth=1,
                font=dict(color=self.aura_colors['text'], size=10),
                itemsizing='constant',
                orientation='v'
            ),
            # Enahnced
            margin=dict(l=120, r=80, t=80, b=60),
            height=450,
            autosize=True
        )
    
    def _apply_donut_theme(self, fig):
        """Apply AURA theme to donut chart - Improved"""
        fig.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 0.9)',
            plot_bgcolor='rgba(15, 23, 42, 0.9)',
            font=dict(color=self.aura_colors['text']),
            # Enahnced
            legend=dict(
                # x=0.02,
                # y=0.95,  # Slightly lower to avoid toggle buttons
                # xanchor='left',
                # yanchor='top',
                bgcolor='rgba(15, 23, 42, 0.9)',
                bordercolor='rgba(124, 58, 237, 0.4)',
                borderwidth=1,
                font=dict(color=self.aura_colors['text'], size=10),
                itemsizing='constant',
                orientation='v',
                itemwidth=30
            ),
            # Enahnced
            margin=dict(l=120, r=80, t=80, b=60),
            height=450,
            autosize=True
        )
    
    def _apply_network_theme(self, fig):
        """Apply AURA theme to network diagram - Improved"""
        fig.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 0.9)',
            plot_bgcolor='rgba(15, 23, 42, 0.9)',
            font=dict(color=self.aura_colors['text']),
            # Enhanced - Improved aces for network chart
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-1.1, 1.1],
                scaleanchor="y",
                scaleratio=1
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-1.1, 1.1]
            ),
            # Enhanced, better legend positioning
            legend=dict(
                x=0.02,
                y=0.98,  # Higher since no toggle buttons
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(15, 23, 42, 0.9)',
                bordercolor='rgba(124, 58, 237, 0.4)',
                borderwidth=1,
                font=dict(color=self.aura_colors['text'], size=10),
                itemsizing='constant',
                orientation='v'
            ),
            # Enhanced
            margin=dict(l=120, r=80, t=60, b=60),
            height=500,
            autosize=True,

            # Better hover
            hovermode='closest'
        )
    
    def _create_chart_html(self, fig, chart_id, buttons=None):
        """Convert Plotly figure to HTML with enhanced toggle buttons"""
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'pan2d', 'lasso2d', 'select2d', 'autoScale2d', 
                'hoverClosestCartesian', 'hoverCompareCartesian'
            ],
            # ENHANCED: Modebar positioning
            'modeBarButtonsToAdd': [],  # Can add custom buttons here if needed
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'{chart_id}',
                'height': 500,
                'width': 700,
                'scale': 2
            },
            # Performance optimizations
            'responsive': True,
            'staticPlot': False,
            'plotlyServerURL': None,
            'showTips': False,
            'doubleClick': 'reset',
            'editable': False,
            'scrollZoom': True,
        }

        # FIXED: Simplified toggle buttons with correct Plotly structure
        if buttons:
            fig.update_layout(
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="left",
                        buttons=buttons,
                        pad={"r": 12, "t": 12, "b": 12, "l": 12},
                        showactive=True,
                        active=0,
                        x=0,
                        xanchor="left", 
                        y=1.1,
                        yanchor="top",
                        
                        # Button container styling
                        bgcolor='rgba(15, 23, 42, 0.95)',
                        bordercolor='rgba(124, 58, 237, 0.4)',
                        borderwidth=1,
                        font=dict(
                            color="#5c52bd",
                            size=11,
                            family='Inter, system-ui, sans-serif'
                        )
                    ),
                ]
            )

        fig.update_layout(
            autosize=True  
        )

        # Add this right before pyo.plot() in your chart method:
        # print(f"DEBUG - Fig: {fig.name}")
        # print(f"DEBUG - xref: {fig.layout.legend.xref}")
        # print(f"DEBUG - Legend X: {fig.layout.legend.x}")
        # print(f"DEBUG - Legend Y: {fig.layout.legend.y}")
        # print(f"DEBUG - Legend config: {fig.layout.legend}")
        # print(f"DEBUG - Showlegend: {fig.layout.showlegend}")
        # print("**********")
        # # print(f"DEBUG - updatemenu X: {fig.layout.updatemenus.x}")
        # # print(f"DEBUG - updatemenu Y: {fig.layout.updatemenus.y}")
        # print(f"DEBUG - Buttons config: {fig.layout.updatemenus}")
        # print()
        # print("===========================")

        graph_html = pyo.plot(
            fig,
            output_type='div',
            include_plotlyjs=True,
            config=config,
            # div_id=chart_id,
        )

        return graph_html

    def _get_mastery_numeric(self, tech):
        """Convert technology mastery to numeric value"""
        total_systems = tech.systems.count()
        if total_systems >= 3:
            return 4  # Advanced
        elif total_systems >= 2:
            return 3  # Intermediate
        elif total_systems >= 1:
            return 2  # Basic
        else:
            return 1  # Beginner

    def _calculate_skill_positions(self):
        """Calculate positions for skills in network layout"""
        positions = {}
        num_skills = len(self.skill_gains)
        
        for i, skill_gain in enumerate(self.skill_gains):
            angle = 2 * np.pi * i / num_skills
            positions[skill_gain.skill.id] = {
                'x': 0.8 * np.cos(angle),
                'y': 0.8 * np.sin(angle)
            }
        
        return positions

    def _calculate_tech_positions(self):
        """Calculate positions for technologies in network layout"""
        positions = {}
        num_techs = len(self.technologies)
        
        for i, tech in enumerate(self.technologies):
            angle = 2 * np.pi * i / num_techs + np.pi / num_techs  # Offset from skills
            positions[tech.id] = {
                'x': 0.4 * np.cos(angle),
                'y': 0.4 * np.sin(angle)
            }
        
        return positions

    def _find_skill_tech_connections(self):
        """Find connections between skills and technologies"""
        connections = []
        
        for skill_gain in self.skill_gains:
            skill = skill_gain.skill
            for tech in self.technologies:
                strength = self._calculate_connection_strength(skill, tech)
                if strength > 0:
                    connections.append({
                        'skill_id': skill.id,
                        'tech_id': tech.id,
                        'strength': strength
                    })
        
        return connections

    def _calculate_connection_strength(self, skill, tech):
        """Calculate connection strength between skill and technology"""
        # Simple name-based matching (you can enhance this)
        skill_name = skill.name.lower()
        tech_name = tech.name.lower()
        
        if skill_name in tech_name or tech_name in skill_name:
            return 1.0
        elif any(word in tech_name for word in skill_name.split()):
            return 0.7
        elif any(word in skill_name for word in tech_name.split()):
            return 0.5
        
        return 0

    def _generate_no_skills_message(self):
        """Generate message when no skills data available"""
        return format_html(
            '<div style="text-align: center; padding: 2rem; color: #94a3b8;">'
            '<i class="fas fa-brain" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>'
            '<h3>No Skills Data Available</h3>'
            '<p>Add skill gains to see the interactive radar chart.</p>'
            '</div>'
        )

    def _generate_no_tech_message(self):
        """Generate message when no technology data available"""
        return format_html(
            '<div style="text-align: center; padding: 2rem; color: #94a3b8;">'
            '<i class="fas fa-cogs" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>'
            '<h3>No Technology Data Available</h3>'
            '<p>Add technologies to see the interactive donut chart.</p>'
            '</div>'
        )

    def _generate_no_network_message(self):
        """Generate message when no network data available"""
        return format_html(
            '<div style="text-align: center; padding: 2rem; color: #94a3b8;">'
            '<i class="fas fa-project-diagram" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>'
            '<h3>No Network Data Available</h3>'
            '<p>Add skills and technologies to see the relationship network.</p>'
            '</div>'
        )
    
    # Method to handle different chart type configurations
    def get_chart_type_config(self, chart_type):
        """Get chart-type specific configurations"""
        configs = {
            'radar': {
                'height': 450,
                'margin': dict(l=120, r=80, t=80, b=60),
                'legend_orientation': 'v'
            },
            'donut': {
                'height': 450,
                'margin': dict(l=120, r=80, t=80, b=60),
                'legend_orientation': 'v'
            },
            'network': {
                'height': 500,
                'margin': dict(l=120, r=80, t=60, b=60),
                'legend_orientation': 'v'
            }
        }
        return configs.get(chart_type, configs['radar'])
