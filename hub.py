import pygame
import math
import random
import sys

from constants import (
    SCREEN_W, SCREEN_H, FPS, TILE,
    ROOM_X, ROOM_Y, ROOM_COLS, ROOM_ROWS,
    UI_WHITE, UI_MUTED, GOLD_COL, FIGHTERS,
)
from dungeon import build_walls, draw_room

_CAZAROG_COL = (120,  40, 170)
_BAMBIE_COL  = (130,  55, 190)
_SALOMON_COL = (108,  96,  84)
_PORTAL_COL  = (140,  60, 215)
_PORTAL_GLOW = (210, 150, 255)

_CAZ_SPD = 3.0
_NPC_SPD = 1.2
_CAZ_W   = 30
_CAZ_H   = 30

# Boss NPCs in the hub (not playable fighters)
_BOSS_NPC_DEFS = [
    ('Bambie',  _BAMBIE_COL,  24, 24),
    ('Salomon', _SALOMON_COL, 28, 28),
]

# Fractional positions (of inner room rect) for NPC spawns
_SPAWN_OFFSETS = [
    (0.22, 0.22), (0.44, 0.72), (0.35, 0.42),
    (0.58, 0.22), (0.52, 0.62), (0.68, 0.48),
]

_DIALOGUE = [
    "What's up, Cazarog!",
    "Did you catch the game last night, Cazarog?",
    "I wonder how many more runs before my shift ends.",
    "Being a miniboss doesn't pay what it used to.",
    "Don't look at me like that, Cazarog.",
    "I keep telling them the dungeon needs better lighting.",
    "Rough day at the office, Cazarog?",
    "Hey, good luck out there.",
    "They really should fix that portal.",
    "Another day, another hero to defeat.",
    "My therapist says I need to set better limits with heroes.",
    "Cazarog, you left the cauldron on again.",
    "The health items are getting stale, just saying.",
    "I heard the next hero is a NUT. Literally.",
    "You ever think we're the bad guys, Cazarog?",
    "I've been practising my evil laugh. Want to hear?",
    "The fireballs were on backorder again this week.",
    "Someone keeps eating my lunch in the break room.",
    "Do you know how tiring it is to wander around all day?",
    "Those earthquakes were totally worth it though.",
]

_BUBBLE_BG  = (20, 14, 28, 215)
_BUBBLE_COL = (100, 78, 130)
_PROXIMITY  = 130   # px from Cazarog centre to trigger dialogue


def _draw_bubble(surf, font, text, cx, bottom_y):
    t   = font.render(text, True, (230, 220, 210))
    pad = 7
    bw  = t.get_width()  + pad * 2
    bh  = t.get_height() + pad * 2
    bx  = max(4, min(cx - bw // 2, SCREEN_W - bw - 4))
    by  = bottom_y - bh - 8
    bg  = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bg.fill(_BUBBLE_BG)
    surf.blit(bg, (bx, by))
    pygame.draw.rect(surf, _BUBBLE_COL, (bx, by, bw, bh), 1)
    surf.blit(t, (bx + pad, by + pad))
    # Tail
    pygame.draw.polygon(surf, (20, 14, 28),
                        [(cx - 5, by + bh), (cx + 5, by + bh), (cx, by + bh + 7)])


class _Wanderer:
    def __init__(self, name, col, w, h, x, y):
        self.name     = name
        self.col      = col
        self.w        = w
        self.h        = h
        self.x        = float(x)
        self.y        = float(y)
        self.dialogue = ""          # assigned in run_hub after pool shuffle
        angle         = random.uniform(0, 2 * math.pi)
        self.vx    = math.cos(angle) * _NPC_SPD
        self.vy    = math.sin(angle) * _NPC_SPD
        self.timer = random.randint(90, 220)

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, walls):
        self.timer -= 1
        if self.timer <= 0:
            angle      = random.uniform(0, 2 * math.pi)
            self.vx    = math.cos(angle) * _NPC_SPD
            self.vy    = math.sin(angle) * _NPC_SPD
            self.timer = random.randint(90, 240)

        self.x += self.vx
        for w in walls:
            if self.rect.colliderect(w):
                self.x  -= self.vx * 2
                self.vx  = -self.vx + random.uniform(-0.2, 0.2)
                break

        self.y += self.vy
        for w in walls:
            if self.rect.colliderect(w):
                self.y  -= self.vy * 2
                self.vy  = -self.vy + random.uniform(-0.2, 0.2)
                break

    def draw(self, surf, font):
        pygame.draw.rect(surf, self.col, self.rect)
        pygame.draw.rect(surf, UI_WHITE, self.rect, 1)
        label = font.render(self.name, True, UI_WHITE)
        surf.blit(label, (self.rect.centerx - label.get_width() // 2,
                          self.rect.top - label.get_height() - 2))


def run_hub(screen, clock, font, font_big, font_title):
    """
    Hub room: player controls Cazarog (WASD), boss and fighter NPCs wander.
    Returns when Cazarog enters the portal → caller sets state = CHAR_SELECT.
    """
    walls = build_walls()
    inner = pygame.Rect(
        ROOM_X + TILE,
        ROOM_Y + TILE,
        (ROOM_COLS - 2) * TILE,
        (ROOM_ROWS - 2) * TILE,
    )

    # Portal sits on the right-centre of the room
    P_W, P_H = 32, 52
    portal_rect = pygame.Rect(
        inner.right - P_W - 60,
        inner.centery - P_H // 2,
        P_W, P_H,
    )

    # Build wanderers: boss NPCs + all playable fighters
    npc_defs = list(_BOSS_NPC_DEFS) + [
        (f['name'], f['color'], 20, 20) for f in FIGHTERS
    ]
    wanderers = []
    for (name, col, w, h), (fx, fy) in zip(npc_defs, _SPAWN_OFFSETS):
        x = inner.left + fx * inner.width  - w // 2
        y = inner.top  + fy * inner.height - h // 2
        wanderers.append(_Wanderer(name, col, w, h, x, y))

    # Assign a unique dialogue line to each NPC
    shuffled = random.sample(_DIALOGUE, len(wanderers))
    for npc, line in zip(wanderers, shuffled):
        npc.dialogue = line

    # Cazarog starts left-centre
    caz_x = float(inner.left + 80)
    caz_y = float(inner.centery - _CAZ_H // 2)

    tick = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Cazarog movement
        keys = pygame.key.get_pressed()
        dx   = (int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
               - int(keys[pygame.K_a] or keys[pygame.K_LEFT]))
        dy   = (int(keys[pygame.K_s] or keys[pygame.K_DOWN])
               - int(keys[pygame.K_w] or keys[pygame.K_UP]))
        if dx or dy:
            ln  = math.hypot(dx, dy)
            dx /= ln
            dy /= ln

        caz_x += dx * _CAZ_SPD
        cr = pygame.Rect(int(caz_x), int(caz_y), _CAZ_W, _CAZ_H)
        for w in walls:
            if cr.colliderect(w):
                caz_x -= dx * _CAZ_SPD
                break

        caz_y += dy * _CAZ_SPD
        cr = pygame.Rect(int(caz_x), int(caz_y), _CAZ_W, _CAZ_H)
        for w in walls:
            if cr.colliderect(w):
                caz_y -= dy * _CAZ_SPD
                break

        cr = pygame.Rect(int(caz_x), int(caz_y), _CAZ_W, _CAZ_H)

        # Portal entry
        if cr.inflate(4, 4).colliderect(portal_rect):
            return

        # Update NPCs
        for npc in wanderers:
            npc.update(walls)

        # ── Draw ─────────────────────────────────────────────────────────────
        draw_room(screen, walls, 9)   # Cazarog's blood-floor palette

        # Portal glow + body
        pulse = 0.5 + 0.5 * math.sin(tick * 0.07)
        glow  = pygame.Surface((P_W + 24, P_H + 24), pygame.SRCALPHA)
        glow.fill((*_PORTAL_GLOW, int(90 * pulse)))
        screen.blit(glow, (portal_rect.x - 12, portal_rect.y - 12))
        pygame.draw.rect(screen, _PORTAL_COL,  portal_rect, border_radius=8)
        pygame.draw.rect(screen, _PORTAL_GLOW, portal_rect, 2, border_radius=8)
        pt = font.render("PORTAL", True, _PORTAL_GLOW)
        screen.blit(pt, (portal_rect.centerx - pt.get_width() // 2,
                         portal_rect.bottom + 4))

        # NPCs + proximity speech bubbles
        for npc in wanderers:
            npc.draw(screen, font)
            dist = math.hypot(cr.centerx - npc.rect.centerx,
                              cr.centery - npc.rect.centery)
            if dist < _PROXIMITY:
                _draw_bubble(screen, font, npc.dialogue,
                             npc.rect.centerx, npc.rect.top - 2)

        # Cazarog (player)
        pygame.draw.rect(screen, _CAZAROG_COL, cr)
        pygame.draw.rect(screen, (190, 90, 255), cr, 2)
        caz_label = font.render("CAZAROG", True, UI_WHITE)
        screen.blit(caz_label, (cr.centerx - caz_label.get_width() // 2,
                                cr.top - caz_label.get_height() - 2))

        # Title + hint
        title = font_big.render("— THE HUB —", True, GOLD_COL)
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 14))
        hint = font.render(
            "WASD to move   ·   walk into the portal to choose your fighter",
            True, UI_MUTED)
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 22))

        pygame.display.flip()
        clock.tick(FPS)
        tick += 1
