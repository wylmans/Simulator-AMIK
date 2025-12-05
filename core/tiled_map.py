"""
Tiled Map Editor Integration
Support untuk .tmx files dari Tiled Map Editor
"""

import pygame
import xml.etree.ElementTree as ET
from core.camera import camera


class TiledMap:
    """
    Load dan render map dari Tiled Map Editor (.tmx format)

    Features:
    - Multiple tile layers
    - Object layers (spawn points, collision areas)
    - Tileset properties
    - Collision detection dari object layer atau tile properties
    """

    def __init__(self, tmx_file):
        """
        Load TMX file dari Tiled Map Editor

        Args:
            tmx_file: Path ke file .tmx
        """
        self.tmx_file = tmx_file
        self.layers = []
        self.tilesets = []
        self.objects = {}
        self.tile_properties = {}

        # Map properties
        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0

        # Parse TMX file
        self._parse_tmx()

    def _parse_tmx(self):
        """Parse TMX XML file"""
        tree = ET.parse(self.tmx_file)
        root = tree.getroot()

        # Get map properties
        self.width = int(root.get('width'))
        self.height = int(root.get('height'))
        self.tile_width = int(root.get('tilewidth'))
        self.tile_height = int(root.get('tileheight'))

        print(f"Loading map: {self.width}x{self.height} tiles ({self.tile_width}x{self.tile_height}px)")

        # Parse tilesets
        for tileset in root.findall('tileset'):
            self._parse_tileset(tileset)

        # Parse layers
        for layer in root.findall('layer'):
            self._parse_layer(layer)

        # Parse object groups (untuk collision, spawn points, dll)
        for objectgroup in root.findall('objectgroup'):
            self._parse_objectgroup(objectgroup)

        print(f"✅ Map loaded: {len(self.layers)} layers, {len(self.tilesets)} tilesets")

    def _parse_tileset(self, tileset_elem):
        """Parse tileset information"""
        firstgid = int(tileset_elem.get('firstgid'))
        name = tileset_elem.get('name')
        tile_width = int(tileset_elem.get('tilewidth'))
        tile_height = int(tileset_elem.get('tileheight'))

        # Get image source
        image_elem = tileset_elem.find('image')
        if image_elem is not None:
            source = image_elem.get('source')
            image_width = int(image_elem.get('width'))
            image_height = int(image_elem.get('height'))

            # Load tileset image
            try:
                tileset_image = pygame.image.load(source)
            except:
                # Try with relative path
                import os
                dir_path = os.path.dirname(self.tmx_file)
                source = os.path.join(dir_path, source)
                tileset_image = pygame.image.load(source)

            # Calculate tiles in tileset
            cols = image_width // tile_width
            rows = image_height // tile_height

            # Extract individual tiles
            tiles = []
            for row in range(rows):
                for col in range(cols):
                    rect = pygame.Rect(
                        col * tile_width,
                        row * tile_height,
                        tile_width,
                        tile_height
                    )
                    tile_surface = tileset_image.subsurface(rect)
                    tiles.append(tile_surface)

            tileset_data = {
                'firstgid': firstgid,
                'name': name,
                'tiles': tiles,
                'tile_width': tile_width,
                'tile_height': tile_height
            }

            # Parse tile properties (collision, etc)
            for tile in tileset_elem.findall('tile'):
                tile_id = int(tile.get('id'))
                global_id = firstgid + tile_id

                properties = {}
                props_elem = tile.find('properties')
                if props_elem is not None:
                    for prop in props_elem.findall('property'):
                        prop_name = prop.get('name')
                        prop_value = prop.get('value')
                        properties[prop_name] = prop_value

                self.tile_properties[global_id] = properties

            self.tilesets.append(tileset_data)
            print(f"  Tileset '{name}': {len(tiles)} tiles")

    def _parse_layer(self, layer_elem):
        """Parse tile layer"""
        name = layer_elem.get('name')
        width = int(layer_elem.get('width'))
        height = int(layer_elem.get('height'))
        visible = layer_elem.get('visible', '1') == '1'

        # Get layer data
        data_elem = layer_elem.find('data')
        encoding = data_elem.get('encoding')

        if encoding == 'csv':
            # CSV encoding (most common)
            csv_data = data_elem.text.strip()
            tile_ids = [int(x) for x in csv_data.replace('\n', '').split(',')]
        else:
            # XML encoding (fallback)
            tile_ids = []
            for tile in data_elem.findall('tile'):
                gid = int(tile.get('gid', 0))
                tile_ids.append(gid)

        # Convert to 2D array
        tiles = []
        for row in range(height):
            row_data = tile_ids[row * width:(row + 1) * width]
            tiles.append(row_data)

        layer_data = {
            'name': name,
            'tiles': tiles,
            'visible': visible,
            'width': width,
            'height': height
        }

        self.layers.append(layer_data)
        print(f"  Layer '{name}': {width}x{height} tiles")

    def _parse_objectgroup(self, objectgroup_elem):
        """Parse object group (collision, spawn points, etc)"""
        name = objectgroup_elem.get('name')
        objects = []

        for obj in objectgroup_elem.findall('object'):
            obj_id = int(obj.get('id'))
            obj_name = obj.get('name', '')
            obj_type = obj.get('type', '')
            x = float(obj.get('x'))
            y = float(obj.get('y'))
            width = float(obj.get('width', 0))
            height = float(obj.get('height', 0))

            # Get custom properties
            properties = {}
            props_elem = obj.find('properties')
            if props_elem is not None:
                for prop in props_elem.findall('property'):
                    prop_name = prop.get('name')
                    prop_value = prop.get('value')
                    properties[prop_name] = prop_value

            obj_data = {
                'id': obj_id,
                'name': obj_name,
                'type': obj_type,
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'properties': properties
            }

            objects.append(obj_data)

        self.objects[name] = objects
        print(f"  Object layer '{name}': {len(objects)} objects")

    def get_tile_surface(self, gid):
        """Get pygame surface untuk tile dengan GID tertentu"""
        if gid == 0:
            return None

        # Find correct tileset
        for tileset in self.tilesets:
            if gid >= tileset['firstgid']:
                local_id = gid - tileset['firstgid']
                if local_id < len(tileset['tiles']):
                    return tileset['tiles'][local_id]

        return None

    def is_tile_solid(self, gid):
        """Check apakah tile solid (dari properties)"""
        if gid == 0:
            return False

        properties = self.tile_properties.get(gid, {})
        return properties.get('solid', 'false').lower() == 'true'

    def get_collision_rects(self):
        """
        Get semua collision rectangles dari object layer 'Collision'

        Returns:
            List of pygame.Rect objects
        """
        collision_rects = []

        if 'Collision' in self.objects:
            for obj in self.objects['Collision']:
                rect = pygame.Rect(
                    int(obj['x']),
                    int(obj['y']),
                    int(obj['width']),
                    int(obj['height'])
                )
                collision_rects.append(rect)

        return collision_rects

    def get_spawn_points(self):
        """
        Get spawn points dari object layer 'Spawns'

        Returns:
            Dict dengan key = name/type, value = (x, y)
        """
        spawns = {}

        if 'Spawns' in self.objects:
            for obj in self.objects['Spawns']:
                key = obj['name'] or obj['type']
                spawns[key] = (int(obj['x']), int(obj['y']))

        return spawns

    def draw(self, screen):
        """Render semua visible layers"""
        for layer in self.layers:
            if not layer['visible']:
                continue

            self.draw_layer(screen, layer)

    def draw_layer(self, screen, layer):
        """Render single layer"""
        for row_idx, row in enumerate(layer['tiles']):
            for col_idx, gid in enumerate(row):
                if gid == 0:
                    continue

                tile_surface = self.get_tile_surface(gid)
                if tile_surface:
                    x = col_idx * self.tile_width - camera.x
                    y = row_idx * self.tile_height - camera.y
                    screen.blit(tile_surface, (x, y))

    def draw_collision_debug(self, screen):
        """Draw collision rectangles untuk debugging"""
        rects = self.get_collision_rects()
        for rect in rects:
            debug_rect = pygame.Rect(
                rect.x - camera.x,
                rect.y - camera.y,
                rect.width,
                rect.height
            )
            # Semi-transparent red overlay
            surface = pygame.Surface((rect.width, rect.height))
            surface.set_alpha(100)
            surface.fill((255, 0, 0))
            screen.blit(surface, debug_rect.topleft)
            pygame.draw.rect(screen, (255, 0, 0), debug_rect, 2)

    def draw_spawns_debug(self, screen):
        """Draw spawn points untuk debugging"""
        spawns = self.get_spawn_points()
        font = pygame.font.Font(None, 20)

        for name, (x, y) in spawns.items():
            screen_x = x - camera.x
            screen_y = y - camera.y

            # Draw cross
            pygame.draw.line(screen, (0, 255, 0),
                           (screen_x - 10, screen_y), (screen_x + 10, screen_y), 2)
            pygame.draw.line(screen, (0, 255, 0),
                           (screen_x, screen_y - 10), (screen_x, screen_y + 10), 2)

            # Draw label
            label = font.render(name, True, (0, 255, 0))
            screen.blit(label, (screen_x + 15, screen_y - 10))


class TiledMapCollision:
    """Collision system untuk Tiled maps"""

    def __init__(self, tiled_map):
        """
        Args:
            tiled_map: TiledMap object
        """
        self.map = tiled_map
        self.collision_rects = tiled_map.get_collision_rects()

        # Generate collision grid dari tile properties
        self.collision_grid = self._generate_collision_grid()

    def _generate_collision_grid(self):
        """Generate 2D grid collision dari tile properties"""
        grid = []

        # Use first layer untuk collision grid
        if self.map.layers:
            layer = self.map.layers[0]
            for row in layer['tiles']:
                grid_row = []
                for gid in row:
                    is_solid = self.map.is_tile_solid(gid)
                    grid_row.append(1 if is_solid else 0)
                grid.append(grid_row)

        return grid

    def is_position_solid(self, x, y):
        """Check apakah posisi solid"""
        # Check tile grid
        tile_x = int(x // self.map.tile_width)
        tile_y = int(y // self.map.tile_height)

        if (tile_y < 0 or tile_y >= len(self.collision_grid) or
            tile_x < 0 or tile_x >= len(self.collision_grid[0])):
            return True

        if self.collision_grid[tile_y][tile_x] == 1:
            return True

        # Check collision rects
        point = pygame.Rect(x, y, 1, 1)
        for rect in self.collision_rects:
            if rect.colliderect(point):
                return True

        return False

    def is_rect_colliding(self, rect):
        """Check apakah rectangle colliding"""
        # Check corners
        corners = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1),
            (rect.centerx, rect.centery)
        ]

        for x, y in corners:
            if self.is_position_solid(x, y):
                return True

        # Check against collision rects
        for col_rect in self.collision_rects:
            if rect.colliderect(col_rect):
                return True

        return False

    def draw_debug(self, screen):
        """Draw collision debug"""
        # Draw grid
        for y, row in enumerate(self.collision_grid):
            for x, is_solid in enumerate(row):
                if is_solid == 1:
                    rect = pygame.Rect(
                        x * self.map.tile_width - camera.x,
                        y * self.map.tile_height - camera.y,
                        self.map.tile_width,
                        self.map.tile_height
                    )
                    surface = pygame.Surface((self.map.tile_width, self.map.tile_height))
                    surface.set_alpha(80)
                    surface.fill((255, 0, 0))
                    screen.blit(surface, rect.topleft)

        # Draw collision rects
        self.map.draw_collision_debug(screen)


# Example usage function
def create_tiled_map_example():
    """
    Contoh cara menggunakan TiledMap
    """
    # Load map
    tiled_map = TiledMap("maps/level1.tmx")

    # Get collision
    map_collision = TiledMapCollision(tiled_map)

    # Get spawn points
    spawns = tiled_map.get_spawn_points()
    player_spawn = spawns.get('player', (100, 100))

    return tiled_map, map_collision, player_spawn
