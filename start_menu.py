# start_menu.py
# Start screen -> Mode screen (ONLY two buttons). Fixed layout: draw rects = click rects.
import os
import pygame
import settings


class StartMenu:
    def __init__(self, width, height):
        pygame.init()
        self.W, self.H = width, height
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Ugolki — Start")
        self.clock = pygame.time.Clock()

        # fonts
        self.title_font = pygame.font.SysFont(None, 64)
        self.ui_font    = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.tiny_font  = pygame.font.SysFont(None, 16)

        # MAIN SCREEN base rects
        bw, bh = 260, 56
        cx = self.W // 2 - bw // 2
        self.btn_play   = pygame.Rect(cx, self.H // 2 + 30, bw, bh)
        self.btn_rules  = pygame.Rect(cx, self.H // 2 + 50, bw, bh)
        self.btn_toggle = pygame.Rect(cx, self.H // 2 + 70, bw, bh)
        self.btn_quit   = pygame.Rect(cx, self.H // 2 + 90, bw, bh)

        self.r_play = self.btn_play
        self.r_rules = self.btn_rules
        self.r_toggle = self.btn_toggle
        self.r_quit = self.btn_quit

        # after click play
        mbw, mbh = 300, 64
        mcx = self.W // 2 - mbw // 2
        self.btn_vs_p2  = pygame.Rect(mcx, self.H // 2 - 40, mbw, mbh)
        self.btn_vs_bot = pygame.Rect(mcx, self.H // 2 + 40, mbw, mbh)

        # rules overlay
        card_w, card_h = 560, 420
        self.rules_rect = pygame.Rect(self.W//2 - card_w//2, self.H//2 - card_h//2, card_w, card_h)
        self.rules_back = pygame.Rect(self.rules_rect.centerx - 80, self.rules_rect.bottom - 70, 160, 44)
        self.show_rules = False

        # state mirrors settings
        self.camp_rule = settings.ENFORCE_CAMP_RULE

        # UI state
        self.mode_select = False  # False = main, True = chọn mode

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

        # rule text
        self.rules_lines = [
            "UGOLKI — Rules (quick):",
            "",
            "• Move 1 cell or jump over a piece if landing is empty.",
            "• Jumps can chain; after each jump, valid jumps are recalculated.",
            "• In a chain you can't land on any cell already visited in that chain.",
            "• Camp rule : a piece enters target camp, it must stay inside.",
            "• Win: fill the opponent's camp completely.",
            "",
            "Controls:",
            "Left-click: select / move   |   ESC: back/quit",
        ]

    # draw utils 
    def draw_btn(self, rect, label):
        pygame.draw.rect(self.screen, self.btncol, rect, border_radius=12)
        text = self.ui_font.render(label, True, self.btn_text)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_footer(self):
        t = self.tiny_font.render("Do Minh Tuong — Python project", True, (210, 220, 240))
        self.screen.blit(t, (10, self.H - t.get_height() - 8))

    #  screens 
    def draw_main(self):
        self.screen.fill(self.bg)

        # card
        card_rect = pygame.Rect(self.W//2 - 280, 20, 560, self.H - 40)  # ăn theo chiều cao cửa sổ
        pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

        # title
        title = self.title_font.render("UGOLKI", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.W//2, card_rect.top + 60)))

        # logo
        y_offset = 0
        base_y = card_rect.top + 120
        if self.logo:
            rlogo = self.logo.get_rect(center=(self.W//2, base_y + 40))
            self.screen.blit(self.logo, rlogo)
            y_offset = 100 

        spacing = 64

        # click rects
        self.r_play   = self.btn_play.move(0, y_offset - 60)     
        self.r_rules  = self.btn_rules.move(0, y_offset - 60 + spacing)
        self.r_toggle = self.btn_toggle.move(0, y_offset - 60 + spacing*2)
        self.r_quit   = self.btn_quit.move(0, y_offset - 60 + spacing*3)

        # if button shorter than window, shift up to fit
        bottom_limit = card_rect.bottom - 20
        overflow = self.r_quit.bottom - bottom_limit
        if overflow > 0:
            shift = overflow + 10
            self.r_play.move_ip(0, -shift)
            self.r_rules.move_ip(0, -shift)
            self.r_toggle.move_ip(0, -shift)
            self.r_quit.move_ip(0, -shift)

        # draw buttons
        self.draw_btn(self.r_play, "Play")
        self.draw_btn(self.r_rules, "Game Rules")
        self.draw_btn(self.r_toggle, f"Camp rule: {'ON' if self.camp_rule else 'OFF'}")
        self.draw_btn(self.r_quit, "Quit")

        self.draw_footer()

    def draw_mode(self):
        self.screen.fill(self.bg)
        card_rect = pygame.Rect(self.W//2 - 300, self.H//2 - 160, 600, 320)
        pygame.draw.rect(self.screen, self.card, card_rect, border_radius=20)

        title = self.title_font.render("Choose Opponent", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.W//2, card_rect.top + 60)))

        self.draw_btn(self.btn_vs_p2,  "Vs Player 2")
        self.draw_btn(self.btn_vs_bot, "Vs Bot")

        hint = self.small_font.render("Press ESC to go back", True, (220, 230, 255))
        self.screen.blit(hint, hint.get_rect(center=(self.W//2, card_rect.bottom - 28)))

        self.draw_footer()

    def draw_rules(self):
        dim = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        dim.fill(self.overlay)
        self.screen.blit(dim, (0, 0))
        pygame.draw.rect(self.screen, self.card2, self.rules_rect, border_radius=16)
        title = self.ui_font.render("Game Rules", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(midtop=(self.rules_rect.centerx, self.rules_rect.top + 18)))
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
                        if self.rules_back.collidepoint(mx, my):
                            self.show_rules = False
                        continue

                    # mode screen (ONLY two buttons)
                    if self.mode_select:
                        if self.btn_vs_p2.collidepoint(mx, my):
                            settings.ENFORCE_CAMP_RULE = self.camp_rule
                            return {"camp_rule": self.camp_rule, "vs_bot": False}
                        if self.btn_vs_bot.collidepoint(mx, my):
                            settings.ENFORCE_CAMP_RULE = self.camp_rule
                            return {"camp_rule": self.camp_rule, "vs_bot": True}
                        continue

                    # main screen 
                    if self.r_play.collidepoint(mx, my):
                        self.mode_select = True
                    elif self.r_rules.collidepoint(mx, my):
                        self.show_rules = True
                    elif self.r_toggle.collidepoint(mx, my):
                        self.camp_rule = not self.camp_rule
                    elif self.r_quit.collidepoint(mx, my):
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
