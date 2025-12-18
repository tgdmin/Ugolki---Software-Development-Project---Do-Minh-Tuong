# pod_start_menu.py
import pygame
import settings


class PodStartMenu:  
    # Start menu for Poddavki
    def __init__(self, width, height):
        self.W, self.H = width, height
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Poddavki — Start")
        self.clock = pygame.time.Clock()

        # fonts
        self.title_font = pygame.font.SysFont(None, 64)
        self.ui_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.tiny_font = pygame.font.SysFont(None, 16)

        # MAIN SCREEN buttons (rects computed when drawing)
        self.main_buttons = [
            {"label": "Play", "action": "play"},
            {"label": "Game Rules", "action": "rules"},
            {"label": "Back", "action": "quit"},
        ]
        self.main_button_layout = []

        # MODE SCREEN buttons
        self.mode_buttons = [
            {"label": "Vs Player 2", "action": "vs_p2", "height": 64},
            {"label": "Vs Bot", "action": "vs_bot", "height": 64},
            {"label": "Role placeholder", "action": "role", "height": 50},
        ]
        self.mode_button_layout = []
        self.play_as_p1 = True

        # BOT DIFFICULTY buttons
        self.bot_buttons = [
            {"label": "Easy", "action": "bot_easy", "width": 300, "height": 64},
            {"label": "Hard", "action": "bot_hard", "width": 300, "height": 64},
            {"label": "Back", "action": "bot_back", "width": 160, "height": 44},
        ]
        self.bot_button_layout = []

        # RULES overlay
        card_w, card_h = 560, 420
        self.rules_rect = pygame.Rect(
            self.W // 2 - card_w // 2,
            self.H // 2 - card_h // 2,
            card_w,
            card_h,
        )
        self.rules_back = pygame.Rect(
            self.rules_rect.centerx - 80,
            self.rules_rect.bottom - 70,
            160,
            44,
        )

        # UI state
        self.show_rules = False
        self.mode_select = False  # False = main screen, True = choosing opponent
        self.bot_difficulty_menu = False

        # colors
        self.bg = (20, 35, 90)
        self.card = (35, 60, 130)
        self.card2 = (28, 48, 110)
        self.btncol = (240, 240, 240)
        self.btn_text = (20, 20, 20)
        self.overlay = (0, 0, 0, 140)

        # rule text
        self.rules_lines = [
            "PODDAVKI — Rules (quick):",
            "",
            "• Men move diagonally forward on dark squares.",
            "• Kings move diagonally one square in any direction.",
            "• Men capture by jumping forward over an adjacent enemy",
            "  to the empty square immediately beyond (no backward capture).",
            "• Kings capture the same way but in all 4 diagonal directions.",
            "• Multiple jumps are allowed; captured pieces stay on board",
            "  during the sequence and can't be jumped again.",
            "• Capturing is mandatory: if any capture exists you must take one.",
            "• You WIN when you have no legal moves left.",
        ]

    # ---------- draw utils ----------
    def draw_btn(self, rect, label):
        pygame.draw.rect(self.screen, self.btncol, rect, border_radius=settings.BORDER_RADIUS)
        text = self.ui_font.render(label, True, self.btn_text)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_footer(self):
        t = self.tiny_font.render(
            "Do Minh Tuong — Python project", True, (210, 220, 240)
        )
        self.screen.blit(t, (10, self.H - t.get_height() - settings.FOOTER_PADDING))

    def _layout_buttons(self, buttons, card_rect, start_y, spacing, default_width, default_height):
        total_height = sum(btn.get("height", default_height) for btn in buttons)
        total_height += spacing * (len(buttons) - 1)
        available_bottom = card_rect.bottom - 20
        overflow = (start_y + total_height) - available_bottom
        if overflow > 0:
            start_y -= overflow + 10

        y = start_y
        layout = []
        for btn in buttons:
            width = btn.get("width", default_width)
            height = btn.get("height", default_height)
            rect = pygame.Rect(0, 0, width, height)
            rect.centerx = self.W // 2
            rect.y = y
            y += height + spacing
            layout.append({"rect": rect, "action": btn["action"], "label": btn["label"]})
        return layout

    # ---------- screens ----------
    def draw_main(self):
        self.screen.fill(self.bg)
        card_rect = pygame.Rect(self.W // 2 - 280, 20, 560, self.H - 40)
        pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

        title = self.title_font.render("PODDAVKI", True, (255, 255, 255))
        self.screen.blit(
            title, title.get_rect(center=(self.W // 2, card_rect.top + 60))
        )

        start_y = card_rect.top + 150
        self.main_button_layout = self._layout_buttons(
            self.main_buttons,
            card_rect,
            start_y,
            spacing=settings.BUTTON_SPACING,
            default_width=260,
            default_height=settings.BUTTON_HEIGHT,
        )
        for btn in self.main_button_layout:
            self.draw_btn(btn["rect"], btn["label"])

        self.draw_footer()

    def draw_mode(self):
        self.screen.fill(self.bg)
        card_rect = pygame.Rect(self.W // 2 - 300, self.H // 2 - 190, 600, 380)
        pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

        title = self.title_font.render("Choose Opponent", True, (255, 255, 255))
        self.screen.blit(
            title, title.get_rect(center=(self.W // 2, card_rect.top + 60))
        )

        start_y = card_rect.top + 140
        self.mode_button_layout = self._layout_buttons(
            self.mode_buttons,
            card_rect,
            start_y,
            spacing=settings.BUTTON_SPACING,
            default_width=300,
            default_height=64,
        )
        for btn in self.mode_button_layout:
            label = btn["label"]
            if btn["action"] == "role":
                label = "Play as: Player 1" if self.play_as_p1 else "Play as: Player 2"
            self.draw_btn(btn["rect"], label)

        hint = self.small_font.render("Press ESC to go back", True, (220, 230, 255))
        self.screen.blit(hint, hint.get_rect(center=(self.W // 2, card_rect.bottom - 28)))

        self.draw_footer()

    def draw_bot_difficulty(self):
        self.screen.fill(self.bg)
        card_rect = pygame.Rect(self.W // 2 - 320, self.H // 2 - 200, 640, 400)
        pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

        title = self.title_font.render("Bot Difficulty", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.W // 2, card_rect.top + 60)))

        start_y = card_rect.top + 140
        self.bot_button_layout = self._layout_buttons(
            self.bot_buttons,
            card_rect,
            start_y,
            spacing=settings.BUTTON_SPACING,
            default_width=300,
            default_height=64,
        )
        for btn in self.bot_button_layout:
            self.draw_btn(btn["rect"], btn["label"])

        self.draw_footer()

    def draw_rules(self):
        dim = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        dim.fill(self.overlay)
        self.screen.blit(dim, (0, 0))

        pygame.draw.rect(self.screen, self.card2, self.rules_rect, border_radius=16)

        title = self.ui_font.render("Game Rules", True, (255, 255, 255))
        self.screen.blit(
            title,
            title.get_rect(midtop=(self.rules_rect.centerx, self.rules_rect.top + 18)),
        )

        y = self.rules_rect.top + 60
        left = self.rules_rect.left + 22
        for line in self.rules_lines:
            t = self.small_font.render(line, True, (230, 235, 255))
            self.screen.blit(t, (left, y))
            y += t.get_height() + 6

        pygame.draw.rect(self.screen, self.btncol, self.rules_back, border_radius=settings.BORDER_RADIUS)
        txt = self.ui_font.render("Back", True, self.btn_text)
        self.screen.blit(txt, txt.get_rect(center=self.rules_back.center))

        self.draw_footer()

    # ---------- main loop ----------
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None

                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.show_rules:
                        self.show_rules = False
                    elif self.mode_select:
                        if self.bot_difficulty_menu:
                            self.bot_difficulty_menu = False
                        else:
                            self.mode_select = False
                            self.bot_difficulty_menu = False
                    else:
                        return None

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos

                    # rules overlay
                    if self.show_rules:
                        if self.rules_back.collidepoint(mx, my):
                            self.show_rules = False
                        continue

                    # bot difficulty selection
                    if self.mode_select and self.bot_difficulty_menu:
                        for btn in self.bot_button_layout:
                            if btn["rect"].collidepoint(mx, my):
                                action = btn["action"]
                                if action == "bot_easy":
                                    hp = settings.P1 if self.play_as_p1 else settings.P2
                                    return {"vs_bot": True, "bot_difficulty": "easy", "human_player": hp}
                                if action == "bot_hard":
                                    hp = settings.P1 if self.play_as_p1 else settings.P2
                                    return {"vs_bot": True, "bot_difficulty": "hard", "human_player": hp}
                                if action == "bot_back":
                                    self.bot_difficulty_menu = False
                                break
                        continue

                    # mode screen
                    if self.mode_select:
                        handled = False
                        for btn in self.mode_button_layout:
                            if btn["rect"].collidepoint(mx, my):
                                action = btn["action"]
                                if action == "role":
                                    self.play_as_p1 = not self.play_as_p1
                                elif action == "vs_p2":
                                    return {"vs_bot": False}
                                elif action == "vs_bot":
                                    self.bot_difficulty_menu = True
                                handled = True
                                break
                        if handled:
                            continue

                    # main screen
                    for btn in self.main_button_layout:
                        if btn["rect"].collidepoint(mx, my):
                            action = btn["action"]
                            if action == "play":
                                self.mode_select = True
                                self.bot_difficulty_menu = False
                            elif action == "rules":
                                self.show_rules = True
                            elif action == "quit":
                                return None
                            break

            # draw
            if self.show_rules:
                self.draw_main()
                self.draw_rules()
            else:
                if self.mode_select:
                    if self.bot_difficulty_menu:
                        self.draw_bot_difficulty()
                    else:
                        self.draw_mode()
                else:
                    self.draw_main()

            pygame.display.flip()
            self.clock.tick(60)
