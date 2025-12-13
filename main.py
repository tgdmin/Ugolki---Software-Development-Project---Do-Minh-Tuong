# main.py
import pygame
import settings
from game_select_menu import GameSelectMenu

# Ugolki
from start_menu import StartMenu as UgolkiMenu
from game import Game as UgolkiGame

# Poddavki
from pod_start_menu import PodStartMenu
from pod_game import PodGame

if __name__ == "__main__":
    while True:
        # select game
        selector = GameSelectMenu(settings.WIDTH, settings.HEIGHT)
        game_choice = selector.run()
        if game_choice is None:
            pygame.quit()
            break

        # 2) Start menu of selected game
        if game_choice == "ugolki":
            menu = UgolkiMenu(settings.WIDTH, settings.HEIGHT)
            opts = menu.run()
            if opts is None:
                continue  # return to select game

            vs_bot = bool(opts.get("vs_bot", True))
            game = UgolkiGame(vs_bot=vs_bot)
            result = game.run()
            if result == "menu":
                continue      # return to select game
            else:
                break

        elif game_choice == "poddavki":
            menu = PodStartMenu(settings.WIDTH, settings.HEIGHT)
            opts = menu.run()
            if opts is None:
                continue

            vs_bot = bool(opts.get("vs_bot", False))  
            game = PodGame(vs_bot=vs_bot)
            result = game.run()
            if result == "menu":
                continue
            else:
                break

    pygame.quit()
