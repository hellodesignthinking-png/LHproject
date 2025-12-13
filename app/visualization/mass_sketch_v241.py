"""
ZeroSite v24.1 - Capacity Mass Sketch Generator
Generates 2D/3D building mass visualizations

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import base64
from io import BytesIO


@dataclass
class BuildingMass:
    """Building mass configuration"""
    footprint_width: float  # meters
    footprint_depth: float  # meters
    floors: int
    floor_height: float = 3.0  # meters
    setbacks: Optional[Dict[str, float]] = None  # {"north": 2.0, "south": 2.0, ...}
    name: str = "Building"


class MassSketchGenerator:
    """
    Building Mass Sketch Generator for ZeroSite v24.1
    
    Creates 2D and isometric 3D building mass visualizations showing:
    - Building footprint
    - Floor levels
    - Setbacks
    - Height variations
    """
    
    def __init__(self):
        """Initialize mass sketch generator"""
        self.version = "24.1.0"
        
        # Styling
        self.colors = {
            "building": "#3498db",
            "setback": "#2980b9",
            "ground": "#95a5a6",
            "outline": "#2c3e50"
        }
        
        self.figsize = (10, 8)
        self.dpi = 100
    
    def generate_2d_plan(
        self,
        mass: BuildingMass,
        title: str = "건축 매스 평면도"
    ) -> str:
        """
        Generate 2D plan view
        
        Args:
            mass: Building mass configuration
            title: Chart title
            
        Returns:
            Base64-encoded PNG image
        """
        fig, ax = plt.subplots(figsize=(8, 8), dpi=self.dpi)
        
        # Draw ground
        ground_size = max(mass.footprint_width, mass.footprint_depth) * 1.5
        ground = patches.Rectangle(
            (-ground_size/2, -ground_size/2),
            ground_size,
            ground_size,
            linewidth=1,
            edgecolor='none',
            facecolor=self.colors["ground"],
            alpha=0.3
        )
        ax.add_patch(ground)
        
        # Calculate building position (centered)
        x_offset = -mass.footprint_width / 2
        y_offset = -mass.footprint_depth / 2
        
        # Draw building footprint
        building = patches.Rectangle(
            (x_offset, y_offset),
            mass.footprint_width,
            mass.footprint_depth,
            linewidth=2,
            edgecolor=self.colors["outline"],
            facecolor=self.colors["building"],
            alpha=0.7
        )
        ax.add_patch(building)
        
        # Draw setbacks if present
        if mass.setbacks:
            self._draw_setbacks_2d(ax, mass, x_offset, y_offset)
        
        # Add dimensions
        self._add_dimensions_2d(ax, mass, x_offset, y_offset)
        
        # Styling
        ax.set_xlim(-ground_size/2 - 5, ground_size/2 + 5)
        ax.set_ylim(-ground_size/2 - 5, ground_size/2 + 5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Width (m)', fontsize=10)
        ax.set_ylabel('Depth (m)', fontsize=10)
        ax.set_title(f"{title}\n{mass.name} - {mass.floors}층", fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_isometric_3d(
        self,
        mass: BuildingMass,
        title: str = "건축 매스 입체도"
    ) -> str:
        """
        Generate isometric 3D view
        
        Args:
            mass: Building mass configuration
            title: Chart title
            
        Returns:
            Base64-encoded PNG image
        """
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')
        
        # Building dimensions
        width = mass.footprint_width
        depth = mass.footprint_depth
        height = mass.floors * mass.floor_height
        
        # Define vertices for the building box
        vertices = self._create_building_vertices(width, depth, height)
        
        # Create faces
        faces = self._create_building_faces(vertices)
        
        # Add building to plot
        building_collection = Poly3DCollection(
            faces,
            alpha=0.7,
            facecolor=self.colors["building"],
            edgecolor=self.colors["outline"],
            linewidth=1.5
        )
        ax.add_collection3d(building_collection)
        
        # Draw floor lines
        self._draw_floor_lines(ax, width, depth, mass.floors, mass.floor_height)
        
        # Draw ground plane
        self._draw_ground_plane(ax, width, depth)
        
        # Set viewing angle (isometric-like)
        ax.view_init(elev=20, azim=45)
        
        # Set labels
        ax.set_xlabel('Width (m)', fontsize=10)
        ax.set_ylabel('Depth (m)', fontsize=10)
        ax.set_zlabel('Height (m)', fontsize=10)
        ax.set_title(
            f"{title}\n{mass.name} - {mass.floors}층 (H={height:.1f}m)",
            fontsize=12,
            fontweight='bold'
        )
        
        # Set limits
        max_dim = max(width, depth, height) * 0.6
        ax.set_xlim(-max_dim, max_dim)
        ax.set_ylim(-max_dim, max_dim)
        ax.set_zlim(0, height * 1.2)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_multi_mass_comparison(
        self,
        masses: List[BuildingMass],
        title: str = "건축 매스 비교"
    ) -> str:
        """
        Generate comparison of multiple building masses
        
        Args:
            masses: List of building mass configurations
            title: Chart title
            
        Returns:
            Base64-encoded PNG image
        """
        n_masses = len(masses)
        fig = plt.figure(figsize=(12, 4 * ((n_masses + 2) // 3)), dpi=self.dpi)
        
        for i, mass in enumerate(masses, 1):
            ax = fig.add_subplot((n_masses + 2) // 3, 3, i, projection='3d')
            
            # Building dimensions
            width = mass.footprint_width
            depth = mass.footprint_depth
            height = mass.floors * mass.floor_height
            
            # Create and add building
            vertices = self._create_building_vertices(width, depth, height)
            faces = self._create_building_faces(vertices)
            building_collection = Poly3DCollection(
                faces,
                alpha=0.7,
                facecolor=self.colors["building"],
                edgecolor=self.colors["outline"],
                linewidth=1
            )
            ax.add_collection3d(building_collection)
            
            # Draw floor lines
            self._draw_floor_lines(ax, width, depth, mass.floors, mass.floor_height)
            
            # Styling
            ax.view_init(elev=20, azim=45)
            ax.set_xlabel('W', fontsize=8)
            ax.set_ylabel('D', fontsize=8)
            ax.set_zlabel('H', fontsize=8)
            ax.set_title(f"{mass.name}\n{mass.floors}층, {height:.1f}m", fontsize=10)
            
            max_dim = max(width, depth, height) * 0.6
            ax.set_xlim(-max_dim, max_dim)
            ax.set_ylim(-max_dim, max_dim)
            ax.set_zlim(0, height * 1.2)
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def generate_elevation_views(
        self,
        mass: BuildingMass,
        title: str = "건축 입면도"
    ) -> str:
        """
        Generate front and side elevation views
        
        Args:
            mass: Building mass configuration
            title: Chart title
            
        Returns:
            Base64-encoded PNG image
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=self.dpi)
        
        height = mass.floors * mass.floor_height
        
        # Front elevation
        front_rect = patches.Rectangle(
            (0, 0),
            mass.footprint_width,
            height,
            linewidth=2,
            edgecolor=self.colors["outline"],
            facecolor=self.colors["building"],
            alpha=0.7
        )
        ax1.add_patch(front_rect)
        
        # Draw floor lines (front)
        for i in range(1, mass.floors):
            y = i * mass.floor_height
            ax1.plot([0, mass.footprint_width], [y, y], 'k--', linewidth=1, alpha=0.5)
            ax1.text(mass.footprint_width + 1, y, f'{i}F', fontsize=8, va='center')
        
        ax1.set_xlim(-2, mass.footprint_width + 5)
        ax1.set_ylim(-1, height + 2)
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlabel('Width (m)', fontsize=10)
        ax1.set_ylabel('Height (m)', fontsize=10)
        ax1.set_title(f'정면 입면도\n{mass.footprint_width}m × {height}m', fontsize=11)
        
        # Side elevation
        side_rect = patches.Rectangle(
            (0, 0),
            mass.footprint_depth,
            height,
            linewidth=2,
            edgecolor=self.colors["outline"],
            facecolor=self.colors["building"],
            alpha=0.7
        )
        ax2.add_patch(side_rect)
        
        # Draw floor lines (side)
        for i in range(1, mass.floors):
            y = i * mass.floor_height
            ax2.plot([0, mass.footprint_depth], [y, y], 'k--', linewidth=1, alpha=0.5)
            ax2.text(mass.footprint_depth + 1, y, f'{i}F', fontsize=8, va='center')
        
        ax2.set_xlim(-2, mass.footprint_depth + 5)
        ax2.set_ylim(-1, height + 2)
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlabel('Depth (m)', fontsize=10)
        ax2.set_ylabel('Height (m)', fontsize=10)
        ax2.set_title(f'측면 입면도\n{mass.footprint_depth}m × {height}m', fontsize=11)
        
        fig.suptitle(f"{title} - {mass.name}", fontsize=13, fontweight='bold')
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    # Helper methods
    
    def _create_building_vertices(
        self,
        width: float,
        depth: float,
        height: float
    ) -> np.ndarray:
        """Create vertices for building box"""
        # Center the building at origin
        x_offset = width / 2
        y_offset = depth / 2
        
        vertices = np.array([
            [-x_offset, -y_offset, 0],
            [x_offset, -y_offset, 0],
            [x_offset, y_offset, 0],
            [-x_offset, y_offset, 0],
            [-x_offset, -y_offset, height],
            [x_offset, -y_offset, height],
            [x_offset, y_offset, height],
            [-x_offset, y_offset, height]
        ])
        return vertices
    
    def _create_building_faces(self, vertices: np.ndarray) -> List:
        """Create faces from vertices"""
        faces = [
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # Front
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # Back
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # Left
            [vertices[1], vertices[2], vertices[6], vertices[5]],  # Right
            [vertices[4], vertices[5], vertices[6], vertices[7]]   # Top
        ]
        return faces
    
    def _draw_floor_lines(
        self,
        ax,
        width: float,
        depth: float,
        floors: int,
        floor_height: float
    ):
        """Draw horizontal lines for each floor"""
        x_offset = width / 2
        y_offset = depth / 2
        
        for i in range(1, floors):
            z = i * floor_height
            # Draw rectangle at each floor
            xs = [-x_offset, x_offset, x_offset, -x_offset, -x_offset]
            ys = [-y_offset, -y_offset, y_offset, y_offset, -y_offset]
            zs = [z, z, z, z, z]
            ax.plot(xs, ys, zs, 'k--', linewidth=0.5, alpha=0.5)
    
    def _draw_ground_plane(self, ax, width: float, depth: float):
        """Draw ground plane"""
        size = max(width, depth) * 1.2
        ground_vertices = [
            [-size/2, -size/2, 0],
            [size/2, -size/2, 0],
            [size/2, size/2, 0],
            [-size/2, size/2, 0]
        ]
        ground = Poly3DCollection(
            [ground_vertices],
            alpha=0.2,
            facecolor=self.colors["ground"],
            edgecolor='none'
        )
        ax.add_collection3d(ground)
    
    def _draw_setbacks_2d(
        self,
        ax,
        mass: BuildingMass,
        x_offset: float,
        y_offset: float
    ):
        """Draw setbacks in 2D plan"""
        setbacks = mass.setbacks or {}
        
        # Draw setback lines
        if "north" in setbacks:
            y = y_offset + mass.footprint_depth
            ax.plot(
                [x_offset, x_offset + mass.footprint_width],
                [y, y],
                'r--', linewidth=2, label='Setback'
            )
            ax.text(
                x_offset + mass.footprint_width/2,
                y + 1,
                f'N: {setbacks["north"]}m',
                ha='center',
                fontsize=8
            )
    
    def _add_dimensions_2d(
        self,
        ax,
        mass: BuildingMass,
        x_offset: float,
        y_offset: float
    ):
        """Add dimension annotations"""
        # Width dimension
        ax.annotate(
            '',
            xy=(x_offset + mass.footprint_width, y_offset - 3),
            xytext=(x_offset, y_offset - 3),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.5)
        )
        ax.text(
            x_offset + mass.footprint_width/2,
            y_offset - 4,
            f'{mass.footprint_width}m',
            ha='center',
            fontsize=9,
            fontweight='bold'
        )
        
        # Depth dimension
        ax.annotate(
            '',
            xy=(x_offset - 3, y_offset + mass.footprint_depth),
            xytext=(x_offset - 3, y_offset),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.5)
        )
        ax.text(
            x_offset - 4,
            y_offset + mass.footprint_depth/2,
            f'{mass.footprint_depth}m',
            ha='right',
            va='center',
            fontsize=9,
            fontweight='bold',
            rotation=90
        )
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=self.dpi)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        return image_base64
    
    def generate_mass_config_3d(
        self,
        mass_config,  # MassConfiguration from capacity_engine_v241
        view_angle: str = "isometric"
    ) -> str:
        """
        Generate 3D visualization from MassConfiguration object
        
        Args:
            mass_config: MassConfiguration object with:
                - floors: int
                - footprint: float (m²)
                - shape_type: str ('tower', 'slab', 'mixed')
                - aspect_ratio: float
            view_angle: 'isometric', 'front', 'top'
        
        Returns:
            Base64-encoded PNG image
        """
        # Extract dimensions from MassConfiguration
        floors = mass_config.floors
        footprint = mass_config.footprint
        aspect_ratio = mass_config.aspect_ratio
        shape_type = mass_config.shape_type
        
        # Calculate building dimensions
        # footprint = width × depth, aspect_ratio = depth / width
        width = (footprint / aspect_ratio) ** 0.5
        depth = width * aspect_ratio
        height = floors * 3.0  # 3m per floor
        
        # Create figure
        fig = plt.figure(figsize=(10, 8), facecolor='white')
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw building volume
        self._draw_3d_building_volume(
            ax, width, depth, height,
            shape_type=shape_type,
            floors=floors
        )
        
        # Set view angle
        if view_angle == "isometric":
            ax.view_init(elev=30, azim=45)
        elif view_angle == "front":
            ax.view_init(elev=0, azim=0)
        elif view_angle == "top":
            ax.view_init(elev=90, azim=0)
        
        # Style
        ax.set_xlabel('East-West (m)', fontsize=10)
        ax.set_ylabel('North-South (m)', fontsize=10)
        ax.set_zlabel('Height (m)', fontsize=10)
        
        # Title with key info
        title = f"{shape_type.upper()} Type - {floors}층\n"
        title += f"건물 규모: {width:.1f}m × {depth:.1f}m × {height:.1f}m\n"
        title += f"효율 점수: {mass_config.efficiency_score:.1f}/100"
        ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
        
        # Set limits
        max_dim = max(width, depth, height)
        ax.set_xlim([0, max_dim])
        ax.set_ylim([0, max_dim])
        ax.set_zlim([0, height * 1.1])
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    
    def _draw_3d_building_volume(
        self,
        ax,
        width: float,
        depth: float,
        height: float,
        shape_type: str = 'tower',
        floors: int = 10
    ):
        """
        Draw 3D building volume with realistic details
        
        Args:
            ax: Matplotlib 3D axes
            width: Building width (m)
            depth: Building depth (m)
            height: Building height (m)
            shape_type: 'tower', 'slab', or 'mixed'
            floors: Number of floors
        """
        # Define building corners
        x = [0, width, width, 0, 0, width, width, 0]
        y = [0, 0, depth, depth, 0, 0, depth, depth]
        z = [0, 0, 0, 0, height, height, height, height]
        
        # Draw floor slabs (horizontal lines)
        floor_height = height / floors
        for i in range(floors + 1):
            z_level = i * floor_height
            # Draw floor outline
            floor_x = [0, width, width, 0, 0]
            floor_y = [0, 0, depth, depth, 0]
            floor_z = [z_level] * 5
            ax.plot(floor_x, floor_y, floor_z, 'k-', linewidth=0.5, alpha=0.3)
        
        # Draw vertical edges
        edges = [
            ([0, 0], [0, 0], [0, height]),     # Corner 1
            ([width, width], [0, 0], [0, height]),  # Corner 2
            ([width, width], [depth, depth], [0, height]),  # Corner 3
            ([0, 0], [depth, depth], [0, height]),  # Corner 4
        ]
        
        for edge in edges:
            ax.plot(edge[0], edge[1], edge[2], 'k-', linewidth=1.5)
        
        # Draw faces
        vertices = [
            # Bottom face
            [(0, 0, 0), (width, 0, 0), (width, depth, 0), (0, depth, 0)],
            # Top face
            [(0, 0, height), (width, 0, height), (width, depth, height), (0, depth, height)],
            # Front face
            [(0, 0, 0), (width, 0, 0), (width, 0, height), (0, 0, height)],
            # Back face
            [(0, depth, 0), (width, depth, 0), (width, depth, height), (0, depth, height)],
            # Left face
            [(0, 0, 0), (0, depth, 0), (0, depth, height), (0, 0, height)],
            # Right face
            [(width, 0, 0), (width, depth, 0), (width, depth, height), (width, 0, height)],
        ]
        
        # Color based on shape type
        if shape_type == 'tower':
            face_color = '#3498db'  # Blue for tower
            alpha = 0.6
        elif shape_type == 'slab':
            face_color = '#e74c3c'  # Red for slab
            alpha = 0.6
        else:  # mixed
            face_color = '#2ecc71'  # Green for mixed
            alpha = 0.6
        
        # Add faces as polygons
        poly = Poly3DCollection(vertices, alpha=alpha, facecolor=face_color, edgecolor='black', linewidth=0.5)
        ax.add_collection3d(poly)
        
        # Add ground plane
        ground = [[(0, 0, 0), (width, 0, 0), (width, depth, 0), (0, depth, 0)]]
        ground_poly = Poly3DCollection(ground, alpha=0.1, facecolor='gray', edgecolor='black')
        ax.add_collection3d(ground_poly)
    
    def generate_multiple_mass_configs(
        self,
        mass_configs: list,  # List of MassConfiguration objects
        max_configs: int = 5
    ) -> List[str]:
        """
        Generate 3D visualizations for multiple mass configurations
        
        Args:
            mass_configs: List of MassConfiguration objects
            max_configs: Maximum number to visualize (default 5)
        
        Returns:
            List of base64-encoded PNG images
        """
        images = []
        
        for i, config in enumerate(mass_configs[:max_configs]):
            try:
                image_base64 = self.generate_mass_config_3d(config, view_angle="isometric")
                images.append(image_base64)
            except Exception as e:
                print(f"Warning: Failed to generate image for config {i}: {e}")
                # Add placeholder
                images.append("")
        
        return images


# Module exports
__all__ = ["MassSketchGenerator", "BuildingMass"]
