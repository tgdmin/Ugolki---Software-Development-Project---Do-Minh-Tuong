# game_select_menu.py
import pygame
import settings

class GameSelectMenu:
    def __init__(self, width, height):
        pygame.init()
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

        bw, bh = 260, 56
        cx = self.W // 2 - bw // 2
        self.btn_ugolki   = pygame.Rect(cx, self.H // 2 - bh - 10, bw, bh)
        self.btn_poddavki = pygame.Rect(cx, self.H // 2 + 10,      bw, bh)
        self.btn_quit     = pygame.Rect(cx, self.H // 2 + 90,      bw, bh)

    def draw_btn(self, rect, label):
        pygame.draw.rect(self.screen, self.btncol, rect, border_radius=12)
        text = self.ui_font.render(label, True, self.btn_text)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return None
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return None
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    if self.btn_ugolki.collidepoint(mx, my):
                        return "ugolki"
                    if self.btn_poddavki.collidepoint(mx, my):
                        return "poddavki"
                    if self.btn_quit.collidepoint(mx, my):
                        return None

            self.screen.fill(self.bg)
            card_rect = pygame.Rect(self.W//2 - 280, self.H//2 - 180, 560, 360)
            pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

            title = self.title_font.render("Choose Game", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(self.W//2, card_rect.top + 60)))

            self.draw_btn(self.btn_ugolki,   "Ugolki")
            self.draw_btn(self.btn_poddavki, "Poddavki")
            self.draw_btn(self.btn_quit,     "Quit")

            hint = self.small_font.render("ESC to quit", True, (220, 230, 255))
            self.screen.blit(hint, hint.get_rect(center=(self.W//2, card_rect.bottom - 20)))

            pygame.display.flip()
            self.clock.tick(60)
