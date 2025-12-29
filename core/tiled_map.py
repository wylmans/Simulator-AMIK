"""
Tiled Map Editor Integration - COMPLETE VERSION
Support untuk .tmx files dari Tiled Map Editor dengan fitur lengkap:
- Infinite maps dengan chunks
- Base64 + zlib/gzip compression
- External tilesets (.tsx)
- CSV dan XML encoding
- Collision detection
- Spawn points
"""

import pygame
import xml.etree.ElementTree as ET
import os
import base64
import zlib
import gzip
import time
from collections import OrderedDict
from core.camera import camera


class LRUCache:
    """Simple LRU cache using OrderedDict."""
    def __init__(self, maxsize=256):
        self.maxsize = int(maxsize)
        self.od = OrderedDict()

    def get(self, key):
        try:
            val = self.od.pop(key)
            # re-insert to mark as recently used
            self.od[key] = val
            return val
        except KeyError:
            return None

    def set(self, key, value):
        if key in self.od:
            self.od.pop(key)
        self.od[key] = value
        # Evict oldest
        if len(self.od) > self.maxsize:
            self.od.popitem(last=False)

    def clear(self):
        self.od.clear()


class TiledMap:
    """
    Load dan render map dari Tiled Map Editor (.tmx format)

    Features:
    - Multiple tile layers (termasuk infinite maps dengan chunks)
    - Object layers (spawn points, collision areas)
    - External dan embedded tilesets
    - Multiple encoding formats (CSV, XML, base64)
    - Compression support (zlib, gzip)
    - Tile properties dan collision detection
    """

    def __init__(self, tmx_file):
        """
        Load TMX file dari Tiled Map Editor

        Args:
            tmx_file: Path ke file .tmx
        """
        self.tmx_file = tmx_file
        self.base_path = os.path.dirname(tmx_file)
        self.layers = []
        self.tilesets = []
        self.objects = {}
        self.tile_properties = {}
        # Small runtime caches
        self._gid_cache = {}
        self._scaled_cache = None
        self._last_zoom = None
        self._timings = {'draw_total': 0.0, 'draw_count': 0, 'tile_scale_time': 0.0}
        self._frame_count = 0
        # Add simple LRU cache class instance available at module scope
        self._gid_cache = {}

        # Map properties
        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0
        self.is_infinite = False

        # Parse TMX file
        self._parse_tmx()

    def _parse_tmx(self):
        """Parse TMX XML file"""
        tree = ET.parse(self.tmx_file)
        root = tree.getroot()

        # Get map properties
        self.width = int(root.get('width', 0))
        self.height = int(root.get('height', 0))
        self.tile_width = int(root.get('tilewidth'))
        self.tile_height = int(root.get('tileheight'))
        self.is_infinite = root.get('infinite', '0') == '1'

        map_type = "INFINITE" if self.is_infinite else "FIXED"
        print(f"[MAP] Loading {map_type} map: {self.width}x{self.height} tiles ({self.tile_width}x{self.tile_height}px)")

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
        """Parse tileset information (embedded or external)"""
        firstgid = int(tileset_elem.get('firstgid'))

        # Check if external tileset
        source = tileset_elem.get('source')
        if source:
            # Load external .tsx file
            tsx_path = os.path.join(self.base_path, source)
            if os.path.exists(tsx_path):
                try:
                    tsx_tree = ET.parse(tsx_path)
                    tsx_root = tsx_tree.getroot()
                    # Pass tileset directory as base for resolving image paths inside tsx
                    tsx_dir = os.path.dirname(tsx_path)
                    self._parse_tileset_data(tsx_root, firstgid, tileset_base=tsx_dir)
                except Exception as e:
                    print(f"⚠️  Failed to load external tileset {source}: {e}")
            else:
                print(f"⚠️  External tileset not found: {tsx_path}")
        else:
            # Embedded tileset
            self._parse_tileset_data(tileset_elem, firstgid, tileset_base=self.base_path)

    def _parse_tileset_data(self, tileset_elem, firstgid, tileset_base=None):
        """Parse actual tileset data (dari embedded atau external tileset)"""
        name = tileset_elem.get('name', 'unnamed')
        tile_width = int(tileset_elem.get('tilewidth'))
        tile_height = int(tileset_elem.get('tileheight'))

        # Get image source
        image_elem = tileset_elem.find('image')
        if image_elem is None:
            print(f"⚠️  No image found for tileset '{name}'")
            return

        source = image_elem.get('source')
        image_width_attr = image_elem.get('width')
        image_height_attr = image_elem.get('height')

        # Load tileset image
        tileset_image = None
        try:
            # If source is absolute, use directly
            if os.path.isabs(source) and os.path.exists(source):
                tileset_image = pygame.image.load(source)
            else:
                # Try relative to tileset_base (tsx dir) first, then TMX base
                tried = []
                if tileset_base:
                    source_path = os.path.join(tileset_base, source)
                    tried.append(source_path)
                    if os.path.exists(source_path):
                        tileset_image = pygame.image.load(source_path)
                if tileset_image is None:
                    # Fallback to TMX base path
                    source_path = os.path.join(self.base_path, source)
                    tried.append(source_path)
                    if os.path.exists(source_path):
                        tileset_image = pygame.image.load(source_path)
                if tileset_image is None:
                    # Try as given (current working dir)
                    tried.append(source)
                    tileset_image = pygame.image.load(source)
        except Exception as e:
            print(f"⚠️  Failed to load tileset image '{source}' (tried: {tried}): {e}")
            return

        # Get image dimensions
        if image_width_attr and image_height_attr:
            image_width = int(image_width_attr)
            image_height = int(image_height_attr)
        else:
            image_width, image_height = tileset_image.get_size()

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
                try:
                    tile_surface = tileset_image.subsurface(rect)
                    tiles.append(tile_surface)
                except:
                    # Create empty tile if subsurface fails
                    empty_tile = pygame.Surface((tile_width, tile_height))
                    empty_tile.fill((255, 0, 255))  # Magenta untuk missing tile
                    tiles.append(empty_tile)

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
        print(f"  📦 Tileset '{name}': {len(tiles)} tiles (firstgid: {firstgid})")

    def _decode_layer_data(self, data_elem, encoding=None, compression=None):
        """Decode layer data berdasarkan encoding dan compression

        If `encoding`/`compression` are provided they take precedence (used when
        decoding <chunk> elements where the parent <data> holds the encoding attrs).
        """
        encoding = encoding or data_elem.get('encoding', 'xml')
        compression = compression or data_elem.get('compression')

        if encoding == 'csv':
            # CSV encoding
            csv_data = data_elem.text.strip()
            tile_ids = [int(x) for x in csv_data.replace('\n', '').split(',') if x.strip()]
            return tile_ids

        elif encoding == 'base64':
            # Base64 encoding
            base64_data = data_elem.text.strip()
            raw_data = base64.b64decode(base64_data)

            # Decompress if needed
            if compression == 'zlib':
                raw_data = zlib.decompress(raw_data)
            elif compression == 'gzip':
                raw_data = gzip.decompress(raw_data)

            # Convert bytes to tile IDs (little-endian 32-bit integers)
            tile_ids = []
            for i in range(0, len(raw_data), 4):
                if i + 4 <= len(raw_data):
                    tile_id = int.from_bytes(raw_data[i:i+4], byteorder='little')
                    tile_ids.append(tile_id)

            return tile_ids

        else:
            # XML encoding (fallback)
            tile_ids = []
            for tile in data_elem.findall('tile'):
                gid = int(tile.get('gid', 0))
                tile_ids.append(gid)
            return tile_ids

    def _parse_layer(self, layer_elem):
        """Parse tile layer (support infinite maps dengan chunks)"""
        name = layer_elem.get('name')
        width = int(layer_elem.get('width', 0))
        height = int(layer_elem.get('height', 0))
        visible = layer_elem.get('visible', '1') == '1'

        data_elem = layer_elem.find('data')
        if data_elem is None:
            return

        # Check for chunks (infinite map)
        chunks = data_elem.findall('chunk')

        if chunks:
            # Infinite map with chunks
            layer_data = {
                'name': name,
                'visible': visible,
                'is_chunked': True,
                'chunks': []
            }

            for chunk_elem in chunks:
                chunk_x = int(chunk_elem.get('x'))
                chunk_y = int(chunk_elem.get('y'))
                chunk_width = int(chunk_elem.get('width'))
                chunk_height = int(chunk_elem.get('height'))

                # Decode chunk data. encoding/compression stored on parent <data>
                tile_ids = self._decode_layer_data(
                    chunk_elem,
                    encoding=data_elem.get('encoding'),
                    compression=data_elem.get('compression')
                )

                # Convert to 2D array
                tiles = []
                for row in range(chunk_height):
                    start = row * chunk_width
                    end = start + chunk_width
                    if end <= len(tile_ids):
                        row_data = tile_ids[start:end]
                        tiles.append(row_data)

                chunk_data = {
                    'x': chunk_x,
                    'y': chunk_y,
                    'width': chunk_width,
                    'height': chunk_height,
                    'tiles': tiles
                }

                layer_data['chunks'].append(chunk_data)

            print(f"  🗺️  Layer '{name}': {len(chunks)} chunks (infinite)")

        else:
            # Standard fixed-size map
            tile_ids = self._decode_layer_data(data_elem)

            # Convert to 2D array
            tiles = []
            for row in range(height):
                start = row * width
                end = start + width
                if end <= len(tile_ids):
                    row_data = tile_ids[start:end]
                    tiles.append(row_data)

            layer_data = {
                'name': name,
                'tiles': tiles,
                'visible': visible,
                'is_chunked': False,
                'width': width,
                'height': height
            }

            print(f"  🗺️  Layer '{name}': {width}x{height} tiles")

        self.layers.append(layer_data)

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

            # Check for polygon/polyline
            polygon_elem = obj.find('polygon')
            polyline_elem = obj.find('polyline')
            polygon_points = None

            if polygon_elem is not None:
                # Parse polygon points
                points_str = polygon_elem.get('points', '')
                polygon_points = self._parse_polygon_points(points_str, x, y)
            elif polyline_elem is not None:
                # Parse polyline points (treat as polygon)
                points_str = polyline_elem.get('points', '')
                polygon_points = self._parse_polygon_points(points_str, x, y)

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
                'polygon': polygon_points,  # None if rectangle
                'properties': properties
            }

            objects.append(obj_data)

        self.objects[name] = objects
        print(f"  📍 Object layer '{name}': {len(objects)} objects")

    def _parse_polygon_points(self, points_str, base_x, base_y):
        """Parse polygon points string to list of (x,y) tuples"""
        if not points_str:
            return None

        points = []
        for point_str in points_str.strip().split():
            try:
                x_str, y_str = point_str.split(',')
                # Points are relative to object position
                px = float(x_str) + base_x
                py = float(y_str) + base_y
                points.append((px, py))
            except:
                continue

        return points if points else None

    def get_tile_surface(self, gid):
        """Get pygame surface untuk tile dengan GID tertentu"""
        if gid == 0:
            return None
        # Use small cache to avoid scanning tilesets every tile draw
        if gid in self._gid_cache:
            return self._gid_cache[gid]

        for tileset in reversed(self.tilesets):  # Check from last to first
            if gid >= tileset['firstgid']:
                local_id = gid - tileset['firstgid']
                if local_id < len(tileset['tiles']):
                    surf = tileset['tiles'][local_id]
                    self._gid_cache[gid] = surf
                    return surf

        self._gid_cache[gid] = None
        return None

    def _ensure_scaled_cache(self):
        if self._scaled_cache is None:
            self._scaled_cache = LRUCache(maxsize=512)

    def get_tile_surface_for_zoom(self, gid, zoom):
        """Return tile surface scaled for current zoom, with LRU caching."""
        base = self.get_tile_surface(gid)
        if base is None:
            return None

        if abs(zoom - 1.0) < 1e-6:
            return base

        self._ensure_scaled_cache()
        key = (gid, round(float(zoom), 3))
        cached = self._scaled_cache.get(key)
        if cached is not None:
            return cached

        # Scale and cache
        t0 = time.perf_counter()
        try:
            w = max(1, int(base.get_width() * zoom))
            h = max(1, int(base.get_height() * zoom))
            scaled = pygame.transform.smoothscale(base, (w, h))
        except Exception:
            scaled = base
        t1 = time.perf_counter()
        self._timings['tile_scale_time'] += (t1 - t0)
        self._scaled_cache.set(key, scaled)
        return scaled

    def is_tile_solid(self, gid):
        """Check apakah tile solid (dari properties)"""
        if gid == 0:
            return False

        properties = self.tile_properties.get(gid, {})
        return properties.get('solid', 'false').lower() == 'true'

    def get_collision_rects(self):
        """Return collision shapes from object layer 'Collision'.

        Returns list of shape dictionaries. Each shape is either:
        - {'type': 'rect', 'rect': pygame.Rect}
        - {'type': 'polygon', 'points': [(x,y), ...]}

        This preserves polygon shapes and avoids converting them to bounding boxes.
        """
        shapes = []

        if 'Collision' in self.objects:
            for obj in self.objects['Collision']:
                if obj.get('polygon'):
                    points = obj['polygon']
                    if points:
                        shapes.append({'type': 'polygon', 'points': points})
                else:
                    # Regular rectangle
                    if obj['width'] > 0 and obj['height'] > 0:
                        rect = pygame.Rect(
                            int(obj['x']),
                            int(obj['y']),
                            int(obj['width']),
                            int(obj['height'])
                        )
                        shapes.append({'type': 'rect', 'rect': rect})

        return shapes

    def get_collision_polygons(self):
        """
        Get collision objects dengan polygon data lengkap (untuk pixel-perfect collision)

        Returns:
            List of dicts: {'type': 'rect'/'polygon', 'rect': Rect/None, 'points': list/None}
        """
        collision_objects = []

        if 'Collision' in self.objects:
            for obj in self.objects['Collision']:
                if obj.get('polygon'):
                    # Polygon object
                    points = obj['polygon']
                    if points:
                        collision_objects.append({
                            'type': 'polygon',
                            'points': points,
                            'rect': None
                        })
                else:
                    # Rectangle object
                    if obj['width'] > 0 and obj['height'] > 0:
                        rect = pygame.Rect(
                            int(obj['x']),
                            int(obj['y']),
                            int(obj['width']),
                            int(obj['height'])
                        )
                        collision_objects.append({
                            'type': 'rect',
                            'rect': rect,
                            'points': None
                        })

        return collision_objects

    def get_spawn_points(self):
        """
        Get spawn points dari object layer 'Spawns' atau 'Spawnner'

        Returns:
            Dict dengan key = name/type, value = (x, y)
        """
        spawns = {}

        # Support both "Spawns" and "Spawnner" (typo common di Tiled)
        layer_name = None
        if 'Spawns' in self.objects:
            layer_name = 'Spawns'
        elif 'Spawnner' in self.objects:
            layer_name = 'Spawnner'

        if layer_name:
            for obj in self.objects[layer_name]:
                key = obj['name'] or obj['type']
                spawns[key] = (int(obj['x']), int(obj['y']))

        return spawns

    def get_collision_polygons(self):
        """
        Get collision objects dengan polygon data lengkap (untuk pixel-perfect collision)

        Returns:
            List of dicts: {'type': 'rect'/'polygon', 'rect': Rect/None, 'points': list/None}
        """
        collision_objects = []

        if 'Collision' in self.objects:
            for obj in self.objects['Collision']:
                if obj.get('polygon'):
                    # Polygon object
                    points = obj['polygon']
                    if points:
                        collision_objects.append({
                            'type': 'polygon',
                            'points': points,
                            'rect': None
                        })
                else:
                    # Rectangle object
                    if obj['width'] > 0 and obj['height'] > 0:
                        rect = pygame.Rect(
                            int(obj['x']),
                            int(obj['y']),
                            int(obj['width']),
                            int(obj['height'])
                        )
                        collision_objects.append({
                            'type': 'rect',
                            'rect': rect,
                            'points': None
                        })

        return collision_objects

    def draw(self, screen):
        """Render semua visible layers"""
        # Invalidate per-zoom caches when zoom changes
        current_zoom = getattr(camera, 'zoom', 1.0)
        if self._last_zoom is None:
            self._last_zoom = current_zoom
        if abs(self._last_zoom - current_zoom) > 1e-6:
            # Clear scaled caches to avoid mismatched sizes and memory growth
            if self._scaled_cache is not None:
                self._scaled_cache.clear()
            self._last_zoom = current_zoom

        t0 = time.perf_counter()
        for layer in self.layers:
            if not layer['visible']:
                continue

            if layer.get('is_chunked', False):
                self.draw_chunked_layer(screen, layer)
            else:
                self.draw_layer(screen, layer)
        t1 = time.perf_counter()
        self._timings['draw_total'] += (t1 - t0)
        self._timings['draw_count'] += 1
        self._frame_count += 1
        if self._frame_count % 60 == 0:
            avg = self._timings['draw_total'] / max(1, self._timings['draw_count'])
            scale_time = self._timings.get('tile_scale_time', 0.0)
            print(f"[PROFILE] draw avg {avg*1000:.2f}ms/frame, tile_scale {scale_time*1000:.2f}ms (last 60 frames)")
            # reset accumulators
            self._timings = {'draw_total': 0.0, 'draw_count': 0, 'tile_scale_time': 0.0}

    def draw_layer(self, screen, layer):
        """Render single standard layer (only iterate visible tiles)."""
        if not layer.get('tiles'):
            return

        layer_width = layer.get('width') or (len(layer['tiles'][0]) if layer['tiles'] else 0)
        layer_height = layer.get('height') or len(layer['tiles'])

        zoom = getattr(camera, 'zoom', 1.0)
        view_left = camera.x
        view_top = camera.y
        view_right = camera.x + screen.get_width() / max(1e-6, zoom)
        view_bottom = camera.y + screen.get_height() / max(1e-6, zoom)

        left = max(0, int(view_left // self.tile_width))
        top = max(0, int(view_top // self.tile_height))
        right = min(layer_width - 1, int(view_right // self.tile_width))
        bottom = min(layer_height - 1, int(view_bottom // self.tile_height))

        if right < left or bottom < top:
            return

        for row_idx in range(top, bottom + 1):
            row = layer['tiles'][row_idx]
            for col_idx in range(left, right + 1):
                gid = row[col_idx]
                if gid == 0:
                    continue

                tile_surface = self.get_tile_surface_for_zoom(gid, zoom)
                if not tile_surface:
                    continue

                x = int((col_idx * self.tile_width - camera.x) * zoom)
                y = int((row_idx * self.tile_height - camera.y) * zoom)
                screen.blit(tile_surface, (x, y))

    def draw_chunked_layer(self, screen, layer):
        """Render chunked layer (infinite map)"""
        zoom = getattr(camera, 'zoom', 1.0)
        view_left = camera.x
        view_top = camera.y
        view_right = camera.x + screen.get_width() / max(1e-6, zoom)
        view_bottom = camera.y + screen.get_height() / max(1e-6, zoom)

        for chunk in layer['chunks']:
            chunk_px_x = chunk['x'] * self.tile_width
            chunk_px_y = chunk['y'] * self.tile_height
            chunk_px_w = chunk['width'] * self.tile_width
            chunk_px_h = chunk['height'] * self.tile_height

            # Cull whole chunk if outside view
            if (chunk_px_x + chunk_px_w < view_left or chunk_px_x > view_right or
                chunk_px_y + chunk_px_h < view_top or chunk_px_y > view_bottom):
                continue

            # Compute local tile range within chunk that intersects view
            start_col = max(0, int((view_left - chunk_px_x) // self.tile_width))
            end_col = min(chunk['width'] - 1, int((view_right - chunk_px_x) // self.tile_width))
            start_row = max(0, int((view_top - chunk_px_y) // self.tile_height))
            end_row = min(chunk['height'] - 1, int((view_bottom - chunk_px_y) // self.tile_height))

            if end_col < start_col or end_row < start_row:
                continue

            for row_idx in range(start_row, end_row + 1):
                row = chunk['tiles'][row_idx]
                for col_idx in range(start_col, end_col + 1):
                    gid = row[col_idx]
                    if gid == 0:
                        continue

                    tile_surface = self.get_tile_surface_for_zoom(gid, zoom)
                    if not tile_surface:
                        continue

                    x = int((chunk_px_x + col_idx * self.tile_width - camera.x) * zoom)
                    y = int((chunk_px_y + row_idx * self.tile_height - camera.y) * zoom)
                    screen.blit(tile_surface, (x, y))

    def draw_collision_debug(self, screen):
        """Draw collision rectangles untuk debugging"""
        shapes = self.get_collision_rects()
        for shape in shapes:
            if shape['type'] == 'rect':
                rect = shape['rect']
                debug_rect = pygame.Rect(
                    rect.x - camera.x,
                    rect.y - camera.y,
                    rect.width,
                    rect.height
                )
                surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                surface.fill((255, 0, 0, 100))
                screen.blit(surface, debug_rect.topleft)
                pygame.draw.rect(screen, (255, 0, 0), debug_rect, 2)
            elif shape['type'] == 'polygon':
                points = shape['points']
                if not points:
                    continue
                # Convert to screen-space points
                pts = [(p[0] - camera.x, p[1] - camera.y) for p in points]

                # Compute bounding box of polygon in screen space to minimize surface size
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                min_x = int(min(xs))
                min_y = int(min(ys))
                max_x = int(max(xs))
                max_y = int(max(ys))

                w = max(1, max_x - min_x)
                h = max(1, max_y - min_y)

                # Create small surface and draw filled polygon with alpha
                poly_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                local_pts = [(px - min_x, py - min_y) for (px, py) in pts]
                pygame.draw.polygon(poly_surf, (255, 0, 0, 100), local_pts)
                screen.blit(poly_surf, (min_x, min_y))

                # Draw outline directly on screen (cheaper than large temporary surfaces)
                pygame.draw.polygon(screen, (255, 0, 0), pts, 2)

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
    """Collision system untuk Tiled maps (support infinite maps)"""

    def __init__(self, tiled_map):
        """
        Args:
            tiled_map: TiledMap object
        """
        self.map = tiled_map
        # Collision shapes (rects and polygons)
        self.collision_shapes = tiled_map.get_collision_rects()

        # Generate collision grid dari tile properties
        if not tiled_map.is_infinite:
            self.collision_grid = self._generate_collision_grid()
        else:
            self.collision_grid = None  # Infinite maps use chunk-based collision
            self.collision_chunks = self._generate_collision_chunks()

    def _generate_collision_grid(self):
        """Generate 2D grid collision dari tile properties (untuk fixed maps)"""
        grid = []

        # Use first layer untuk collision grid
        if self.map.layers:
            layer = self.map.layers[0]
            if not layer.get('is_chunked', False):
                for row in layer['tiles']:
                    grid_row = []
                    for gid in row:
                        is_solid = self.map.is_tile_solid(gid)
                        grid_row.append(1 if is_solid else 0)
                    grid.append(grid_row)

        return grid

    def _generate_collision_chunks(self):
        """Generate collision data untuk infinite maps (chunk-based)"""
        chunks = {}

        if self.map.layers:
            layer = self.map.layers[0]
            if layer.get('is_chunked', False):
                for chunk in layer['chunks']:
                    chunk_key = (chunk['x'], chunk['y'])
                    chunk_grid = []

                    for row in chunk['tiles']:
                        grid_row = []
                        for gid in row:
                            is_solid = self.map.is_tile_solid(gid)
                            grid_row.append(1 if is_solid else 0)
                        chunk_grid.append(grid_row)

                    chunks[chunk_key] = {
                        'grid': chunk_grid,
                        'width': chunk['width'],
                        'height': chunk['height']
                    }

        return chunks



    def _point_in_polygon(self, x, y, polygon):
        """
        Ray casting algorithm untuk point-in-polygon test

        Args:
            x, y: Point coordinates
            polygon: List of (x, y) tuples

        Returns:
            True if point inside polygon, False otherwise
        """
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]

            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside

            p1x, p1y = p2x, p2y

        return inside
    def _rect_corners(self, rect):
        return [
            (rect.left, rect.top),
            (rect.right, rect.top),
            (rect.right, rect.bottom),
            (rect.left, rect.bottom)
        ]

    def _segments_intersect(self, a1, a2, b1, b2):
        def ccw(p1, p2, p3):
            return (p3[1]-p1[1]) * (p2[0]-p1[0]) > (p2[1]-p1[1]) * (p3[0]-p1[0])
        return (ccw(a1, b1, b2) != ccw(a2, b1, b2)) and (ccw(a1, a2, b1) != ccw(a1, a2, b2))

    def _polygon_rect_intersect(self, polygon, rect):
        # 1) Any polygon point inside rect
        for px, py in polygon:
            if rect.collidepoint(px, py):
                return True

        # 2) Any rect corner inside polygon
        for cx, cy in self._rect_corners(rect):
            if self._point_in_polygon(cx, cy, polygon):
                return True

        # 3) Any edge intersects
        poly_len = len(polygon)
        rect_pts = self._rect_corners(rect)
        rect_edges = []
        for i in range(4):
            rect_edges.append((rect_pts[i], rect_pts[(i+1)%4]))

        for i in range(poly_len):
            a1 = polygon[i]
            a2 = polygon[(i+1) % poly_len]
            for b1, b2 in rect_edges:
                if self._segments_intersect(a1, a2, b1, b2):
                    return True

        return False
    def is_position_solid(self, x, y):
        """Check apakah posisi solid (with pixel-perfect polygon support)"""
        # Check collision objects (polygons and rects) - PRIORITY!
        for obj in self.collision_shapes:
            if obj['type'] == 'polygon':
                if self._point_in_polygon(x, y, obj['points']):
                    return True
            elif obj['type'] == 'rect':
                point_rect = pygame.Rect(x, y, 1, 1)
                if obj['rect'].colliderect(point_rect):
                    return True

        # Check tile grid
        if self.collision_grid:
            # Fixed map
            tile_x = int(x // self.map.tile_width)
            tile_y = int(y // self.map.tile_height)

            if (0 <= tile_y < len(self.collision_grid) and
                0 <= tile_x < len(self.collision_grid[0])):
                return self.collision_grid[tile_y][tile_x] == 1

        elif self.collision_chunks:
            # Infinite map - check relevant chunk
            chunk_x = int(x // (self.map.tile_width * 16))  # Assuming 16x16 chunks
            chunk_y = int(y // (self.map.tile_height * 16))
            chunk_key = (chunk_x, chunk_y)

            if chunk_key in self.collision_chunks:
                chunk = self.collision_chunks[chunk_key]
                local_x = int((x - chunk_x * self.map.tile_width * 16) // self.map.tile_width)
                local_y = int((y - chunk_y * self.map.tile_height * 16) // self.map.tile_height)

                if (0 <= local_y < len(chunk['grid']) and
                    0 <= local_x < len(chunk['grid'][0])):
                    return chunk['grid'][local_y][local_x] == 1

        return False

    def is_rect_colliding(self, rect):
        """Check apakah rectangle colliding"""
        # Check corners and center
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
        for shape in self.collision_shapes:
            if shape['type'] == 'rect':
                if rect.colliderect(shape['rect']):
                    return True
            elif shape['type'] == 'polygon':
                if self._polygon_rect_intersect(shape['points'], rect):
                    return True

        return False

    def draw_debug(self, screen):
        """Draw collision debug"""
        # Draw grid
        if self.collision_grid:
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
    tiled_map = TiledMap("maps/campus.tmx")

    # Get collision
    map_collision = TiledMapCollision(tiled_map)

    # Get spawn points
    spawns = tiled_map.get_spawn_points()
    player_spawn = spawns.get('player', (100, 100))

    return tiled_map, map_collision, player_spawn
