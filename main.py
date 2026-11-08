import pygame
import sys

from config import *
from screens.menu import MenuScreen
from screens.lesson_map import LessonMapScreen
from screens.lesson import LessonScreen


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MathSpark")
    clock = pygame.time.Clock()

    menu = MenuScreen()
    lesson_map = LessonMapScreen()
    lesson = None
    current_screen = "menu"
    running = True

    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if current_screen == "menu":
                action = menu.handle_event(event)
                if action == "start":
                    current_screen = "map"
                elif action == "guide":
                    menu.show_message("Huong dan se duoc cap nhat sau!")
                elif action == "quit":
                    running = False

            elif current_screen == "map":
                action = lesson_map.handle_event(event)
                if action == "back":
                    current_screen = "menu"
                elif action == "lesson_1":
                    lesson = LessonScreen()
                    current_screen = "lesson"

            elif current_screen == "lesson" and lesson is not None:
                if lesson.handle_event(event) == "map":
                    current_screen = "map"
                    lesson = None

        if not running:
            break

        if current_screen == "menu":
            menu.update(dt)
            menu.draw(screen)
        elif current_screen == "map":
            lesson_map.update(dt)
            lesson_map.draw(screen)
        elif current_screen == "lesson" and lesson is not None:
            lesson.update(dt)
            lesson.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
