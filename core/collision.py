import pygame

class CollisionBox:
    """
    Collision box untuk entity (player, NPC, dll)
    Bisa berupa rectangle atau circle
    """

    def __init__(self, x, y, width, height, shape="rect"):
        """
        Args:
            x, y: Posisi collision box (biasanya relative ke sprite)
            width, height: Ukuran collision box
            shape: "rect" atau "circle"
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.shape = shape

        # Offset dari posisi sprite (untuk fine-tuning)
        self.offset_x = 0
        self.offset_y = 0

    def get_rect(self, entity_x, entity_y):
        """Get pygame Rect untuk collision check"""
        return pygame.Rect(
            entity_x + self.offset_x,
            entity_y + self.offset_y,
            self.width,
            self.height
        )

    def get_circle(self, entity_x, entity_y):
        """Get circle data (center_x, center_y, radius)"""
        center_x = entity_x + self.offset_x + self.width // 2
        center_y = entity_y + self.offset_y + self.height // 2
        radius = min(self.width, self.height) // 2
        return (center_x, center_y, radius)

    def draw_debug(self, screen, entity_x, entity_y, camera):
        """Draw collision box untuk debugging"""
        if self.shape == "rect":
            rect = self.get_rect(entity_x, entity_y)
            # Adjust untuk camera
            debug_rect = pygame.Rect(
                rect.x - camera.x,
                rect.y - camera.y,
                rect.width,
                rect.height
            )
            pygame.draw.rect(screen, (255, 0, 0), debug_rect, 2)

        elif self.shape == "circle":
            cx, cy, radius = self.get_circle(entity_x, entity_y)
            # Adjust untuk camera
            pygame.draw.circle(screen, (255, 0, 0),
                             (int(cx - camera.x), int(cy - camera.y)),
                             radius, 2)


class CollisionChecker:
    """Helper untuk check collision antara entities"""

    @staticmethod
    def rect_vs_rect(rect1, rect2):
        """Check collision antara 2 rectangle"""
        return rect1.colliderect(rect2)

    @staticmethod
    def circle_vs_circle(circle1, circle2):
        """
        Check collision antara 2 circle
        circle = (center_x, center_y, radius)
        """
        cx1, cy1, r1 = circle1
        cx2, cy2, r2 = circle2

        dx = cx2 - cx1
        dy = cy2 - cy1
        distance = (dx*dx + dy*dy) ** 0.5

        return distance < (r1 + r2)

    @staticmethod
    def rect_vs_circle(rect, circle):
        """Check collision antara rectangle dan circle"""
        cx, cy, radius = circle

        # Find closest point on rectangle to circle center
        closest_x = max(rect.left, min(cx, rect.right))
        closest_y = max(rect.top, min(cy, rect.bottom))

        # Calculate distance
        dx = cx - closest_x
        dy = cy - closest_y
        distance = (dx*dx + dy*dy) ** 0.5

        return distance < radius

    @staticmethod
    def check_collision(entity1, entity2):
        """
        Check collision antara 2 entity yang punya collision_box

        Args:
            entity1, entity2: Object dengan atribut collision_box, x, y

        Returns:
            True jika collide, False jika tidak
        """
        if not hasattr(entity1, 'collision_box') or not hasattr(entity2, 'collision_box'):
            return False

        box1 = entity1.collision_box
        box2 = entity2.collision_box

        # Both rect
        if box1.shape == "rect" and box2.shape == "rect":
            rect1 = box1.get_rect(entity1.x, entity1.y)
            rect2 = box2.get_rect(entity2.x, entity2.y)
            return CollisionChecker.rect_vs_rect(rect1, rect2)

        # Both circle
        elif box1.shape == "circle" and box2.shape == "circle":
            circle1 = box1.get_circle(entity1.x, entity1.y)
            circle2 = box2.get_circle(entity2.x, entity2.y)
            return CollisionChecker.circle_vs_circle(circle1, circle2)

        # Mixed
        else:
            if box1.shape == "rect":
                rect = box1.get_rect(entity1.x, entity1.y)
                circle = box2.get_circle(entity2.x, entity2.y)
            else:
                rect = box2.get_rect(entity2.x, entity2.y)
                circle = box1.get_circle(entity1.x, entity1.y)

            return CollisionChecker.rect_vs_circle(rect, circle)


class MapCollision:
    """
    Sistem collision untuk tile map
    Support collision layer dari Tiled atau manual definition
    """

    def __init__(self, map_obj, collision_layer=None):
        """
        Args:
            map_obj: Object Map dari map.py
            collision_layer: List 2D yang marking tile collision (optional)
                           1 = solid, 0 = walkable
        """
        self.map = map_obj
        self.collision_layer = collision_layer

        # Jika tidak ada collision layer, gunakan is_solid dari tile_kinds
        if collision_layer is None:
            self._generate_collision_from_tiles()

    def _generate_collision_from_tiles(self):
        """Generate collision layer dari tile properties"""
        self.collision_layer = []
        for row in self.map.tiles:
            collision_row = []
            for tile_id in row:
                if tile_id < len(self.map.tile_kinds):
                    is_solid = self.map.tile_kinds[tile_id].is_solid
                    collision_row.append(1 if is_solid else 0)
                else:
                    collision_row.append(0)
            self.collision_layer.append(collision_row)

    def is_position_solid(self, x, y):
        """
        Check apakah posisi (x, y) di map adalah solid tile

        Args:
            x, y: Koordinat dalam pixel

        Returns:
            True jika solid, False jika walkable
        """
        # Convert pixel ke tile coordinate
        tile_x = int(x // self.map.tile_size)
        tile_y = int(y // self.map.tile_size)

        # Defensive checks: collision_layer may be empty or rows may vary in length
        if not self.collision_layer:
            # No collision data — treat everything as walkable (not solid)
            return False

        # Check tile_y bounds first
        if tile_y < 0 or tile_y >= len(self.collision_layer):
            return True  # Out of bounds vertically = solid

        row = self.collision_layer[tile_y]
        # If the row is missing or shorter than expected treat as solid
        if not row or tile_x < 0 or tile_x >= len(row):
            return True

        return row[tile_x] == 1

    def is_rect_colliding(self, rect):
        """
        Check apakah rectangle collide dengan solid tiles
        Improved: Check lebih banyak points untuk collision lebih akurat

        Args:
            rect: pygame.Rect object

        Returns:
            True jika collide dengan tile solid
        """
        # Check corners
        corners = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),  # -1 untuk avoid pixel perfect edge cases
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1)
        ]

        for x, y in corners:
            if self.is_position_solid(x, y):
                return True

        # Check midpoints untuk object yang lebih besar
        midpoints = [
            (rect.centerx, rect.top),
            (rect.centerx, rect.bottom - 1),
            (rect.left, rect.centery),
            (rect.right - 1, rect.centery)
        ]

        for x, y in midpoints:
            if self.is_position_solid(x, y):
                return True

        # Check center
        if self.is_position_solid(rect.centerx, rect.centery):
            return True

        return False

    def get_collision_tiles_in_area(self, rect):
        """
        Get semua tile collision dalam area tertentu

        Returns:
            List of (tile_x, tile_y) yang solid
        """
        solid_tiles = []

        # Convert rect ke tile coordinates
        start_x = max(0, int(rect.left // self.map.tile_size))
        # Choose an end_x that won't blow past any individual row — we'll bounds-check when indexing
        max_row_len = max((len(r) for r in self.collision_layer), default=0)
        end_x = min(max_row_len, int(rect.right // self.map.tile_size) + 1)
        start_y = max(0, int(rect.top // self.map.tile_size))
        end_y = min(len(self.collision_layer),
                   int(rect.bottom // self.map.tile_size) + 1)

        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                # Ensure tx is a valid index for this row
                if tx < len(self.collision_layer[ty]) and self.collision_layer[ty][tx] == 1:
                    solid_tiles.append((tx, ty))

        return solid_tiles

    def push_out_of_collision(self, rect, velocity_x, velocity_y):
        """
        Push rect keluar dari collision (untuk smooth sliding)

        Returns:
            (new_x, new_y, hit_x, hit_y) - posisi baru dan flag collision per axis
        """
        hit_x = False
        hit_y = False

        # Get collision tiles
        solid_tiles = self.get_collision_tiles_in_area(rect)

        if not solid_tiles:
            return (rect.x, rect.y, hit_x, hit_y)

        # Simple push out: revert ke posisi sebelumnya
        new_x = rect.x
        new_y = rect.y

        # Check X axis collision
        if velocity_x != 0:
            test_rect = rect.copy()
            test_rect.x -= velocity_x
            if not self.is_rect_colliding(test_rect):
                new_x = test_rect.x
                hit_x = True

        # Check Y axis collision
        if velocity_y != 0:
            test_rect = rect.copy()
            test_rect.y -= velocity_y
            if not self.is_rect_colliding(test_rect):
                new_y = test_rect.y
                hit_y = True

        return (new_x, new_y, hit_x, hit_y)

    def draw_debug(self, screen, camera):
        """Draw collision layer untuk debugging"""
        for y, row in enumerate(self.collision_layer):
            for x, is_solid in enumerate(row):
                if is_solid == 1:
                    rect = pygame.Rect(
                        x * self.map.tile_size - camera.x,
                        y * self.map.tile_size - camera.y,
                        self.map.tile_size,
                        self.map.tile_size
                    )
                    # Draw semi-transparent red overlay
                    surface = pygame.Surface((self.map.tile_size, self.map.tile_size))
                    surface.set_alpha(100)
                    surface.fill((255, 0, 0))
                    screen.blit(surface, rect.topleft)
                    pygame.draw.rect(screen, (255, 0, 0), rect, 1)
