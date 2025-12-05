import pygame
from core.input import is_key_pressed
from core.camera import camera
from core.collision import CollisionBox
from core.animated_sprite import AnimatedSprite


class Player:
    """
    Player dengan animated sprite dan directional animations
    Support untuk idle dan walking animations dalam 4 arah
    """

    def __init__(self, spritesheet_path, json_path, x, y, name="Player"):
        """
        Args:
            spritesheet_path: Path ke PNG spritesheet
            json_path: Path ke JSON metadata dari Aseprite
            x, y: Posisi spawn
            name: Nama player yang ditampilkan
        """
        self.x = x
        self.y = y
        self.name = name

        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.15  # Smooth acceleration (slower increase)
        self.friction = 0.85  # Friction for smooth deceleration
        self.max_speed = 3.5  # Normal max speed
        self.sprint_speed = 6.0  # Sprint max speed
        self.is_sprinting = False  # Sprint state

        # Direction tracking
        self.facing_direction = "down"  # "up", "down", "left", "right"
        self.is_moving = False

        # Animated sprite
        self.sprite = AnimatedSprite(
            spritesheet_path,
            json_path,
            x, y,
            fallback_color=(100, 150, 255)  # Blue fallback
        )

        # Directional sprites for different directions
        # Maps direction to sprite object: {"left": sprite, "right": sprite, etc}
        self.directional_sprites = {}  # Can be populated with set_directional_sprite()

        # Idle directional sprites (separate from walk sprites)
        # Maps direction to idle sprite: {"left": sprite, "right": sprite, etc}
        self.idle_directional_sprites = {}  # Can be populated with set_idle_directional_sprite()

        # Alternative sprites for walking (optional)
        # Can be set with set_walk_sprite()
        self.walk_sprite = None
        self.current_sprite_type = "idle"  # "idle" or "walk"

        # Collision box
        self.collision_box = CollisionBox(0, 0, 24, 24, "rect")
        self.collision_box.offset_x = 4
        self.collision_box.offset_y = 32  # Offset lebih ke bawah untuk sprite 32x64

        # Font for name display
        self.name_font = pygame.font.Font(None, 20)
        self.name_color = (255, 255, 255)
        self.name_bg_color = (0, 0, 0)
        self.show_name = True

    def set_walk_sprite(self, spritesheet_path, json_path):
        """Set sprite untuk walking animation (optional)"""
        try:
            self.walk_sprite = AnimatedSprite(
                spritesheet_path,
                json_path,
                self.x, self.y,
                fallback_color=(100, 150, 255)
            )
            print(f"[OK] Walk sprite loaded: {spritesheet_path}")
        except Exception as e:
            print(f"[WARNING] Failed to load walk sprite: {e}")

    def set_directional_sprite(self, direction, spritesheet_path, json_path):
        """
        Set sprite untuk specific direction (left, right, up, down)

        Args:
            direction: "left", "right", "up", or "down"
            spritesheet_path: Path ke PNG file
            json_path: Path ke JSON file
        """
        try:
            sprite = AnimatedSprite(
                spritesheet_path,
                json_path,
                self.x, self.y,
                fallback_color=(100, 150, 255)
            )
            self.directional_sprites[direction] = sprite
            print(f"[OK] Direction sprite '{direction}' loaded: {spritesheet_path}")
        except Exception as e:
            print(f"[WARNING] Failed to load {direction} sprite: {e}")

    def set_idle_directional_sprite(self, direction, spritesheet_path, json_path):
        """
        Set idle sprite untuk specific direction (left, right, up, down)

        Args:
            direction: "left", "right", "up", or "down"
            spritesheet_path: Path ke PNG file
            json_path: Path ke JSON file
        """
        try:
            sprite = AnimatedSprite(
                spritesheet_path,
                json_path,
                self.x, self.y,
                fallback_color=(100, 150, 255)
            )
            self.idle_directional_sprites[direction] = sprite
            print(f"[OK] Idle direction sprite '{direction}' loaded: {spritesheet_path}")
        except Exception as e:
            print(f"[WARNING] Failed to load idle {direction} sprite: {e}")

    def update(self, map_collision=None, dt=16):
        """
        Update player movement dan animation

        Args:
            map_collision: Collision system
            dt: Delta time (default 16ms for 60fps)
        """
        # Get input direction
        input_x = 0
        input_y = 0

        if is_key_pressed(pygame.K_w):
            input_y -= 1
        if is_key_pressed(pygame.K_s):
            input_y += 1
        if is_key_pressed(pygame.K_a):
            input_x -= 1
        if is_key_pressed(pygame.K_d):
            input_x += 1

        # Check sprint (LShift)
        self.is_sprinting = is_key_pressed(pygame.K_LSHIFT) and (input_x != 0 or input_y != 0)

        # Check if moving
        self.is_moving = (input_x != 0 or input_y != 0)

        # Update facing direction
        if input_x > 0:
            self.facing_direction = "right"
        elif input_x < 0:
            self.facing_direction = "left"
        elif input_y > 0:
            self.facing_direction = "down"
        elif input_y < 0:
            self.facing_direction = "up"

        # Normalize diagonal movement
        if input_x != 0 and input_y != 0:
            input_x *= 0.707
            input_y *= 0.707

        # Apply acceleration
        if input_x != 0:
            self.velocity_x += input_x * self.acceleration
        else:
            self.velocity_x *= self.friction

        if input_y != 0:
            self.velocity_y += input_y * self.acceleration
        else:
            self.velocity_y *= self.friction

        # Clamp velocity to max speed (normal or sprint)
        current_max_speed = self.sprint_speed if self.is_sprinting else self.max_speed
        speed = (self.velocity_x**2 + self.velocity_y**2)**0.5
        if speed > current_max_speed:
            self.velocity_x = (self.velocity_x / speed) * current_max_speed
            self.velocity_y = (self.velocity_y / speed) * current_max_speed

        # Stop small velocities
        if abs(self.velocity_x) < 0.01:
            self.velocity_x = 0
        if abs(self.velocity_y) < 0.01:
            self.velocity_y = 0

        # Apply movement with collision
        if map_collision:
            self._move_with_collision(map_collision)
        else:
            self.x += self.velocity_x
            self.y += self.velocity_y

        # Update sprite position
        self.sprite.x = self.x
        self.sprite.y = self.y
        if self.walk_sprite:
            self.walk_sprite.x = self.x
            self.walk_sprite.y = self.y
        # Update all directional sprites
        for direction, sprite in self.directional_sprites.items():
            sprite.x = self.x
            sprite.y = self.y
        # Update all idle directional sprites
        for direction, sprite in self.idle_directional_sprites.items():
            sprite.x = self.x
            sprite.y = self.y

        # Update animation
        self._update_animation()

        # Update the active sprite based on movement state and direction
        active_sprite = self._get_active_sprite()
        active_sprite.update(dt)

        # Update camera
        camera.x = self.x - camera.width / 2 + 16  # Center on sprite (32/2 = 16)
        camera.y = self.y - camera.height / 2 + 32  # Center vertically

    def _get_active_sprite(self):
        """Get the sprite to use based on current direction and movement state"""
        # If moving: prioritize directional walk sprites
        if self.is_moving:
            if self.facing_direction in self.directional_sprites:
                return self.directional_sprites[self.facing_direction]
            elif self.walk_sprite:
                return self.walk_sprite
        else:
            # If idle: prioritize idle directional sprites
            if self.facing_direction in self.idle_directional_sprites:
                return self.idle_directional_sprites[self.facing_direction]

        # Default to main sprite
        return self.sprite

    def _update_animation(self):
        """Update animation berdasarkan movement dan direction"""
        # Get the active sprite to use
        sprite = self._get_active_sprite()

        # Determine animation name
        if self.is_moving and self.facing_direction in self.directional_sprites:
            # Walking animations for directional sprites
            anim_name = f"walk_{self.facing_direction}"
        elif self.is_moving and self.walk_sprite and self.facing_direction not in self.directional_sprites:
            # Walking animations (use walk_sprite)
            anim_name = f"walk_{self.facing_direction}"
        else:
            # Idle animations (use main sprite)
            anim_name = f"idle_{self.facing_direction}"

        # Try exact animation first
        if anim_name in sprite.animations:
            sprite.play_animation(anim_name)
            return

        # Fallback: try generic versions
        if self.is_moving:
            walk_variants = [k for k in sprite.animations.keys() if k.startswith("walk_")]
            if walk_variants:
                sprite.play_animation(walk_variants[0])
            elif "walk" in sprite.animations:
                sprite.play_animation("walk")
        else:
            # For idle, check all idle_* variants
            idle_variants = [k for k in sprite.animations.keys() if k.startswith("idle_")]
            if idle_variants:
                sprite.play_animation(idle_variants[0])
            elif "idle" in sprite.animations:
                sprite.play_animation("idle")

    def _move_with_collision(self, map_collision):
        """Movement dengan collision detection"""
        def _step_move(axis: str, delta: float):
            if delta == 0:
                return

            steps = max(1, int(abs(delta)))
            step_amount = delta / steps

            for _ in range(steps):
                if axis == 'x':
                    self.x += step_amount
                else:
                    self.y += step_amount

                rect = self.collision_box.get_rect(self.x, self.y)
                if map_collision.is_rect_colliding(rect):
                    if axis == 'x':
                        self.x -= step_amount
                        self.velocity_x = 0
                    else:
                        self.y -= step_amount
                        self.velocity_y = 0
                    break

        _step_move('x', self.velocity_x)
        _step_move('y', self.velocity_y)

    def draw(self, screen):
        """Draw player sprite dan nama"""
        # Draw the correct sprite based on direction and movement state
        active_sprite = self._get_active_sprite()
        active_sprite.draw(screen)

        # Draw name above character
        if self.show_name:
            self._draw_name(screen)

    def _draw_name(self, screen):
        """Draw nama di atas karakter"""
        # Render name text
        name_surface = self.name_font.render(self.name, True, self.name_color)

        # Calculate position (centered above sprite)
        name_x = self.x - camera.x + 16 - name_surface.get_width() // 2
        name_y = self.y - camera.y - 10  # 10px above sprite

        # Draw background (semi-transparent)
        bg_padding = 4
        bg_rect = pygame.Rect(
            name_x - bg_padding,
            name_y - bg_padding,
            name_surface.get_width() + bg_padding * 2,
            name_surface.get_height() + bg_padding * 2
        )

        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill(self.name_bg_color)
        screen.blit(bg_surface, (bg_rect.x, bg_rect.y))

        # Draw border
        pygame.draw.rect(screen, self.name_color, bg_rect, 1)

        # Draw name text
        screen.blit(name_surface, (name_x, name_y))

    def draw_debug(self, screen):
        """Draw collision box untuk debugging"""
        self.collision_box.draw_debug(screen, self.x, self.y, camera)

        # Draw center point
        center_x = int(self.x - camera.x + 16)
        center_y = int(self.y - camera.y + 32)
        pygame.draw.circle(screen, (255, 0, 255), (center_x, center_y), 3)

        # Draw direction indicator
        dir_offsets = {
            "up": (0, -20),
            "down": (0, 20),
            "left": (-20, 0),
            "right": (20, 0)
        }

        if self.facing_direction in dir_offsets:
            dx, dy = dir_offsets[self.facing_direction]
            pygame.draw.line(
                screen,
                (255, 255, 0),
                (center_x, center_y),
                (center_x + dx, center_y + dy),
                2
            )

    def get_rect(self):
        """Get bounding rect untuk collision checks"""
        return self.collision_box.get_rect(self.x, self.y)
