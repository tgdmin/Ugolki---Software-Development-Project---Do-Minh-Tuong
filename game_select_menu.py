# game_select_menu.py
import pygame
import settings

class GameSelectMenu:
    def __init__(self, width, height):
        self.W, self.H = width, height
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Choose Game")
        self.clock = pygame.time.Clock()

        self.bg = (20, 35, 90)
        self.card = (35, 60, 130)
        self.btncol = (240, 240, 240)
        self.btn_text = (20, 20, 20)

        self.title_font = pygame.font.SysFont(None, 64)
        self.ui_font    = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 20)

        button_height = settings.BUTTON_HEIGHT
        self.buttons = [
            {"label": "Ugolki", "action": "ugolki", "rect": pygame.Rect(0, 0, 260, button_height)},
            {"label": "Poddavki", "action": "poddavki", "rect": pygame.Rect(0, 0, 260, button_height)},
            {"label": "Quit", "action": "quit", "rect": pygame.Rect(0, 0, 260, button_height)},
        ]

    def draw_btn(self, rect, label):
        pygame.draw.rect(self.screen, self.btncol, rect, border_radius=settings.BORDER_RADIUS)
        text = self.ui_font.render(label, True, self.btn_text)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _layout_buttons(self, card_rect, start_y, spacing, default_width=260, default_height=None):
        default_height = default_height or settings.BUTTON_HEIGHT
        total_height = default_height * len(self.buttons) + spacing * (len(self.buttons) - 1)
        available_bottom = card_rect.bottom - 20
        overflow = (start_y + total_height) - available_bottom
        if overflow > 0:
            start_y -= overflow + 10

        y = start_y
        for btn in self.buttons:
            rect = btn["rect"]
            rect.width, rect.height = default_width, default_height
            rect.centerx = self.W // 2
            rect.y = y
            y += default_height + spacing

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return None
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    for btn in self.buttons:
                        if btn["rect"].collidepoint(mx, my):
                            action = btn["action"]
                            if action == "ugolki":
                                return "ugolki"
                            if action == "poddavki":
                                return "poddavki"
                            if action == "quit":
                                return None
                            break

            self.screen.fill(self.bg)
            card_rect = pygame.Rect(self.W//2 - 280, self.H//2 - 180, 560, 360)
            pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

            title = self.title_font.render("Choose Game", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(self.W//2, card_rect.top + 60)))

            start_y = card_rect.top + 130
            self._layout_buttons(card_rect, start_y, spacing=settings.BUTTON_SPACING)
            for btn in self.buttons:
                self.draw_btn(btn["rect"], btn["label"])

            hint = self.small_font.render("ESC to quit", True, (220, 230, 255))
            self.screen.blit(hint, hint.get_rect(center=(self.W//2, card_rect.bottom - 20)))

            pygame.display.flip()
            self.clock.tick(60)
