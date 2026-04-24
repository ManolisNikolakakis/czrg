import pygame
import math

from constants import INNER_RECT, FIREBALL_COL, MISSILE_COL, PLAYER_ARROW_C, BOMB_COL


class Projectile:
    """Enemy / boss ranged attack — fireball or homing missile."""

    _SIZE = {'fireball': 14, 'missile': 7, 'witch_bolt': 9}

    def __init__(self, x, y, vx, vy, damage, kind, lifetime=220, homing=False):
        self.x        = float(x)
        self.y        = float(y)
        self.vx       = vx
        self.vy       = vy
        self._speed   = math.hypot(vx, vy)
        self.damage   = damage
        self.kind     = kind
        self.lifetime = lifetime
        # Missiles home for 50 frames, turning at most 2°/frame — easy to sidestep
        self.homing_frames = 50 if homing else 0
        self.alive    = True

    @property
    def rect(self):
        sz = self._SIZE[self.kind]
        return pygame.Rect(int(self.x) - sz // 2, int(self.y) - sz // 2, sz, sz)

    def update(self, player):
        if self.homing_frames > 0:
            self.homing_frames -= 1
            target  = math.atan2(player.cy - self.y, player.cx - self.x)
            current = math.atan2(self.vy, self.vx)
            diff    = target - current
            while diff >  math.pi: diff -= 2 * math.pi
            while diff < -math.pi: diff += 2 * math.pi
            angle   = current + max(-math.radians(2), min(math.radians(2), diff))
            self.vx = math.cos(angle) * self._speed
            self.vy = math.sin(angle) * self._speed

        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        if self.lifetime <= 0 or not INNER_RECT.collidepoint(int(self.x), int(self.y)):
            self.alive = False
            return

        if self.rect.colliderect(player.rect):
            player.take_damage(self.damage)
            self.alive = False

    def draw(self, surf, tick):
        r = self.rect
        if self.kind == 'fireball':
            pygame.draw.rect(surf, FIREBALL_COL, r)
            inner = r.inflate(-4, -4)
            if inner.w > 0:
                pygame.draw.rect(surf, (255, 220, 60), inner)
        elif self.kind == 'witch_bolt':
            sz = self._SIZE['witch_bolt']
            pygame.draw.circle(surf, (180, 70, 230), (int(self.x), int(self.y)), sz // 2)
            pygame.draw.circle(surf, (240, 170, 255), (int(self.x), int(self.y)), sz // 2 - 2)
        else:
            pygame.draw.rect(surf, MISSILE_COL, r)
            spd = math.hypot(self.vx, self.vy)
            if spd:
                tx = int(self.x - self.vx / spd * 8)
                ty = int(self.y - self.vy / spd * 8)
                pygame.draw.line(surf, (100, 170, 220), (tx, ty), (int(self.x), int(self.y)), 2)


class PlayerArrow:
    """Player's ranged attack — travels in facing direction, deals 2 damage."""

    SPEED  = 7.0
    DAMAGE = 2

    def __init__(self, x, y, vx, vy):
        self.x        = float(x)
        self.y        = float(y)
        self.vx       = vx
        self.vy       = vy
        self.lifetime = 220
        self.alive    = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - 5, int(self.y) - 3, 10, 6)

    def update(self, enemies, boss):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        if self.lifetime <= 0 or not INNER_RECT.collidepoint(int(self.x), int(self.y)):
            self.alive = False
            return

        for e in enemies:
            if e.alive and self.rect.colliderect(e.rect):
                e.take_damage(self.DAMAGE)
                self.alive = False
                return

        if boss and boss.alive and self.rect.colliderect(boss.rect):
            boss.take_damage(self.DAMAGE)
            self.alive = False

    def draw(self, surf):
        spd = math.hypot(self.vx, self.vy)
        if spd == 0:
            return
        nx, ny = self.vx / spd, self.vy / spd
        tail = (int(self.x - nx * 9), int(self.y - ny * 9))
        mid  = (int(self.x),          int(self.y))
        tip  = (int(self.x + nx * 5), int(self.y + ny * 5))
        pygame.draw.line(surf, (110, 150, 50), tail, mid, 2)
        pygame.draw.line(surf, PLAYER_ARROW_C, mid,  tip, 3)
        pygame.draw.circle(surf, (240, 255, 160), tip, 2)


class Bomb:
    """Area-of-effect weapon thrown in facing direction; explodes after a short fuse."""

    SPEED          = 3.5
    FUSE           = 42
    RADIUS         = 80
    DAMAGE         = 8
    EXPLODE_FRAMES = 24

    def __init__(self, x, y, vx, vy):
        self.x         = float(x)
        self.y         = float(y)
        self.vx        = vx
        self.vy        = vy
        self.fuse      = self.FUSE
        self.alive     = True
        self.exploding = False
        self.exp_frame = 0

    def update(self, enemies, boss):
        if self.exploding:
            self.exp_frame += 1
            if self.exp_frame >= self.EXPLODE_FRAMES:
                self.alive = False
            return

        self.x += self.vx
        self.y += self.vy
        self.fuse -= 1

        if not INNER_RECT.collidepoint(int(self.x), int(self.y)):
            self.x = max(float(INNER_RECT.left  + 4), min(self.x, float(INNER_RECT.right  - 4)))
            self.y = max(float(INNER_RECT.top   + 4), min(self.y, float(INNER_RECT.bottom - 4)))
            self._explode(enemies, boss)
            return

        if self.fuse <= 0:
            self._explode(enemies, boss)

    def _explode(self, enemies, boss):
        import math as _math
        self.exploding = True
        self.exp_frame = 0
        for e in enemies:
            if e.alive and _math.hypot(e.cx - self.x, e.cy - self.y) < self.RADIUS:
                e.take_damage(self.DAMAGE)
        if boss and boss.alive and _math.hypot(boss.cx - self.x, boss.cy - self.y) < self.RADIUS:
            boss.take_damage(self.DAMAGE)

    def draw(self, surf, tick):
        if self.exploding:
            t = self.exp_frame / self.EXPLODE_FRAMES
            r = max(1, int(self.RADIUS * t))
            a = int(255 * (1 - t))
            s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 160, 40, a // 2), (r + 1, r + 1), r)
            if r > 12:
                pygame.draw.circle(s, (255, 240, 150, min(255, a)), (r + 1, r + 1), r - 10)
            surf.blit(s, (int(self.x) - r - 1, int(self.y) - r - 1))
        else:
            rate = max(3, int(18 * self.fuse / self.FUSE))
            lit  = (tick // rate) % 2 == 0
            col  = (255, 180, 40) if lit else (160, 70, 15)
            ic   = (255, 245, 160) if lit else (200, 110, 30)
            pygame.draw.circle(surf, col, (int(self.x), int(self.y)), 6)
            pygame.draw.circle(surf, ic,  (int(self.x), int(self.y)), 3)
            frac = self.fuse / self.FUSE
            if frac > 0.02:
                ar = pygame.Rect(int(self.x) - 9, int(self.y) - 9, 18, 18)
                try:
                    pygame.draw.arc(surf, (255, 240, 100), ar, 0, frac * 2 * math.pi, 2)
                except Exception:
                    pass
