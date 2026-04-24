import pygame
import math

from constants import HEALTH_COL, SPEED_COL, ATTACK_BCOL, INVULN_COL


_ITEM_META = {
    'health': (HEALTH_COL,  (40,  160,  70)),
    'speed':  (SPEED_COL,   (40,  150, 180)),
    'attack': (ATTACK_BCOL, (190, 100,  30)),
    'invuln': (INVULN_COL,  (110, 115, 200)),
}


class Item:
    W, H = 14, 14

    def __init__(self, x, y, kind):
        self.x    = x
        self.y    = y
        self.kind = kind   # 'health' | 'speed' | 'attack' | 'invuln'

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def draw(self, surf, tick):
        bob = int(math.sin(tick * 0.07 + self.x * 0.05) * 2)
        r   = pygame.Rect(self.x, self.y + bob, self.W, self.H)
        col, border = _ITEM_META[self.kind]
        pygame.draw.rect(surf, col,    r)
        pygame.draw.rect(surf, border, r, 1)

        cx, cy = r.centerx, r.centery
        sc = tuple(min(c + 80, 255) for c in col)

        if self.kind == 'health':
            pygame.draw.line(surf, sc, (cx, cy - 4), (cx, cy + 4), 2)
            pygame.draw.line(surf, sc, (cx - 4, cy), (cx + 4, cy), 2)
        elif self.kind == 'speed':
            for ox in (-2, 2):
                pygame.draw.line(surf, sc, (cx + ox - 2, cy - 3), (cx + ox + 2, cy),     1)
                pygame.draw.line(surf, sc, (cx + ox + 2, cy),     (cx + ox - 2, cy + 3), 1)
        elif self.kind == 'attack':
            pygame.draw.line(surf, sc, (cx - 3, cy - 3), (cx + 3, cy + 3), 2)
            pygame.draw.line(surf, sc, (cx + 3, cy - 3), (cx - 3, cy + 3), 2)
        elif self.kind == 'invuln':
            pts = [(cx, cy - 5), (cx + 4, cy - 2), (cx + 4, cy + 2),
                   (cx, cy + 5), (cx - 4, cy + 2), (cx - 4, cy - 2)]
            pygame.draw.polygon(surf, sc, pts, 1)
