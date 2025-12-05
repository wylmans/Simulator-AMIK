import pygame
import random
import math
from core.camera import camera


class Particle:
    """Individual particle dalam emitter"""

    def __init__(self, x, y, vx, vy, lifetime, color, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.alpha = 255

    def update(self, dt):
        """Update posisi dan lifetime"""
        self.x += self.vx * (dt / 16.0)  # Normalize to 16ms frame
        self.y += self.vy * (dt / 16.0)
        self.lifetime -= dt

        # Fade out as lifetime decreases
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, screen):
        """Draw particle ke screen"""
        if self.alpha <= 0:
            return

        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)

        # Create surface dengan alpha
        surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*self.color, self.alpha), (self.size, self.size), self.size)
        screen.blit(surface, (screen_x - self.size, screen_y - self.size))

    def is_alive(self):
        """Check if particle masih hidup"""
        return self.lifetime > 0


class ParticleEmitter:
    """Emitter untuk spawn particles"""

    def __init__(self, x, y, emission_rate=5, velocity_range=(-3, 3), lifetime=500):
        """
        Args:
            x, y: Posisi emitter
            emission_rate: Jumlah particles per frame
            velocity_range: Tuple (min, max) untuk random velocity
            lifetime: Lifetime particles dalam milliseconds
        """
        self.x = x
        self.y = y
        self.emission_rate = emission_rate
        self.velocity_range = velocity_range
        self.lifetime = lifetime
        self.particles = []
        self.color = (200, 180, 160)  # Dust color (brownish)
        self.size = 3

    def update(self, x, y, dt):
        """Update posisi emitter dan emit particles"""
        self.x = x
        self.y = y

        # Emit new particles
        for _ in range(self.emission_rate):
            # Random velocity dalam semua arah
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(self.velocity_range[0], self.velocity_range[1])
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            # Spread dari posisi emitter
            spread = 5
            px = self.x + random.uniform(-spread, spread)
            py = self.y + random.uniform(-spread, spread)

            particle = Particle(px, py, vx, vy, self.lifetime, self.color, self.size)
            self.particles.append(particle)

        # Update existing particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

    def draw(self, screen):
        """Draw semua particles"""
        for particle in self.particles:
            particle.draw(screen)

    def set_color(self, color):
        """Set warna particles"""
        self.color = color

    def set_emission_rate(self, rate):
        """Set emission rate"""
        self.emission_rate = rate


class DustEmitter(ParticleEmitter):
    """Emitter khusus untuk dust/dirt saat movement"""

    def __init__(self, x, y):
        super().__init__(x, y, emission_rate=3, velocity_range=(-2, 2), lifetime=400)
        self.set_color((150, 140, 120))  # Darker brown for dirt
        self.size = 2


class SprintEmitter(ParticleEmitter):
    """Emitter khusus untuk sprint effect (lebih banyak particles, lebih cepat)"""

    def __init__(self, x, y):
        super().__init__(x, y, emission_rate=8, velocity_range=(-4, 4), lifetime=300)
        self.set_color((100, 200, 255))  # Light blue for speed effect
        self.size = 3
