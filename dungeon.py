import pygame
import math
import random

from constants import (
    ROOM_X, ROOM_Y, ROOM_COLS, ROOM_ROWS, TILE, TOTAL_ROOMS,
    FLOOR_COL, WALL_COL, WALL_EDGE, BLACK,
    PORTAL_COL, PORTAL_GLOW,
    ROOM_CONFIG,
)
from enemies import Enemy, RangedEnemy, Boss, Salomon, Bambie
from items import Item
from player import Player


# ── Portal ────────────────────────────────────────────────────────────────────

class Portal:
    W, H = 32, 32

    def __init__(self):
        self.x = float(ROOM_X + ROOM_COLS * TILE // 2 - self.W // 2)
        self.y = float(ROOM_Y + ROOM_ROWS * TILE // 2 - self.H // 2)

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def draw(self, surf, tick):
        pulse = math.sin(tick * 0.09)
        size  = self.W + int(pulse * 5)
        ox    = (self.W - size) // 2
        r     = pygame.Rect(int(self.x) + ox, int(self.y) + ox, size, size)
        s     = pygame.Surface((size, size), pygame.SRCALPHA)
        s.fill((*PORTAL_COL, int(140 + pulse * 55)))
        surf.blit(s, r.topleft)
        pygame.draw.rect(surf, PORTAL_GLOW, r, 2)
        cx, cy = r.centerx, r.centery
        arm = size // 3
        for angle in (0, 45):
            rad = math.radians(angle)
            ex  = int(math.cos(rad) * arm)
            ey  = int(math.sin(rad) * arm)
            pygame.draw.line(surf, PORTAL_GLOW, (cx - ex, cy - ey), (cx + ex, cy + ey), 2)


# ── Room drawing ──────────────────────────────────────────────────────────────

def build_walls():
    walls = []
    for col in range(ROOM_COLS):
        for row in range(ROOM_ROWS):
            if col == 0 or col == ROOM_COLS - 1 or row == 0 or row == ROOM_ROWS - 1:
                walls.append(pygame.Rect(ROOM_X + col * TILE, ROOM_Y + row * TILE, TILE, TILE))
    return walls


def draw_room(surf, walls, room_num):
    if room_num == TOTAL_ROOMS:       # Cazarog — dark blood red
        fc, grid = (38, 28, 28), (52, 36, 36)
        wc, we   = (95, 60, 60),  (70, 42, 42)
    elif room_num == 6:               # Salomon — stone grey
        fc, grid = (46, 41, 35),  (58, 52, 44)
        wc, we   = (86, 76, 64),  (66, 57, 47)
    elif room_num == 3:               # Bambie — witch lair dark purple
        fc, grid = (28, 22, 38),  (40, 32, 54)
        wc, we   = (70, 50, 100), (52, 36, 76)
    else:
        fc, grid = FLOOR_COL,     (48, 42, 36)
        wc, we   = WALL_COL,      WALL_EDGE
    pygame.draw.rect(surf, fc,
        pygame.Rect(ROOM_X + TILE, ROOM_Y + TILE, (ROOM_COLS - 2) * TILE, (ROOM_ROWS - 2) * TILE))
    for col in range(1, ROOM_COLS - 1):
        x = ROOM_X + col * TILE
        pygame.draw.line(surf, grid, (x, ROOM_Y + TILE), (x, ROOM_Y + (ROOM_ROWS - 1) * TILE))
    for row in range(1, ROOM_ROWS - 1):
        y = ROOM_Y + row * TILE
        pygame.draw.line(surf, grid, (ROOM_X + TILE, y), (ROOM_X + (ROOM_COLS - 1) * TILE, y))
    for w in walls:
        pygame.draw.rect(surf, wc, w)
        pygame.draw.rect(surf, we, w, 1)


# ── Spawning ──────────────────────────────────────────────────────────────────

def _spawn_positions(count):
    m     = 2 * TILE + 10
    fixed = [
        (ROOM_X + m,                    ROOM_Y + m),
        (ROOM_X + (ROOM_COLS - 3) * TILE, ROOM_Y + m),
        (ROOM_X + m,                    ROOM_Y + (ROOM_ROWS - 3) * TILE),
        (ROOM_X + (ROOM_COLS - 3) * TILE, ROOM_Y + (ROOM_ROWS - 3) * TILE),
        (ROOM_X + ROOM_COLS * TILE // 2 - 9, ROOM_Y + m + TILE),
    ]
    pos  = list(fixed[:min(count, len(fixed))])
    cx0  = ROOM_X + ROOM_COLS * TILE // 2
    cy0  = ROOM_Y + ROOM_ROWS * TILE // 2
    att  = 0
    while len(pos) < count and att < 500:
        att += 1
        x = random.randint(ROOM_X + 2 * TILE, ROOM_X + (ROOM_COLS - 2) * TILE - 20)
        y = random.randint(ROOM_Y + 2 * TILE, ROOM_Y + (ROOM_ROWS - 2) * TILE - 20)
        if math.hypot(x - cx0, y - cy0) < 90:
            continue
        if any(math.hypot(x - px, y - py) < 36 for px, py in pos):
            continue
        pos.append((x, y))
    return pos


def spawn_enemies(room_num):
    count, hp, spd = ROOM_CONFIG[room_num]
    ranged_chance  = 0.25 if room_num == 1 else 0.40
    enemies = []
    for x, y in _spawn_positions(count):
        if random.random() < ranged_chance:
            enemies.append(RangedEnemy(x, y, hp=max(1, hp - 1), speed=max(0.6, spd - 0.1)))
        else:
            enemies.append(Enemy(x, y, hp=hp, speed=spd))
    return enemies


def spawn_bambie_minions():
    m = 2 * TILE + 12
    corners = [
        (ROOM_X + m,                      ROOM_Y + m),
        (ROOM_X + (ROOM_COLS - 3) * TILE, ROOM_Y + (ROOM_ROWS - 3) * TILE),
    ]
    return [RangedEnemy(x, y, hp=3, speed=1.1) for x, y in corners]


def spawn_salomon_minions():
    m = 2 * TILE + 12
    corners = [
        (ROOM_X + m,                      ROOM_Y + m),
        (ROOM_X + (ROOM_COLS - 3) * TILE, ROOM_Y + (ROOM_ROWS - 3) * TILE),
    ]
    return [
        RangedEnemy(x, y, hp=3, speed=0.85) if i % 2 == 0
        else Enemy(x, y, hp=3, speed=1.0)
        for i, (x, y) in enumerate(corners)
    ]


def spawn_boss_minions():
    m = 2 * TILE + 12
    corners = [
        (ROOM_X + m,                    ROOM_Y + m),
        (ROOM_X + (ROOM_COLS - 3) * TILE, ROOM_Y + m),
        (ROOM_X + m,                    ROOM_Y + (ROOM_ROWS - 3) * TILE),
        (ROOM_X + (ROOM_COLS - 3) * TILE, ROOM_Y + (ROOM_ROWS - 3) * TILE),
    ]
    return [
        RangedEnemy(x, y, hp=3, speed=0.9) if random.random() < 0.5
        else Enemy(x, y, hp=4, speed=1.0)
        for x, y in corners
    ]


def spawn_items():
    pool  = ['health'] * 4 + ['speed'] * 3 + ['attack'] * 3 + ['invuln'] * 2
    kinds = random.sample(pool, k=random.randint(5, 7))
    ix1 = ROOM_X + 2 * TILE
    ix2 = ROOM_X + (ROOM_COLS - 2) * TILE - Item.W
    iy1 = ROOM_Y + 2 * TILE
    iy2 = ROOM_Y + (ROOM_ROWS - 2) * TILE - Item.H
    cxr = ROOM_X + ROOM_COLS * TILE // 2
    cyr = ROOM_Y + ROOM_ROWS * TILE // 2
    items = []
    for kind in kinds:
        for _ in range(300):
            x = random.randint(ix1, ix2)
            y = random.randint(iy1, iy2)
            if math.hypot(x - cxr, y - cyr) < 90:
                continue
            if any(math.hypot(x - it.x, y - it.y) < 36 for it in items):
                continue
            items.append(Item(x, y, kind))
            break
    return items


def setup_room(room_num):
    """Returns (enemies_list, boss_or_None) for the given room."""
    if room_num == TOTAL_ROOMS:
        return [], Boss()
    if room_num == 6:
        return [], Salomon()
    if room_num == 3:
        return [], Bambie()
    return spawn_enemies(room_num), None


def new_game(fighter_name='Pistachio'):
    walls         = build_walls()
    player        = Player(fighter_name)
    enemies, boss = setup_room(1)
    return walls, player, enemies, spawn_items(), boss
