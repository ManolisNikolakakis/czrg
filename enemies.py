import pygame
import math
import random

from constants import (
    ROOM_X, ROOM_Y, ROOM_COLS, ROOM_ROWS, TILE, INNER_RECT,
    ENEMY_COL, HIT_COL, HP_BG, HP_FG,
    RANGED_E_COL, RANGED_E_ORB,
    BOSS_COL1, BOSS_COL2,
)
from projectiles import Projectile


def _pt_seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    lsq = dx * dx + dy * dy
    if lsq == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / lsq))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _ray_room_end(cx, cy, dx, dy):
    ts = []
    if dx > 0:   ts.append((INNER_RECT.right  - cx) / dx)
    elif dx < 0: ts.append((INNER_RECT.left   - cx) / dx)
    if dy > 0:   ts.append((INNER_RECT.bottom - cy) / dy)
    elif dy < 0: ts.append((INNER_RECT.top    - cy) / dy)
    t = min(v for v in ts if v > 0)
    return cx + dx * t, cy + dy * t


class Enemy:
    """Standard melee enemy — chases the player and deals contact damage."""

    W, H        = 18, 18
    AGGRO_RANGE = 320
    IFRAMES     = 18

    def __init__(self, x, y, hp=3, speed=0.90):
        self.x       = float(x)
        self.y       = float(y)
        self.hp      = hp
        self.max_hp  = hp
        self.speed   = speed
        self.alive   = True
        self.iframes = 0

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def cx(self): return self.x + self.W / 2

    @property
    def cy(self): return self.y + self.H / 2

    def take_damage(self, amount):
        if not self.iframes:
            self.hp     -= amount
            self.iframes = self.IFRAMES
            if self.hp <= 0:
                self.alive = False

    def update(self, player, walls):
        if self.iframes:
            self.iframes -= 1
        dx   = player.cx - self.cx
        dy   = player.cy - self.cy
        dist = math.hypot(dx, dy)
        if 0 < dist < self.AGGRO_RANGE:
            dx /= dist
            dy /= dist
            self.x += dx * self.speed
            for w in walls:
                if self.rect.colliderect(w):
                    self.x = w.right if dx < 0 else w.left - self.W
            self.y += dy * self.speed
            for w in walls:
                if self.rect.colliderect(w):
                    self.y = w.bottom if dy < 0 else w.top - self.H
        if self.rect.colliderect(player.rect):
            player.take_damage(1)

    def draw_projectiles(self, surf, tick):
        pass   # melee enemies have no projectiles

    def draw(self, surf):
        flash = self.iframes and (self.iframes // 3) % 2 == 0
        pygame.draw.rect(surf, HIT_COL if flash else ENEMY_COL, self.rect)
        bx, by = int(self.x), int(self.y) - 7
        pygame.draw.rect(surf, HP_BG, (bx, by, self.W, 4))
        fill = max(0, int(self.W * self.hp / self.max_hp))
        if fill:
            pygame.draw.rect(surf, HP_FG, (bx, by, fill, 4))


class RangedEnemy:
    """Keeps its distance and fires fireballs at the player."""

    W, H        = 18, 18
    AGGRO_RANGE = 360
    PREFER_DIST = 140
    IFRAMES     = 18

    def __init__(self, x, y, hp=2, speed=0.75):
        self.x       = float(x)
        self.y       = float(y)
        self.hp      = hp
        self.max_hp  = hp
        self.speed   = speed
        self.alive   = True
        self.iframes = 0
        self.strafe  = random.choice((-1, 1))
        self.shoot_cd = random.randint(30, 80)   # stagger initial shots
        self.projectiles = []

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def cx(self): return self.x + self.W / 2

    @property
    def cy(self): return self.y + self.H / 2

    def take_damage(self, amount):
        if not self.iframes:
            self.hp     -= amount
            self.iframes = self.IFRAMES
            if self.hp <= 0:
                self.alive = False

    def update(self, player, walls):
        if self.iframes:
            self.iframes -= 1

        dx   = player.cx - self.cx
        dy   = player.cy - self.cy
        dist = math.hypot(dx, dy)

        if 0 < dist < self.AGGRO_RANGE:
            ndx, ndy = dx / dist, dy / dist

            if dist < self.PREFER_DIST - 20:
                mx, my = -ndx * self.speed * 0.6, -ndy * self.speed * 0.6
            elif dist > self.PREFER_DIST + 50:
                mx, my = ndx * self.speed, ndy * self.speed
            else:
                if random.random() < 0.004:
                    self.strafe *= -1
                mx = -ndy * self.speed * 0.45 * self.strafe
                my =  ndx * self.speed * 0.45 * self.strafe

            self.x += mx
            for w in walls:
                if self.rect.colliderect(w):
                    self.x = w.right if mx < 0 else w.left - self.W
                    self.strafe *= -1
            self.y += my
            for w in walls:
                if self.rect.colliderect(w):
                    self.y = w.bottom if my < 0 else w.top - self.H
                    self.strafe *= -1

            if self.shoot_cd > 0:
                self.shoot_cd -= 1
            else:
                self.projectiles.append(
                    Projectile(self.cx, self.cy, ndx * 2.3, ndy * 2.3,
                               damage=1, kind='fireball', lifetime=200)
                )
                self.shoot_cd = random.randint(80, 115)

        for p in self.projectiles:
            p.update(player)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def draw_projectiles(self, surf, tick):
        for p in self.projectiles:
            p.draw(surf, tick)

    def draw(self, surf):
        flash = self.iframes and (self.iframes // 3) % 2 == 0
        pygame.draw.rect(surf, HIT_COL if flash else RANGED_E_COL, self.rect)
        pygame.draw.circle(surf, RANGED_E_ORB,     (int(self.cx), int(self.cy)), 5)
        pygame.draw.circle(surf, (255, 255, 200),  (int(self.cx), int(self.cy)), 2)
        bx, by = int(self.x), int(self.y) - 7
        pygame.draw.rect(surf, HP_BG, (bx, by, self.W, 4))
        fill = max(0, int(self.W * self.hp / self.max_hp))
        if fill:
            pygame.draw.rect(surf, HP_FG, (bx, by, fill, 4))


class Salomon:
    """Stone golem miniboss. Triggers floor earthquakes and punishes close-range players with a slam."""

    W, H          = 36, 36
    MAX_HP        = 22
    SPEED         = 0.38
    IFRAMES       = 40
    AGGRO         = 600
    name          = "SALOMON"
    hp_bar_col    = ((88, 72, 55), (125, 105, 78))

    PROX_DIST     = 88
    PROX_FRAMES   = 180        # 3 s at 60 fps
    SLAM_RADIUS   = 130
    SLAM_DMG      = 2
    SLAM_CD_AFTER = 360        # 6 s cooldown after slam

    QUAKE_NORMAL  = 280
    QUAKE_FAST    = 160        # phase 2 interval
    QUAKE_TILES_N = 9
    QUAKE_TILES_P2 = 14
    QUAKE_LIFE    = 200

    def __init__(self):
        self.x      = float(ROOM_X + ROOM_COLS * TILE // 2 - self.W // 2)
        self.y      = float(ROOM_Y + 2 * TILE + 10)
        self.hp     = self.MAX_HP
        self.lag_hp = float(self.MAX_HP)
        self.alive  = True
        self.iframes = 0
        self.phase2 = False
        self.phase2_just_triggered = False

        self.quake_cd     = self.QUAKE_NORMAL // 2   # first quake comes sooner
        self.hazard_tiles = []
        self.hazard_life  = 0

        self.prox_timer  = 0
        self.slam_cd     = 120     # initial delay before first slam possible
        self.slam_active = False
        self.slam_anim   = 0

        self.projectiles = []      # required for interface compatibility

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def cx(self): return self.x + self.W / 2

    @property
    def cy(self): return self.y + self.H / 2

    def take_damage(self, amount):
        if not self.iframes:
            self.hp     -= amount
            self.iframes = self.IFRAMES
            if self.hp <= 0:
                self.hp    = 0
                self.alive = False

    def update(self, player, walls):
        if self.iframes:
            self.iframes -= 1
        if self.lag_hp > self.hp:
            self.lag_hp = max(float(self.hp), self.lag_hp - 0.15)

        if not self.phase2 and self.hp <= self.MAX_HP // 2:
            self.phase2 = True
            self.phase2_just_triggered = True

        dx   = player.cx - self.cx
        dy   = player.cy - self.cy
        dist = math.hypot(dx, dy)

        if 0 < dist < self.AGGRO:
            spd  = self.SPEED * (1.4 if self.phase2 else 1.0)
            ndx, ndy = dx / dist, dy / dist
            self.x += ndx * spd
            for w in walls:
                if self.rect.colliderect(w):
                    self.x = w.right if ndx < 0 else w.left - self.W
            self.y += ndy * spd
            for w in walls:
                if self.rect.colliderect(w):
                    self.y = w.bottom if ndy < 0 else w.top - self.H

        if self.rect.colliderect(player.rect):
            player.take_damage(1)

        # Earthquake hazard tiles
        if self.hazard_life > 0:
            self.hazard_life -= 1
            if self.hazard_life == 0:
                self.hazard_tiles = []
            else:
                for tile in self.hazard_tiles:
                    if player.rect.colliderect(tile):
                        player.take_damage(1)
                        break

        if self.quake_cd > 0:
            self.quake_cd -= 1
        else:
            self._trigger_quake()

        # Proximity slam
        if self.slam_active:
            self.slam_anim += 1
            if self.slam_anim >= 45:
                self.slam_active = False
                self.slam_anim   = 0
                self.slam_cd     = self.SLAM_CD_AFTER
        elif self.slam_cd > 0:
            self.slam_cd    -= 1
            self.prox_timer  = 0
        else:
            if dist < self.PROX_DIST:
                self.prox_timer += 1
                if self.prox_timer >= self.PROX_FRAMES:
                    self._do_slam(player, dist)
            else:
                self.prox_timer = max(0, self.prox_timer - 3)

    def _trigger_quake(self):
        count    = self.QUAKE_TILES_P2 if self.phase2 else self.QUAKE_TILES_N
        interval = self.QUAKE_FAST     if self.phase2 else self.QUAKE_NORMAL
        self.quake_cd    = interval
        self.hazard_life = self.QUAKE_LIFE
        self.hazard_tiles = []
        cx0, cy0 = int(self.cx), int(self.cy)
        attempts = 0
        while len(self.hazard_tiles) < count and attempts < count * 8:
            attempts += 1
            col = random.randint(2, ROOM_COLS - 3)
            row = random.randint(2, ROOM_ROWS - 3)
            tx  = ROOM_X + col * TILE
            ty  = ROOM_Y + row * TILE
            if math.hypot(tx + TILE // 2 - cx0, ty + TILE // 2 - cy0) < 56:
                continue
            r = pygame.Rect(tx, ty, TILE, TILE)
            if not any(r.colliderect(h) for h in self.hazard_tiles):
                self.hazard_tiles.append(r)

    def _do_slam(self, player, dist):
        self.slam_active = True
        self.slam_anim   = 0
        self.prox_timer  = 0
        if dist < self.SLAM_RADIUS:
            player.take_damage(self.SLAM_DMG)

    def draw_projectiles(self, surf, tick):
        # Hazard tiles drawn here so they appear under everything else
        if not self.hazard_tiles:
            return
        pulse = abs(math.sin(tick * 0.07))
        for r in self.hazard_tiles:
            s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            s.fill((200, 75, 15, int(110 + 80 * pulse)))
            surf.blit(s, r.topleft)
            pygame.draw.rect(surf, (255, 140, 35), r, 1)
            cx, cy = r.centerx, r.centery
            pygame.draw.line(surf, (240, 100, 20), (cx - 6, cy - 8), (cx + 2, cy + 2), 1)
            pygame.draw.line(surf, (240, 100, 20), (cx + 2, cy + 2), (cx + 8, cy + 6), 1)

    def draw(self, surf, tick):
        # Proximity warning ring (drawn before body so body sits on top)
        if self.prox_timer > 0 and not self.slam_active and self.slam_cd == 0:
            frac   = self.prox_timer / self.PROX_FRAMES
            rc     = (255, int(200 * (1 - frac)), 0)
            pd     = self.PROX_DIST
            s      = pygame.Surface((pd * 2 + 4, pd * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*rc, int(160 * frac)), (pd + 2, pd + 2), pd, 2)
            surf.blit(s, (int(self.cx) - pd - 2, int(self.cy) - pd - 2))

        # Body
        flash = self.iframes and (self.iframes // 4) % 2 == 0
        if flash:
            col, outline = HIT_COL, HIT_COL
        elif self.phase2:
            col, outline = (155, 120, 78), (220, 160, 70)
        else:
            col, outline = (108, 96, 84), (158, 142, 125)

        r = self.rect
        pygame.draw.rect(surf, col, r)
        pygame.draw.rect(surf, outline, r, 3)

        ey = (220, 80, 30) if self.phase2 else (195, 175, 95)
        for ex in (int(self.cx) - 8, int(self.cx) + 8):
            pygame.draw.circle(surf, ey,           (ex, int(self.cy) - 5), 4)
            pygame.draw.circle(surf, (255, 255, 200), (ex, int(self.cy) - 5), 2)

        # Expanding slam ring animation
        if self.slam_active:
            t      = self.slam_anim / 45
            radius = int(self.SLAM_RADIUS * t)
            alpha  = int(255 * (1 - t))
            if radius > 0:
                size = radius * 2 + 4
                s    = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 210, 50, alpha),
                                   (size // 2, size // 2), radius, 5)
                surf.blit(s, (int(self.cx) - size // 2, int(self.cy) - size // 2))


class Bambie:
    """Fast witch miniboss — triple witch bolts and a telegraphed beam attack."""

    W, H          = 22, 22
    MAX_HP        = 20
    SPEED         = 1.7
    IFRAMES       = 25
    AGGRO         = 700
    PREFER_DIST   = 160
    name          = "BAMBIE"
    hp_bar_col    = ((80, 35, 120), (150, 65, 210))

    ARROW_CD_N    = 95
    ARROW_CD_P2   = 55
    BEAM_CD_N     = 270
    BEAM_CD_P2    = 160
    BEAM_TEL      = 90   # telegraph frames before beam fires
    BEAM_ACTIVE   = 35   # frames the beam is live
    BEAM_HALF_W   = 12   # half-width for collision check

    def __init__(self):
        self.x      = float(ROOM_X + ROOM_COLS * TILE // 2 - self.W // 2)
        self.y      = float(ROOM_Y + 2 * TILE + 10)
        self.hp     = self.MAX_HP
        self.lag_hp = float(self.MAX_HP)
        self.alive  = True
        self.iframes = 0
        self.phase2 = False
        self.phase2_just_triggered = False
        self.strafe  = random.choice((-1, 1))
        self.arrow_cd = 60
        self.beam_cd  = 150

        self.beam_state = None   # None | 'telegraph' | 'active'
        self.beam_timer = 0
        self.beam_dir   = (1.0, 0.0)
        self.beam_end   = (0.0, 0.0)

        self.projectiles = []

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def cx(self): return self.x + self.W / 2

    @property
    def cy(self): return self.y + self.H / 2

    def take_damage(self, amount):
        if not self.iframes:
            self.hp     -= amount
            self.iframes = self.IFRAMES
            if self.hp <= 0:
                self.hp    = 0
                self.alive = False

    def update(self, player, walls):
        if self.iframes:
            self.iframes -= 1
        if self.lag_hp > self.hp:
            self.lag_hp = max(float(self.hp), self.lag_hp - 0.18)

        if not self.phase2 and self.hp <= self.MAX_HP // 2:
            self.phase2 = True
            self.phase2_just_triggered = True

        # Freeze movement during beam sequence so the telegraph is readable
        if self.beam_state is None:
            dx   = player.cx - self.cx
            dy   = player.cy - self.cy
            dist = math.hypot(dx, dy)
            if 0 < dist < self.AGGRO:
                spd = self.SPEED * (1.3 if self.phase2 else 1.0)
                ndx, ndy = dx / dist, dy / dist
                pd = self.PREFER_DIST
                if dist < pd - 25:
                    mx, my = -ndx * spd * 0.8, -ndy * spd * 0.8
                elif dist > pd + 60:
                    mx, my = ndx * spd, ndy * spd
                else:
                    if random.random() < 0.008:
                        self.strafe *= -1
                    mx = -ndy * spd * 0.85 * self.strafe
                    my =  ndx * spd * 0.85 * self.strafe
                self.x += mx
                for w in walls:
                    if self.rect.colliderect(w):
                        self.x = w.right if mx < 0 else w.left - self.W
                        self.strafe *= -1
                self.y += my
                for w in walls:
                    if self.rect.colliderect(w):
                        self.y = w.bottom if my < 0 else w.top - self.H
                        self.strafe *= -1

        if self.rect.colliderect(player.rect):
            player.take_damage(1)

        # Triple bolt attack
        if self.beam_state is None:
            if self.arrow_cd > 0:
                self.arrow_cd -= 1
            else:
                self._shoot_triple(player)
                self.arrow_cd = self.ARROW_CD_P2 if self.phase2 else self.ARROW_CD_N

        # Beam sequence
        if self.beam_state is None:
            if self.beam_cd > 0:
                self.beam_cd -= 1
            else:
                self._start_beam(player)
        elif self.beam_state == 'telegraph':
            self.beam_timer -= 1
            if self.beam_timer <= 0:
                self.beam_state = 'active'
                self.beam_timer = self.BEAM_ACTIVE
        elif self.beam_state == 'active':
            self._check_beam_hit(player)
            self.beam_timer -= 1
            if self.beam_timer <= 0:
                self.beam_state = None
                self.beam_cd = self.BEAM_CD_P2 if self.phase2 else self.BEAM_CD_N

        for p in self.projectiles:
            p.update(player)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def _shoot_triple(self, player):
        dx   = player.cx - self.cx
        dy   = player.cy - self.cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        base = math.atan2(dy, dx)
        for deg in (-18, 0, 18):
            a = base + math.radians(deg)
            self.projectiles.append(
                Projectile(self.cx, self.cy,
                           math.cos(a) * 3.5, math.sin(a) * 3.5,
                           damage=1, kind='witch_bolt', lifetime=270)
            )

    def _start_beam(self, player):
        dx   = player.cx - self.cx
        dy   = player.cy - self.cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        bdx, bdy = dx / dist, dy / dist
        self.beam_dir   = (bdx, bdy)
        self.beam_end   = _ray_room_end(self.cx, self.cy, bdx, bdy)
        self.beam_state = 'telegraph'
        self.beam_timer = self.BEAM_TEL

    def _check_beam_hit(self, player):
        bx, by = self.beam_end
        d = _pt_seg_dist(player.cx, player.cy,
                         self.cx, self.cy, bx, by)
        if d < self.BEAM_HALF_W + 8:
            player.take_damage(2)

    def draw_projectiles(self, surf, tick):
        for p in self.projectiles:
            p.draw(surf, tick)

        if self.beam_state == 'telegraph':
            frac  = 1.0 - self.beam_timer / self.BEAM_TEL
            alpha = int(60 + 140 * frac)
            ex, ey = self.beam_end
            s = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
            pygame.draw.line(s, (220, 100, 255, alpha),
                             (int(self.cx), int(self.cy)), (int(ex), int(ey)), 8)
            pygame.draw.line(s, (255, 220, 255, alpha // 2),
                             (int(self.cx), int(self.cy)), (int(ex), int(ey)), 2)
            surf.blit(s, (0, 0))

        elif self.beam_state == 'active':
            t_frac = self.beam_timer / self.BEAM_ACTIVE
            alpha  = int(180 + 75 * t_frac)
            bx, by = int(self.beam_end[0]), int(self.beam_end[1])
            s = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
            pygame.draw.line(s, (255, 120, 255, alpha),
                             (int(self.cx), int(self.cy)), (bx, by),
                             self.BEAM_HALF_W * 2)
            pygame.draw.line(s, (255, 255, 255, min(255, alpha)),
                             (int(self.cx), int(self.cy)), (bx, by), 4)
            surf.blit(s, (0, 0))

    def draw(self, surf, tick):
        flash = self.iframes and (self.iframes // 3) % 2 == 0
        if flash:
            col, outline = HIT_COL, HIT_COL
        elif self.phase2:
            col, outline = (190, 75, 240), (240, 170, 255)
        else:
            col, outline = (130, 55, 190), (200, 140, 255)

        r = self.rect
        pygame.draw.rect(surf, col, r)
        pygame.draw.rect(surf, outline, r, 2)

        ey_col = (255, 80, 80) if self.phase2 else (255, 240, 80)
        for ex in (int(self.cx) - 5, int(self.cx) + 5):
            pygame.draw.circle(surf, ey_col,          (ex, int(self.cy) - 2), 3)
            pygame.draw.circle(surf, (255, 255, 200), (ex, int(self.cy) - 2), 1)


class Boss:
    """Cazarog — fires fireballs and homing missiles; enrages at 50 % HP."""

    W, H       = 32, 32
    MAX_HP     = 40
    SPEED      = 0.65
    IFRAMES    = 30
    AGGRO      = 500
    name       = "CAZAROG"
    hp_bar_col = ((160, 28, 28), (210, 60, 60))

    def __init__(self):
        self.x       = float(ROOM_X + ROOM_COLS * TILE // 2 - self.W // 2)
        self.y       = float(ROOM_Y + 2 * TILE + 8)
        self.hp      = self.MAX_HP
        self.lag_hp  = float(self.MAX_HP)
        self.alive   = True
        self.iframes = 0
        self.phase2  = False
        self.phase2_just_triggered = False
        self.fb_cd   = 60
        self.ms_cd   = 0
        self.projectiles = []

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def cx(self): return self.x + self.W / 2

    @property
    def cy(self): return self.y + self.H / 2

    def take_damage(self, amount):
        if not self.iframes:
            self.hp     -= amount
            self.iframes = self.IFRAMES
            if self.hp <= 0:
                self.hp    = 0
                self.alive = False

    def update(self, player, walls):
        if self.iframes:
            self.iframes -= 1

        if self.lag_hp > self.hp:
            self.lag_hp = max(float(self.hp), self.lag_hp - 0.18)

        if not self.phase2 and self.hp <= self.MAX_HP // 2:
            self.phase2 = True
            self.phase2_just_triggered = True

        dx   = player.cx - self.cx
        dy   = player.cy - self.cy
        dist = math.hypot(dx, dy)

        if 0 < dist < self.AGGRO:
            spd = self.SPEED * (1.35 if self.phase2 else 1.0)
            ndx, ndy = dx / dist, dy / dist
            self.x += ndx * spd
            for w in walls:
                if self.rect.colliderect(w):
                    self.x = w.right if ndx < 0 else w.left - self.W
            self.y += ndy * spd
            for w in walls:
                if self.rect.colliderect(w):
                    self.y = w.bottom if ndy < 0 else w.top - self.H

        if self.rect.colliderect(player.rect):
            player.take_damage(1)

        fb_max = 55 if self.phase2 else 90
        ms_max = 95 if self.phase2 else 145
        if self.fb_cd > 0: self.fb_cd -= 1
        if self.ms_cd > 0: self.ms_cd -= 1
        if self.fb_cd == 0:
            self._shoot_fireballs(dx, dy, dist)
            self.fb_cd = fb_max
        if self.ms_cd == 0:
            self._shoot_missiles(dx, dy, dist)
            self.ms_cd = ms_max

        for p in self.projectiles:
            p.update(player)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def _shoot_fireballs(self, dx, dy, dist):
        if dist == 0:
            return
        base    = math.atan2(dy, dx)
        offsets = [-22, 0, 22] if self.phase2 else [0]
        for deg in offsets:
            a = base + math.radians(deg)
            self.projectiles.append(
                Projectile(self.cx, self.cy,
                           math.cos(a) * 2.0, math.sin(a) * 2.0,
                           damage=2, kind='fireball', lifetime=230)
            )

    def _shoot_missiles(self, dx, dy, dist):
        if dist == 0:
            return
        base    = math.atan2(dy, dx)
        offsets = [-12, 12] if self.phase2 else [0]
        for deg in offsets:
            a = base + math.radians(deg)
            self.projectiles.append(
                Projectile(self.cx, self.cy,
                           math.cos(a) * 3.8, math.sin(a) * 3.8,
                           damage=1, kind='missile', lifetime=190, homing=True)
            )

    def draw_projectiles(self, surf, tick):
        for p in self.projectiles:
            p.draw(surf, tick)

    def draw(self, surf, tick):
        flash   = self.iframes and (self.iframes // 4) % 2 == 0
        col     = HIT_COL if flash else (BOSS_COL2 if self.phase2 else BOSS_COL1)
        r       = self.rect
        outline = (255, 160, 160) if self.phase2 else (200, 130, 255)
        pygame.draw.rect(surf, col, r)
        pygame.draw.rect(surf, outline, r, 2)
        eye = (255, 80, 80) if self.phase2 else (255, 220, 80)
        pygame.draw.circle(surf, eye,           (int(self.cx), int(self.cy)), 5)
        pygame.draw.circle(surf, (255, 255, 255), (int(self.cx), int(self.cy)), 2)
