import math
import os
import random
import pygame

from config import *


class LessonScreen:
    """MathSpark - Level 1: Cau cau tri thuc.

    Compatible with the existing main.py interface:
        update(dt), draw(screen), handle_event(event)
    """

    QUESTIONS = [
        {
            "question": "Số nào là số thập phân vô hạn tuần hoàn?",
            "options": ["0,25", "0,3333...", "1,75", "2,125"],
            "answer": 1,
            "explain": "0,3333... có chữ số 3 lặp lại vô hạn lần.",
            "level": "KHỞI ĐỘNG",
        },
        {
            "question": "Trong số 0,181818..., chu kỳ là nhóm chữ số nào?",
            "options": ["18", "81", "181", "8"],
            "answer": 0,
            "explain": "Nhóm 18 là nhóm ngắn nhất lặp lại liên tiếp.",
            "level": "KHỞI ĐỘNG",
        },
        {
            "question": "Số 0,272727... có chu kỳ tuần hoàn là gì?",
            "options": ["2", "7", "27", "272"],
            "answer": 2,
            "explain": "Nhóm chữ số 27 lặp lại vô hạn lần.",
            "level": "TĂNG TỐC",
        },
        {
            "question": "Phân số nào viết được thành số thập phân hữu hạn?",
            "options": ["1/3", "2/9", "3/8", "5/6"],
            "answer": 2,
            "explain": "3/8 = 0,375 nên đây là số thập phân hữu hạn.",
            "level": "THỬ THÁCH",
        },
        {
            "question": "Phân số tối giản biểu diễn 0,121212... là gì?",
            "options": ["12/100", "4/33", "12/99", "6/55"],
            "answer": 1,
            "explain": "0,(12) = 12/99 = 4/33 sau khi rút gọn.",
            "level": "CHINH PHỤC",
        },
    ]

    # Palette
    SKY_TOP = (63, 151, 218)
    SKY_BOTTOM = (190, 224, 238)
    NAVY = (22, 43, 66)
    DEEP = (13, 30, 48)
    GOLD = (255, 205, 91)
    CREAM = (255, 242, 211)
    WOOD = (119, 70, 43)
    WOOD_LIGHT = (190, 128, 72)
    TEAL = (36, 151, 172)

    def __init__(self):
        self.font = self.load_font(21, True)
        self.body = self.load_font(18)
        self.small = self.load_font(15)
        self.tiny = self.load_font(12)
        self.title = self.load_font(27, True)
        self.big = self.load_font(35, True)

        self.world_width = 1740
        self.camera_x = 0.0
        self.bridge_y = 447
        self.water_y = 477
        self.player_x = 105.0
        self.player_y = float(self.bridge_y - 57)
        self.player_vy = 0.0
        self.speed = 255.0
        self.gravity = 1120.0
        self.jump_speed = -430.0
        self.on_ground = True
        self.facing = 1

        self.question_x = [340, 625, 910, 1195, 1480]
        self.question_index = 0
        self.question_open = False
        self.selected = None
        self.feedback = ""
        self.state = "playing"
        self.state_timer = 0.0
        self.completed = False
        self.t = 0.0
        self.message = "Di chuyển đến cổng tri thức đầu tiên!"
        self.message_timer = 3.5

        self.score = 0
        self.coins = 0
        self.combo = 0
        self.best_combo = 0
        self.lives = 3
        self.hints_used = 0
        self.level_started = 0.0
        self.elapsed = 0.0
        self.question_time = 24.0
        self.question_timer = self.question_time
        self.answer_locked = False

        self.left_held = False
        self.right_held = False
        self.jump_held = False

        self.left_button = pygame.Rect(28, SCREEN_HEIGHT - 91, 72, 62)
        self.right_button = pygame.Rect(112, SCREEN_HEIGHT - 91, 72, 62)
        self.jump_button = pygame.Rect(SCREEN_WIDTH - 112, SCREEN_HEIGHT - 101, 88, 76)
        self.return_button = pygame.Rect(SCREEN_WIDTH // 2 - 120, 475, 240, 55)
        self.option_rects = []
        self.confirm_rect = pygame.Rect(SCREEN_WIDTH // 2 - 108, 438, 216, 48)
        self.hint_rect = pygame.Rect(SCREEN_WIDTH // 2 - 340, 438, 190, 48)
        self.close_rect = pygame.Rect(1015, 82, 42, 42)

        self.particles = []
        self.splash_particles = []
        self.ripple_radius = 0.0
        self.ripple_alpha = 255
        self.splash_x = 0
        self.shake = 0.0
        self.flash = 0.0
        self.paused = False
        self.show_hint = False
        self.music_enabled = True
        self.audio_ready = False
        self.music_channel = None
        self.sound_correct = None
        self.sound_wrong = None
        self.sound_jump = None
        self.sound_splash = None
        self.init_audio()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def load_font(self, size, bold=False):
        windir = os.environ.get("WINDIR", "C:/Windows")
        candidates = [
            os.path.join(windir, "Fonts", "arialbd.ttf" if bold else "arial.ttf"),
            os.path.join(windir, "Fonts", "segoeuib.ttf" if bold else "segoeui.ttf"),
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return pygame.font.Font(path, size)
                except pygame.error:
                    pass
        return pygame.font.SysFont("arial", size, bold=bold)

    def text(self, surface, value, font, color, center, shadow=False):
        image = font.render(str(value), True, color)
        rect = image.get_rect(center=center)
        if shadow:
            shade = font.render(str(value), True, (22, 32, 43))
            surface.blit(shade, rect.move(1, 2))
        surface.blit(image, rect)
        return rect

    def sx(self, world_x):
        return int(world_x - self.camera_x)

    def rounded_panel(self, surface, rect, fill, border, radius=16, width=2, shadow=True):
        if shadow:
            pygame.draw.rect(surface, (13, 25, 37), rect.move(0, 6), border_radius=radius)
        pygame.draw.rect(surface, fill, rect, border_radius=radius)
        pygame.draw.rect(surface, border, rect, width, border_radius=radius)

    def gradient(self, surface, rect, top, bottom):
        x, y, w, h = rect
        if h <= 0:
            return
        for row in range(h):
            k = row / max(1, h - 1)
            color = tuple(int(top[i] * (1-k) + bottom[i] * k) for i in range(3))
            pygame.draw.line(surface, color, (x, y + row), (x + w, y + row))

    # ------------------------------------------------------------------
    # Audio - external files are optional; game remains playable without them
    # ------------------------------------------------------------------
    def init_audio(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.sound_correct = self.make_tone(880, 0.16, 0.24)
            self.sound_wrong = self.make_tone(185, 0.28, 0.22)
            self.sound_jump = self.make_tone(520, 0.09, 0.12)
            self.sound_splash = self.make_tone(115, 0.32, 0.2)
            self.audio_ready = True
            music_dir = os.path.join("assets", "audio", "music")
            music_path = next((os.path.join(music_dir, name) for name in
                               ("bridge_adventure.ogg", "bridge_adventure.wav")
                               if os.path.exists(os.path.join(music_dir, name))), None)
            if music_path:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.30)
                pygame.mixer.music.play(-1)
        except (pygame.error, OSError):
            self.audio_ready = False

    def make_tone(self, frequency, duration, volume):
        from array import array
        rate = 22050
        count = int(rate * duration)
        samples = array("h")
        for i in range(count):
            t = i / rate
            fade = min(1.0, i / 250, (count - i) / 450)
            value = math.sin(2 * math.pi * frequency * t) * volume * max(0, fade)
            samples.append(int(value * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play_sound(self, sound):
        if self.audio_ready and sound:
            try:
                sound.play()
            except pygame.error:
                pass

    # ------------------------------------------------------------------
    # Background / environment
    # ------------------------------------------------------------------
    def draw_background(self, screen):
        self.gradient(screen, (0, 0, SCREEN_WIDTH, 390), self.SKY_TOP, self.SKY_BOTTOM)

        # Warm atmospheric glow
        glow = pygame.Surface((SCREEN_WIDTH, 390), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 226, 166, 55), (930 - int(self.camera_x * .05), 92), 115)
        screen.blit(glow, (0, 0))

        # Sun
        sun_x = int(960 - self.camera_x * .08)
        pygame.draw.circle(screen, (255, 235, 175), (sun_x, 105), 52)
        pygame.draw.circle(screen, (255, 248, 215), (sun_x, 105), 38)

        # Clouds with parallax
        for i in range(6):
            x = int((i * 260 - self.camera_x * .14 + self.t * 7) % (SCREEN_WIDTH + 300)) - 120
            y = 65 + (i % 3) * 48
            pygame.draw.ellipse(screen, (255, 255, 250), (x, y + 12, 105, 30))
            pygame.draw.ellipse(screen, (255, 255, 250), (x + 22, y, 58, 48))
            pygame.draw.ellipse(screen, (255, 255, 250), (x + 54, y + 7, 64, 37))

        # Distant mountain silhouettes
        for i in range(8):
            x = i * 240 - int(self.camera_x * .22) % 240 - 80
            peak = 185 + (i % 3) * 26
            pygame.draw.polygon(screen, (113, 166, 174), [(x, 365), (x + 125, peak), (x + 265, 365)])
            pygame.draw.polygon(screen, (143, 190, 190), [(x + 85, 365), (x + 190, peak + 42), (x + 310, 365)])
            pygame.draw.polygon(screen, (220, 235, 226), [(x + 111, peak + 23), (x + 125, peak), (x + 141, peak + 24)])

        # Forest hills
        pygame.draw.rect(screen, (48, 119, 91), (0, 330, SCREEN_WIDTH, 120))
        for i in range(25):
            x = (i * 73 - int(self.camera_x * .38)) % (SCREEN_WIDTH + 90) - 45
            y = 337 + (i % 4) * 13
            color = (35 + (i % 3) * 7, 105 + (i % 4) * 9, 75 + (i % 3) * 5)
            pygame.draw.rect(screen, (94, 73, 49), (x + 18, y + 16, 9, 52))
            pygame.draw.circle(screen, color, (x + 20, y + 5), 27)
            pygame.draw.circle(screen, (68, 151, 100), (x + 1, y + 18), 20)
            pygame.draw.circle(screen, (77, 160, 105), (x + 42, y + 18), 20)

        # Distant pagoda silhouette on the right
        temple_x = self.sx(1450)
        if -180 < temple_x < SCREEN_WIDTH + 180:
            pygame.draw.rect(screen, (103, 83, 76), (temple_x - 34, 245, 68, 112))
            for level in range(3):
                yy = 240 + level * 35
                width = 112 - level * 20
                pygame.draw.polygon(screen, (91, 57, 50), [(temple_x - width//2, yy), (temple_x, yy - 22), (temple_x + width//2, yy)])
                pygame.draw.line(screen, (226, 174, 99), (temple_x - width//2, yy), (temple_x + width//2, yy), 4)
            for yy in (275, 310, 345):
                pygame.draw.rect(screen, (255, 210, 132), (temple_x - 5, yy, 10, 15), border_radius=3)

        # Foreground river bank
        pygame.draw.rect(screen, (54, 126, 88), (0, 408, SCREEN_WIDTH, 70))
        for i in range(30):
            x = (i * 51 - int(self.camera_x * .62)) % (SCREEN_WIDTH + 60) - 30
            y = 414 + (i % 3) * 14
            pygame.draw.ellipse(screen, (43, 105, 71), (x, y, 43, 24))
            pygame.draw.ellipse(screen, (76, 158, 97), (x + 8, y - 4, 24, 17))

    def draw_river(self, screen):
        self.gradient(screen, (0, self.water_y, SCREEN_WIDTH, SCREEN_HEIGHT-self.water_y), (33, 147, 181), (12, 79, 119))
        # Reflected light columns
        for i in range(22):
            x = (i * 67 + int(self.t * (18 + i % 5))) % SCREEN_WIDTH
            y = self.water_y + 12 + (i * 29) % 155
            width = 15 + (i % 4) * 8
            pygame.draw.line(screen, (112, 208, 220), (x, y), (x + width, y), 2)
        # Animated ripples
        for i in range(19):
            x = int((i * 91 - self.t * (28 + i % 4) + 1300) % (SCREEN_WIDTH + 80)) - 40
            y = self.water_y + 18 + (i % 5) * 32
            pygame.draw.arc(screen, (160, 230, 232), (x, y, 58, 15), .2, 2.9, 2)
            pygame.draw.arc(screen, (218, 248, 244), (x + 18, y + 7, 42, 11), .3, 2.8, 1)
        # Lotus leaves
        for i in range(7):
            x = (i * 187 - int(self.camera_x * .28) + 1500) % (SCREEN_WIDTH + 100) - 40
            y = self.water_y + 125 + (i % 2) * 35
            pygame.draw.ellipse(screen, (66, 160, 105), (x, y, 38, 16))
            pygame.draw.line(screen, (153, 211, 145), (x + 18, y + 8), (x + 34, y + 1), 1)

    # ------------------------------------------------------------------
    # Bridge and checkpoints
    # ------------------------------------------------------------------
    def draw_bridge(self, screen):
        left, right = self.sx(35), self.sx(self.world_width - 25)
        # Suspension cables
        cable = []
        for i in range(48):
            wx = 35 + i * ((self.world_width - 60) / 47)
            x = self.sx(wx)
            y = int(344 + 42 * math.sin(i / 47 * math.pi))
            cable.append((x, y))
        if len(cable) > 1:
            pygame.draw.lines(screen, (67, 49, 39), False, cable, 9)
            pygame.draw.lines(screen, (222, 168, 101), False, cable, 3)

        # Support posts and ropes
        for wx in range(55, self.world_width, 105):
            x = self.sx(wx)
            if -35 < x < SCREEN_WIDTH + 35:
                pygame.draw.rect(screen, (75, 47, 34), (x - 7, 356, 14, 100), border_radius=3)
                pygame.draw.rect(screen, (181, 119, 65), (x - 10, 356, 5, 93), border_radius=2)
                pygame.draw.circle(screen, (255, 208, 128), (x, 360), 5)
        pygame.draw.line(screen, (95, 57, 37), (left, 375), (right, 382), 7)
        pygame.draw.line(screen, (229, 180, 111), (left, 372), (right, 379), 2)
        pygame.draw.line(screen, (95, 57, 37), (left, 408), (right, 414), 6)
        pygame.draw.line(screen, (229, 180, 111), (left, 406), (right, 412), 2)

        # Bridge underside
        pygame.draw.rect(screen, (62, 43, 34), (left, self.bridge_y + 15, right-left, 34))
        for wx in range(70, self.world_width, 145):
            x = self.sx(wx)
            if -50 < x < SCREEN_WIDTH + 50:
                pygame.draw.polygon(screen, (81, 52, 39), [(x, self.bridge_y+20), (x+34, self.bridge_y+20), (x+17, self.bridge_y+67)])
                pygame.draw.rect(screen, (107, 68, 43), (x+10, self.bridge_y+16, 13, 62))

        # Individual planks with bevels
        for wx in range(35, self.world_width, 47):
            x = self.sx(wx)
            if -55 < x < SCREEN_WIDTH + 55:
                pygame.draw.rect(screen, (77, 46, 31), (x, self.bridge_y + 3, 44, 22), border_radius=3)
                pygame.draw.rect(screen, (166, 104, 58), (x, self.bridge_y, 44, 17), border_radius=3)
                pygame.draw.line(screen, (226, 165, 99), (x+4, self.bridge_y+3), (x+36, self.bridge_y+3), 2)
                pygame.draw.circle(screen, (71, 47, 34), (x+8, self.bridge_y+10), 2)
                pygame.draw.circle(screen, (71, 47, 34), (x+36, self.bridge_y+10), 2)

        # Bridge end stone platforms
        for wx in (25, self.world_width - 65):
            x = self.sx(wx)
            pygame.draw.rect(screen, (83, 91, 82), (x-15, self.bridge_y-4, 50, 28), border_radius=5)
            pygame.draw.line(screen, (169, 174, 144), (x-8, self.bridge_y), (x+28, self.bridge_y), 3)

    def draw_markers(self, screen):
        for i, wx in enumerate(self.question_x):
            x = self.sx(wx)
            if not -60 < x < SCREEN_WIDTH + 60:
                continue
            active = i == self.question_index and not self.completed
            pulse = (math.sin(self.t * 3.4 + i) + 1) / 2
            radius = int(20 + pulse * (7 if active else 3))
            cy = 370 + int(math.sin(self.t * 2 + i) * 3)
            if active:
                glow = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 202, 74, 42), (50, 50), radius + 20)
                screen.blit(glow, (x-50, cy-50))
            pygame.draw.ellipse(screen, (70, 45, 30), (x-29, 421, 58, 15))
            pygame.draw.rect(screen, (113, 71, 40), (x-22, 397, 44, 24), border_radius=6)
            pygame.draw.rect(screen, (204, 143, 68), (x-22, 397, 44, 7), border_radius=4)
            pygame.draw.circle(screen, (95, 57, 31), (x, cy), radius+4)
            pygame.draw.circle(screen, (255, 190, 55), (x, cy), radius)
            pygame.draw.circle(screen, (255, 226, 139), (x-5, cy-7), max(4, radius//3))
            self.text(screen, "?", self.big, (91, 52, 25), (x, cy+1))
            if i < self.question_index:
                pygame.draw.circle(screen, (39, 155, 99), (x+20, cy-19), 10)
                self.text(screen, "✓", self.small, (255, 255, 255), (x+20, cy-20))

    # ------------------------------------------------------------------
    # Character
    # ------------------------------------------------------------------
    def draw_player(self, screen):
        x = self.sx(self.player_x)
        y = int(self.player_y)
        moving = self.left_held or self.right_held
        step = int(math.sin(self.t * 14) * 4) if moving and self.on_ground else 0
        bob = int(math.sin(self.t * 5) * 2) if self.on_ground else 0
        y += bob

        # Shadow
        pygame.draw.ellipse(screen, (20, 46, 49), (x-20, self.bridge_y+5, 40, 8))
        # Backpack
        pygame.draw.rect(screen, (34, 91, 139), (x-19, y+20, 12, 25), border_radius=5)
        pygame.draw.rect(screen, (71, 145, 184), (x-18, y+21, 5, 19), border_radius=3)
        # Legs
        skin = (239, 184, 137)
        pygame.draw.line(screen, (44, 54, 70), (x-7, y+39), (x-10+step, y+54), 7)
        pygame.draw.line(screen, (44, 54, 70), (x+7, y+39), (x+10-step, y+54), 7)
        pygame.draw.ellipse(screen, (88, 53, 36), (x-20+step, y+49, 19, 9))
        pygame.draw.ellipse(screen, (88, 53, 36), (x+1-step, y+49, 19, 9))
        # Scarf
        pygame.draw.polygon(screen, (190, 48, 43), [(x-8, y+16), (x+13, y+19), (x+24, y+28), (x+12, y+27)])
        pygame.draw.polygon(screen, (224, 69, 52), [(x+17, y+23), (x+34, y+31+step), (x+20, y+30)])
        # Body
        pygame.draw.rect(screen, (219, 120, 56), (x-14, y+16, 28, 27), border_radius=8)
        pygame.draw.polygon(screen, (255, 224, 174), [(x-5, y+17), (x, y+28), (x+5, y+17)])
        pygame.draw.line(screen, (119, 67, 43), (x-11, y+24), (x-18, y+35+step), 5)
        pygame.draw.line(screen, skin, (x+11, y+24), (x+17, y+34-step), 5)
        # Head and hair
        pygame.draw.circle(screen, skin, (x, y+7), 14)
        pygame.draw.circle(screen, (48, 37, 34), (x-2, y+1), 14)
        pygame.draw.circle(screen, skin, (x+2, y+11), 10)
        pygame.draw.arc(screen, (48, 37, 34), (x-14, y-8, 29, 25), 0, math.pi, 6)
        pygame.draw.circle(screen, (48, 37, 34), (x-10, y-2), 5)
        pygame.draw.circle(screen, (48, 37, 34), (x-2, y-6), 5)
        # Goggles
        pygame.draw.arc(screen, (232, 170, 68), (x-13, y-10, 26, 15), math.pi, math.tau, 3)
        pygame.draw.circle(screen, (255, 210, 112), (x-7, y-7), 4, 2)
        pygame.draw.circle(screen, (255, 210, 112), (x+3, y-7), 4, 2)
        eye_x = x + (5 if self.facing >= 0 else -5)
        pygame.draw.circle(screen, (38, 40, 44), (eye_x, y+10), 2)

    # ------------------------------------------------------------------
    # Particles
    # ------------------------------------------------------------------
    def spawn_dust(self, x, y, amount=2):
        for _ in range(amount):
            self.particles.append({"x": x + random.uniform(-8, 8), "y": y,
                                   "vx": random.uniform(-35, 35), "vy": random.uniform(-55, -15),
                                   "life": random.uniform(.25, .5), "max": .5,
                                   "size": random.randint(2, 4), "color": (235, 204, 151)})

    def update_particles(self, dt):
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 120 * dt
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw_particles(self, screen):
        for p in self.particles:
            alpha = max(0, min(255, int(255 * p["life"] / p["max"])))
            size = max(1, int(p["size"] * p["life"] / p["max"]))
            layer = pygame.Surface((size*2+2, size*2+2), pygame.SRCALPHA)
            pygame.draw.circle(layer, (*p["color"], alpha), (size+1, size+1), size)
            screen.blit(layer, (int(p["x"])-size, int(p["y"])-size))

    # ------------------------------------------------------------------
    # HUD and controls
    # ------------------------------------------------------------------
    def draw_hud(self, screen):
        # Top glass bar
        bar = pygame.Surface((SCREEN_WIDTH-32, 68), pygame.SRCALPHA)
        pygame.draw.rect(bar, (17, 39, 58, 224), bar.get_rect(), border_radius=18)
        pygame.draw.rect(bar, (238, 190, 101, 220), bar.get_rect(), 2, border_radius=18)
        screen.blit(bar, (16, 12))
        self.text(screen, "MATHSPARK", self.title, (255, 218, 133), (128, 35), True)
        self.text(screen, "MÀN 1  •  CÂY CẦU TRI THỨC", self.small, (255, 248, 225), (390, 37))

        # Progress
        progress_x, progress_y = 780, 31
        pygame.draw.rect(screen, (55, 70, 78), (progress_x, progress_y, 245, 15), border_radius=8)
        amount = self.question_index / len(self.QUESTIONS)
        if amount > 0:
            pygame.draw.rect(screen, (255, 194, 73), (progress_x, progress_y, int(245*amount), 15), border_radius=8)
        self.text(screen, f"{self.question_index}/{len(self.QUESTIONS)}", self.small, (255,255,255), (1044, 38))
        self.text(screen, f"★ {self.score}", self.font, (255, 220, 108), (1115, 38))

        # Lives
        self.text(screen, "♥ " * self.lives, self.font, (255, 102, 112), (110, 91))

        # Mission tag
        mission = pygame.Rect(18, 99, 218, 47)
        self.rounded_panel(screen, mission, (22, 49, 66), (223, 174, 93), 12, 2, False)
        self.text(screen, "NHIỆM VỤ", self.small, (255, 226, 163), mission.center)

    def draw_control(self, screen, rect, label, pressed=False):
        fill = (32, 91, 122) if not pressed else (19, 60, 88)
        pygame.draw.ellipse(screen, (10, 28, 42), rect.move(0, 5))
        pygame.draw.ellipse(screen, fill, rect)
        pygame.draw.ellipse(screen, (128, 207, 223), rect, 3)
        pygame.draw.ellipse(screen, (225, 245, 241), rect.inflate(-10, -10), 1)
        self.text(screen, label, self.title, (255, 255, 255), rect.center, True)

    def draw_controls(self, screen):
        self.draw_control(screen, self.left_button, "◀", self.left_held)
        self.draw_control(screen, self.right_button, "▶", self.right_held)
        self.draw_control(screen, self.jump_button, "▲", self.jump_held)
        self.text(screen, "DI CHUYỂN", self.tiny, (255,255,255), (110, SCREEN_HEIGHT-16))
        self.text(screen, "NHẢY", self.tiny, (255,255,255), (self.jump_button.centerx, self.jump_button.bottom + 10))

    # ------------------------------------------------------------------
    # Question panel
    # ------------------------------------------------------------------
    def draw_question(self, screen):
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((5, 15, 27, 190))
        screen.blit(shade, (0, 0))

        # Panel with parchment gradient
        panel = pygame.Rect(145, 92, 910, 485)
        pygame.draw.rect(screen, (45, 28, 21), panel.move(0, 9), border_radius=27)
        self.gradient(screen, (panel.x, panel.y, panel.w, panel.h), (255, 244, 215), (232, 204, 153))
        pygame.draw.rect(screen, (126, 77, 43), panel, 7, border_radius=27)
        pygame.draw.rect(screen, (255, 222, 151), panel.inflate(-13, -13), 2, border_radius=22)

        q = self.QUESTIONS[self.question_index]
        self.text(screen, f"THỬ THÁCH {self.question_index + 1}/{len(self.QUESTIONS)}", self.title, (112, 62, 34), (SCREEN_WIDTH//2, 137))
        self.text(screen, q["level"], self.tiny, (150, 105, 56), (SCREEN_WIDTH//2, 169))

        # Question text supports wrapping
        words = q["question"].split()
        lines, current = [], ""
        for word in words:
            test = (current + " " + word).strip()
            if self.font.size(test)[0] > 790 and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
        for i, line in enumerate(lines[:2]):
            self.text(screen, line, self.font, (62, 45, 34), (SCREEN_WIDTH//2, 207 + i*27))

        self.option_rects = []
        start_y = 264 if len(lines) == 1 else 286
        for i, option in enumerate(q["options"]):
            col, row = i % 2, i // 2
            rect = pygame.Rect(205 + col*405, start_y + row*77, 375, 59)
            self.option_rects.append(rect)
            if self.selected == i:
                fill, border = (174, 226, 241), (36, 153, 194)
            else:
                fill, border = (255, 250, 231), (183, 135, 77)
            self.rounded_panel(screen, rect, fill, border, 13, 2, False)
            pygame.draw.circle(screen, (223, 151, 39), (rect.x+31, rect.centery), 19)
            pygame.draw.circle(screen, (255, 220, 129), (rect.x+31, rect.centery), 19, 2)
            self.text(screen, chr(65+i), self.body, (79, 48, 25), (rect.x+31, rect.centery))
            self.text(screen, option, self.body, (61, 47, 35), (rect.x+205, rect.centery))

        # Timer
        timer_rect = pygame.Rect(850, 111, 166, 42)
        self.rounded_panel(screen, timer_rect, (91, 54, 39), (226, 174, 93), 13, 2, False)
        timer_color = (255, 117, 90) if self.question_timer < 7 else (255, 245, 216)
        self.text(screen, f"⏱ {max(0, int(self.question_timer)):02d}s", self.body, timer_color, timer_rect.center)

        self.hint_rect = pygame.Rect(245, 451, 205, 48)
        self.confirm_rect = pygame.Rect(750, 451, 205, 48)
        self.rounded_panel(screen, self.hint_rect, (255, 216, 119), (157, 94, 40), 13, 2, False)
        self.text(screen, "GỢI Ý  (-1 SAO)", self.small, (91, 54, 25), self.hint_rect.center)
        self.rounded_panel(screen, self.confirm_rect, (43, 139, 91), (255, 215, 127), 13, 2, False)
        self.text(screen, "TRẢ LỜI", self.body, (255, 255, 245), self.confirm_rect.center)

        if self.feedback:
            color = (31, 119, 70) if self.state == "correct" else (156, 54, 43)
            self.text(screen, self.feedback, self.small, color, (SCREEN_WIDTH//2, 421))
        elif self.show_hint:
            hint = "Gợi ý: Hãy quan sát nhóm chữ số lặp lại sau dấu phẩy."
            self.text(screen, hint, self.small, (104, 73, 39), (SCREEN_WIDTH//2, 421))
        else:
            self.text(screen, "Chọn đáp án bằng chuột hoặc phím 1–4 · Enter để xác nhận", self.tiny, (108, 84, 60), (SCREEN_WIDTH//2, 533))

    # ------------------------------------------------------------------
    # End screen / splash
    # ------------------------------------------------------------------
    def draw_complete(self, screen):
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((5, 17, 29, 205))
        screen.blit(shade, (0, 0))
        panel = pygame.Rect(275, 145, 650, 390)
        self.rounded_panel(screen, panel, (255, 239, 202), (211, 153, 68), 25, 5)
        self.text(screen, "CHINH PHỤC THÀNH CÔNG!", self.title, (111, 70, 34), (600, 218))
        self.text(screen, "Bạn đã vượt qua Cây Cầu Tri Thức", self.body, (82, 66, 49), (600, 274))
        stars = min(3, max(1, self.score // 2 + 1))
        self.text(screen, "★ " * stars, self.big, (237, 164, 36), (600, 337))
        self.text(screen, f"Điểm số: {self.score}     Chuỗi đúng tốt nhất: {self.best_combo}", self.body, (82, 66, 49), (600, 388))
        self.rounded_panel(screen, self.return_button, (49, 133, 86), (255, 220, 130), 13, 3, False)
        self.text(screen, "QUAY LẠI BẢN ĐỒ", self.font, (255,255,245), self.return_button.center)

    def start_splash(self):
        self.state = "splash"
        self.state_timer = 1.0
        self.splash_x = self.sx(self.player_x)
        self.ripple_radius = 5
        self.ripple_alpha = 255
        self.splash_particles = []
        for _ in range(36):
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(90, 280)
            self.splash_particles.append({
                "x": float(self.splash_x), "y": float(self.water_y),
                "vx": math.cos(angle)*speed,
                "vy": -abs(math.sin(angle)*speed)-random.uniform(50, 150),
                "life": random.uniform(.4, .85), "size": random.randint(2, 6)
            })
        self.play_sound(self.sound_splash)
        self.shake = .35

    def update_splash(self, dt):
        self.state_timer -= dt
        self.ripple_radius += 150 * dt
        self.ripple_alpha = max(0, self.ripple_alpha - 230 * dt)
        for p in self.splash_particles:
            p["vy"] += 520 * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.splash_particles = [p for p in self.splash_particles if p["life"] > 0]
        if self.state_timer <= 0:
            self.state = "respawning"
            self.state_timer = .65

    def draw_splash(self, screen):
        if self.ripple_alpha > 0:
            r = int(self.ripple_radius)
            pygame.draw.ellipse(screen, (174, 239, 245), (self.splash_x-r, self.water_y-7, r*2, 17), 3)
        for p in self.splash_particles:
            size = max(1, int(p["size"] * min(1, p["life"]*2)))
            pygame.draw.circle(screen, (196, 241, 249), (int(p["x"]), int(p["y"])), size)

    # ------------------------------------------------------------------
    # Gameplay
    # ------------------------------------------------------------------
    def open_question(self):
        self.question_open = True
        self.selected = None
        self.feedback = ""
        self.show_hint = False
        self.question_timer = max(18.0, 28.0 - self.question_index * 2.0)
        self.left_held = self.right_held = self.jump_held = False

    def submit_answer(self):
        if self.selected is None or self.answer_locked:
            self.feedback = "Hãy chọn một đáp án trước nhé!"
            return
        q = self.QUESTIONS[self.question_index]
        self.answer_locked = True
        if self.selected == q["answer"]:
            self.combo += 1
            self.best_combo = max(self.best_combo, self.combo)
            earned = 100 + max(0, int(self.question_timer)) * 2 + (self.combo-1)*20
            self.score += earned
            self.coins += 5
            self.feedback = f"Chính xác! +{earned} điểm. {q['explain']}"
            self.play_sound(self.sound_correct)
            self.state = "correct"
            self.state_timer = 1.8
            self.flash = .18
        else:
            self.combo = 0
            self.lives = max(0, self.lives - 1)
            self.feedback = "Chưa chính xác! Bạn cần thử lại thử thách này."
            self.play_sound(self.sound_wrong)
            self.state = "falling"
            self.state_timer = 0
            self.player_vy = 80
            self.on_ground = False
            self.question_open = False
            self.shake = .3
        self.left_held = self.right_held = self.jump_held = False

    def update(self, dt):
        dt = min(dt, 0.04)
        self.t += dt
        self.elapsed += dt
        self.update_particles(dt)
        self.shake = max(0, self.shake - dt)
        self.flash = max(0, self.flash - dt)
        if self.message_timer > 0:
            self.message_timer = max(0, self.message_timer-dt)

        if self.question_open and self.state == "playing":
            self.question_timer -= dt
            if self.question_timer <= 0:
                self.feedback = "Hết thời gian! Hãy thử lại nhé."
                self.combo = 0
                self.state = "falling"
                self.question_open = False
                self.player_vy = 80
                self.on_ground = False
                self.play_sound(self.sound_wrong)

        if self.state == "correct":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.question_index += 1
                self.question_open = False
                self.answer_locked = False
                self.feedback = ""
                self.state = "waiting_move"
                self.message = "Tốt lắm! Tiếp tục tiến về cổng tiếp theo."
                self.message_timer = 2.8
                if self.question_index >= len(self.QUESTIONS):
                    self.message = "Đã mở khóa toàn bộ cổng! Hãy đến cuối cầu."
        elif self.state == "falling":
            self.player_vy += self.gravity*dt
            self.player_y += self.player_vy*dt
            if self.player_y + 54 >= self.water_y:
                self.start_splash()
        elif self.state == "splash":
            self.update_splash(dt)
        elif self.state == "respawning":
            self.state_timer -= dt
            if self.state_timer <= 0:
                checkpoint = self.question_x[min(self.question_index, len(self.question_x)-1)]
                self.player_x = max(65, checkpoint-115)
                self.player_y = float(self.bridge_y-57)
                self.player_vy = 0
                self.on_ground = True
                self.state = "playing"
                self.answer_locked = False
                self.message = "Hồi sinh tại checkpoint. Hãy đọc kỹ câu hỏi!"
                self.message_timer = 2.5
        elif self.state in ("playing", "waiting_move") and not self.question_open and not self.completed and not self.paused:
            direction = int(self.right_held) - int(self.left_held)
            if direction:
                self.state = "playing"
                self.player_x += direction*self.speed*dt
                self.facing = direction
                if self.on_ground and random.random() < .20:
                    self.spawn_dust(self.sx(self.player_x), self.bridge_y+5, 1)
            self.player_x = max(45, min(self.world_width-45, self.player_x))

            if self.jump_held and self.on_ground:
                self.player_vy = self.jump_speed
                self.on_ground = False
                self.jump_held = False
                self.play_sound(self.sound_jump)

            if not self.on_ground:
                self.player_vy += self.gravity*dt
                self.player_y += self.player_vy*dt
                floor_y = self.bridge_y-57
                if self.player_y >= floor_y:
                    self.player_y = float(floor_y)
                    self.player_vy = 0
                    self.on_ground = True

            if self.question_index < len(self.question_x):
                target = self.question_x[self.question_index]
                if self.player_x >= target-37:
                    self.player_x = target-37
                    self.open_question()

            self.camera_x = max(0, min(self.world_width-SCREEN_WIDTH, self.player_x-SCREEN_WIDTH*.38))

        if self.question_index >= len(self.QUESTIONS) and self.player_x >= self.world_width-120 and self.state in ("playing", "waiting_move"):
            self.completed = True
            self.question_open = False

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.question_open:
                self.question_open = False
                self.state = "playing"
            else:
                return "map"

        if self.completed:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.return_button.collidepoint(event.pos):
                return "map"
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "map"
            return None

        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self.paused = not self.paused
            return None

        if self.question_open:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected = i
                        return None
                if self.confirm_rect.collidepoint(event.pos):
                    self.submit_answer()
                elif self.hint_rect.collidepoint(event.pos):
                    if not self.show_hint:
                        self.show_hint = True
                        self.hints_used += 1
                        self.score = max(0, self.score-25)
                return None
            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_4:
                    self.selected = event.key-pygame.K_1
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.submit_answer()
            return None

        if self.state in ("falling", "splash", "respawning", "correct") or self.paused:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.state = "playing"
                self.left_held = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.state = "playing"
                self.right_held = True
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.state = "playing"
                self.jump_held = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.left_held = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.right_held = False
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.jump_held = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.left_button.collidepoint(event.pos):
                self.state = "playing"
                self.left_held = True
            elif self.right_button.collidepoint(event.pos):
                self.state = "playing"
                self.right_held = True
            elif self.jump_button.collidepoint(event.pos):
                self.state = "playing"
                self.jump_held = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.left_held = self.right_held = self.jump_held = False
        return None

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------
    def draw(self, screen):
        self.draw_background(screen)
        self.draw_river(screen)
        self.draw_bridge(screen)
        self.draw_markers(screen)

        if self.state not in ("splash", "respawning"):
            self.draw_player(screen)
        if self.state == "splash":
            self.draw_splash(screen)

        self.draw_particles(screen)
        self.draw_hud(screen)

        if self.question_open:
            self.draw_question(screen)
        elif self.state in ("playing", "waiting_move"):
            self.draw_controls(screen)

        if self.message_timer > 0 and not self.question_open and not self.completed and self.state not in ("falling", "splash", "respawning"):
            image = self.small.render(self.message, True, (255, 255, 245))
            rect = image.get_rect(center=(SCREEN_WIDTH//2, 105)).inflate(28, 14)
            self.rounded_panel(screen, rect, (25, 53, 68), (229, 185, 109), 10, 1, False)
            screen.blit(image, image.get_rect(center=rect.center))

        if self.paused:
            shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 155))
            screen.blit(shade, (0, 0))
            self.text(screen, "TẠM DỪNG", self.big, (255, 231, 173), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.text(screen, "Nhấn P để tiếp tục", self.body, (255,255,255), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2+48))

        if self.completed:
            self.draw_complete(screen)

        if self.flash > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 244, 190, int(65*self.flash/.18)))
            screen.blit(overlay, (0, 0))
