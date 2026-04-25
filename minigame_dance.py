import pygame
import math
import random
import sys

from constants import (
    SCREEN_W, SCREEN_H, FPS,
    UI_WHITE, UI_MUTED, GOLD_COL, HP_FG,
)
from dungeon import draw_room, build_walls


# ── Palette ───────────────────────────────────────────────────────────────────
_BAMBIE_COL   = (130,  55, 190)
_ROOM_BG      = ( 28,  22,  38)
_ROOM_GRID    = ( 40,  32,  54)
_OVERLAY_RGBA = ( 18,  12,  30, 205)
_BEAT_COL     = (200, 120, 255)
_WARM_AMBER   = (230, 150,  50)
_WARM_YELLOW  = (255, 210,  80)
_WARM_RED     = (210,  65,  55)
_WARM_GREEN   = ( 75, 205,  95)
_KEY_IDLE     = ( 52,  40,  72)
_KEY_SHOWN    = ( 88,  66, 116)
_KEY_ACTIVE   = (200, 150, 255)
_KEY_HIDDEN   = ( 40,  30,  55)
_KEY_CORRECT  = ( 52, 180,  88)
_KEY_WRONG    = (190,  55,  55)
_KEY_DONE     = ( 60,  46,  80)

_SHOW_FRAMES   = 50    # frames each step is highlighted during Bambie's turn
_HIDE_FRAMES   = 38    # brief blank pause before player input
_RESULT_FRAMES = 115   # frames the round-result screen stays up
_INTRO_FRAMES  = 170

_VALID_KEYS  = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
_SEQ_LENGTHS = [3, 5, 7]
_KEY_LABEL   = {
    pygame.K_w: 'W',
    pygame.K_a: 'A',
    pygame.K_s: 'S',
    pygame.K_d: 'D',
}


# ── Draw helpers ──────────────────────────────────────────────────────────────

def _draw_bg(surf, walls):
    surf.fill(_ROOM_BG)
    for col in range(1, 39):
        pygame.draw.line(surf, _ROOM_GRID,
                         (col * 32, 32), (col * 32, SCREEN_H - 32))
    for row in range(1, 21):
        pygame.draw.line(surf, _ROOM_GRID,
                         (32, 32 + row * 32), (SCREEN_W - 32, 32 + row * 32))
    draw_room(surf, walls, 3)
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill(_OVERLAY_RGBA)
    surf.blit(overlay, (0, 0))


def _draw_dir_arrow(surf, bam_cx, bam_cy, key, size=26):
    """Draw a bright polygon arrow in the direction of the given key."""
    gap  = 38
    col  = _WARM_YELLOW
    bord = (255, 240, 160)
    if key == pygame.K_w:
        tip = (bam_cx,      bam_cy - 26 - gap - size)
        pts = [tip,
               (bam_cx - size // 2, bam_cy - 26 - gap),
               (bam_cx + size // 2, bam_cy - 26 - gap)]
    elif key == pygame.K_s:
        tip = (bam_cx,      bam_cy + 26 + gap + size)
        pts = [tip,
               (bam_cx - size // 2, bam_cy + 26 + gap),
               (bam_cx + size // 2, bam_cy + 26 + gap)]
    elif key == pygame.K_a:
        tip = (bam_cx - 26 - gap - size, bam_cy)
        pts = [tip,
               (bam_cx - 26 - gap, bam_cy - size // 2),
               (bam_cx - 26 - gap, bam_cy + size // 2)]
    else:  # K_d
        tip = (bam_cx + 26 + gap + size, bam_cy)
        pts = [tip,
               (bam_cx + 26 + gap, bam_cy - size // 2),
               (bam_cx + 26 + gap, bam_cy + size // 2)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, bord, pts, 1)


def _draw_bambie(surf, cx, cy, tick, dancing=False, direction=None):
    size = 52
    if dancing and direction is not None:
        t    = tick * 0.28
        amp  = 10
        if direction == pygame.K_w:
            ox, oy = 0, -int(abs(math.sin(t)) * amp)
        elif direction == pygame.K_s:
            ox, oy = 0,  int(abs(math.sin(t)) * amp)
        elif direction == pygame.K_a:
            ox, oy = -int(abs(math.sin(t)) * amp), 0
        else:
            ox, oy = int(abs(math.sin(t)) * amp), 0
    else:
        ox = int(math.sin(tick * 0.055) * 3)
        oy = int(math.sin(tick * 0.13)  * 4)

    rx, ry = cx - size // 2 + ox, cy - size // 2 + oy

    pygame.draw.rect(surf, _BAMBIE_COL, (rx, ry, size, size), border_radius=4)
    pygame.draw.rect(surf, (175, 115, 225), (rx, ry, size, size), 2, border_radius=4)

    # Eyes
    pygame.draw.circle(surf, (242, 212, 255), (rx + 14, ry + 21), 5)
    pygame.draw.circle(surf, (242, 212, 255), (rx + 38, ry + 21), 5)
    pygame.draw.circle(surf, ( 38,  14,  62), (rx + 14, ry + 21), 2)
    pygame.draw.circle(surf, ( 38,  14,  62), (rx + 38, ry + 21), 2)

    # Witch hat
    hat_cx = rx + size // 2
    pygame.draw.polygon(surf, (32, 16, 54), [
        (hat_cx,      ry - 24),
        (hat_cx - 20, ry + 1),
        (hat_cx + 20, ry + 1),
    ])
    pygame.draw.rect(surf, (52, 26, 78), (hat_cx - 24, ry - 6, 48, 9), border_radius=2)
    # star on hat
    pygame.draw.circle(surf, _WARM_YELLOW, (hat_cx, ry - 16), 4)

    if dancing and direction is not None:
        _draw_dir_arrow(surf, cx + ox, cy + oy, direction)


def _draw_key_box(surf, cx, cy, label, state, font):
    size = 52
    rx   = cx - size // 2
    ry   = cy - size // 2
    if state == 'active':
        bg, txt = _KEY_ACTIVE, (20, 12, 40)
    elif state == 'shown':
        bg, txt = _KEY_SHOWN, (170, 135, 210)
    elif state == 'hidden':
        bg, txt, label = _KEY_HIDDEN, (90, 70, 115), '?'
    elif state == 'correct':
        bg, txt = _KEY_CORRECT, (10, 55, 22)
    elif state == 'wrong':
        bg, txt, label = _KEY_WRONG, (245, 218, 218), 'X'
    elif state == 'done':
        bg, txt = _KEY_DONE, (135, 108, 165)
    else:  # idle — empty box, no label
        bg, txt, label = _KEY_IDLE, (0, 0, 0), ''
    pygame.draw.rect(surf, bg, (rx, ry, size, size), border_radius=6)
    pygame.draw.rect(surf, (145, 108, 188), (rx, ry, size, size), 1, border_radius=6)
    if label:
        t = font.render(label, True, txt)
        surf.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))


def _draw_seq_row(surf, sequence, states, row_y, font):
    cx      = SCREEN_W // 2
    n       = len(sequence)
    spacing = 62
    x0      = cx - (n * spacing) // 2 + spacing // 2
    for i, (k, st) in enumerate(zip(sequence, states)):
        label = _KEY_LABEL[k] if st not in ('idle', 'hidden') else ''
        _draw_key_box(surf, x0 + i * spacing, row_y, label, st, font)


def _draw_hp_bar(surf, font, label, hp, max_hp, x, y, w, col, right_align=False):
    pygame.draw.rect(surf, (28, 20, 40), (x, y, w, 18))
    fw = max(0, int(w * (max(0, hp) / max_hp)))
    if fw:
        pygame.draw.rect(surf, col, (x, y, fw, 18))
    pygame.draw.rect(surf, (115, 84, 155), (x, y, w, 18), 1)
    t = font.render(f"{label}  {max(0, hp)}/{max_hp}", True, UI_WHITE)
    if right_align:
        surf.blit(t, (x + w - t.get_width() - 4, y + 2))
    else:
        surf.blit(t, (x + 4, y + 2))


def _draw_beat_dots(surf, tick, cx, y):
    """Pulsing beat indicator row."""
    n = 8
    for i in range(n):
        phase  = (tick * 0.12 + i * 0.8) % (2 * math.pi)
        radius = int(3 + abs(math.sin(phase)) * 4)
        alpha  = int(80 + abs(math.sin(phase)) * 175)
        col    = tuple(int(c * alpha / 255) for c in _BEAT_COL)
        pygame.draw.circle(surf, col, (cx - (n // 2) * 22 + i * 22, y), radius)


# ── Public entry point ────────────────────────────────────────────────────────

def run_dance_battle(screen, clock, font, font_big, font_title, player, bambie):
    """
    Blocking dance-battle pre-fight minigame.

    Bambie shows a WASD sequence; the player must reproduce it.
    Round 1: 3 inputs, Round 2: 5, Round 3: 7.
    Correct → bambie.hp -= 2.  Wrong → player.hp -= 2.
    Returns True when all 3 rounds finish (proceed to boss fight).
    Returns False if player.hp reaches 0 (trigger game-over in caller).
    """
    walls = build_walls()
    tick  = 0
    cx    = SCREEN_W // 2

    # ── State machine ─────────────────────────────────────────────────────────
    phase        = 'intro'
    phase_timer  = _INTRO_FRAMES

    round_idx    = 0      # 0-based current round (0..2)
    round_wins   = []     # bool per completed round

    sequence     = []     # current round's key sequence
    show_idx     = 0      # which step Bambie is currently showing
    show_timer   = 0      # frames left on the current shown step
    input_idx    = 0      # how many inputs the player has confirmed
    box_states   = []     # per-box draw state for current phase

    result_won    = False
    result_timer  = 0
    result_msg    = ''
    result_states = []    # box states frozen at round end for display

    def _start_round(r):
        nonlocal sequence, show_idx, show_timer, input_idx, box_states, phase
        n          = _SEQ_LENGTHS[r]
        sequence   = [random.choice(_VALID_KEYS) for _ in range(n)]
        show_idx   = 0
        show_timer = _SHOW_FRAMES
        input_idx  = 0
        box_states = ['idle'] * n
        phase      = 'show'

    def _end_round(won):
        nonlocal result_won, result_timer, result_msg, result_states, phase
        result_won    = won
        result_timer  = _RESULT_FRAMES
        phase         = 'result'
        round_wins.append(won)
        if won:
            bambie.hp     = max(0, bambie.hp - 2)
            bambie.lag_hp = max(bambie.lag_hp - 2, 0)
            result_states = ['correct'] * len(sequence)
            result_msg    = 'PERFECT!  Bambie takes 2 damage!'
        else:
            player.hp          = max(0, player.hp - 2)
            player.total_damage = getattr(player, 'total_damage', 0) + 2
            # Freeze current box_states — the wrong box already marked 'wrong'
            result_states = list(box_states)
            # Remaining boxes after wrong idx stay idle for clarity
            for j in range(input_idx + 1, len(sequence)):
                result_states[j] = 'idle'
            result_msg = 'WRONG!  You take 2 damage!'

    # ── Main loop ─────────────────────────────────────────────────────────────
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if phase == 'intro':
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                                     pygame.K_SPACE):
                        _start_round(round_idx)

                elif phase == 'input':
                    if event.key in _VALID_KEYS:
                        if event.key == sequence[input_idx]:
                            box_states[input_idx] = 'done'
                            input_idx += 1
                            if input_idx >= len(sequence):
                                _end_round(True)
                        else:
                            box_states[input_idx] = 'wrong'
                            _end_round(False)

        # ── Phase transitions ─────────────────────────────────────────────────
        if phase == 'intro':
            phase_timer -= 1
            if phase_timer <= 0:
                _start_round(round_idx)

        elif phase == 'show':
            show_timer -= 1
            if show_timer <= 0:
                box_states[show_idx] = 'shown'   # dim the just-shown key
                show_idx += 1
                if show_idx >= len(sequence):
                    phase       = 'hide'
                    phase_timer = _HIDE_FRAMES
                else:
                    show_timer = _SHOW_FRAMES

        elif phase == 'hide':
            phase_timer -= 1
            if phase_timer <= 0:
                box_states = ['hidden'] * len(sequence)
                phase      = 'input'

        elif phase == 'result':
            result_timer -= 1
            if result_timer <= 0:
                if player.hp <= 0:
                    return False
                round_idx += 1
                if round_idx >= 3:
                    return True
                _start_round(round_idx)

        # ── Draw ──────────────────────────────────────────────────────────────
        _draw_bg(screen, walls)

        # Title
        t = font_title.render('♪  DANCE BATTLE  ♪', True, _BEAT_COL)
        screen.blit(t, (cx - t.get_width() // 2, 14))

        # Beat dots (decorative rhythm bar)
        _draw_beat_dots(screen, tick, cx, 68)

        # Round pip indicators
        for i in range(3):
            px = cx - 30 + i * 30
            if i < len(round_wins):
                pip_col = _WARM_GREEN if round_wins[i] else _WARM_RED
            elif i == round_idx:
                pip_col = _WARM_AMBER
            else:
                pip_col = (50, 38, 68)
            pygame.draw.circle(screen, pip_col, (px, 85), 9)
            pygame.draw.circle(screen, (155, 115, 195), (px, 85), 9, 1)
            rt = font.render(str(i + 1), True, (20, 10, 32))
            screen.blit(rt, (px - rt.get_width() // 2, 85 - rt.get_height() // 2))

        # HP bars
        _draw_hp_bar(screen, font, 'YOU', player.hp, player.max_hp,
                     28, 100, 200, HP_FG)
        _draw_hp_bar(screen, font, 'BAMBIE', bambie.hp, bambie.MAX_HP,
                     SCREEN_W - 228, 100, 200, _BAMBIE_COL, right_align=True)

        bam_cx, bam_cy = cx, 225

        # ── Phase-specific draw ───────────────────────────────────────────────
        if phase == 'intro':
            _draw_bambie(screen, bam_cx, bam_cy, tick)
            fade = min(255, (_INTRO_FRAMES - phase_timer) * 6)
            c    = lambda base: tuple(int(b * fade / 255) for b in base)
            t = font_big.render('BAMBIE CHALLENGES YOU!', True, c((220, 185, 255)))
            screen.blit(t, (cx - t.get_width() // 2, 310))
            t = font.render('Memorise her moves, then repeat them!',
                            True, c(UI_MUTED))
            screen.blit(t, (cx - t.get_width() // 2, 350))
            t = font.render('Win all 3 rounds to begin the boss fight.',
                            True, c((138, 105, 168)))
            screen.blit(t, (cx - t.get_width() // 2, 370))
            t = font.render('Round 1: 3 moves    Round 2: 5 moves    Round 3: 7 moves',
                            True, c((100, 76, 128)))
            screen.blit(t, (cx - t.get_width() // 2, 420))
            if _INTRO_FRAMES - phase_timer > 55:
                t = font.render('PRESS ENTER or SPACE to start', True, _WARM_AMBER)
                screen.blit(t, (cx - t.get_width() // 2, 468))

        elif phase == 'show':
            cur_key = sequence[show_idx]
            _draw_bambie(screen, bam_cx, bam_cy, tick,
                         dancing=True, direction=cur_key)
            cur_states = list(box_states)
            cur_states[show_idx] = 'active'
            _draw_seq_row(screen, sequence, cur_states, 395, font_big)

            t = font.render("WATCH BAMBIE'S MOVES!", True, _WARM_AMBER)
            screen.blit(t, (cx - t.get_width() // 2, 458))
            # Per-step progress bar
            frac = 1.0 - show_timer / _SHOW_FRAMES
            bw   = 180
            pygame.draw.rect(screen, (38, 28, 52),
                             (cx - bw // 2, 476, bw, 5))
            pygame.draw.rect(screen, _BEAT_COL,
                             (cx - bw // 2, 476, int(bw * frac), 5))
            # Step counter
            t = font.render(f'{show_idx + 1} / {len(sequence)}', True, UI_MUTED)
            screen.blit(t, (cx - t.get_width() // 2, 484))

        elif phase == 'hide':
            _draw_bambie(screen, bam_cx, bam_cy, tick)
            idle_states = ['idle'] * len(sequence)
            _draw_seq_row(screen, sequence, idle_states, 395, font_big)
            t = font.render('Get ready…', True, (175, 135, 215))
            screen.blit(t, (cx - t.get_width() // 2, 458))

        elif phase == 'input':
            _draw_bambie(screen, bam_cx, bam_cy, tick)
            _draw_seq_row(screen, sequence, box_states, 395, font_big)
            t = font.render('YOUR TURN!   W  A  S  D', True, _WARM_YELLOW)
            screen.blit(t, (cx - t.get_width() // 2, 458))
            t = font.render(f'{input_idx} / {len(sequence)}', True, UI_MUTED)
            screen.blit(t, (cx - t.get_width() // 2, 476))

        elif phase == 'result':
            dancing = result_won
            _draw_bambie(screen, bam_cx, bam_cy, tick,
                         dancing=dancing,
                         direction=sequence[0] if dancing else None)
            _draw_seq_row(screen, sequence, result_states, 395, font_big)
            col = _WARM_GREEN if result_won else _WARM_RED
            t   = font_big.render(result_msg, True, col)
            screen.blit(t, (cx - t.get_width() // 2, 315))
            sub = '-2 HP  to BAMBIE' if result_won else '-2 HP  to YOU'
            t   = font.render(sub, True, _BAMBIE_COL if result_won else _WARM_RED)
            screen.blit(t, (cx - t.get_width() // 2, 355))
            if result_timer < _RESULT_FRAMES // 2:
                if round_idx < 2:
                    hint = f'Round {round_idx + 2} incoming…'
                elif round_idx == 2:
                    hint = 'Prepare for the boss fight!' if result_won else 'Dance battle over…'
                else:
                    hint = ''
                t = font.render(hint, True, (138, 105, 168))
                screen.blit(t, (cx - t.get_width() // 2, 480))

        # Bottom hint strip
        hint_map = {
            'intro':  'ENTER / SPACE  start',
            'show':   'Watch carefully…',
            'hide':   'Getting ready…',
            'input':  'Press the correct WASD keys in order',
            'result': '',
        }
        ht = font.render(hint_map.get(phase, ''), True, (62, 48, 80))
        screen.blit(ht, (cx - ht.get_width() // 2, SCREEN_H - 20))

        pygame.display.flip()
        clock.tick(FPS)
        tick += 1
