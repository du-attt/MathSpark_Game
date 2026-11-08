
import pygame
import os

from config import *
from components.button import Button, draw_3d_text


class MenuScreen:

    def __init__(self):
        self.title_font = self.load_system_font(76, bold=True)
        self.subtitle_font = self.load_system_font(23, bold=True)
        self.button_font = self.load_system_font(19, bold=True)
        self.info_font = self.load_system_font(16, bold=True)

        self.background = self.load_background()

        self.message = ""
        self.message_timer = 0

        self.create_buttons()

    # LOAD WINDOWS FONT
    def load_system_font(self, size, bold=False):
        windows_dir = os.environ.get("WINDIR", "C:/Windows")
        font_dir = os.path.join(windows_dir, "Fonts")

        if bold:
            candidates = ["arialbd.ttf", "segoeuib.ttf"]
        else:
            candidates = ["arial.ttf", "segoeui.ttf"]

        for filename in candidates:
            font_path = os.path.join(font_dir, filename)

            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)

        return pygame.font.SysFont("arial", size, bold=bold)

    # LOAD BACKGROUND
    def load_background(self):
        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        image_path = os.path.join(
            base_dir,
            "assets",
            "images",
            "backgrounds",
            "menu_background.png"
        )

        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Không tìm thấy ảnh nền:\n{image_path}"
            )

        image = pygame.image.load(image_path).convert()

        return pygame.transform.smoothscale(
            image,
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

    # CREATE BUTTONS
    def create_buttons(self):
        button_width = 155
        button_height = 53

        button_y = SCREEN_HEIGHT - button_height - 22

        button_positions = [267, 533, 783]

        self.buttons = [
            Button(
                button_positions[0],
                button_y,
                button_width,
                button_height,
                "BẮT ĐẦU",
                self.button_font,
                color=(55, 155, 85),
                hover_color=(80, 190, 110),
                shadow_color=(30, 85, 45),
                outline_color=(25, 75, 40)
            ),

            Button(
                button_positions[1],
                button_y,
                button_width,
                button_height,
                "HƯỚNG DẪN",
                self.button_font,
                color=(55, 125, 190),
                hover_color=(85, 160, 225),
                shadow_color=(30, 70, 120),
                outline_color=(25, 60, 105)
            ),

            Button(
                button_positions[2],
                button_y,
                button_width,
                button_height,
                "THOÁT GAME",
                self.button_font,
                color=(210, 105, 65),
                hover_color=(240, 135, 85),
                shadow_color=(125, 55, 35),
                outline_color=(110, 45, 30)
            )
        ]

    # DRAW BACKGROUND
    def draw_background(self, screen):
        screen.blit(self.background, (0, 0))

    # DRAW TITLE WITHOUT PANEL
    def draw_title(self, screen):

        # Main title
        draw_3d_text(
            screen=screen,
            text="Math Adventure",
            font=self.title_font,
            center=(SCREEN_WIDTH // 2, 105),
            face_color=(255, 225, 105),
            outline_color=(75, 35, 10),
            shadow_color=(120, 55, 15),
            depth=10,
            outline_width=4
        )

        # Subtitle shadow
        subtitle_shadow = self.subtitle_font.render(
            "Học Toán qua những cuộc phiêu lưu",
            True,
            (55, 35, 15)
        )

        shadow_rect = subtitle_shadow.get_rect(
            center=(SCREEN_WIDTH // 2 + 2, 169 + 3)
        )

        screen.blit(subtitle_shadow, shadow_rect)

        # Subtitle main text
        subtitle = self.subtitle_font.render(
            "Học Toán qua những cuộc phiêu lưu",
            True,
            (255, 250, 220)
        )

        subtitle_rect = subtitle.get_rect(
            center=(SCREEN_WIDTH // 2, 169)
        )

        screen.blit(subtitle, subtitle_rect)

    # DRAW BUTTONS
    def draw_buttons(self, screen):
        for button in self.buttons:
            button.draw(screen)

    # SHOW MESSAGE
    def show_message(self, message):
        self.message = message
        self.message_timer = 3

    # DRAW MESSAGE
    def draw_message(self, screen):
        if self.message_timer <= 0:
            return

        text = self.info_font.render(
            self.message,
            True,
            (255, 250, 225)
        )

        text_rect = text.get_rect(
            center=(SCREEN_WIDTH // 2, 570)
        )

        background_rect = text_rect.inflate(40, 20)

        pygame.draw.rect(
            screen,
            (65, 75, 50),
            background_rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            GOLD,
            background_rect,
            width=2,
            border_radius=12
        )

        screen.blit(text, text_rect)

    # DRAW VERSION
    def draw_version(self, screen):
        version = self.info_font.render(
            f"MathSpark v{GAME_VERSION}",
            True,
            (255, 255, 235)
        )

        screen.blit(
            version,
            (18, SCREEN_HEIGHT - 30)
        )

    # UPDATE
    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt

            if self.message_timer <= 0:
                self.message = ""

    # DRAW
    def draw(self, screen):
        self.draw_background(screen)
        self.draw_title(screen)
        self.draw_buttons(screen)
        self.draw_message(screen)
        self.draw_version(screen)

    # HANDLE EVENTS
    def handle_event(self, event):
        for index, button in enumerate(self.buttons):
            if button.handle_event(event):
                if index == 0:
                    return "start"

                elif index == 1:
                    return "guide"

                elif index == 2:
                    return "quit"

        return None
