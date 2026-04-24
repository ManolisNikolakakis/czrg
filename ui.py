import pygame
import math

from constants import (
    SCREEN_W, SCREEN_H, FPS, TOTAL_ROOMS,
    ROOM_X, ROOM_Y, ROOM_COLS, ROOM_ROWS, TILE, BLACK,
    ARROW_RECHARGE, BOMB_RECHARGE, INVULN_DURATION,
    HP_BG, HP_FG, UI_MUTED, UI_WHITE,
    GOLD_COL, SILVER_COL, BRONZE_COL,
    OVERLAY_R, OVERLAY_W,
    SPEED_COL, ATTACK_BCOL, INVULN_COL,
    PLAYER_ARROW_C, BOMB_COL, PORTAL_GLOW,
    BOSS_NAME_C, PANEL_COL,
)


# ── Name entry ────────────────────────────────────────────────────────────────

class NameEntry:
    MAX_LEN = 20

    def __init__(self, score):
        self.score = score
        self.text  = ""

    @property
    def name(self):
        return self.text.strip() or "PLAYER"

    def handle(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return True
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif len(self.text) < self.MAX_LEN and event.unicode:
            ch = event.unicode.upper()
            if ch.isalnum() or ch == ' ':
                self.text += ch
        return False


# ── Shared helpers ────────────────────────────────────────────────────────────

def _hbar(surf, x, y, w, h, frac, bg, fg, border=None):
    pygame.draw.rect(surf, bg, (x, y, w, h))
    fw = max(0, int(w * frac))
    if fw:
        pygame.draw.rect(surf, fg, (x, y, fw, h))
    if border:
        pygame.draw.rect(surf, border, (x, y, w, h), 1)


def draw_bg(surf):
    """Very faint dungeon silhouette used by menu / overlay screens."""
    surf.fill(BLACK)
    pygame.draw.rect(surf, (22, 18, 14),
        pygame.Rect(ROOM_X + TILE, ROOM_Y + TILE,
                    (ROOM_COLS - 2) * TILE, (ROOM_ROWS - 2) * TILE))
    for col in range(ROOM_COLS):
        for row in range(ROOM_ROWS):
            if col == 0 or col == ROOM_COLS - 1 or row == 0 or row == ROOM_ROWS - 1:
                pygame.draw.rect(surf, (32, 27, 22),
                    (ROOM_X + col * TILE, ROOM_Y + row * TILE, TILE, TILE))


# ── In-game HUD ───────────────────────────────────────────────────────────────

def draw_hud(surf, font, player, enemies, elapsed_ticks, best_score,
             room_num, portal, boss):
    # ── Left: HP / buffs / portal hint ────────────────────────────────────────
    bx, by, bw, bh = 10, 10, 120, 14
    _hbar(surf, bx, by, bw, bh, player.hp / player.max_hp, HP_BG, HP_FG, UI_WHITE)
    surf.blit(font.render(f"HP {player.hp}/{player.max_hp}", True, UI_WHITE), (bx + 2, by + 1))

    elabel = f"Enemies: {len(enemies)}" + ("  +BOSS" if boss and boss.alive else "")
    surf.blit(font.render(elabel, True, UI_MUTED), (bx, by + 18))

    py = by + 36
    for label, timer, dur, col in [
        ("SPEED",  player.speed_timer,  player.SPEED_DUR,  SPEED_COL),
        ("ATTACK", player.attack_timer, player.ATTACK_DUR, ATTACK_BCOL),
        ("INVULN", player.invuln_timer, INVULN_DURATION,   INVULN_COL),
    ]:
        if timer:
            _hbar(surf, bx, py, bw, bh, timer / dur, HP_BG, col, col)
            surf.blit(font.render(label, True, col), (bx + 2, py + 1))
            py += 18

    if portal:
        surf.blit(font.render("Enter the portal ›", True, PORTAL_GLOW), (bx, py))

    # ── Right: timer / best / arrows / bomb ───────────────────────────────────
    rx = SCREEN_W - 10

    t = font.render(f"{elapsed_ticks / FPS:.1f}s", True, UI_WHITE)
    surf.blit(t, (rx - t.get_width(), 10))
    if best_score:
        t = font.render(f"Best: {best_score:,}", True, UI_MUTED)
        surf.blit(t, (rx - t.get_width(), 26))

    KEY_COL = (95, 88, 78)

    # Arrows
    AY = 44
    surf.blit(font.render("E", True, KEY_COL), (rx - 62, AY + 1))
    for i in range(player.MAX_ARROWS):
        ready = i < player.arrows
        col   = PLAYER_ARROW_C if ready else (50, 58, 44)
        ix    = rx - 14 - (player.MAX_ARROWS - 1 - i) * 17
        iy    = AY
        pygame.draw.polygon(surf, col, [(ix + 10, iy + 4), (ix + 3, iy), (ix + 3, iy + 8)])
        pygame.draw.line(surf, col, (ix - 2, iy + 4), (ix + 7, iy + 4), 2)
    if player.arrows < player.MAX_ARROWS:
        frac = 1.0 - player.arrow_timer / ARROW_RECHARGE
        _hbar(surf, rx - 54, AY + 12, 46, 3, frac, (35, 44, 30), PLAYER_ARROW_C)

    # Bomb
    BY = 62
    surf.blit(font.render("Q", True, KEY_COL), (rx - 62, BY + 1))
    bready = player.bombs > 0
    bcol = BOMB_COL if bready else (65, 50, 38)
    ic   = (255, 245, 160) if bready else (110, 80, 50)
    pygame.draw.circle(surf, bcol, (rx - 26, BY + 5), 6)
    pygame.draw.circle(surf, ic,   (rx - 26, BY + 5), 3)
    if bready:
        pygame.draw.line(surf, (160, 110, 20), (rx - 26, BY - 1), (rx - 21, BY - 6), 2)
    else:
        frac = 1.0 - player.bomb_timer / BOMB_RECHARGE
        _hbar(surf, rx - 54, BY + 12, 46, 3, frac, (50, 40, 30), BOMB_COL)

    # Room pips (top-centre)
    pip_r, pip_gap = 6, 18
    total_w = TOTAL_ROOMS * pip_r * 2 + (TOTAL_ROOMS - 1) * (pip_gap - pip_r * 2)
    px0     = SCREEN_W // 2 - total_w // 2
    for i in range(TOTAL_ROOMS):
        px  = px0 + i * pip_gap
        col = GOLD_COL if i < room_num else (55, 48, 40)
        brd = UI_WHITE  if i == room_num - 1 else UI_MUTED
        pygame.draw.circle(surf, col, (px, 16), pip_r)
        pygame.draw.circle(surf, brd, (px, 16), pip_r, 1)
    lbl = f"Room {room_num}/{TOTAL_ROOMS}"
    surf.blit(font.render(lbl, True, UI_MUTED),
              (SCREEN_W // 2 - font.size(lbl)[0] // 2, 26))

    t = font.render("WASD move  SPACE attack  E arrow  Q bomb  ESC menu", True, UI_MUTED)
    surf.blit(t, (SCREEN_W // 2 - t.get_width() // 2, SCREEN_H - 22))


def draw_boss_bar(surf, font, font_big, boss):
    if not boss or not boss.alive:
        return
    BW, BH = 560, 22
    bx = (SCREEN_W - BW) // 2
    by = SCREEN_H - 58
    nc = (220, 80, 80) if boss.phase2 else BOSS_NAME_C
    nt = font_big.render("CAZAROG", True, nc)
    surf.blit(nt, (SCREEN_W // 2 - nt.get_width() // 2, by - 30))
    if boss.phase2:
        et = font.render("— ENRAGED —", True, (200, 70, 50))
        surf.blit(et, (SCREEN_W // 2 - et.get_width() // 2, by - 12))
    pygame.draw.rect(surf, (22, 10, 10), (bx, by, BW, BH))
    lag_fill = max(0, int(BW * boss.lag_hp / boss.MAX_HP))
    if lag_fill:
        pygame.draw.rect(surf, (180, 140, 30), (bx, by, lag_fill, BH))
    fill = max(0, int(BW * boss.hp / boss.MAX_HP))
    if fill:
        pygame.draw.rect(surf, (160, 28, 28), (bx, by, fill, BH))
        pygame.draw.rect(surf, (210, 60, 60), (bx, by, fill, BH // 3))
    pygame.draw.line(surf, (120, 80, 80), (bx + BW // 2, by), (bx + BW // 2, by + BH), 1)
    pygame.draw.rect(surf, (100, 60, 60), (bx, by, BW, BH), 1)
    ht = font.render(f"{max(0, boss.hp)} / {boss.MAX_HP}", True, (190, 160, 150))
    surf.blit(ht, (SCREEN_W // 2 - ht.get_width() // 2, by + 3))


def draw_end_panel(surf, font, font_big, title, title_col,
                   elapsed_ticks, damage_taken, score,
                   speed_bonus, survival_bonus, best_score):
    pw, ph = 300, 218
    px = (SCREEN_W - pw) // 2
    py = (SCREEN_H - ph) // 2
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill(PANEL_COL)
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, UI_MUTED, (px, py, pw, ph), 1)
    cx, lh = px + pw // 2, 20

    def row(text, y, col=UI_WHITE, f=None):
        t = (f or font).render(text, True, col)
        surf.blit(t, (cx - t.get_width() // 2, y))

    def row_lr(left, right, y, lc=UI_MUTED, rc=UI_WHITE):
        surf.blit(font.render(left, True, lc), (px + 16, y))
        rt = font.render(right, True, rc)
        surf.blit(rt, (px + pw - rt.get_width() - 16, y))

    y = py + 12
    row(title, y, title_col, font_big);                                      y += 30
    row_lr("Time:",           f"{elapsed_ticks / FPS:.1f}s",  y);           y += lh
    row_lr("Speed bonus:",    f"+{speed_bonus:,}",     y, rc=SPEED_COL);    y += lh
    row_lr("Damage taken:",   str(damage_taken),               y);           y += lh
    row_lr("Survival bonus:", f"+{survival_bonus:,}", y, rc=(80, 210, 90)); y += lh
    pygame.draw.line(surf, UI_MUTED, (px + 16, y + 4), (px + pw - 16, y + 4))
    y += 12
    row_lr("SCORE:", f"{score:,}", y, rc=GOLD_COL);  y += lh + 4
    if best_score:
        row_lr("Best:", f"{best_score:,}", y, rc=UI_MUTED)
    row("R restart   ESC menu", py + ph - 20, UI_MUTED)


def draw_room_banner(surf, font_big, text, timer):
    if timer <= 0:
        return
    fade = 255 if timer > 30 else int(255 * timer / 30)
    col  = tuple(int(c * fade / 255) for c in UI_WHITE)
    t    = font_big.render(text, True, col)
    pad  = 14
    bw, bh = t.get_width() + pad * 2, t.get_height() + pad
    bx   = SCREEN_W // 2 - bw // 2
    by   = SCREEN_H // 2 - bh // 2
    bg   = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bg.fill((0, 0, 0, int(180 * fade / 255)))
    surf.blit(bg, (bx, by))
    surf.blit(t, (SCREEN_W // 2 - t.get_width() // 2, by + pad // 2))


# ── Menu screens ──────────────────────────────────────────────────────────────

def draw_menu(surf, font, font_big, font_title, sel, scores):
    draw_bg(surf)
    cx = SCREEN_W // 2
    t = font_title.render("COZY ROGUELIKE", True, UI_WHITE)
    surf.blit(t, (cx - t.get_width() // 2, 88))
    t = font.render("a tiny dungeon adventure", True, UI_MUTED)
    surf.blit(t, (cx - t.get_width() // 2, 136))
    pygame.draw.line(surf, (55, 48, 40), (cx - 120, 158), (cx + 120, 158))
    for i, label in enumerate(("NEW GAME", "HIGH SCORES", "QUIT")):
        y      = 186 + i * 50
        active = i == sel
        t = font_big.render((">  " if active else "   ") + label,
                            True, GOLD_COL if active else UI_MUTED)
        surf.blit(t, (cx - t.get_width() // 2, y))
    if scores:
        champ = scores[0]
        t = font.render(f"Record: {champ['name']}  {champ['score']:,}", True, (85, 76, 66))
        surf.blit(t, (cx - t.get_width() // 2, SCREEN_H - 40))
    t = font.render("W/S  ↑↓  navigate     ENTER  select", True, (65, 58, 50))
    surf.blit(t, (cx - t.get_width() // 2, SCREEN_H - 22))


def draw_scores_screen(surf, font, font_big, scores, highlight_idx=-1):
    draw_bg(surf)
    cx = SCREEN_W // 2
    t  = font_big.render("HIGH SCORES", True, GOLD_COL)
    surf.blit(t, (cx - t.get_width() // 2, 16))
    if not scores:
        t = font.render("No scores yet — play a game!", True, UI_MUTED)
        surf.blit(t, (cx - t.get_width() // 2, SCREEN_H // 2 - 10))
    else:
        PW  = 520
        hx  = (SCREEN_W - PW) // 2
        hy  = 56
        NC  = hx + 50
        SC  = hx + PW
        surf.blit(font.render("#",     True, UI_MUTED), (hx, hy))
        surf.blit(font.render("NAME",  True, UI_MUTED), (NC, hy))
        sh = font.render("SCORE", True, UI_MUTED)
        surf.blit(sh, (SC - sh.get_width(), hy))
        pygame.draw.line(surf, (58, 50, 42), (hx, hy + 18), (hx + PW, hy + 18))
        for i, entry in enumerate(scores):
            ry = hy + 24 + i * 19
            if i == highlight_idx:
                pygame.draw.rect(surf, (50, 44, 34), (hx - 4, ry - 2, PW + 8, 19))
            col = (GOLD_COL   if i == 0             else
                   SILVER_COL if i == 1             else
                   BRONZE_COL if i == 2             else
                   GOLD_COL   if i == highlight_idx else UI_WHITE)
            surf.blit(font.render(f"{i + 1}.", True, col), (hx, ry))
            ns = font.render(entry['name'], True, col)
            surf.set_clip(pygame.Rect(NC, ry - 2, SC - NC - 80, 20))
            surf.blit(ns, (NC, ry))
            surf.set_clip(None)
            sc = font.render(f"{entry['score']:,}", True, col)
            surf.blit(sc, (SC - sc.get_width(), ry))
    t = font.render("ESC / ENTER  back to menu", True, (65, 58, 50))
    surf.blit(t, (cx - t.get_width() // 2, SCREEN_H - 22))


def draw_name_entry_screen(surf, font, font_big, ne, tick):
    draw_bg(surf)
    cx = SCREEN_W // 2
    t  = font_big.render("NEW RECORD!", True, GOLD_COL)
    surf.blit(t, (cx - t.get_width() // 2, 155))
    t = font.render(f"Score: {ne.score:,}", True, UI_WHITE)
    surf.blit(t, (cx - t.get_width() // 2, 198))
    t = font.render("Enter your name:", True, UI_MUTED)
    surf.blit(t, (cx - t.get_width() // 2, 222))

    BOX_W, BOX_H = 380, 38
    bx = cx - BOX_W // 2
    by = 248
    pygame.draw.rect(surf, (44, 38, 32), (bx, by, BOX_W, BOX_H))
    pygame.draw.rect(surf, GOLD_COL,     (bx, by, BOX_W, BOX_H), 1)

    cur = "|" if (tick // 18) % 2 == 0 else " "
    t   = font_big.render(ne.text + cur, True, UI_WHITE)
    iw  = BOX_W - 16
    tx  = bx + 8 if t.get_width() <= iw else bx + 8 + iw - t.get_width()
    surf.set_clip(pygame.Rect(bx + 2, by + 2, BOX_W - 4, BOX_H - 4))
    surf.blit(t, (tx, by + (BOX_H - t.get_height()) // 2))
    surf.set_clip(None)

    cc = GOLD_COL if len(ne.text) == NameEntry.MAX_LEN else UI_MUTED
    ct = font.render(f"{len(ne.text)} / {NameEntry.MAX_LEN}", True, cc)
    surf.blit(ct, (bx + BOX_W - ct.get_width(), by + BOX_H + 4))

    t = font.render("Type your name   BACKSPACE delete   ENTER confirm   ESC skip", True, UI_MUTED)
    surf.blit(t, (cx - t.get_width() // 2, by + BOX_H + 28))
