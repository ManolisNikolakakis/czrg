import pygame
import sys
import random
import math

_SW  = 1280
_SH  = 720
_FPS = 60

# ── Layout ─────────────────────────────────────────────────────────────────────
BARRIER_Y  = 278
WALL_H     = 52
SHOOT_Y    = 558
LR_MARGIN  = 160

TARGET_W   = 64
TARGET_H   = 98

# ── Game params ────────────────────────────────────────────────────────────────
ARROW_SPEED  = 630
CURSOR_SPEED = 285
TOTAL_ARROWS = 5
HITS_TO_WIN  = 3
TIME_LIMIT   = 20.0

# ── Colours ────────────────────────────────────────────────────────────────────
SKY         = (24, 18, 38)
SKY_HORIZON = (38, 28, 54)
GROUND      = (30, 25, 20)
WALL_BASE   = (60, 50, 40)
WALL_CAP    = (80, 68, 54)
TARGET_COL  = (128, 48, 182)
TARGET_DARK = (86, 28, 130)
TARGET_EYE  = (216, 192, 252)
TARGET_PUPIL= (28, 18, 38)
ARROW_COL   = (190, 245, 80)
AIM_COL     = (90, 132, 200)
CURSOR_COL  = (158, 208, 255)
CURSOR_RIM  = (86, 140, 210)
WHITE       = (255, 255, 255)
GREY        = (148, 148, 148)
GREEN       = (92, 212, 102)
RED         = (212, 72, 72)
ORANGE      = (255, 162, 38)


# ── Target ─────────────────────────────────────────────────────────────────────

class _Target:
    DUCK_DUR = 0.44
    RISE_DUR = 0.38

    def __init__(self):
        self.x        = float(_SW // 2)
        self.vx       = random.choice([-1, 1]) * random.uniform(110, 195)
        self.sink     = 0.0
        self.state    = "visible"
        self.state_t  = random.uniform(1.6, 2.8)
        self.hit_flash = 0.0

    @property
    def head_y(self):
        return BARRIER_Y - TARGET_H + self.sink

    def visible_height(self) -> float:
        return max(0.0, TARGET_H - self.sink)

    def is_hittable(self) -> bool:
        return self.visible_height() > TARGET_H * 0.15

    def hit_box(self) -> pygame.Rect:
        vh = int(self.visible_height())
        return pygame.Rect(int(self.x) - TARGET_W // 2,
                           BARRIER_Y - vh, TARGET_W, vh)

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        lx = LR_MARGIN + TARGET_W // 2
        rx = _SW - LR_MARGIN - TARGET_W // 2
        if self.x < lx: self.x = lx; self.vx =  abs(self.vx)
        if self.x > rx: self.x = rx; self.vx = -abs(self.vx)

        self.state_t   -= dt
        self.hit_flash  = max(0.0, self.hit_flash - dt)

        if self.state == "visible" and self.state_t <= 0:
            self.state = "ducking"; self.state_t = self.DUCK_DUR

        elif self.state == "ducking":
            progress  = 1.0 - max(0.0, self.state_t) / self.DUCK_DUR
            self.sink = TARGET_H * progress
            if self.state_t <= 0:
                self.sink = float(TARGET_H)
                self.state = "hidden"; self.state_t = random.uniform(0.65, 1.45)

        elif self.state == "hidden" and self.state_t <= 0:
            self.state = "rising"; self.state_t = self.RISE_DUR
            if random.random() < 0.55:
                self.vx = -(self.vx + random.uniform(-25, 25))

        elif self.state == "rising":
            progress  = 1.0 - max(0.0, self.state_t) / self.RISE_DUR
            self.sink = TARGET_H * (1.0 - progress)
            if self.state_t <= 0:
                self.sink = 0.0; self.state = "visible"
                self.state_t = random.uniform(1.6, 2.8)

    def register_hit(self) -> None:
        self.hit_flash = 0.35

    def draw(self, surf: pygame.Surface) -> None:
        if self.visible_height() <= 0:
            return
        ix      = int(self.x)
        head_cy = int(self.head_y) + 30
        head_r  = TARGET_W // 2 - 4
        body_top    = head_cy + head_r + 2
        body_bottom = BARRIER_Y - 2
        body_w      = TARGET_W - 20
        col = (240, 210, 90) if (self.hit_flash > 0 and
               int(self.hit_flash * 10) % 2 == 0) else TARGET_COL

        old_clip = surf.get_clip()
        surf.set_clip(pygame.Rect(0, 0, _SW, BARRIER_Y))
        if body_bottom > body_top:
            pygame.draw.rect(surf, col,
                             (ix - body_w // 2, body_top, body_w, body_bottom - body_top),
                             border_radius=4)
        if head_cy + head_r > 0:
            pygame.draw.circle(surf, col,         (ix, head_cy), head_r)
            pygame.draw.circle(surf, TARGET_DARK, (ix, head_cy), head_r, 2)
            for ex in (ix - 9, ix + 9):
                pygame.draw.circle(surf, TARGET_EYE,   (ex, head_cy - 4), 5)
                pygame.draw.circle(surf, TARGET_PUPIL, (ex, head_cy - 4), 2)
        surf.set_clip(old_clip)


# ── Arrow ──────────────────────────────────────────────────────────────────────

class _Arrow:
    def __init__(self, x: float):
        self.x      = x
        self.y      = float(SHOOT_Y)
        self.prev_y = float(SHOOT_Y)
        self.hit    = False
        self.done   = False

    def update(self, dt: float) -> None:
        self.prev_y = self.y
        self.y -= ARROW_SPEED * dt
        if self.y < -30:
            self.done = True

    def check_hit(self, target: _Target) -> bool:
        if not target.is_hittable():
            return False
        hb = target.hit_box()
        if not (hb.left - 4 <= self.x <= hb.right + 4):
            return False
        y_lo = min(self.y, self.prev_y)
        y_hi = max(self.y, self.prev_y)
        return y_lo <= hb.bottom and y_hi >= hb.top

    def draw(self, surf: pygame.Surface) -> None:
        tip_x, tip_y = int(self.x), int(self.y)
        pygame.draw.line(surf, ARROW_COL, (tip_x, tip_y + 22), (tip_x, tip_y + 6), 3)
        pygame.draw.polygon(surf, ARROW_COL, [
            (tip_x,     tip_y),
            (tip_x - 5, tip_y + 9),
            (tip_x + 5, tip_y + 9),
        ])
        trail_y = min(int(self.prev_y), SHOOT_Y)
        pygame.draw.line(surf, (100, 150, 40), (tip_x, tip_y + 22), (tip_x, trail_y), 1)


# ── Drawing helpers ────────────────────────────────────────────────────────────

def _draw_background(surf: pygame.Surface) -> None:
    surf.fill(SKY)
    pygame.draw.rect(surf, SKY_HORIZON, (0, BARRIER_Y - 120, _SW, 120))
    pygame.draw.rect(surf, GROUND,      (0, BARRIER_Y + WALL_H, _SW, _SH - BARRIER_Y - WALL_H))


def _draw_wall(surf: pygame.Surface) -> None:
    pygame.draw.rect(surf, WALL_BASE, (0, BARRIER_Y, _SW, WALL_H))
    pygame.draw.rect(surf, WALL_CAP,  (0, BARRIER_Y, _SW, 8))
    pygame.draw.rect(surf, (55, 47, 38), (0, SHOOT_Y + 4, _SW, 6))


def _draw_aim_guide(surf: pygame.Surface, cx: float) -> None:
    ix = int(cx)
    dash_len, gap = 10, 7
    y = SHOOT_Y - 10
    while y > BARRIER_Y + WALL_H:
        pygame.draw.line(surf, AIM_COL, (ix, y),
                         (ix, max(BARRIER_Y + WALL_H, y - dash_len)), 1)
        y -= dash_len + gap


def _draw_cursor(surf: pygame.Surface, cx: float) -> None:
    ix = int(cx)
    pygame.draw.polygon(surf, CURSOR_RIM, [(ix, SHOOT_Y - 3), (ix - 10, SHOOT_Y + 12), (ix + 10, SHOOT_Y + 12)])
    pygame.draw.polygon(surf, CURSOR_COL, [(ix, SHOOT_Y - 1), (ix - 8,  SHOOT_Y + 10), (ix + 8,  SHOOT_Y + 10)])


def _draw_hud(surf: pygame.Surface, font_md, font_sm,
              hits: int, arrows_left: int, time_left: float) -> None:
    bar_w, bar_h = 420, 22
    bx = _SW // 2 - bar_w // 2
    by = SHOOT_Y + 44
    ratio   = max(0.0, time_left / TIME_LIMIT)
    bar_col = GREEN if ratio > 0.4 else (ORANGE if ratio > 0.2 else RED)
    pygame.draw.rect(surf, (42, 38, 32), (bx, by, bar_w, bar_h), border_radius=6)
    pygame.draw.rect(surf, bar_col,      (bx, by, int(bar_w * ratio), bar_h), border_radius=6)
    pygame.draw.rect(surf, GREY,         (bx, by, bar_w, bar_h), 2, border_radius=6)
    t_txt = font_sm.render(f"{max(0.0, time_left):.1f}s", True, WHITE)
    surf.blit(t_txt, (_SW // 2 - t_txt.get_width() // 2, by + bar_h + 5))
    h_txt = font_md.render(f"Hits: {hits} / {HITS_TO_WIN}", True, WHITE)
    surf.blit(h_txt, (60, SHOOT_Y + 30))
    arr_lbl = font_sm.render("ARROWS", True, GREY)
    surf.blit(arr_lbl, (60, SHOOT_Y + 75))
    for i in range(TOTAL_ARROWS):
        ax, ay = 62 + i * 24, SHOOT_Y + 100
        col = ARROW_COL if i < arrows_left else (65, 60, 50)
        pygame.draw.polygon(surf, col, [(ax, ay), (ax - 4, ay + 8), (ax + 4, ay + 8)])
        pygame.draw.line(surf, col, (ax, ay + 8), (ax, ay + 18), 2)
    hint = font_sm.render("A / D — aim   ·   SPACE — shoot", True, GREY)
    surf.blit(hint, (_SW // 2 - hint.get_width() // 2, SHOOT_Y + 30))


def _show_result(surf: pygame.Surface, font_lg, font_md, won: bool, hits: int) -> None:
    overlay = pygame.Surface((_SW, _SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    surf.blit(overlay, (0, 0))
    col  = GREEN if won else RED
    big  = font_lg.render("YOU WIN!" if won else "MISSED!", True, col)
    sub  = font_md.render(f"Hits: {hits} / {HITS_TO_WIN}", True, WHITE)
    hint = font_md.render("Press any key to continue", True, GREY)
    surf.blit(big,  (_SW // 2 - big.get_width()  // 2, _SH // 2 - 90))
    surf.blit(sub,  (_SW // 2 - sub.get_width()  // 2, _SH // 2 - 10))
    surf.blit(hint, (_SW // 2 - hint.get_width() // 2, _SH // 2 + 50))


def _show_intro(surf: pygame.Surface, clock, font_lg, font_md, font_sm,
                title: str, subtitle: str) -> None:
    """Blocks until SPACE is pressed."""
    # Challenger title can be ~47 chars; size 44 keeps it comfortably within 1280 px.
    font_hd = pygame.font.SysFont(None, 44)
    surf.fill(SKY)
    _draw_wall(surf)
    overlay = pygame.Surface((_SW, _SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 148))
    surf.blit(overlay, (0, 0))
    entries = [
        (font_hd, title,                                                WHITE),
        (font_md, subtitle,                                             GREY),
        (font_sm, f"A / D to aim  ·  SPACE to shoot  ·  {TOTAL_ARROWS} arrows", GREY),
        (font_sm, "The target ducks behind the wall — wait for your opening!", ORANGE),
        (font_md, "Press SPACE to begin",                               WHITE),
    ]
    y = _SH // 2 - 160
    for f, text, col in entries:
        txt = f.render(text, True, col)
        surf.blit(txt, (_SW // 2 - txt.get_width() // 2, y))
        y += f.size("A")[1] + 14
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        clock.tick(_FPS)


# ── Core game loop ─────────────────────────────────────────────────────────────

def _game_loop(screen: pygame.Surface, clock,
               font_lg, font_md, font_sm) -> tuple[bool, int]:
    """Runs the shooting game. Returns (won, hits)."""
    target       = _Target()
    arrows       = []
    arrows_fired = 0
    hits         = 0
    cx           = float(_SW // 2)
    start_t      = pygame.time.get_ticks() / 1000.0
    result       = None
    result_shown = False
    shoot_cd     = 0.0

    while True:
        dt  = clock.tick(_FPS) / 1000.0
        now = pygame.time.get_ticks() / 1000.0
        time_left = TIME_LIMIT - (now - start_t)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if result_shown:
                    return hits >= HITS_TO_WIN, hits
                if event.key == pygame.K_ESCAPE:
                    return False, hits

        if result is None:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]: cx -= CURSOR_SPEED * dt
            if keys[pygame.K_d]: cx += CURSOR_SPEED * dt
            cx = max(LR_MARGIN + TARGET_W // 2,
                     min(_SW - LR_MARGIN - TARGET_W // 2, cx))

            shoot_cd = max(0.0, shoot_cd - dt)
            if keys[pygame.K_SPACE] and shoot_cd <= 0 and arrows_fired < TOTAL_ARROWS:
                arrows.append(_Arrow(cx))
                arrows_fired += 1
                shoot_cd = 0.28

            target.update(dt)

            for arrow in arrows:
                arrow.update(dt)
                if not arrow.hit and arrow.check_hit(target):
                    arrow.hit  = True
                    arrow.done = True
                    hits += 1
                    target.register_hit()
            arrows = [a for a in arrows if not a.done]

            if hits >= HITS_TO_WIN:
                result = True
            elif time_left <= 0:
                result = False
            elif arrows_fired >= TOTAL_ARROWS and not arrows and hits < HITS_TO_WIN:
                result = False

        _draw_background(screen)
        target.draw(screen)
        _draw_wall(screen)
        for arrow in arrows:
            arrow.draw(screen)
        _draw_aim_guide(screen, cx)
        _draw_cursor(screen, cx)
        _draw_hud(screen, font_md, font_sm, hits, TOTAL_ARROWS - arrows_fired, time_left)

        if result is not None:
            result_shown = True
            _show_result(screen, font_lg, font_md, result, hits)

        pygame.display.flip()


# ── Public integrated API ──────────────────────────────────────────────────────

def run_shooting_battle(screen, clock, font, font_big, font_title, player, boss) -> bool:
    """
    Shooting contest triggered by boss.
    Win → boss −2 HP.   Lose → player −1 HP.
    Returns True if player survives (hp > 0).
    """
    font_lg = pygame.font.SysFont(None, 72)
    font_md = pygame.font.SysFont(None, 36)
    font_sm = pygame.font.SysFont(None, 26)

    _show_intro(screen, clock, font_lg, font_md, font_sm,
                f"{boss.name.upper()} CHALLENGES YOU TO A SHOOTING CONTEST!",
                f"Hit the target {HITS_TO_WIN} times → deal 2 damage.  Fail → take 1 damage.")

    won, _ = _game_loop(screen, clock, font_lg, font_md, font_sm)

    if won:
        boss.take_damage(2)
        if hasattr(boss, 'lag_hp'):
            boss.lag_hp = max(boss.lag_hp - 2, 0)
    else:
        player.hp = max(0, player.hp - 1)
        player.total_damage = getattr(player, 'total_damage', 0) + 1

    return player.hp > 0


# ── Standalone entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    pygame.init()
    _screen = pygame.display.set_mode((_SW, _SH))
    pygame.display.set_caption("Target Shooting — Cazarog")
    _clock  = pygame.time.Clock()
    _fnt_lg = pygame.font.SysFont(None, 80)
    _fnt_md = pygame.font.SysFont(None, 38)
    _fnt_sm = pygame.font.SysFont(None, 26)

    _show_intro(_screen, _clock, _fnt_lg, _fnt_md, _fnt_sm,
                "TARGET SHOOTING",
                f"Hit the target {HITS_TO_WIN} times in {int(TIME_LIMIT)} seconds!")
    won, hits = _game_loop(_screen, _clock, _fnt_lg, _fnt_md, _fnt_sm)
    print(f"Outcome: {'win' if won else 'lose'}  |  Hits: {hits}")
    pygame.quit()
