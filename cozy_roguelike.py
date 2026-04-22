import pygame
import sys
import math
import random
import os

pygame.init()

SCREEN_W, SCREEN_H = 800, 600
TILE = 32
FPS = 60

# Room is exactly 25x18 tiles = 800x576 px
ROOM_COLS = 25
ROOM_ROWS = 18
ROOM_X = 0
ROOM_Y = (SCREEN_H - ROOM_ROWS * TILE) // 2  # 12px top margin

SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")

# Colors
BLACK       = (10, 8, 12)
FLOOR_COL   = (42, 36, 30)
WALL_COL    = (78, 70, 62)
WALL_EDGE   = (55, 48, 42)
PLAYER_COL  = (95, 200, 130)
HIT_COL     = (240, 240, 240)
ENEMY_COL   = (210, 75, 75)
ATTACK_COL  = (255, 210, 60)
HP_BG       = (55, 45, 45)
HP_FG       = (80, 210, 90)
UI_MUTED    = (130, 120, 110)
UI_WHITE    = (220, 210, 200)
OVERLAY_R   = (200, 60, 60)
OVERLAY_W   = (220, 210, 160)
GOLD_COL    = (255, 210, 60)
HEALTH_COL  = (70, 210, 100)
SPEED_COL   = (70, 200, 230)
ATTACK_BCOL = (240, 150, 60)
PANEL_COL   = (18, 14, 20, 210)   # RGBA for overlay panel


# ---------------------------------------------------------------------------
# Score helpers
# ---------------------------------------------------------------------------

def calculate_score(elapsed_ticks: int, damage_taken: int) -> tuple[int, int, int]:
    """Return (total, speed_bonus, survival_bonus)."""
    elapsed_secs = elapsed_ticks / FPS
    speed_bonus    = max(0, 5000 - int(elapsed_secs * 20))
    survival_bonus = max(0, 3000 - damage_taken * 500)
    return speed_bonus + survival_bonus, speed_bonus, survival_bonus


def load_highscore() -> int:
    try:
        with open(SCORE_FILE) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_highscore(score: int) -> None:
    with open(SCORE_FILE, "w") as f:
        f.write(str(score))


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    W, H = 20, 20
    BASE_SPEED = 3.0
    BOOSTED_SPEED = 5.5
    ATTACK_COOLDOWN = 20
    ATTACK_DURATION = 10
    IFRAMES = 60
    SPEED_BOOST_DURATION  = 360   # 6 s at 60 fps
    ATTACK_BOOST_DURATION = 360

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.facing = (1.0, 0.0)
        self.hp = 10
        self.max_hp = 10
        self.cooldown = 0
        self.atk_timer = 0
        self.iframes = 0
        self.attack_rect: pygame.Rect | None = None
        self.speed_timer  = 0
        self.attack_timer = 0
        self.total_damage_taken = 0   # tracks hits across the whole run

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def cx(self):
        return self.x + self.W / 2

    @property
    def cy(self):
        return self.y + self.H / 2

    @property
    def current_speed(self):
        return self.BOOSTED_SPEED if self.speed_timer > 0 else self.BASE_SPEED

    @property
    def atk_size(self):
        return 42 if self.attack_timer > 0 else 26

    @property
    def atk_cooldown(self):
        return 10 if self.attack_timer > 0 else self.ATTACK_COOLDOWN

    def move(self, dx, dy, walls):
        if dx or dy:
            length = math.hypot(dx, dy)
            self.facing = (dx / length, dy / length)

        spd = self.current_speed
        self.x += dx * spd
        for w in walls:
            if self.rect.colliderect(w):
                self.x = w.right if dx < 0 else w.left - self.W
        self.y += dy * spd
        for w in walls:
            if self.rect.colliderect(w):
                self.y = w.bottom if dy < 0 else w.top - self.H

    def attack(self):
        if self.cooldown == 0:
            self.cooldown = self.atk_cooldown
            self.atk_timer = self.ATTACK_DURATION

    def take_damage(self, amount):
        if self.iframes == 0:
            self.hp -= amount
            self.total_damage_taken += amount
            self.iframes = self.IFRAMES

    def apply_item(self, kind):
        if kind == 'health':
            self.hp = min(self.max_hp, self.hp + 4)
        elif kind == 'speed':
            self.speed_timer = self.SPEED_BOOST_DURATION
        elif kind == 'attack':
            self.attack_timer = self.ATTACK_BOOST_DURATION

    def update(self):
        if self.cooldown:
            self.cooldown -= 1
        if self.iframes:
            self.iframes -= 1
        if self.speed_timer:
            self.speed_timer -= 1
        if self.attack_timer:
            self.attack_timer -= 1

        if self.atk_timer:
            self.atk_timer -= 1
            half = self.atk_size // 2
            fx, fy = self.facing
            ax = self.cx + fx * (half + 13) - half
            ay = self.cy + fy * (half + 13) - half
            self.attack_rect = pygame.Rect(int(ax), int(ay), self.atk_size, self.atk_size)
        else:
            self.attack_rect = None

    def draw(self, surf):
        if self.attack_timer:
            pygame.draw.rect(surf, ATTACK_BCOL, self.rect.inflate(8, 8), 2)
        if self.speed_timer:
            pygame.draw.rect(surf, SPEED_COL, self.rect.inflate(4, 4), 2)

        flashing = self.iframes and (self.iframes // 4) % 2 == 0
        body_col = HIT_COL if flashing else PLAYER_COL
        pygame.draw.rect(surf, body_col, self.rect)

        fx, fy = self.facing
        length = math.hypot(fx, fy)
        if length:
            fx /= length
            fy /= length
        dot = (int(self.cx + fx * 7), int(self.cy + fy * 7))
        pygame.draw.circle(surf, (30, 30, 30), dot, 3)

        if self.attack_rect and self.atk_timer:
            flash_col = ATTACK_BCOL if self.attack_timer else ATTACK_COL
            alpha = int(200 * self.atk_timer / self.ATTACK_DURATION)
            s = pygame.Surface((self.attack_rect.w, self.attack_rect.h), pygame.SRCALPHA)
            s.fill((*flash_col, alpha))
            surf.blit(s, self.attack_rect.topleft)
            pygame.draw.rect(surf, flash_col, self.attack_rect, 2)


# ---------------------------------------------------------------------------
# Enemy
# ---------------------------------------------------------------------------

class Enemy:
    W, H = 18, 18
    SPEED = 0.9
    AGGRO_RANGE = 320
    IFRAMES = 18

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.hp = 3
        self.max_hp = 3
        self.alive = True
        self.iframes = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def cx(self):
        return self.x + self.W / 2

    @property
    def cy(self):
        return self.y + self.H / 2

    def take_damage(self, amount):
        if not self.iframes:
            self.hp -= amount
            self.iframes = self.IFRAMES
            if self.hp <= 0:
                self.alive = False

    def update(self, player: Player, walls):
        if self.iframes:
            self.iframes -= 1

        dx = player.cx - self.cx
        dy = player.cy - self.cy
        dist = math.hypot(dx, dy)

        if 0 < dist < self.AGGRO_RANGE:
            dx /= dist
            dy /= dist
            self.x += dx * self.SPEED
            for w in walls:
                if self.rect.colliderect(w):
                    self.x = w.right if dx < 0 else w.left - self.W
            self.y += dy * self.SPEED
            for w in walls:
                if self.rect.colliderect(w):
                    self.y = w.bottom if dy < 0 else w.top - self.H

        if self.rect.colliderect(player.rect):
            player.take_damage(1)

    def draw(self, surf):
        flashing = self.iframes and (self.iframes // 3) % 2 == 0
        col = HIT_COL if flashing else ENEMY_COL
        pygame.draw.rect(surf, col, self.rect)

        bx, by = int(self.x), int(self.y) - 7
        pygame.draw.rect(surf, HP_BG, (bx, by, self.W, 4))
        fill = max(0, int(self.W * self.hp / self.max_hp))
        if fill:
            pygame.draw.rect(surf, HP_FG, (bx, by, fill, 4))


# ---------------------------------------------------------------------------
# Item (health pickup + powerups)
# ---------------------------------------------------------------------------

_ITEM_META = {
    'health': (HEALTH_COL,  (40, 160, 70)),
    'speed':  (SPEED_COL,   (40, 150, 180)),
    'attack': (ATTACK_BCOL, (190, 100, 30)),
}


class Item:
    W, H = 14, 14

    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def draw(self, surf, tick):
        bob = int(math.sin(tick * 0.07 + self.x * 0.05) * 2)
        r = pygame.Rect(self.x, self.y + bob, self.W, self.H)
        col, border = _ITEM_META[self.kind]
        pygame.draw.rect(surf, col, r)
        pygame.draw.rect(surf, border, r, 1)

        cx, cy = r.centerx, r.centery
        sc = tuple(min(c + 80, 255) for c in col)

        if self.kind == 'health':
            pygame.draw.line(surf, sc, (cx, cy - 4), (cx, cy + 4), 2)
            pygame.draw.line(surf, sc, (cx - 4, cy), (cx + 4, cy), 2)
        elif self.kind == 'speed':
            for ox in (-2, 2):
                pygame.draw.line(surf, sc, (cx + ox - 2, cy - 3), (cx + ox + 2, cy), 1)
                pygame.draw.line(surf, sc, (cx + ox + 2, cy), (cx + ox - 2, cy + 3), 1)
        elif self.kind == 'attack':
            pygame.draw.line(surf, sc, (cx - 3, cy - 3), (cx + 3, cy + 3), 2)
            pygame.draw.line(surf, sc, (cx + 3, cy - 3), (cx - 3, cy + 3), 2)


# ---------------------------------------------------------------------------
# Room
# ---------------------------------------------------------------------------

def build_walls():
    walls = []
    for col in range(ROOM_COLS):
        for row in range(ROOM_ROWS):
            if col == 0 or col == ROOM_COLS - 1 or row == 0 or row == ROOM_ROWS - 1:
                walls.append(pygame.Rect(
                    ROOM_X + col * TILE,
                    ROOM_Y + row * TILE,
                    TILE, TILE,
                ))
    return walls


def draw_room(surf, walls):
    floor = pygame.Rect(
        ROOM_X + TILE, ROOM_Y + TILE,
        (ROOM_COLS - 2) * TILE, (ROOM_ROWS - 2) * TILE,
    )
    pygame.draw.rect(surf, FLOOR_COL, floor)

    for col in range(1, ROOM_COLS - 1):
        x = ROOM_X + col * TILE
        pygame.draw.line(surf, (48, 42, 36), (x, ROOM_Y + TILE), (x, ROOM_Y + (ROOM_ROWS - 1) * TILE))
    for row in range(1, ROOM_ROWS - 1):
        y = ROOM_Y + row * TILE
        pygame.draw.line(surf, (48, 42, 36), (ROOM_X + TILE, y), (ROOM_X + (ROOM_COLS - 1) * TILE, y))

    for w in walls:
        pygame.draw.rect(surf, WALL_COL, w)
        pygame.draw.rect(surf, WALL_EDGE, w, 1)


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

def _hbar(surf, x, y, w, h, fill_frac, bg, fg, border=None):
    pygame.draw.rect(surf, bg, (x, y, w, h))
    fw = max(0, int(w * fill_frac))
    if fw:
        pygame.draw.rect(surf, fg, (x, y, fw, h))
    if border:
        pygame.draw.rect(surf, border, (x, y, w, h), 1)


def draw_hud(surf, font, player: Player, enemies, elapsed_ticks: int, highscore: int):
    bx, by, bw, bh = 10, 10, 120, 14

    # HP bar
    _hbar(surf, bx, by, bw, bh, player.hp / player.max_hp, HP_BG, HP_FG, UI_WHITE)
    surf.blit(font.render(f"HP {player.hp}/{player.max_hp}", True, UI_WHITE), (bx + 2, by + 1))

    surf.blit(font.render(f"Enemies: {len(enemies)}", True, UI_MUTED), (bx, by + 18))

    # Active powerup bars
    py = by + 36
    for label, timer, duration, col in [
        ("SPEED",  player.speed_timer,  Player.SPEED_BOOST_DURATION,  SPEED_COL),
        ("ATTACK", player.attack_timer, Player.ATTACK_BOOST_DURATION, ATTACK_BCOL),
    ]:
        if timer > 0:
            _hbar(surf, bx, py, bw, bh, timer / duration, HP_BG, col, col)
            surf.blit(font.render(f"{label}  {timer/FPS:.1f}s", True, col), (bx + 2, py + 1))
            py += 18

    # Timer (top-right)
    secs = elapsed_ticks / FPS
    timer_txt = font.render(f"{secs:.1f}s", True, UI_WHITE)
    surf.blit(timer_txt, (SCREEN_W - timer_txt.get_width() - 10, 10))

    # Best (top-right, below timer)
    if highscore > 0:
        best_txt = font.render(f"Best: {highscore}", True, UI_MUTED)
        surf.blit(best_txt, (SCREEN_W - best_txt.get_width() - 10, 26))

    controls = font.render("WASD move   SPACE attack   R restart", True, UI_MUTED)
    surf.blit(controls, (SCREEN_W // 2 - controls.get_width() // 2, SCREEN_H - 22))


def draw_end_panel(surf, font, font_big, title, title_col,
                   elapsed_ticks, damage_taken, score, speed_bonus,
                   survival_bonus, highscore, is_new_best):
    """Semi-transparent centred panel shown on win / game-over."""
    pw, ph = 300, 230
    px = (SCREEN_W - pw) // 2
    py = (SCREEN_H - ph) // 2

    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill(PANEL_COL)
    surf.blit(panel, (px, py))
    pygame.draw.rect(surf, UI_MUTED, (px, py, pw, ph), 1)

    cx = px + pw // 2
    lh = 20   # line height

    def row(text, y, col=UI_WHITE, f=None):
        t = (f or font).render(text, True, col)
        surf.blit(t, (cx - t.get_width() // 2, y))

    def row_lr(left, right, y, lc=UI_MUTED, rc=UI_WHITE):
        lt = font.render(left, True, lc)
        rt = font.render(right, True, rc)
        surf.blit(lt, (px + 16, y))
        surf.blit(rt, (px + pw - rt.get_width() - 16, y))

    y = py + 12
    row(title, y, title_col, font_big);  y += 30

    secs = elapsed_ticks / FPS
    row_lr("Time:",          f"{secs:.1f}s",     y);  y += lh
    row_lr("Speed bonus:",   f"+{speed_bonus}",  y, rc=SPEED_COL);  y += lh
    row_lr("Damage taken:",  str(damage_taken),  y);  y += lh
    row_lr("Survival bonus:", f"+{survival_bonus}", y, rc=HEALTH_COL);  y += lh

    # Divider
    pygame.draw.line(surf, UI_MUTED, (px + 16, y + 4), (px + pw - 16, y + 4))
    y += 12

    score_col = GOLD_COL if is_new_best else UI_WHITE
    row_lr("SCORE:", str(score), y, rc=score_col);  y += lh + 4

    if is_new_best:
        row("NEW BEST!", y, GOLD_COL);  y += lh
    elif highscore > 0:
        row_lr("Best:", str(highscore), y, rc=UI_MUTED);  y += lh

    y = py + ph - 22
    row("Press R to play again", y, UI_MUTED)


# ---------------------------------------------------------------------------
# Spawning
# ---------------------------------------------------------------------------

def spawn_enemies():
    margin = 2 * TILE + 10
    positions = [
        (ROOM_X + margin,                    ROOM_Y + margin),
        (ROOM_X + (ROOM_COLS - 3) * TILE,    ROOM_Y + margin),
        (ROOM_X + margin,                    ROOM_Y + (ROOM_ROWS - 3) * TILE),
        (ROOM_X + (ROOM_COLS - 3) * TILE,    ROOM_Y + (ROOM_ROWS - 3) * TILE),
        (ROOM_X + ROOM_COLS * TILE // 2 - 9, ROOM_Y + margin + TILE),
    ]
    return [Enemy(x, y) for x, y in positions]


def spawn_items():
    inner_x1 = ROOM_X + 2 * TILE
    inner_x2 = ROOM_X + (ROOM_COLS - 2) * TILE - Item.W
    inner_y1 = ROOM_Y + 2 * TILE
    inner_y2 = ROOM_Y + (ROOM_ROWS - 2) * TILE - Item.H
    centre_x = ROOM_X + ROOM_COLS * TILE // 2
    centre_y = ROOM_Y + ROOM_ROWS * TILE // 2

    items: list[Item] = []
    for kind, count in [('health', 3), ('speed', 2), ('attack', 2)]:
        placed = 0
        for _ in range(300):
            if placed == count:
                break
            x = random.randint(inner_x1, inner_x2)
            y = random.randint(inner_y1, inner_y2)
            if math.hypot(x - centre_x, y - centre_y) < 90:
                continue
            if any(math.hypot(x - it.x, y - it.y) < 36 for it in items):
                continue
            items.append(Item(x, y, kind))
            placed += 1
    return items


def new_game():
    walls = build_walls()
    cx = ROOM_X + ROOM_COLS * TILE // 2 - Player.W // 2
    cy = ROOM_Y + ROOM_ROWS * TILE // 2 - Player.H // 2
    player = Player(cx, cy)
    return walls, player, spawn_enemies(), spawn_items()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Cozy Roguelike")
    clock = pygame.time.Clock()
    font     = pygame.font.SysFont(None, 22)
    font_big = pygame.font.SysFont(None, 40)

    highscore = load_highscore()
    walls, player, enemies, items = new_game()

    game_over = False
    won       = False
    tick      = 0          # increments only while the game is active
    final_score    = 0
    speed_bonus    = 0
    survival_bonus = 0
    is_new_best    = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not won:
                    player.attack()
                if event.key == pygame.K_r:
                    walls, player, enemies, items = new_game()
                    game_over = False
                    won       = False
                    tick      = 0
                    final_score = speed_bonus = survival_bonus = 0
                    is_new_best = False

        if not game_over and not won:
            keys = pygame.key.get_pressed()
            dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            dy = (keys[pygame.K_s] or keys[pygame.K_DOWN])  - (keys[pygame.K_w] or keys[pygame.K_UP])

            player.move(dx, dy, walls)
            player.update()

            prect = player.rect.inflate(4, 4)
            for item in items[:]:
                if prect.colliderect(item.rect):
                    player.apply_item(item.kind)
                    items.remove(item)

            for e in enemies:
                e.update(player, walls)
                if player.attack_rect and e.alive:
                    if player.attack_rect.colliderect(e.rect):
                        e.take_damage(1)

            enemies = [e for e in enemies if e.alive]

            if player.hp <= 0:
                game_over = True
                final_score, speed_bonus, survival_bonus = calculate_score(
                    tick, player.total_damage_taken
                )
            elif not enemies:
                won = True
                final_score, speed_bonus, survival_bonus = calculate_score(
                    tick, player.total_damage_taken
                )
                if final_score > highscore:
                    highscore = final_score
                    save_highscore(highscore)
                    is_new_best = True

            tick += 1

        # --- Draw ---
        screen.fill(BLACK)
        draw_room(screen, walls)

        for item in items:
            item.draw(screen, tick)
        for e in enemies:
            e.draw(screen)
        player.draw(screen)

        draw_hud(screen, font, player, enemies, tick, highscore)

        if won:
            draw_end_panel(
                screen, font, font_big,
                "YOU WIN!", OVERLAY_W,
                tick, player.total_damage_taken,
                final_score, speed_bonus, survival_bonus,
                highscore, is_new_best,
            )
        elif game_over:
            draw_end_panel(
                screen, font, font_big,
                "GAME OVER", OVERLAY_R,
                tick, player.total_damage_taken,
                final_score, speed_bonus, survival_bonus,
                highscore, False,
            )

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
