import pygame
import os
import math
import random

from config import *


class LessonMapScreen:
    """Bản đồ MathSpark với hiệu ứng phép thuật mới."""

    def __init__(self):
        self.background = self.load_background()
        self.time = 0.0
        self.rng = random.Random()

        self.levels = [
            {"id": 1, "x": 510, "y": 371, "unlocked": True},
            {"id": 2, "x": 255, "y": 345, "unlocked": False},
            {"id": 3, "x": 313, "y": 153, "unlocked": False},
            {"id": 4, "x": 553, "y": 91, "unlocked": False},
            {"id": 5, "x": 633, "y": 338, "unlocked": False},
            {"id": 6, "x": 805, "y": 189, "unlocked": False},
            {"id": 7, "x": 899, "y": 306, "unlocked": False},
            {"id": 8, "x": 972, "y": 535, "unlocked": False},
        ]

        self.message = ""
        self.message_timer = 0.0
        self.font = self.load_font(20, True)

        # Các điểm đom đóm bay lượn trên đảo.
        self.fireflies = []
        for _ in range(22):
            self.fireflies.append({
                "cx": self.rng.uniform(320, 930),
                "cy": self.rng.uniform(125, 520),
                "phase": self.rng.uniform(0, math.tau),
                "speed": self.rng.uniform(0.45, 1.0),
                "rx": self.rng.uniform(12, 38),
                "ry": self.rng.uniform(8, 24),
                "size": self.rng.uniform(2, 3.5),
                "tail": []
            })

        # Các điểm sao lấp lánh rải rác trên đảo.
        positions = [
            (370, 205), (445, 170), (590, 175), (690, 220),
            (750, 285), (390, 455), (570, 475), (730, 430),
            (850, 390), (930, 245), (470, 285), (650, 115),
            (330, 285), (780, 485), (600, 520)
        ]
        self.twinkles = [
            {
                "x": x, "y": y,
                "phase": self.rng.uniform(0, math.tau),
                "speed": self.rng.uniform(1.1, 2.4),
                "size": self.rng.uniform(3, 6)
            }
            for x, y in positions
        ]

        # Gợn sóng hình elip tại vùng biển ngoài đảo.
        self.water_zones = [
            (18, 20, 155, 120), (1000, 18, 185, 125),
            (5, 220, 95, 210), (1090, 220, 105, 230),
            (20, 520, 175, 135), (1000, 520, 190, 140),
            (390, 0, 260, 35), (430, 640, 350, 35)
        ]
        self.ripples = [self.make_ripple() for _ in range(10)]

        # Lớp trong suốt tái sử dụng, tránh tạo Surface liên tục.
        self.layer = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

    def load_font(self, size, bold=False):
        windows_dir = os.environ.get("WINDIR", "C:/Windows")
        filename = "arialbd.ttf" if bold else "arial.ttf"
        font_path = os.path.join(windows_dir, "Fonts", filename)
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        return pygame.font.SysFont("arial", size, bold=bold)

    def load_background(self):
        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        image_path = os.path.join(
            base_dir, "assets", "images", "backgrounds",
            "map_background.png"
        )
        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Không tìm thấy ảnh bản đồ:\n{image_path}"
            )
        image = pygame.image.load(image_path).convert()
        return pygame.transform.smoothscale(
            image, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

    # -------------------- ĐOM ĐÓM MA THUẬT --------------------

    def update_fireflies(self):
        for item in self.fireflies:
            angle = self.time * item["speed"] + item["phase"]
            x = item["cx"] + math.cos(angle) * item["rx"]
            y = item["cy"] + math.sin(angle * 1.35) * item["ry"]

            item["tail"].append((x, y))
            if len(item["tail"]) > 7:
                item["tail"].pop(0)

            item["x"], item["y"] = x, y

    def draw_fireflies(self, screen):
        self.layer.fill((0, 0, 0, 0))

        for item in self.fireflies:
            pulse = (
                math.sin(self.time * 4 + item["phase"]) + 1
            ) / 2
            alpha = int(100 + pulse * 130)
            radius = max(2, int(item["size"] + pulse * 1.5))

            tail = item["tail"]
            for i in range(1, len(tail)):
                fade = int(75 * i / max(1, len(tail)))
                pygame.draw.line(
                    self.layer, (90, 245, 210, fade),
                    (int(tail[i - 1][0]), int(tail[i - 1][1])),
                    (int(tail[i][0]), int(tail[i][1])), 2
                )

            x, y = int(item["x"]), int(item["y"])
            pygame.draw.circle(
                self.layer, (65, 235, 205, alpha // 4),
                (x, y), radius * 5
            )
            pygame.draw.circle(
                self.layer, (100, 255, 225, alpha // 2),
                (x, y), radius * 2
            )
            pygame.draw.circle(
                self.layer, (255, 255, 225, alpha),
                (x, y), radius
            )

        screen.blit(self.layer, (0, 0))

    # -------------------- SAO LẤP LÁNH --------------------

    @staticmethod
    def draw_star(surface, x, y, size, color):
        points = [
            (x, y - size), (x + size // 4, y - size // 4),
            (x + size, y), (x + size // 4, y + size // 4),
            (x, y + size), (x - size // 4, y + size // 4),
            (x - size, y), (x - size // 4, y - size // 4)
        ]
        pygame.draw.polygon(surface, color, points)

    def draw_twinkles(self, screen):
        self.layer.fill((0, 0, 0, 0))

        for star in self.twinkles:
            wave = (
                math.sin(self.time * star["speed"] + star["phase"]) + 1
            ) / 2
            if wave < 0.78:
                continue

            strength = (wave - 0.78) / 0.22
            size = max(2, int(star["size"] * strength))
            alpha = int(210 * strength)
            x, y = int(star["x"]), int(star["y"])

            pygame.draw.circle(
                self.layer, (255, 220, 120, alpha // 4),
                (x, y), size * 3
            )
            self.draw_star(
                self.layer, x, y, size,
                (255, 250, 210, alpha)
            )

        screen.blit(self.layer, (0, 0))

    # -------------------- GỢN SÓNG BIỂN --------------------

    def make_ripple(self):
        zone = self.rng.choice(self.water_zones)
        return {
            "x": self.rng.uniform(zone[0], zone[0] + zone[2]),
            "y": self.rng.uniform(zone[1], zone[1] + zone[3]),
            "radius": self.rng.uniform(2, 20),
            "max_radius": self.rng.uniform(18, 34),
            "speed": self.rng.uniform(8, 17),
            "alpha": self.rng.randint(65, 115)
        }

    def update_ripples(self, dt):
        for ripple in self.ripples:
            ripple["radius"] += ripple["speed"] * dt
            if ripple["radius"] >= ripple["max_radius"]:
                ripple.update(self.make_ripple())

    def draw_ripples(self, screen):
        self.layer.fill((0, 0, 0, 0))

        for ripple in self.ripples:
            progress = ripple["radius"] / ripple["max_radius"]
            alpha = int(ripple["alpha"] * (1 - progress))
            radius = max(1, int(ripple["radius"]))

            rect = pygame.Rect(
                int(ripple["x"] - radius),
                int(ripple["y"] - radius * 0.45),
                radius * 2,
                max(2, int(radius * 0.9))
            )
            pygame.draw.ellipse(
                self.layer, (170, 245, 255, alpha), rect, 2
            )

        screen.blit(self.layer, (0, 0))

    # -------------------- CỔNG NĂNG LƯỢNG MỐC 1 --------------------

    def draw_level_portal(self, screen):
        x, y = self.levels[0]["x"], self.levels[0]["y"]
        pulse = (math.sin(self.time * 2.7) + 1) / 2
        rotation = self.time * 0.9

        self.layer.fill((0, 0, 0, 0))

        # Hai vòng elip xoay lệch nhau.
        for index in range(2):
            angle = rotation + index * math.pi / 2
            rx = 43 + pulse * 5
            ry = 19 + pulse * 3
            points = []

            for step in range(49):
                t = step * math.tau / 48
                px = math.cos(t) * rx
                py = math.sin(t) * ry
                px2 = px * math.cos(angle) - py * math.sin(angle)
                py2 = px * math.sin(angle) + py * math.cos(angle)
                points.append((int(x + px2), int(y + py2 + 4)))

            pygame.draw.lines(
                self.layer,
                (255, 220, 90, 120 if index == 0 else 75),
                True, points, 3 if index == 0 else 2
            )

        # Tia năng lượng xoay quanh tâm.
        for index in range(8):
            angle = rotation * 1.8 + index * math.tau / 8
            inner = 36 + pulse * 2
            outer = 47 + pulse * 5
            start = (
                int(x + math.cos(angle) * inner),
                int(y + math.sin(angle) * inner)
            )
            end = (
                int(x + math.cos(angle) * outer),
                int(y + math.sin(angle) * outer)
            )
            pygame.draw.line(
                self.layer, (255, 240, 160, 175), start, end, 2
            )
            pygame.draw.circle(
                self.layer, (255, 250, 210, 220), end, 2
            )

        pygame.draw.circle(
            self.layer,
            (255, 205, 65, int(20 + pulse * 28)),
            (x, y), int(31 + pulse * 7)
        )
        screen.blit(self.layer, (0, 0))

    # -------------------- LUỒNG SÁNG QUÉT QUA ĐẢO --------------------

    def draw_light_sweep(self, screen):
        progress = (self.time * 0.10) % 1.35
        center_x = int(-260 + progress * (SCREEN_WIDTH + 520))

        self.layer.fill((0, 0, 0, 0))
        polygon = [
            (center_x - 95, 0),
            (center_x - 35, 0),
            (center_x + 250, SCREEN_HEIGHT),
            (center_x + 165, SCREEN_HEIGHT)
        ]
        pygame.draw.polygon(
            self.layer, (255, 250, 205, 17), polygon
        )
        screen.blit(self.layer, (0, 0))

    # -------------------- KHÓA BÀI HỌC --------------------

    def draw_lock(self, screen, x, y):
        overlay = pygame.Surface((64, 64), pygame.SRCALPHA)

        pygame.draw.circle(
            overlay, (25, 35, 45, 145), (32, 32), 29
        )
        pygame.draw.rect(
            overlay, (230, 185, 75), (21, 29, 22, 19),
            border_radius=4
        )
        pygame.draw.arc(
            overlay, (245, 225, 165), (24, 16, 16, 22),
            0, math.pi, 4
        )
        pygame.draw.circle(
            overlay, (90, 60, 25), (32, 37), 3
        )
        screen.blit(overlay, (x - 32, y - 32))

    def draw_levels(self, screen):
        for level in self.levels:
            if not level["unlocked"]:
                self.draw_lock(screen, level["x"], level["y"])

    # -------------------- THÔNG BÁO --------------------

    def show_message(self, message):
        self.message = message
        self.message_timer = 2.5

    def draw_message(self, screen):
        if self.message_timer <= 0:
            return

        text = self.font.render(
            self.message, True, (255, 255, 255)
        )
        text_rect = text.get_rect(
            center=(SCREEN_WIDTH // 2, 45)
        )
        panel = text_rect.inflate(40, 20)

        pygame.draw.rect(
            screen, (35, 65, 90), panel, border_radius=12
        )
        pygame.draw.rect(
            screen, (255, 210, 90), panel,
            width=2, border_radius=12
        )
        screen.blit(text, text_rect)

    # -------------------- UPDATE / DRAW --------------------

    def update(self, dt):
        self.time += dt
        self.update_fireflies()
        self.update_ripples(dt)

        if self.message_timer > 0:
            self.message_timer = max(0, self.message_timer - dt)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        # Hiệu ứng môi trường mới.
        self.draw_ripples(screen)
        self.draw_fireflies(screen)
        self.draw_twinkles(screen)
        self.draw_light_sweep(screen)

        # Cổng năng lượng quanh mốc đầu tiên.
        self.draw_level_portal(screen)

        # Giữ trạng thái khóa của các bài chưa mở.
        self.draw_levels(screen)
        self.draw_message(screen)

    # -------------------- INPUT --------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            for level in self.levels:
                x, y = level["x"], level["y"]
                distance = math.hypot(mouse_x - x, mouse_y - y)

                if distance <= 35:
                    if level["unlocked"]:
                        return f"lesson_{level['id']}"

                    self.show_message(
                        "Bài học này chưa được mở khóa!"
                    )
                    return None

        return None
