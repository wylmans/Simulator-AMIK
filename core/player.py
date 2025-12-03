import pygame
from core.sprite import Sprite
from core.input import is_key_pressed
from core.camera import camera
from core.collision import CollisionBox


class Player(Sprite):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
        self.movement_speed = 2

        # Vector untuk movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.5  # Seberapa cepat karakter berakselerasi
        self.friction = 0.8  # Seberapa cepat karakter berhenti (0-1, lebih kecil = lebih lambat)
        self.max_speed = 2.5  # Kecepatan maksimal

        # Collision box for the player (rectangular by default)
        self.collision_box = CollisionBox(0, 0, 24, 24, "rect")
        self.collision_box.offset_x = 4
        self.collision_box.offset_y = 4

    def update(self, map_collision=None):
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

        # Normalize diagonal movement agar tidak lebih cepat
        if input_x != 0 and input_y != 0:
            # Diagonal: bagi dengan sqrt(2) ≈ 1.414
            input_x *= 0.707
            input_y *= 0.707

        # Apply acceleration based on input
        if input_x != 0:
            self.velocity_x += input_x * self.acceleration
        else:
            # Apply friction when no input
            self.velocity_x *= self.friction

        if input_y != 0:
            self.velocity_y += input_y * self.acceleration
        else:
            self.velocity_y *= self.friction

        # Clamp velocity to max speed
        speed = (self.velocity_x**2 + self.velocity_y**2)**0.5
        if speed > self.max_speed:
            self.velocity_x = (self.velocity_x / speed) * self.max_speed
            self.velocity_y = (self.velocity_y / speed) * self.max_speed

        # Stop movement if velocity is very small (prevent endless sliding)
        if abs(self.velocity_x) < 0.01:
            self.velocity_x = 0
        if abs(self.velocity_y) < 0.01:
            self.velocity_y = 0

        # Apply movement with collision detection (separate X and Y)
        if map_collision:
            self._move_with_collision(map_collision)
        else:
            self.x += self.velocity_x
            self.y += self.velocity_y

        # Update camera to keep player centered
        camera.x = self.x - camera.width / 2 + self.image.get_width() / 2
        camera.y = self.y - camera.height / 2 + self.image.get_height() / 2

    def _move_with_collision(self, map_collision):
        """
        Movement dengan collision detection yang lebih smooth.
        Menggunakan separasi axis (X dan Y dicheck terpisah) untuk sliding di dinding.
        """
        # Safer incremental movement: move in small steps along each axis to avoid tunneling
        # and stop at the nearest non-colliding position for a smooth slide effect.

        # Helper to move along one axis with small steps
        def _step_move(axis: str, delta: float):
            if delta == 0:
                return

            # Number of steps -- ensures we don't skip over thin colliders. At least 1 step.
            steps = max(1, int(abs(delta)))
            step_amount = delta / steps

            for _ in range(steps):
                if axis == 'x':
                    self.x += step_amount
                else:
                    self.y += step_amount

                rect = self.collision_box.get_rect(self.x, self.y)
                if map_collision.is_rect_colliding(rect):
                    # Undo this small step and stop the velocity on that axis
                    if axis == 'x':
                        self.x -= step_amount
                        self.velocity_x = 0
                    else:
                        self.y -= step_amount
                        self.velocity_y = 0
                    # Stop trying further steps on this axis
                    break

        # Move X then Y (separation of axis provides smooth sliding along obstacles)
        _step_move('x', self.velocity_x)
        _step_move('y', self.velocity_y)

    def draw_debug(self, screen):
        """Draw collision box untuk debugging"""
        self.collision_box.draw_debug(screen, self.x, self.y, camera)
