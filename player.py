import pygame
import math

from constants import (
    ROOM_X, ROOM_Y, ROOM_COLS, ROOM_ROWS, TILE,
    PLAYER_COL, HIT_COL, ATTACK_BCOL, ATTACK_COL, SPEED_COL, INVULN_COL,
    ARROW_RECHARGE, BOMB_RECHARGE, INVULN_DURATION,
)
from projectiles import PlayerArrow, Bomb


class Player:
    W, H        = 20, 20
    BASE_SPEED  = 3.0
    BOOST_SPD   = 5.5
    ATK_CD      = 20
    ATK_DUR     = 10
    IFRAMES     = 60
    SPEED_DUR   = 360
    ATTACK_DUR  = 360
    MAX_ARROWS  = 3
    MAX_BOMBS   = 1

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.facing       = (1.0, 0.0)
        self.hp           = 10
        self.max_hp       = 10
        self.cooldown     = 0
        self.atk_timer    = 0
        self.iframes      = 0
        self.attack_rect  = None
        self.speed_timer  = 0
        self.attack_timer = 0
        self.invuln_timer = 0
        self.total_damage = 0
        self.arrows       = self.MAX_ARROWS
        self.arrow_timer  = 0
        self.bombs        = self.MAX_BOMBS
        self.bomb_timer   = 0
        self.place_at_center()

    def place_at_center(self):
        self.x = float(ROOM_X + ROOM_COLS * TILE // 2 - self.W // 2)
        self.y = float(ROOM_Y + ROOM_ROWS * TILE // 2 - self.H // 2)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def cx(self): return self.x + self.W / 2

    @property
    def cy(self): return self.y + self.H / 2

    @property
    def spd(self):
        return self.BOOST_SPD if self.speed_timer else self.BASE_SPEED

    @property
    def atk_size(self):
        return 42 if self.attack_timer else 26

    @property
    def eff_cd(self):
        return 10 if self.attack_timer else self.ATK_CD

    # ── Actions ───────────────────────────────────────────────────────────────

    def move(self, dx, dy, walls):
        if dx or dy:
            ln = math.hypot(dx, dy)
            self.facing = (dx / ln, dy / ln)
        self.x += dx * self.spd
        for w in walls:
            if self.rect.colliderect(w):
                self.x = w.right if dx < 0 else w.left - self.W
        self.y += dy * self.spd
        for w in walls:
            if self.rect.colliderect(w):
                self.y = w.bottom if dy < 0 else w.top - self.H

    def attack(self):
        if not self.cooldown:
            self.cooldown  = self.eff_cd
            self.atk_timer = self.ATK_DUR

    def shoot_arrow(self):
        if self.arrows > 0:
            self.arrows -= 1
            if self.arrow_timer == 0:
                self.arrow_timer = ARROW_RECHARGE
            fx, fy = self.facing
            return PlayerArrow(self.cx, self.cy, fx * PlayerArrow.SPEED, fy * PlayerArrow.SPEED)
        return None

    def shoot_bomb(self):
        if self.bombs > 0:
            self.bombs -= 1
            if self.bomb_timer == 0:
                self.bomb_timer = BOMB_RECHARGE
            fx, fy = self.facing
            return Bomb(self.cx, self.cy, fx * Bomb.SPEED, fy * Bomb.SPEED)
        return None

    def take_damage(self, amount):
        if self.invuln_timer > 0:
            return
        if not self.iframes:
            self.hp           -= amount
            self.total_damage += amount
            self.iframes       = self.IFRAMES

    def apply_item(self, kind):
        if   kind == 'health': self.hp = min(self.max_hp, self.hp + 4)
        elif kind == 'speed':  self.speed_timer  = self.SPEED_DUR
        elif kind == 'attack': self.attack_timer = self.ATTACK_DUR
        elif kind == 'invuln': self.invuln_timer = INVULN_DURATION

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self):
        if self.cooldown:     self.cooldown -= 1
        if self.iframes:      self.iframes  -= 1
        if self.speed_timer:  self.speed_timer  -= 1
        if self.attack_timer: self.attack_timer -= 1
        if self.invuln_timer: self.invuln_timer -= 1

        # Arrow recharge — one slot at a time, sequential
        if self.arrows < self.MAX_ARROWS:
            if self.arrow_timer > 0:
                self.arrow_timer -= 1
            if self.arrow_timer == 0:
                self.arrows += 1
                if self.arrows < self.MAX_ARROWS:
                    self.arrow_timer = ARROW_RECHARGE

        # Bomb recharge
        if self.bombs < self.MAX_BOMBS:
            if self.bomb_timer > 0:
                self.bomb_timer -= 1
            if self.bomb_timer == 0:
                self.bombs += 1

        if self.atk_timer:
            self.atk_timer -= 1
            half = self.atk_size // 2
            fx, fy = self.facing
            self.attack_rect = pygame.Rect(
                int(self.cx + fx * (half + 13) - half),
                int(self.cy + fy * (half + 13) - half),
                self.atk_size, self.atk_size,
            )
        else:
            self.attack_rect = None

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surf):
        if self.invuln_timer > 0:
            pulse = int(math.sin(self.invuln_timer * 0.25) * 3)
            pygame.draw.rect(surf, INVULN_COL, self.rect.inflate(10 + pulse, 10 + pulse), 2)
        if self.attack_timer:
            pygame.draw.rect(surf, ATTACK_BCOL, self.rect.inflate(8, 8), 2)
        if self.speed_timer:
            pygame.draw.rect(surf, SPEED_COL,   self.rect.inflate(4, 4), 2)

        flash = self.iframes and (self.iframes // 4) % 2 == 0
        pygame.draw.rect(surf, HIT_COL if flash else PLAYER_COL, self.rect)

        fx, fy = self.facing
        ln = math.hypot(fx, fy)
        if ln:
            fx /= ln
            fy /= ln
        pygame.draw.circle(surf, (30, 30, 30), (int(self.cx + fx * 7), int(self.cy + fy * 7)), 3)

        if self.attack_rect and self.atk_timer:
            fc = ATTACK_BCOL if self.attack_timer else ATTACK_COL
            a  = int(200 * self.atk_timer / self.ATK_DUR)
            s  = pygame.Surface((self.attack_rect.w, self.attack_rect.h), pygame.SRCALPHA)
            s.fill((*fc, a))
            surf.blit(s, self.attack_rect.topleft)
            pygame.draw.rect(surf, fc, self.attack_rect, 2)
