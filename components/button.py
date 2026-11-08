import pygame


def draw_3d_text(
    screen,
    text,
    font,
    center,
    face_color,
    outline_color,
    shadow_color,
    depth=5,
    outline_width=2
):
    """
    Draw cartoon-style 3D text.
    """

    text_surface = font.render(
        text, True, face_color
    )

    outline_surface = font.render(
        text, True, outline_color
    )

    text_rect = text_surface.get_rect(
        center=center
    )

    # 1. Draw extrusion / 3D depth
    for offset in range(depth, 0, -1):

        shadow_rect = text_rect.copy()
        shadow_rect.y += offset

        screen.blit(
            outline_surface,
            shadow_rect
        )

    # 2. Draw outline
    for dx in range(-outline_width, outline_width + 1):

        for dy in range(-outline_width, outline_width + 1):

            if dx == 0 and dy == 0:
                continue

            if dx * dx + dy * dy <= outline_width ** 2 + 2:

                screen.blit(
                    outline_surface,
                    (
                        text_rect.x + dx,
                        text_rect.y + dy
                    )
                )

    # 3. Draw main text
    screen.blit(
        text_surface,
        text_rect
    )


class Button:

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        font,
        color,
        hover_color,
        shadow_color,
        outline_color,
        border_color=(255, 215, 120),
        text_color=(255, 250, 225),
        radius=18
    ):

        self.rect = pygame.Rect(
            x, y, width, height
        )

        self.text = text
        self.font = font

        self.color = color
        self.hover_color = hover_color

        self.shadow_color = shadow_color
        self.outline_color = outline_color

        self.border_color = border_color
        self.text_color = text_color

        self.radius = radius

        self.is_hovered = False
        self.is_pressed = False

    # ==================================
    # DRAW BUTTON
    # ==================================

    def draw(self, screen):

        mouse_pos = pygame.mouse.get_pos()

        self.is_hovered = self.rect.collidepoint(
            mouse_pos
        )

        draw_rect = self.rect.copy()

        # Hover effect
        if self.is_hovered:
            draw_rect.inflate_ip(6, 4)

        # Press effect
        if self.is_pressed:
            draw_rect.y += 4

        current_color = (
            self.hover_color
            if self.is_hovered
            else self.color
        )

        # Button shadow
        shadow_rect = draw_rect.copy()
        shadow_rect.y += 7

        pygame.draw.rect(
            screen,
            self.shadow_color,
            shadow_rect,
            border_radius=self.radius
        )

        # Main background
        pygame.draw.rect(
            screen,
            current_color,
            draw_rect,
            border_radius=self.radius
        )

        # Outer gold border
        pygame.draw.rect(
            screen,
            self.border_color,
            draw_rect,
            width=3,
            border_radius=self.radius
        )

        # Inner highlight
        inner_rect = draw_rect.inflate(-9, -9)

        pygame.draw.rect(
            screen,
            (255, 255, 235),
            inner_rect,
            width=1,
            border_radius=max(3, self.radius - 5)
        )

        # 3D text
        text_center = (
            draw_rect.centerx,
            draw_rect.centery - 3
        )

        draw_3d_text(
            screen=screen,
            text=self.text,
            font=self.font,
            center=text_center,
            face_color=self.text_color,
            outline_color=self.outline_color,
            shadow_color=self.shadow_color,
            depth=4,
            outline_width=2
        )

    # ==================================
    # HANDLE EVENTS
    # ==================================

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                self.is_pressed = (
                    self.rect.collidepoint(event.pos)
                )

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                clicked = (
                    self.is_pressed
                    and self.rect.collidepoint(event.pos)
                )

                self.is_pressed = False

                return clicked

        return False