# main.py
import sys
import pygame
import settings
from game_select_menu import GameSelectMenu

# Ugolki
from ugolki.start_menu import StartMenu as UgolkiMenu
from ugolki.game import Game as UgolkiGame

# Poddavki
from poddavki.start_menu import PodStartMenu
from poddavki.game import PodGame

if __name__ == "__main__":
    pygame.init()
    try:
        while True:
            # select game
            selector = GameSelectMenu(settings.WIDTH, settings.HEIGHT)
            game_choice = selector.run()
            if game_choice is None:
                break

            # 2) Start menu of selected game
            if game_choice == "ugolki":
                menu = UgolkiMenu(settings.WIDTH, settings.HEIGHT)
                opts = menu.run()
                if opts is None:
                    continue  # return to select game

                vs_bot = bool(opts.get("vs_bot", True))
                human_player = opts.get("human_player", settings.P1)
                game = UgolkiGame(vs_bot=vs_bot, human_player=human_player)
                try:
                    result = game.run()
                except Exception as exc:
                    print(f"Error during game loop: {exc}", file=sys.stderr)
                    break
                if result == settings.RESTART_MENU:
                    continue      # return to select game
                else:
                    break

            elif game_choice == "poddavki":
                menu = PodStartMenu(settings.WIDTH, settings.HEIGHT)
                opts = menu.run()
                if opts is None:
                    continue

                vs_bot = bool(opts.get("vs_bot", False))  
                bot_diff = opts.get("bot_difficulty", "easy")
                human_player = opts.get("human_player", settings.P1)
                game = PodGame(vs_bot=vs_bot, bot_difficulty=bot_diff, human_player=human_player)
                try:
                    result = game.run()
                except Exception as exc:
                    print(f"Error during game loop: {exc}", file=sys.stderr)
                    break
                if result == settings.RESTART_MENU:
                    continue
                else:
                    break
    finally:
        pygame.quit()
