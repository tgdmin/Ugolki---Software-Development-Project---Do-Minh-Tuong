# pod_start_menu.py
import pygame
import settings


class PodStartMenu:  
    # Start menu for Poddavki
    def __init__(self, width, height):
        pygame.init()
        self.W, self.H = width, height
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Poddavki — Start")
        self.clock = pygame.time.Clock()

        # fonts
        self.title_font = pygame.font.SysFont(None, 64)
        self.ui_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.tiny_font = pygame.font.SysFont(None, 16)

        # MAIN SCREEN buttons
        bw, bh = 260, 56
        cx = self.W // 2 - bw // 2
        self.btn_play = pygame.Rect(cx, self.H // 2, bw, bh)
        self.btn_rules = pygame.Rect(cx, self.H // 2 + 70, bw, bh)
        self.btn_quit = pygame.Rect(cx, self.H // 2 + 140, bw, bh)

        # MODE SCREEN buttons
        mbw, mbh = 300, 64
        mcx = self.W // 2 - mbw // 2
        self.btn_vs_p2 = pygame.Rect(mcx, self.H // 2 - 40, mbw, mbh)
        self.btn_vs_bot = pygame.Rect(mcx, self.H // 2 + 40, mbw, mbh)

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
            "• Capturing is mandatory for the SELECTED piece only.",
            "• If that piece can capture, it must; otherwise it may move.",
            "• You WIN when you have no legal moves left.",
        ]

    # ---------- draw utils ----------
    def draw_btn(self, rect, label):
        pygame.draw.rect(self.screen, self.btncol, rect, border_radius=12)
        text = self.ui_font.render(label, True, self.btn_text)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_footer(self):
        t = self.tiny_font.render(
            "Do Minh Tuong — Python project", True, (210, 220, 240)
        )
        self.screen.blit(t, (10, self.H - t.get_height() - 8))

    # ---------- screens ----------
    def draw_main(self):
        self.screen.fill(self.bg)
        card_rect = pygame.Rect(self.W // 2 - 280, 20, 560, self.H - 40)
        pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

        title = self.title_font.render("PODDAVKI", True, (255, 255, 255))
        self.screen.blit(
            title, title.get_rect(center=(self.W // 2, card_rect.top + 60))
        )

        self.draw_btn(self.btn_play, "Play")
        self.draw_btn(self.btn_rules, "Game Rules")
        self.draw_btn(self.btn_quit, "Back")

        self.draw_footer()

    def draw_mode(self):
        self.screen.fill(self.bg)
        card_rect = pygame.Rect(self.W // 2 - 300, self.H // 2 - 160, 600, 320)
        pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

        title = self.title_font.render("Choose Opponent", True, (255, 255, 255))
        self.screen.blit(
            title, title.get_rect(center=(self.W // 2, card_rect.top + 60))
        )

        self.draw_btn(self.btn_vs_p2, "Vs Player 2")
        self.draw_btn(self.btn_vs_bot, "Vs Bot")

        hint = self.small_font.render("Press ESC to go back", True, (220, 230, 255))
        self.screen.blit(hint, hint.get_rect(center=(self.W // 2, card_rect.bottom - 28)))

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

        pygame.draw.rect(self.screen, self.btncol, self.rules_back, border_radius=12)
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
                        self.mode_select = False
                    else:
                        return None

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos

                    # rules overlay
                    if self.show_rules:
                        if self.rules_back.collidepoint(mx, my):
                            self.show_rules = False
                        continue

                    # mode screen
                    if self.mode_select:
                        if self.btn_vs_p2.collidepoint(mx, my):
                            return {"vs_bot": False}
                        if self.btn_vs_bot.collidepoint(mx, my):
                            return {"vs_bot": True}
                        continue

                    # main screen
                    if self.btn_play.collidepoint(mx, my):
                        self.mode_select = True
                    elif self.btn_rules.collidepoint(mx, my):
                        self.show_rules = True
                    elif self.btn_quit.collidepoint(mx, my):
                        return None

            # draw
            if self.show_rules:
                self.draw_main()
                self.draw_rules()
            else:
                if self.mode_select:
                    self.draw_mode()
                else:
                    self.draw_main()

            pygame.display.flip()
            self.clock.tick(60)
