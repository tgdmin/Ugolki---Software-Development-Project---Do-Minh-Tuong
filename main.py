# main.py
from start_menu import StartMenu
from game import Game
import settings
import pygame

if __name__ == "__main__":
    while True:
        # show start screen
        menu = StartMenu(settings.WIDTH, settings.HEIGHT)
        opts = menu.run()
        if opts is None:
            pygame.quit()
            break

        # start game with selected mode
        vs_bot = bool(opts.get("vs_bot", True))
        game = Game(vs_bot=vs_bot)
        result = game.run()

        # back to menu if requested from the win overlay
        if result == "menu":
            continue
        else:
            break
