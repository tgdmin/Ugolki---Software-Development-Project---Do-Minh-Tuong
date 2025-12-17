# start_menu.py
# Start screen -> Mode screen (ONLY two buttons). Fixed layout: draw rects = click rects.
import os
import pygame
import settings


class Button:
    def __init__(self, action, label=None, *, width=260, height=settings.BUTTON_HEIGHT, label_getter=None):
        self.action = action
        self.width = width
        self.height = height
        self._label = label or ""
        self.label_getter = label_getter
        self.rect = pygame.Rect(0, 0, width, height)

    def get_label(self):
        if self.label_getter:
            return self.label_getter()
        return self._label

    def update_rect(self, center_x, top_y):
        self.rect.width = self.width
        self.rect.height = self.height
        self.rect.centerx = center_x
        self.rect.y = top_y

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)


class MenuScreen:
    bottom_margin = 20
    overflow_padding = 10

    def __init__(self, menu):
        self.menu = menu
        self.buttons = []

    def layout_buttons(self, card_rect, start_y, spacing=None):
        if not self.buttons:
            return
        spacing = spacing if spacing is not None else settings.BUTTON_SPACING
        total_height = sum(btn.height for btn in self.buttons)
        total_height += spacing * (len(self.buttons) - 1)
        available_bottom = card_rect.bottom - self.bottom_margin
        overflow = (start_y + total_height) - available_bottom
        if overflow > 0:
            start_y -= overflow + self.overflow_padding

        y = start_y
        center = self.menu.W // 2
        for btn in self.buttons:
            btn.update_rect(center, y)
            y += btn.height + spacing

    def draw_buttons(self):
        for btn in self.buttons:
            self.menu.draw_btn(btn.rect, btn.get_label())

    def handle_click(self, pos):
        for btn in self.buttons:
            if btn.collidepoint(pos):
                return btn.action
        return None


class MainMenuScreen(MenuScreen):
    def __init__(self, menu):
        super().__init__(menu)
        self.buttons = [
            Button(action="play", label="Play"),
            Button(action="rules", label="Game Rules"),
            Button(action="toggle", label_getter=self._camp_rule_label),
            Button(action="quit", label="Quit"),
        ]

    def _camp_rule_label(self):
        return f"Camp rule: {'ON' if self.menu.camp_rule else 'OFF'}"

    def draw(self):
        screen = self.menu.screen
        screen.fill(self.menu.bg)
        card_rect = pygame.Rect(self.menu.W//2 - 280, 20, 560, self.menu.H - 40)
        pygame.draw.rect(screen, self.menu.card, card_rect, border_radius=20)

        title = self.menu.title_font.render("UGOLKI", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.menu.W//2, card_rect.top + 60)))

        base_y = card_rect.top + 120
        y_offset = 0
        if self.menu.logo:
            rlogo = self.menu.logo.get_rect(center=(self.menu.W//2, base_y + 40))
            screen.blit(self.menu.logo, rlogo)
            y_offset = 100

        self.layout_buttons(card_rect, base_y + y_offset)
        self.draw_buttons()
        self.menu.draw_footer()


class ModeScreen(MenuScreen):
    def __init__(self, menu):
        super().__init__(menu)
        self.buttons = [
            Button(action="vs_p2", label="Vs Player 2", width=300, height=64),
            Button(action="vs_bot", label="Vs Bot", width=300, height=64),
            Button(action="role", label_getter=self._role_label, width=300, height=50),
        ]

    def _role_label(self):
        return "Play as: Player 1" if self.menu.play_as_p1 else "Play as: Player 2"

    def draw(self):
        screen = self.menu.screen
        screen.fill(self.menu.bg)
        card_rect = pygame.Rect(self.menu.W//2 - 300, self.menu.H//2 - 190, 600, 380)
        pygame.draw.rect(screen, self.menu.card, card_rect, border_radius=20)

        title = self.menu.title_font.render("Choose Opponent", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.menu.W//2, card_rect.top + 60)))

        start_y = card_rect.top + 140
        self.layout_buttons(card_rect, start_y)
        self.draw_buttons()

        hint = self.menu.small_font.render("Press ESC to go back", True, (220, 230, 255))
        screen.blit(hint, hint.get_rect(center=(self.menu.W//2, card_rect.bottom - 28)))

        self.menu.draw_footer()


class RulesOverlay:
    def __init__(self, menu):
        self.menu = menu
        card_w, card_h = 560, 420
        self.rules_rect = pygame.Rect(self.menu.W//2 - card_w//2, self.menu.H//2 - card_h//2, card_w, card_h)
        self.back_button = Button(action="back", label="Back", width=160, height=44)
        self.rules_lines = [
            "UGOLKI — Rules (quick):",
            "",
            "• Move 1 cell or jump over a piece if landing is empty.",
            "• If any capture is available, you must take it.",
            "• Jumps can chain; after each jump, valid jumps are recalculated.",
            "• In a chain you can't land on any cell already visited in that chain.",
            "• Camp rule : a piece enters target camp, it must stay inside.",
            "• Win: fill the opponent's camp completely.",
            "",
            "Controls:",
            "Left-click: select / move   |   ESC: back/quit",
        ]

    def draw(self):
        dim = pygame.Surface((self.menu.W, self.menu.H), pygame.SRCALPHA)
        dim.fill(self.menu.overlay)
        self.menu.screen.blit(dim, (0, 0))
        pygame.draw.rect(self.menu.screen, self.menu.card2, self.rules_rect, border_radius=16)
        title = self.menu.ui_font.render("Game Rules", True, (255, 255, 255))
        self.menu.screen.blit(title, title.get_rect(midtop=(self.rules_rect.centerx, self.rules_rect.top + 18)))
        y = self.rules_rect.top + 60
        left = self.rules_rect.left + 22
        for line in self.rules_lines:
            t = self.menu.small_font.render(line, True, (230, 235, 255))
            self.menu.screen.blit(t, (left, y))
            y += t.get_height() + 6

        self.back_button.update_rect(self.rules_rect.centerx, self.rules_rect.bottom - 70)
        self.menu.draw_btn(self.back_button.rect, self.back_button.get_label())
        self.menu.draw_footer()

    def handle_click(self, pos):
        if self.back_button.collidepoint(pos):
            return self.back_button.action
        return None


class StartMenu:
    def __init__(self, width, height):
        self.W, self.H = width, height
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Ugolki — Start")
        self.clock = pygame.time.Clock()

        # fonts
        self.title_font = pygame.font.SysFont(None, 64)
        self.ui_font    = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.tiny_font  = pygame.font.SysFont(None, 16)

        self.play_as_p1 = True
        self.show_rules = False

        # state mirrors settings
        self.camp_rule = settings.ENFORCE_CAMP_RULE

        # UI state
        self.mode_select = False  # False = main screen, True = choosing opponent

        # colors
        self.bg     = (20, 35, 90)
        self.card   = (35, 60, 130)
        self.card2  = (28, 48, 110)
        self.btncol = (240, 240, 240)
        self.btn_text = (20, 20, 20)
        self.overlay  = (0, 0, 0, 140)

        # logo 
        self.logo = None
        if os.path.exists(getattr(settings, "LOGO_PATH", "")):
            try:
                img = pygame.image.load(settings.LOGO_PATH).convert_alpha()
                lw, lh = img.get_size()
                scale = min(180 / lw, 180 / lh)
                self.logo = pygame.transform.smoothscale(img, (int(lw*scale), int(lh*scale)))
            except Exception as e:
                print("Could not load logo:", e)
                self.logo = None

        self.main_screen = MainMenuScreen(self)
        self.mode_screen = ModeScreen(self)
        self.rules_overlay = RulesOverlay(self)

    # draw utils 
    def draw_btn(self, rect, label):
        pygame.draw.rect(self.screen, self.btncol, rect, border_radius=settings.BORDER_RADIUS)
        text = self.ui_font.render(label, True, self.btn_text)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_footer(self):
        t = self.tiny_font.render("Do Minh Tuong — Python project", True, (210, 220, 240))
        self.screen.blit(t, (10, self.H - t.get_height() - settings.FOOTER_PADDING))

    # loop 
    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None

                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.show_rules:
                        self.show_rules = False
                    elif self.mode_select:
                        self.mode_select = False
                    else:
                        return None

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos

                    # rules overlay
                    if self.show_rules:
                        action = self.rules_overlay.handle_click((mx, my))
                        if action == "back":
                            self.show_rules = False
                        continue

                    # mode screen
                    if self.mode_select:
                        action = self.mode_screen.handle_click((mx, my))
                        if action == "role":
                            self.play_as_p1 = not self.play_as_p1
                        elif action == "vs_p2":
                            return {"camp_rule": self.camp_rule, "vs_bot": False}
                        elif action == "vs_bot":
                            hp = settings.P1 if self.play_as_p1 else settings.P2
                            return {"camp_rule": self.camp_rule, "vs_bot": True, "human_player": hp}
                        if action:
                            continue
                        continue

                    # main screen 
                    action = self.main_screen.handle_click((mx, my))
                    if not action:
                        continue
                    if action == "play":
                        self.mode_select = True
                    elif action == "rules":
                        self.show_rules = True
                    elif action == "toggle":
                        self.camp_rule = not self.camp_rule
                    elif action == "quit":
                        return None
                    continue

            # draw
            if self.show_rules:
                self.main_screen.draw()
                self.rules_overlay.draw()
            else:
                if self.mode_select:
                    self.mode_screen.draw()
                else:
                    self.main_screen.draw()

            pygame.display.flip()
            self.clock.tick(60)
