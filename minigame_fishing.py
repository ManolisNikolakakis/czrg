import pygame
import sys
import random
import math

# Screen constants match the game's fixed resolution
_SW = 1280
_SH = 720
_FPS = 60

POND             = pygame.Rect(240, 130, 800, 460)
CURSOR_SPEED     = 240
CURSOR_R         = 13
FISH_R           = 11
WARNING_DURATION = 2.0
CYCLE_INTERVAL   = 2.0
FISH_PER_CYCLE   = 2
START_FISH       = 5
WIN_FISH         = 5
TIME_LIMIT       = 10.0

BG         = (30, 25, 20)
POND_MID   = (22, 65, 118)
POND_WAVE  = (28, 78, 138)
POND_EDGE  = (12, 38, 72)
FISH_NORM  = (255, 210, 55)
FISH_WARN  = (255, 70, 50)
FISH_WARN2 = (255, 165, 40)
CURSOR_COL = (160, 235, 185)
CURSOR_RIM = (70, 170, 105)
WHITE      = (255, 255, 255)
GREY       = (155, 155, 155)
GREEN      = (95, 215, 105)
RED_COL    = (215, 75, 75)
ORANGE     = (255, 165, 40)


# ── Fish ───────────────────────────────────────────────────────────────────────

class Fish:
    def __init__(self, now: float):
        margin = FISH_R + 14
        self.x = float(random.randint(POND.left + margin, POND.right  - margin))
        self.y = float(random.randint(POND.top  + margin, POND.bottom - margin))
        self.angle   = random.uniform(0, 2 * math.pi)
        self.speed   = random.uniform(38, 78)
        self.turn_cd = random.uniform(0.4, 1.3)
        self.warning    = False
        self.warn_start = 0.0

    def start_warning(self, now: float) -> None:
        self.warning    = True
        self.warn_start = now

    def warn_progress(self, now: float) -> float:
        if not self.warning:
            return 0.0
        return min(1.0, (now - self.warn_start) / WARNING_DURATION)

    def update(self, dt: float) -> None:
        self.turn_cd -= dt
        if self.turn_cd <= 0:
            self.angle   += random.uniform(-1.3, 1.3)
            self.turn_cd  = random.uniform(0.4, 1.3)
        nx = self.x + math.cos(self.angle) * self.speed * dt
        ny = self.y + math.sin(self.angle) * self.speed * dt
        margin = FISH_R + 4
        if not (POND.left + margin <= nx <= POND.right  - margin):
            self.angle = math.pi - self.angle
        if not (POND.top  + margin <= ny <= POND.bottom - margin):
            self.angle = -self.angle
        self.x = max(POND.left + margin, min(POND.right  - margin, nx))
        self.y = max(POND.top  + margin, min(POND.bottom - margin, ny))

    def draw(self, surf: pygame.Surface, now: float, font_sm) -> None:
        ix, iy = int(self.x), int(self.y)
        if self.warning:
            flash_hz = 3.0 + self.warn_progress(now) * 6.0
            elapsed  = now - self.warn_start
            col = FISH_WARN if int(elapsed * flash_hz) % 2 == 0 else FISH_WARN2
        else:
            col = FISH_NORM
        ta = self.angle + math.pi
        tx = self.x + math.cos(ta) * FISH_R
        ty = self.y + math.sin(ta) * FISH_R
        p1 = (int(tx + math.cos(ta + 0.65) * FISH_R * 0.9),
              int(ty + math.sin(ta + 0.65) * FISH_R * 0.9))
        p2 = (int(tx + math.cos(ta - 0.65) * FISH_R * 0.9),
              int(ty + math.sin(ta - 0.65) * FISH_R * 0.9))
        pygame.draw.polygon(surf, col, [(int(tx), int(ty)), p1, p2])
        pygame.draw.circle(surf, col, (ix, iy), FISH_R)
        ex = int(self.x + math.cos(self.angle) * FISH_R * 0.5)
        ey = int(self.y + math.sin(self.angle) * FISH_R * 0.5)
        pygame.draw.circle(surf, (18, 13, 8), (ex, ey), 2)
        if self.warning:
            ring_r = int(FISH_R * 2.4 * (1.0 - self.warn_progress(now)) + FISH_R * 0.6)
            pygame.draw.circle(surf, FISH_WARN, (ix, iy), ring_r, 2)
            bang = font_sm.render("!", True, FISH_WARN)
            surf.blit(bang, (ix - bang.get_width() // 2, iy - FISH_R - 20))


# ── Drawing helpers ────────────────────────────────────────────────────────────

def _draw_pond(surf: pygame.Surface, now: float) -> None:
    pygame.draw.rect(surf, POND_MID, POND)
    offset = (now * 18) % 28
    for i in range(int(POND.height / 28) + 2):
        y = int(POND.top + i * 28 + offset)
        if POND.top < y < POND.bottom:
            pygame.draw.line(surf, POND_WAVE, (POND.left + 8, y), (POND.right - 8, y), 1)
    pygame.draw.rect(surf, POND_EDGE, POND, 3)


def _draw_cursor(surf: pygame.Surface, cx: float, cy: float, now: float) -> None:
    pulse = 0.5 + 0.5 * math.sin(now * 6)
    r = int(CURSOR_R + pulse * 2)
    ix, iy = int(cx), int(cy)
    pygame.draw.circle(surf, CURSOR_RIM, (ix, iy), r + 3, 2)
    pygame.draw.circle(surf, CURSOR_COL, (ix, iy), r,     2)
    pygame.draw.line(surf, CURSOR_COL, (ix - 7, iy), (ix + 7, iy), 1)
    pygame.draw.line(surf, CURSOR_COL, (ix, iy - 7), (ix, iy + 7), 1)


def _draw_hud(surf: pygame.Surface, font_md, font_sm,
              collected: int, time_left: float) -> None:
    bar_w, bar_h = 420, 22
    bx = _SW // 2 - bar_w // 2
    by = POND.bottom + 18
    ratio   = max(0.0, time_left / TIME_LIMIT)
    bar_col = GREEN if ratio > 0.4 else (ORANGE if ratio > 0.2 else RED_COL)
    pygame.draw.rect(surf, (45, 40, 35), (bx, by, bar_w, bar_h), border_radius=6)
    pygame.draw.rect(surf, bar_col,     (bx, by, int(bar_w * ratio), bar_h), border_radius=6)
    pygame.draw.rect(surf, GREY,        (bx, by, bar_w, bar_h), 2, border_radius=6)
    t_txt = font_sm.render(f"{max(0.0, time_left):.1f}s", True, WHITE)
    surf.blit(t_txt, (_SW // 2 - t_txt.get_width() // 2, by + bar_h + 5))
    fc   = font_md.render(f"Fish caught: {collected} / {WIN_FISH}", True, WHITE)
    hint = font_sm.render("WASD to move  ·  catch 5 fish in 10 seconds", True, GREY)
    surf.blit(fc,   (POND.left, POND.top - 44))
    surf.blit(hint, (_SW // 2 - hint.get_width() // 2, POND.top - 44))


def _show_result(surf: pygame.Surface, font_lg, font_md, won: bool, collected: int) -> None:
    overlay = pygame.Surface((_SW, _SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surf.blit(overlay, (0, 0))
    col  = GREEN if won else RED_COL
    big  = font_lg.render("YOU WIN!" if won else "TIME'S UP!", True, col)
    sub  = font_md.render(f"Fish caught: {collected} / {WIN_FISH}", True, WHITE)
    hint = font_md.render("Press any key to continue", True, GREY)
    surf.blit(big,  (_SW // 2 - big.get_width()  // 2, _SH // 2 - 90))
    surf.blit(sub,  (_SW // 2 - sub.get_width()  // 2, _SH // 2 - 10))
    surf.blit(hint, (_SW // 2 - hint.get_width() // 2, _SH // 2 + 50))


def _show_intro(surf: pygame.Surface, clock, font_lg, font_md, font_sm,
                title: str, subtitle: str) -> None:
    """Blocks until SPACE is pressed."""
    # Challenger title can be ~46 chars; size 44 keeps it comfortably within 1280 px.
    font_hd = pygame.font.SysFont(None, 44)
    surf.fill(BG)
    _draw_pond(surf, 0.0)
    overlay = pygame.Surface((_SW, _SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 145))
    surf.blit(overlay, (0, 0))
    entries = [
        (font_hd, title,                                             WHITE),
        (font_md, subtitle,                                          GREY),
        (font_sm, "WASD  —  move cursor",                           GREY),
        (font_sm, "Flashing fish vanish soon — catch them fast!",   ORANGE),
        (font_md, "Press SPACE to begin",                            WHITE),
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
    """Runs the fishing game. Returns (won, fish_collected)."""
    now = pygame.time.get_ticks() / 1000.0
    fish_list = [Fish(now) for _ in range(START_FISH)]
    for f in random.sample(fish_list, FISH_PER_CYCLE):
        f.start_warning(now)
    cx, cy     = float(POND.centerx), float(POND.centery)
    collected  = 0
    start_t    = now
    last_cycle = now
    result       = None
    result_shown = False

    while True:
        dt  = clock.tick(_FPS) / 1000.0
        now = pygame.time.get_ticks() / 1000.0
        time_left = TIME_LIMIT - (now - start_t)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if result_shown:
                    return collected >= WIN_FISH, collected
                if event.key == pygame.K_ESCAPE:
                    return False, collected

        if result is None:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: cy -= CURSOR_SPEED * dt
            if keys[pygame.K_s]: cy += CURSOR_SPEED * dt
            if keys[pygame.K_a]: cx -= CURSOR_SPEED * dt
            if keys[pygame.K_d]: cx += CURSOR_SPEED * dt
            cx = max(POND.left + CURSOR_R, min(POND.right  - CURSOR_R, cx))
            cy = max(POND.top  + CURSOR_R, min(POND.bottom - CURSOR_R, cy))

            for f in fish_list:
                f.update(dt)

            caught = [f for f in fish_list
                      if math.hypot(cx - f.x, cy - f.y) < CURSOR_R + FISH_R]
            for f in caught:
                fish_list.remove(f)
                collected += 1

            if now - last_cycle >= CYCLE_INTERVAL:
                last_cycle += CYCLE_INTERVAL
                expired = [f for f in fish_list
                           if f.warning and (now - f.warn_start) >= WARNING_DURATION]
                for f in expired:
                    fish_list.remove(f)
                fish_list.extend(Fish(now) for _ in expired)
                candidates = [f for f in fish_list if not f.warning]
                for f in random.sample(candidates, min(FISH_PER_CYCLE, len(candidates))):
                    f.start_warning(now)

            if collected >= WIN_FISH:
                result = True
            elif time_left <= 0:
                result = False

        screen.fill(BG)
        _draw_pond(screen, now)
        for f in fish_list:
            f.draw(screen, now, font_sm)
        _draw_cursor(screen, cx, cy, now)
        _draw_hud(screen, font_md, font_sm, collected, time_left)

        if result is not None:
            result_shown = True
            _show_result(screen, font_lg, font_md, result, collected)

        pygame.display.flip()


# ── Public integrated API ──────────────────────────────────────────────────────

def run_fishing_battle(screen, clock, font, font_big, font_title, player, boss) -> bool:
    """
    Fishing contest triggered by boss.
    Win → boss −2 HP.   Lose → player −2 HP.
    Returns True if player survives (hp > 0).
    """
    font_lg = pygame.font.SysFont(None, 72)
    font_md = pygame.font.SysFont(None, 36)
    font_sm = pygame.font.SysFont(None, 26)

    _show_intro(screen, clock, font_lg, font_md, font_sm,
                f"{boss.name.upper()} CHALLENGES YOU TO A FISHING CONTEST!",
                "Catch 5 fish in 10 seconds → deal 2 damage.  Fail → take 2 damage.")

    won, _ = _game_loop(screen, clock, font_lg, font_md, font_sm)

    if won:
        boss.take_damage(2)
        if hasattr(boss, 'lag_hp'):
            boss.lag_hp = max(boss.lag_hp - 2, 0)
    else:
        player.hp = max(0, player.hp - 2)
        player.total_damage = getattr(player, 'total_damage', 0) + 2

    return player.hp > 0


# ── Standalone entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    pygame.init()
    _screen = pygame.display.set_mode((_SW, _SH))
    pygame.display.set_caption("Fishing Minigame — Cazarog")
    _clock  = pygame.time.Clock()
    _fnt_lg = pygame.font.SysFont(None, 80)
    _fnt_md = pygame.font.SysFont(None, 38)
    _fnt_sm = pygame.font.SysFont(None, 26)

    _show_intro(_screen, _clock, _fnt_lg, _fnt_md, _fnt_sm,
                "FISHING MINIGAME",
                "Catch 5 fish in 10 seconds to win!")
    won, collected = _game_loop(_screen, _clock, _fnt_lg, _fnt_md, _fnt_sm)
    print(f"Outcome: {'win' if won else 'lose'}  |  Fish caught: {collected}")
    pygame.quit()
