import pygame
import sys
import random
import math

# ── Colours ──────────────────────────────────────────────────────────────────
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
NEON_YELLOW = (255, 240,  50)
NEON_PINK   = (255,  50, 180)
NEON_CYAN   = (50,  230, 255)
NEON_GREEN  = (80,  255, 120)
NEON_ORANGE = (255, 140,  20)
DEEP_PURPLE = (30,   10,  60)
MID_PURPLE  = (80,   20, 140)
CAZAROG_COL = (180,  40, 255)
PLAYER_COL  = (80,  255, 120)
HEALTH_BG   = (60,   20,  80)
CORRECT_COL = (80,  255, 120)
WRONG_COL   = (255,  60,  60)
OPTION_BG   = (50,   15,  90)
OPTION_HL   = (120,  40, 200)
OPTION_BORD = (180,  40, 255)

# ── Rap data ─────────────────────────────────────────────────────────────────
# Each entry: cazarog line + chunks list.
# Each chunk: (correct_text, [wrong1, wrong2, wrong3]).
# Chunks join with "".join() to form the full player response.
RAP_BATTLES = [
    {
        "cazarog": "I am Cazarog, lord of the deep",
        "chunks": [
            ("your reign",            ["their hope", "my blade", "all gods"]),
            (" ends here",            [" lives on", " fades out", " falls cold"]),
            (" while the others sleep",[" when the ravens weep", " as the dungeon seeps", " beneath the castle keep"]),
        ],
    },
    {
        "cazarog": "You dare enter my cursed domain",
        "chunks": [
            ("I'll wash",    ["you'll drown", "I'll fade", "we'll break"]),
            (" you out",     [" it down", " them all", " us both"]),
            (" like acid rain",[" like a hurricane", " like a bitter stain", " like the falling crane"]),
        ],
    },
    {
        "cazarog": "My homing missiles never miss",
        "chunks": [
            ("I'll dodge", ["I'll block", "I'll break", "I'll run"]),
            (" them all",  [" each one", " the wall", " your call"]),
            (" and end this",[" and prevail", " and stand tall", " and press on"]),
        ],
    },
    {
        "cazarog": "Phase two begins, feel my rage",
        "chunks": [
            ("I'll turn",   ["you'll burn", "we'll fight", "I'll run"]),
            (" the tide",   [" away now", " it loose", " and hide"]),
            (" and flip the page",[" and leave the stage", " and end this age", " and free the cage"]),
        ],
    },
    {
        "cazarog": "Minions rise at my command",
        "chunks": [
            ("I'll cut",       ["they'll fall", "I'll run", "you'll bleed"]),
            (" them down",     [" you out", " us free", " them loose"]),
            (" where they stand",[" with my hand", " across this land", " as I planned"]),
        ],
    },
    {
        "cazarog": "The final room is mine alone",
        "chunks": [
            ("I'll make",      ["I'll find", "I'll break", "I'll take"]),
            (" this dungeon",  [" the passage", " your power", " each chamber"]),
            (" my new home",   [" my own throne", " where I roam", " carved in stone"]),
        ],
    },
    {
        "cazarog": "I am the dark, you are the light",
        "chunks": [
            ("and light",   ["but dark", "though night", "while hate"]),
            (" will always",[" can never", " might just", " could barely"]),
            (" end the night",[" find its might", " burn so bright", " win the fight"]),
        ],
    },
    {
        "cazarog": "Every step you take I see",
        "chunks": [
            ("but you",         ["and I", "though we", "since they"]),
            (" can't catch",    [" won't block", " can't match", " won't touch"]),
            (" what moves so free",[" what hides in me", " what sets us free", " what the eyes can't see"]),
        ],
    },
    {
        "cazarog": "Your little nut can't crack my shell",
        "chunks": [
            ("your shell",      ["my husk", "this wall", "that core"]),
            (" will ring",      [" will crack", " might break", " could fall"]),
            (" like a church bell",[" like a death knell", " like a wishing well", " like a bat out of hell"]),
        ],
    },
    {
        "cazarog": "I've ruled these halls since time began",
        "chunks": [
            ("I'll end",     ["I'll bend", "I'll mend", "I'll fend"]),
            (" your rule",   [" the deal", " each hall", " your cool"]),
            (", I have a plan",[", just watch me man", ", do all I can", ", I'll take your clan"]),
        ],
    },
]

PLAYER_START_HP   = 12
CAZAROG_START_HP  = 24
DAMAGE_TO_CAZAROG = 2
DAMAGE_TO_PLAYER  = 1
CHUNK_TIMER_MAX   = 3.0

FPS  = 60
W, H = 1280, 720

# WASD → option index mapping
KEY_TO_IDX = {
    pygame.K_w: 0,
    pygame.K_a: 1,
    pygame.K_s: 2,
    pygame.K_d: 3,
}
KEY_LABELS = ['W', 'A', 'S', 'D']


# ── Helpers ───────────────────────────────────────────────────────────────────

def lerp_colour(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_text_centered(surf, text, font, colour, cx, y, shadow=None):
    if shadow:
        s = font.render(text, True, shadow)
        surf.blit(s, s.get_rect(centerx=cx, y=y + 2))
    s = font.render(text, True, colour)
    r = s.get_rect(centerx=cx, y=y)
    surf.blit(s, r)
    return r


def draw_health_bar(surf, x, y, w, h, current, maximum, fg, label_font, label, label_col):
    pygame.draw.rect(surf, HEALTH_BG, (x, y, w, h), border_radius=6)
    fill = int(w * max(0, current) / maximum)
    if fill:
        pygame.draw.rect(surf, fg, (x, y, fill, h), border_radius=6)
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2, border_radius=6)
    txt = label_font.render(f"{label}  {current}/{maximum}", True, label_col)
    surf.blit(txt, (x, y - txt.get_height() - 4))


def shake_offset(tick, intensity):
    if intensity <= 0:
        return 0, 0
    return (int(math.sin(tick * 1.7) * intensity),
            int(math.cos(tick * 2.3) * intensity))


def make_options(correct, wrongs):
    """Return list of 4 (text, is_correct) shuffled."""
    opts = [(correct, True)] + [(w, False) for w in wrongs]
    random.shuffle(opts)
    return opts


def draw_options(surf, options, font_opt, font_key, cx, cy, selected_idx, feedback):
    """Diamond layout: W=top, A=left, S=bottom, D=right."""
    BOX_W, BOX_H = 370, 54
    SPREAD_X, SPREAD_Y = 250, 100
    centres = [
        (cx,            cy - SPREAD_Y),   # W
        (cx - SPREAD_X, cy),              # A
        (cx,            cy + SPREAD_Y),   # S
        (cx + SPREAD_X, cy),              # D
    ]
    for i, ((bx, by), (text, is_correct)) in enumerate(zip(centres, options)):
        rect = pygame.Rect(bx - BOX_W // 2, by - BOX_H // 2, BOX_W, BOX_H)
        if selected_idx == i:
            bg     = (20, 80, 30)  if feedback == 'correct' else (80, 20, 20)
            border = CORRECT_COL   if feedback == 'correct' else WRONG_COL
        else:
            bg, border = OPTION_BG, OPTION_BORD

        pygame.draw.rect(surf, bg, rect, border_radius=8)
        pygame.draw.rect(surf, border, rect, 2, border_radius=8)

        key_s = font_key.render(f"[{KEY_LABELS[i]}]", True, NEON_YELLOW)
        surf.blit(key_s, (rect.x + 10, rect.y + (BOX_H - key_s.get_height()) // 2))

        txt_s = font_opt.render(text.strip(), True, WHITE)
        tx = rect.x + key_s.get_width() + 16
        ty = rect.y + (BOX_H - txt_s.get_height()) // 2
        surf.blit(txt_s, (tx, ty))


# ── Entry point ───────────────────────────────────────────────────────────────

def run_rap_battle(screen, clock, player_fighter_name="Pistachio"):
    """Called from the main game before the Cazarog fight.
    Returns {"player_hp": int, "cazarog_hp": int, "won": bool}."""
    pygame.display.set_caption("RAP BATTLE — Cazarog drops bars")

    font_huge = pygame.font.SysFont("Arial Black", 52, bold=True)
    font_big  = pygame.font.SysFont("Arial Black", 32, bold=True)
    font_med  = pygame.font.SysFont("Arial",       24, bold=True)
    font_opt  = pygame.font.SysFont("Arial",       22, bold=True)
    font_sm   = pygame.font.SysFont("Arial",       18)

    player_hp  = PLAYER_START_HP
    cazarog_hp = CAZAROG_START_HP

    battles = random.sample(RAP_BATTLES, 3)

    state        = "INTRO"
    intro_timer  = 3.0
    bg_tick      = 0.0
    pulse        = 0.0
    shake_frames = 0

    battle_idx   = 0
    chunk_idx    = 0
    assembled    = []       # correct chunk texts selected so far this battle
    options      = []
    selected_idx = None
    feedback     = None     # None | 'correct' | 'wrong' | 'timeout'
    fb_timer     = 0.0
    chunk_timer  = CHUNK_TIMER_MAX

    def load_chunk():
        nonlocal options, selected_idx, feedback, chunk_timer
        correct, wrongs = battles[battle_idx]["chunks"][chunk_idx]
        options      = make_options(correct, wrongs)
        selected_idx = None
        feedback     = None
        chunk_timer  = CHUNK_TIMER_MAX

    load_chunk()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        bg_tick += dt
        pulse   += dt

        # ── Events ───────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if state == "BATTLE" and feedback is None and event.type == pygame.KEYDOWN:
                if event.key in KEY_TO_IDX:
                    idx = KEY_TO_IDX[event.key]
                    selected_idx = idx
                    _, is_correct = options[idx]
                    if is_correct:
                        feedback = 'correct'
                    else:
                        feedback = 'wrong'
                        player_hp    = max(0, player_hp - DAMAGE_TO_PLAYER)
                        shake_frames = 10
                    fb_timer = 0.55

            elif state == "RESULT" and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state = "DONE"

        # ── Update ───────────────────────────────────────────────────────
        if state == "INTRO":
            intro_timer -= dt
            if intro_timer <= 0:
                state = "BATTLE"

        elif state == "BATTLE":
            if shake_frames > 0:
                shake_frames -= 1

            if feedback is not None:
                fb_timer -= dt
                if fb_timer <= 0:
                    if feedback == 'correct':
                        correct_text = battles[battle_idx]["chunks"][chunk_idx][0]
                        assembled.append(correct_text)
                        chunk_idx += 1
                        if chunk_idx >= len(battles[battle_idx]["chunks"]):
                            # Full response built — deal damage to Cazarog
                            cazarog_hp  = max(0, cazarog_hp - DAMAGE_TO_CAZAROG)
                            battle_idx += 1
                            chunk_idx   = 0
                            assembled   = []
                            if battle_idx >= 3:
                                state = "RESULT"
                            else:
                                load_chunk()
                        else:
                            load_chunk()
                    else:
                        # Wrong or timeout — reshuffle same chunk and retry
                        load_chunk()
            else:
                chunk_timer -= dt
                if chunk_timer <= 0:
                    player_hp    = max(0, player_hp - DAMAGE_TO_PLAYER)
                    feedback     = 'timeout'
                    fb_timer     = 0.6
                    shake_frames = 10

            if player_hp <= 0:
                state = "RESULT"

        # ── Draw ─────────────────────────────────────────────────────────
        screen.fill(DEEP_PURPLE)
        for i in range(8):
            r   = int(60 + 40 * math.sin(bg_tick * 0.7 + i * 0.8))
            col = (max(0, min(255, 50 + r)), 0, max(0, min(255, 80 + r)))
            pygame.draw.circle(screen, col,
                               (int(W * (i / 8.0) + 80 * math.sin(bg_tick * 0.4 + i)),
                                int(H // 2 + 150 * math.cos(bg_tick * 0.3 + i * 1.1))),
                               int(120 + 40 * math.sin(bg_tick + i)))

        ox, oy = shake_offset(pygame.time.get_ticks() // 16, shake_frames * 1.5)
        surf = pygame.Surface((W, H), pygame.SRCALPHA)

        if state == "INTRO":
            col = lerp_colour(WHITE, NEON_YELLOW, abs(math.sin(pulse * 4)))
            draw_text_centered(surf, "CAZAROG CHALLENGES YOU IN A RAP BATTLE!", font_big, NEON_PINK,   W // 2, 195, BLACK)
            draw_text_centered(surf, "RAP BATTLE",                               font_huge, col,       W // 2, 240, BLACK)
            draw_text_centered(surf, "Pick the right chunks to rebuild the comeback!", font_med, NEON_CYAN, W // 2, 360)
            draw_text_centered(surf, f"Starting in {max(0, int(intro_timer) + 1)}...", font_big, NEON_ORANGE, W // 2, 420, BLACK)

        elif state == "BATTLE" and battle_idx < 3:
            battle   = battles[battle_idx]
            all_chunks = battle["chunks"]

            # Health bars
            draw_health_bar(surf, 55, 28, 380, 22, player_hp,  PLAYER_START_HP,
                            PLAYER_COL,  font_sm, player_fighter_name, PLAYER_COL)
            draw_health_bar(surf, W - 435, 28, 380, 22, cazarog_hp, CAZAROG_START_HP,
                            CAZAROG_COL, font_sm, "CAZAROG", CAZAROG_COL)

            # Round progress dots
            for bi in range(3):
                dot_col = (NEON_GREEN if bi < battle_idx
                           else CAZAROG_COL if bi == battle_idx
                           else (55, 15, 80))
                pygame.draw.circle(surf, dot_col, (W // 2 - 20 + bi * 20, 60), 7)
            draw_text_centered(surf, f"ROUND {battle_idx + 1} / 3", font_sm, (160, 120, 200), W // 2, 73)

            # Cazarog's line
            draw_text_centered(surf, "CAZAROG:", font_sm, CAZAROG_COL, W // 2, 92)
            caz_col = lerp_colour(CAZAROG_COL, NEON_PINK, 0.4 + 0.4 * math.sin(pulse * 2.5))
            draw_text_centered(surf, f'"{battle["cazarog"]}"', font_big, caz_col, W // 2, 112, BLACK)

            pygame.draw.line(surf, MID_PURPLE, (80, 162), (W - 80, 162), 2)

            # Full target response
            full_response = "".join(c[0] for c in all_chunks)
            draw_text_centered(surf, "YOUR COMEBACK:", font_sm, NEON_GREEN, W // 2, 172)
            draw_text_centered(surf, f'"{full_response}"', font_med, NEON_YELLOW, W // 2, 193, BLACK)

            pygame.draw.line(surf, MID_PURPLE, (80, 232), (W - 80, 232), 1)

            # Assembled so far with [ ??? ] for current and ▪▪▪ for future
            parts = list(assembled)
            parts.append("[ ??? ]")
            for _ in range(len(all_chunks) - chunk_idx - 1):
                parts.append(" ▪▪▪")
            assembled_line = "".join(parts)
            draw_text_centered(surf, assembled_line, font_med,
                               NEON_CYAN if chunk_idx > 0 else WHITE,
                               W // 2, 242, BLACK)

            prog = font_sm.render(f"chunk {chunk_idx + 1} of {len(all_chunks)}", True, (140, 100, 180))
            surf.blit(prog, (W // 2 - prog.get_width() // 2, 268))

            # Chunk countdown timer bar
            timer_frac = max(0.0, chunk_timer / CHUNK_TIMER_MAX) if feedback is None else max(0.0, chunk_timer / CHUNK_TIMER_MAX)
            bar_w = 420
            bar_x = W // 2 - bar_w // 2
            bar_y = 292
            pygame.draw.rect(surf, (25, 8, 45), (bar_x, bar_y, bar_w, 12), border_radius=4)
            if timer_frac > 0:
                t_col = ((80, 220, 80) if timer_frac > 0.55
                         else (255, 200, 30) if timer_frac > 0.28
                         else (255, 60, 60))
                pygame.draw.rect(surf, t_col, (bar_x, bar_y, int(bar_w * timer_frac), 12), border_radius=4)
            pygame.draw.rect(surf, WHITE, (bar_x, bar_y, bar_w, 12), 1, border_radius=4)
            t_num = font_sm.render(f"{max(0.0, chunk_timer):.1f}s", True,
                                   (255, 60, 60) if timer_frac < 0.28 else WHITE)
            surf.blit(t_num, (bar_x + bar_w + 8, bar_y - 2))

            # Options diamond
            draw_options(surf, options, font_opt, font_sm,
                         W // 2, 455, selected_idx,
                         feedback if fb_timer > 0 else None)

            # Feedback flash
            if feedback is not None and fb_timer > 0:
                if feedback == 'correct':
                    draw_text_centered(surf, "CORRECT!", font_big, NEON_GREEN, W // 2, 588, BLACK)
                elif feedback == 'timeout':
                    draw_text_centered(surf, f"TIME'S UP!  -{DAMAGE_TO_PLAYER} HP", font_big, WRONG_COL, W // 2, 588, BLACK)
                else:
                    draw_text_centered(surf, f"WRONG!  -{DAMAGE_TO_PLAYER} HP", font_big, WRONG_COL, W // 2, 588, BLACK)
            elif feedback is None:
                draw_text_centered(surf, "W / A / S / D  to pick a chunk", font_sm, (160, 120, 200), W // 2, 594)

        elif state == "RESULT":
            p_dmg = CAZAROG_START_HP - cazarog_hp
            c_dmg = PLAYER_START_HP  - player_hp
            won   = p_dmg > c_dmg and player_hp > 0
            title = ("Cazarog respects your mad bars."
                     if won else "Cazarog looks at you condescendingly.")
            draw_text_centered(surf, title, font_big,
                               NEON_GREEN if won else NEON_PINK, W // 2, 200, BLACK)
            draw_text_centered(surf, f"Damage dealt to Cazarog: {p_dmg}", font_big, NEON_YELLOW, W // 2, 285, BLACK)
            draw_text_centered(surf, f"Damage taken: {c_dmg}",            font_big, NEON_ORANGE, W // 2, 335, BLACK)
            draw_text_centered(surf, "These carry into the boss fight!",   font_med, NEON_CYAN,   W // 2, 400)
            draw_text_centered(surf, "Press ENTER to continue",            font_med, WHITE,        W // 2, 460)

        elif state == "DONE":
            running = False

        screen.blit(surf, (ox, oy))
        pygame.display.flip()

    p_dmg = CAZAROG_START_HP - cazarog_hp
    c_dmg = PLAYER_START_HP  - player_hp
    return {
        "player_hp":  player_hp,
        "cazarog_hp": cazarog_hp,
        "won":        p_dmg > c_dmg and player_hp > 0,
    }


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock  = pygame.time.Clock()
    result = run_rap_battle(screen, clock, "Pistachio")
    print("Result:", result)
    pygame.quit()
