import pygame
import os

# ── Screen / timing ──────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 720
TILE        = 32
FPS         = 60
TOTAL_ROOMS = 9

# ── Room geometry ─────────────────────────────────────────────────────────────
ROOM_COLS = 40
ROOM_ROWS = 22
ROOM_X    = 0
ROOM_Y    = (SCREEN_H - ROOM_ROWS * TILE) // 2

# Playable inner area (used for boundary checks on projectiles / bombs)
INNER_RECT = pygame.Rect(
    ROOM_X + TILE,
    ROOM_Y + TILE,
    (ROOM_COLS - 2) * TILE,
    (ROOM_ROWS - 2) * TILE,
)

# ── Persistence ───────────────────────────────────────────────────────────────
SCORES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")

# ── Gameplay timers (frames) ──────────────────────────────────────────────────
ARROW_RECHARGE  = 360   # 6 s
BOMB_RECHARGE   = 600   # 10 s
INVULN_DURATION = 210   # 3.5 s

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK          = (10,  8,  12)
FLOOR_COL      = (42,  36, 30)
WALL_COL       = (78,  70, 62)
WALL_EDGE      = (55,  48, 42)
PLAYER_COL     = (95,  200, 130)
HIT_COL        = (240, 240, 240)
ENEMY_COL      = (210, 75,  75)
ATTACK_COL     = (255, 210, 60)
HP_BG          = (55,  45,  45)
HP_FG          = (80,  210, 90)
UI_MUTED       = (130, 120, 110)
UI_WHITE       = (220, 210, 200)
OVERLAY_R      = (200, 60,  60)
OVERLAY_W      = (220, 210, 160)
GOLD_COL       = (255, 210, 60)
SILVER_COL     = (180, 180, 195)
BRONZE_COL     = (200, 130, 80)
HEALTH_COL     = (70,  210, 100)
SPEED_COL      = (70,  200, 230)
ATTACK_BCOL    = (240, 150, 60)
INVULN_COL     = (180, 190, 255)
PLAYER_ARROW_C = (190, 245, 80)
BOMB_COL       = (255, 150, 30)
RANGED_E_COL   = (200, 155, 40)
RANGED_E_ORB   = (255, 210, 90)
PORTAL_COL     = (140, 60,  215)
PORTAL_GLOW    = (210, 150, 255)
FIREBALL_COL   = (255, 110, 20)
MISSILE_COL    = (160, 225, 255)
BOSS_COL1      = (120, 40,  170)
BOSS_COL2      = (200, 45,  45)
BOSS_NAME_C    = (210, 185, 165)
PANEL_COL      = (18,  14,  20, 215)

# ── Game states ───────────────────────────────────────────────────────────────
MENU        = 'menu'
CHAR_SELECT = 'char_select'
PLAYING     = 'playing'
PAUSED      = 'paused'
NAME_ENTRY  = 'name_entry'
SCORES      = 'scores'

# ── Fighter definitions ───────────────────────────────────────────────────────
FIGHTERS = [
    {
        'name':           'Pistachio',
        'color':          (95, 200, 130),
        'hp':             10,
        'melee_dmg':      1,
        'atk_size_base':  36,
        'atk_size_boost': 54,
        'arrow_dmg':      2,
        'bomb_dmg':       8,
        'traits': ['Balanced all-rounder', 'No strengths or weaknesses'],
    },
    {
        'name':           'Cashew',
        'color':          (215, 195, 155),
        'hp':             14,
        'melee_dmg':      2,
        'atk_size_base':  46,
        'atk_size_boost': 66,
        'arrow_dmg':      1,
        'bomb_dmg':       5,
        'traits': ['High HP & melee power', 'Reduced arrow & bomb damage'],
    },
    {
        'name':           'Almond',
        'color':          (190, 162, 118),
        'hp':             8,
        'melee_dmg':      1,
        'atk_size_base':  26,
        'atk_size_boost': 40,
        'arrow_dmg':      3,
        'bomb_dmg':       13,
        'traits': ['High arrow & bomb damage', 'Lower HP & melee power'],
    },
]

# ── Per-room enemy config: {room_num: (count, hp, speed)} ────────────────────
# Rooms 3 (Bambie), 6 (Salomon), 9 (Cazarog) are boss rooms — not in this table.
ROOM_CONFIG = {
    1: (5,  3, 0.90),
    2: (7,  4, 1.00),
    4: (8,  4, 1.05),
    5: (9,  5, 1.10),
    7: (9,  5, 1.15),
    8: (10, 6, 1.20),
}
