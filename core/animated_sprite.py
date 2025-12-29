import pygame
import json
import os
from core.camera import camera

class AnimatedSprite:
    """
    Class untuk animated sprite yang kompatibel dengan Aseprite
    Fallback ke kotak warna jika sprite tidak ada
    """

    def __init__(self, spritesheet_path, json_path=None, x=0, y=0, fallback_color=(100, 100, 200)):
        """
        Args:
            spritesheet_path: Path ke file PNG spritesheet dari Aseprite
            json_path: Path ke file JSON metadata (optional, auto-detect jika None)
            x, y: Posisi sprite di map
            fallback_color: Warna kotak fallback jika sprite tidak ada
        """
        self.x = x
        self.y = y
        self.fallback_color = fallback_color

        # Animation state
        self.current_animation = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.animations = {}

        # Try load sprite, fallback ke kotak jika gagal
        self.using_fallback = False

        if json_path is None:
            # Auto-detect JSON file (sama nama dengan PNG tapi .json)
            json_path = spritesheet_path.replace('.png', '.json')

        if os.path.exists(spritesheet_path) and os.path.exists(json_path):
            try:
                self._load_aseprite_sprite(spritesheet_path, json_path)
                print(f"[OK] Loaded animated sprite: {os.path.basename(spritesheet_path)}")
            except Exception as e:
                print(f"[WARNING] Failed to load sprite, using fallback: {e}")
                self._create_fallback_sprite()
        else:
            self._create_fallback_sprite()

    def _load_aseprite_sprite(self, spritesheet_path, json_path):
        """Load spritesheet dan metadata dari Aseprite export"""
        # Load spritesheet image
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

        # Load JSON metadata
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Parse frames dari Aseprite JSON
        frames_data = data['frames']

        # Kelompokkan frames berdasarkan animation tag
        # Prepare frame surfaces cache
        self.frame_surfaces = {}

        if 'meta' in data and 'frameTags' in data['meta']:
            # Jika ada animation tags
            for tag in data['meta']['frameTags']:
                anim_name = tag['name']
                from_frame = tag['from']
                to_frame = tag['to']

                frames = []
                frame_keys = list(frames_data.keys())

                # Handle case where we only have one frame entry but multiple tags
                # (Aseprite grid-based export)
                if len(frame_keys) == 1 and len(frames_data) == 1:
                    # Get frame dimensions
                    single_frame = frames_data[frame_keys[0]]
                    total_width = single_frame['frame']['w']
                    frame_height = single_frame['frame']['h']
                    num_frames = to_frame - from_frame + 1
                    frame_width = total_width // num_frames

                    # Generate frame rects from the grid
                    for i in range(from_frame, to_frame + 1):
                        frame_x = (i - from_frame) * frame_width
                        frames.append({
                            'rect': {
                                'x': frame_x,
                                'y': 0,
                                'w': frame_width,
                                'h': frame_height
                            },
                            'duration': single_frame['duration']
                        })
                else:
                    # Standard multi-frame export
                    for i in range(from_frame, to_frame + 1):
                        if i < len(frame_keys):
                            frame_key = frame_keys[i]
                            frame_info = frames_data[frame_key]
                            frames.append({
                                'rect': frame_info['frame'],
                                'duration': frame_info['duration']
                            })

                self.animations[anim_name] = frames

        # Pre-extract surfaces for all frames to avoid per-frame Surface creation
        for anim_name, frames in self.animations.items():
            surf_list = []
            for frame_data in frames:
                rect = frame_data['rect']
                frame_surface = pygame.Surface((rect['w'], rect['h']), pygame.SRCALPHA)
                frame_surface.blit(self.spritesheet, (0, 0), (rect['x'], rect['y'], rect['w'], rect['h']))
                surf_list.append(frame_surface)
            self.frame_surfaces[anim_name] = surf_list
        else:
            # Jika tidak ada tags, semua frame jadi "idle"
            frames = []
            for frame_key, frame_info in frames_data.items():
                frames.append({
                    'rect': frame_info['frame'],
                    'duration': frame_info['duration']
                })
            self.animations['idle'] = frames

        # Set default animation
        if 'idle' not in self.animations and self.animations:
            self.current_animation = list(self.animations.keys())[0]

        self.using_fallback = False

    def _create_fallback_sprite(self):
        """Buat sprite fallback (kotak warna)"""
        self.spritesheet = pygame.Surface((48, 48))
        self.spritesheet.fill(self.fallback_color)

        # Single frame "animation"
        self.animations = {
            'idle': [{
                'rect': {'x': 0, 'y': 0, 'w': 48, 'h': 48},
                'duration': 100
            }]
        }

        self.using_fallback = True
        # Pre-extract fallback frame
        self.frame_surfaces = {'idle': [self.spritesheet.copy()]}
        print(f"[FALLBACK] Using fallback sprite (colored box)")

    def play_animation(self, animation_name):
        """Ganti animasi"""
        if animation_name in self.animations and animation_name != self.current_animation:
            self.current_animation = animation_name
            self.current_frame = 0
            self.frame_timer = 0

    def update(self, dt=16):
        """
        Update animation frame

        Args:
            dt: Delta time dalam milidetik (default 16ms = ~60fps)
        """
        if not self.animations or self.current_animation not in self.animations:
            return

        anim = self.animations[self.current_animation]
        if not anim:
            return

        # Update frame timer
        current_frame_data = anim[self.current_frame]
        self.frame_timer += dt

        # Check if need to advance frame
        if self.frame_timer >= current_frame_data['duration']:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(anim)

    def get_current_image(self):
        """Get current frame sebagai surface"""
        if not self.animations or self.current_animation not in self.animations:
            return self.spritesheet

        # Return pre-extracted surface
        anim_surfs = self.frame_surfaces.get(self.current_animation)
        if anim_surfs:
            idx = self.current_frame % len(anim_surfs)
            return anim_surfs[idx]
        # Fallback
        anim = self.animations[self.current_animation]
        frame_data = anim[self.current_frame]
        rect = frame_data['rect']
        frame_surface = pygame.Surface((rect['w'], rect['h']), pygame.SRCALPHA)
        frame_surface.blit(self.spritesheet, (0, 0), (rect['x'], rect['y'], rect['w'], rect['h']))
        return frame_surface

    def draw(self, screen, offset_x=0, offset_y=0):
        """
        Render sprite ke screen dengan camera offset

        Args:
            screen: pygame screen surface
            offset_x, offset_y: Offset tambahan (optional)
        """
        image = self.get_current_image()
        # Position should respect camera zoom for consistent placement
        zoom = getattr(camera, 'zoom', 1.0)
        sx = int(round((self.x - camera.x) * zoom + offset_x))
        sy = int(round((self.y - camera.y) * zoom + offset_y))
        screen.blit(image, (sx, sy))

    def get_rect(self):
        """Get bounding rect untuk collision"""
        image = self.get_current_image()
        return pygame.Rect(self.x, self.y, image.get_width(), image.get_height())


class SimpleAnimatedSprite:
    """
    Versi sederhana untuk sprite strip horizontal (tidak perlu JSON)
    Cocok untuk sprite sederhana yang semua frame sama ukuran
    """

    def __init__(self, sprite_path, frame_width, frame_height,
                 num_frames, frame_duration=100, x=0, y=0,
                 fallback_color=(100, 100, 200)):
        """
        Args:
            sprite_path: Path ke sprite strip PNG
            frame_width, frame_height: Ukuran setiap frame
            num_frames: Jumlah frame dalam strip
            frame_duration: Durasi setiap frame (ms)
            x, y: Posisi sprite
            fallback_color: Warna fallback
        """
        self.x = x
        self.y = y
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frame_duration = frame_duration

        self.current_frame = 0
        self.frame_timer = 0

        # Try load sprite
        self.frame_surfaces = []
        if os.path.exists(sprite_path):
            try:
                self.spritesheet = pygame.image.load(sprite_path).convert_alpha()
                self.using_fallback = False
                # Pre-extract frames
                for i in range(self.num_frames):
                    frame_x = i * self.frame_width
                    frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                    frame_surface.blit(self.spritesheet, (0, 0), (frame_x, 0, self.frame_width, self.frame_height))
                    self.frame_surfaces.append(frame_surface)
                print(f"✅ Loaded simple sprite: {os.path.basename(sprite_path)}")
            except:
                self._create_fallback(fallback_color)
        else:
            self._create_fallback(fallback_color)

    def _create_fallback(self, color):
        """Buat fallback sprite"""
        self.spritesheet = pygame.Surface((self.frame_width, self.frame_height))
        self.spritesheet.fill(color)
        self.num_frames = 1
        self.using_fallback = True
        print(f"[FALLBACK] Using fallback sprite (colored box)")

    def update(self, dt=16):
        """Update animation"""
        if self.num_frames <= 1:
            return

        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % self.num_frames

    def get_current_image(self):
        """Get current frame"""
        if self.using_fallback or self.num_frames <= 1:
            return self.spritesheet
        if self.frame_surfaces:
            idx = self.current_frame % len(self.frame_surfaces)
            return self.frame_surfaces[idx]
        # Fallback: extract on the fly
        frame_x = self.current_frame * self.frame_width
        frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surface.blit(self.spritesheet, (0, 0), (frame_x, 0, self.frame_width, self.frame_height))
        return frame_surface

    def draw(self, screen):
        """Render sprite"""
        image = self.get_current_image()
        zoom = getattr(camera, 'zoom', 1.0)
        sx = int(round((self.x - camera.x) * zoom))
        sy = int(round((self.y - camera.y) * zoom))
        screen.blit(image, (sx, sy))

    def get_rect(self):
        """Get collision rect"""
        return pygame.Rect(self.x, self.y, self.frame_width, self.frame_height)
