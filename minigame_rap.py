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
TIMER_OK    = (80,  220,  80)
TIMER_WARN  = (255, 200,  30)
TIMER_CRIT  = (255,  60,  60)
HEALTH_BG   = (60,   20,  80)
INPUT_BG    = (20,   10,  40)
INPUT_BORDER= (180,  40, 255)
CORRECT_COL = (80,  255, 120)
WRONG_COL   = (255,  60,  60)

# ── 100 Rap Pairs ─────────────────────────────────────────────────────────────
# Each tuple: (cazarog_line, player_response)
RAP_PAIRS = [
    ("I am Cazarog, lord of the deep",           "your reign ends here while the others sleep"),
    ("You dare enter my cursed domain",           "I'll wash you out like acid rain"),
    ("My fireballs light the midnight sky",       "dodge and weave til your flames die"),
    ("No hero has survived my wrath",             "I'll be the first to walk your path"),
    ("I crush your bones beneath my feet",        "I rise again, I won't accept defeat"),
    ("Your sword is weak, your aim is poor",      "watch me kick down every door"),
    ("I've devoured legends, eaten kings",        "I'll clip your wings and end your strings"),
    ("The darkness bows when I appear",           "I face the dark without a fear"),
    ("My homing missiles never miss",             "I'll dodge them all and end this"),
    ("Phase two begins, feel my rage",            "I'll turn the tide and flip the page"),
    ("Minions rise at my command",                "I'll cut them down where they stand"),
    ("You're just a nut in my dungeon",           "a nut who'll crack your whole function"),
    ("I've ruled these halls since time began",   "I'll end your rule, I have a plan"),
    ("Your health is thin, your hope is gone",    "I keep on fighting, I stay strong"),
    ("Every step you take I see",                 "but you can't catch what moves so free"),
    ("I'll burn your world to ash and smoke",     "your fire's weak, your spirit's broke"),
    ("The final room is mine alone",              "I'll make this dungeon my new home"),
    ("You trembled at my opening line",           "I came prepared and I'll be fine"),
    ("Feel the heat of purple flame",             "I'll douse your fire all the same"),
    ("No powerup can save you now",               "watch me show you how"),
    ("I am the end, the final gate",              "I'll shatter it and seal your fate"),
    ("Your arrows bounce off my hide",            "then I'll stay close by your side"),
    ("I feast on fear and broken dreams",         "not mine, yours — nothing's as it seems"),
    ("Kneel before the dungeon throne",           "I kneel to no one, standing alone"),
    ("The walls themselves obey my will",         "I'll run them over with a thrill"),
    ("Your bombs are toys, your blades are dull", "I'll show you they can knock your skull"),
    ("I laugh at your pitiful health bar",        "I'll outlast you near and far"),
    ("The ground shakes with every roar",         "I've trained for this and more"),
    ("My purple bolts will fill the room",        "I'll weave through them and seal your doom"),
    ("No champion has bested me twice",           "I'll beat you once and that'll suffice"),
    ("Your fighter name means nothing here",      "my fighter name is something to fear"),
    ("I swallow whole the bravest soul",          "I'll crawl right out and stay in control"),
    ("Ancient magic flows through me",            "but ancient magic can't stop what I'll be"),
    ("You'll scream my name before the end",      "I'll make your name a trend instead"),
    ("The leaderboard will show my score",        "a hundred thousand, maybe more"),
    ("Every room before was just a test",         "and I passed every single test"),
    ("I am the peak, the final height",           "I'll scale you down and win this fight"),
    ("Your last run ends inside my lair",         "I'll make you wish you weren't there"),
    ("Feel my hunger, feel my hate",              "I'll serve it back on a plate"),
    ("No blessing guards you in my halls",        "I'll climb straight up your tallest walls"),
    ("I eat speed boosts for breakfast now",      "then I'll outrun you anyhow"),
    ("Your face shows fear inside my room",       "that face will be your winning gloom"),
    ("I shatter shields like paper thin",         "then I'll paper-cut your thin skin"),
    ("The sky weeps purple at my birth",          "I'll paint it green across the earth"),
    ("I've never known a worthy foe",             "then let me put on quite a show"),
    ("My voice alone could crack the stone",      "my rhymes will rattle every bone"),
    ("You crawled through eight rooms to reach me","I'll make room nine your last decree"),
    ("Each scar you earned meant nothing here",   "each scar taught me to persevere"),
    ("I drain the courage from your chest",       "I'll fill it back and beat the rest"),
    ("The dungeon sings a requiem",               "I'll turn that song to a hymn"),
    ("My eyes burn bright as dying stars",        "I'll close them both behind these bars"),
    ("You'll leave these halls in pieces small",  "or leave them having cleared them all"),
    ("I've watched a thousand heroes fall",       "then watch the thousand and first stand tall"),
    ("My laugh echoes through the deep below",    "your laugh will stop when I steal your glow"),
    ("Purple lightning is my art",                "green lightning comes straight from my heart"),
    ("I'll rend your soul from edge to edge",     "I'll hold it firm right off the ledge"),
    ("The darkness here is absolute",             "I lit it up from the roots"),
    ("Your timer ticks down to the bone",         "I'll finish this before it's gone"),
    ("I summon death with every breath",          "I'll take your breath, that's what it said"),
    ("No mercy lives within my code",             "I'll reprogram every node"),
    ("These halls are mine from stone to ceil",   "I'll peel away everything you feel"),
    ("I tower over everything below",             "I'll cut your tower at its low"),
    ("My missiles lock and never roam",           "I'll send them spinning back to home"),
    ("You thought you'd win? How bold, how bright","I came prepared to win the fight"),
    ("Your run will end the way it starts",       "I'll finish strong with all my heart"),
    ("Cazarog never loses twice",                 "then today you'll pay the price"),
    ("Feel the weight of ancient wrong",          "I'll right it with my battle song"),
    ("The ground itself cries out in pain",       "I'll heal it all and end your reign"),
    ("You dance around my AoE ring",              "just watch me do my victory thing"),
    ("The minions serve my every thought",        "I'll beat the lesson that you've taught"),
    ("My phase two speeds exceed your own",       "my phase two's better than you've known"),
    ("I've broken wills like dry-rotten wood",    "I'll hold together like I should"),
    ("Your potion stash won't save your skin",    "I've saved enough health to win"),
    ("Each room prepared you — barely — for me",  "then I was built for victory"),
    ("My HP bar stretches far and wide",          "I'll chip it down from every side"),
    ("I'll grind you down to nothing, friend",    "nothing will stop me in the end"),
    ("Your little nut can't crack my shell",      "your shell will ring like a church bell"),
    ("I am inevitable, absolute",                 "I'll find the one and only route"),
    ("The dungeon ends exactly here",             "and here's where your ending disappears"),
    ("Your reflexes will fail the test",          "my reflexes will do the rest"),
    ("I've memorised your every move",            "I'll cut a brand new groove"),
    ("Purple is the colour of despair",           "green is the colour beyond compare"),
    ("My name itself invokes the dread",          "your name's the one they'll dread instead"),
    ("The portal home is locked and sealed",      "I'll break it open once you're healed"),
    ("You'll beg for mercy, beg for light",       "I'll take no mercy, only fight"),
    ("I've swallowed whole a dozen runs",         "this run's the one that finally won"),
    ("My fire burns at zero kelvin",              "I'll cool your jets and send you spellin"),
    ("No item drop will tip the scale",           "I'll tip it all beyond the pale"),
    ("I am the storm, the end, the night",        "and I'm the dawn that follows night"),
    ("Your little crew won't see you home",       "I'll carry every friend I've known"),
    ("The final boss has final say",              "the final say is mine today"),
    ("Every strike you land means nothing more",  "every strike builds a higher score"),
    ("I'll scatter all your hope like dust",      "from dust I rise like I always must"),
    ("The leaderboard won't show your name",      "I'll etch my name into the frame"),
    ("Lay down your weapons, save your pride",    "I'll save my pride and never hide"),
    ("Cazarog stands eternal, vast",              "then I'm the one who ends you last"),
    ("Your journey ends inside my hall",          "I'll make this journey worth it all"),
    ("I am the dark, you are the light",          "and light will always end the night"),
    ("You'll choke on every word you said",        "I'll speak the truth until you're dead"),
    ("Step aside or be erased",                    "I'll take your place at my own pace"),
]

# ── Round configuration: (timer_seconds, label) ───────────────────────────────
ROUNDS = [
    (7.0, "ROUND 1"),
    (7.0, "ROUND 2"),
    (7.0, "ROUND 3"),
]
ROUNDS_PER_STAGE = 1   # 1 line per round → 3 lines total

PLAYER_START_HP  = 12
CAZAROG_START_HP = 24
DAMAGE_TO_CAZAROG = 2
DAMAGE_TO_PLAYER  = 1

FPS   = 60
W, H  = 1280, 720


def lerp_colour(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_text_centered(surf, text, font, colour, cx, y, shadow=None):
    if shadow:
        s = font.render(text, True, shadow)
        r = s.get_rect(centerx=cx, y=y + 2)
        surf.blit(s, r)
    s = font.render(text, True, colour)
    r = s.get_rect(centerx=cx, y=y)
    surf.blit(s, r)
    return r


def draw_health_bar(surf, x, y, w, h, current, maximum, fg, label_font, label, label_col):
    pygame.draw.rect(surf, HEALTH_BG, (x, y, w, h), border_radius=6)
    fill = int(w * max(0, current) / maximum)
    if fill > 0:
        pygame.draw.rect(surf, fg, (x, y, fill, h), border_radius=6)
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2, border_radius=6)
    txt = label_font.render(f"{label}  {current}/{maximum}", True, label_col)
    surf.blit(txt, (x, y - txt.get_height() - 4))


def shake_offset(tick, intensity):
    if intensity <= 0:
        return (0, 0)
    ox = int(math.sin(tick * 1.7) * intensity)
    oy = int(math.cos(tick * 2.3) * intensity)
    return (ox, oy)


def run_rap_battle(screen, clock, player_fighter_name="Pistachio"):
    """
    Entry point called from the main game before the Cazarog fight.
    Returns a dict: {"player_hp": int, "cazarog_hp": int, "won": bool}
    """
    pygame.display.set_caption("RAP BATTLE — Cazarog drops bars")

    # Fonts
    font_huge  = pygame.font.SysFont("Arial Black", 52, bold=True)
    font_big   = pygame.font.SysFont("Arial Black", 34, bold=True)
    font_med   = pygame.font.SysFont("Arial",       26, bold=True)
    font_small = pygame.font.SysFont("Arial",       20)
    font_timer = pygame.font.SysFont("Arial Black", 30, bold=True)

    player_hp   = PLAYER_START_HP
    cazarog_hp  = CAZAROG_START_HP

    # Build line queue: pick ROUNDS_PER_STAGE unique pairs per round
    all_pairs   = RAP_PAIRS.copy()
    random.shuffle(all_pairs)
    line_queue  = []
    used        = 0
    for round_idx, (timer_sec, round_label) in enumerate(ROUNDS):
        chunk = all_pairs[used: used + ROUNDS_PER_STAGE]
        used += ROUNDS_PER_STAGE
        for pair in chunk:
            line_queue.append((round_idx, timer_sec, round_label, pair))

    state        = "INTRO"   # INTRO → BATTLE → RESULT → DONE
    intro_timer  = 3.0
    line_idx     = 0
    typed        = ""
    time_left    = 0.0
    shake_frames = 0
    last_result  = None   # "correct" | "timeout"
    result_timer = 0.0
    bg_tick      = 0.0
    pulse        = 0.0
    current_round_label = ROUNDS[0][1]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        bg_tick += dt
        pulse   += dt

        # ── Events ─────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if state == "BATTLE" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    target = line_queue[line_idx][3][1]
                    if typed.strip().lower() == target.lower():
                        cazarog_hp  = max(0, cazarog_hp - DAMAGE_TO_CAZAROG)
                        last_result = "correct"
                    else:
                        player_hp   = max(0, player_hp - DAMAGE_TO_PLAYER)
                        last_result = "wrong"
                    result_timer = 0.8
                    typed        = ""
                    line_idx    += 1
                    if line_idx >= len(line_queue):
                        state = "RESULT"
                    else:
                        r_idx       = line_queue[line_idx][0]
                        time_left   = line_queue[line_idx][1]
                        current_round_label = line_queue[line_idx][2]
                        shake_frames = 8 if last_result == "wrong" else 0
                elif event.key == pygame.K_BACKSPACE:
                    typed = typed[:-1]
                else:
                    if len(typed) < 120:
                        typed += event.unicode

            elif state == "RESULT" and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state = "DONE"

        # ── Update ─────────────────────────────────────────────────────────
        if state == "INTRO":
            intro_timer -= dt
            if intro_timer <= 0:
                state     = "BATTLE"
                time_left = line_queue[0][1]

        elif state == "BATTLE":
            if line_idx < len(line_queue):
                time_left -= dt
                if result_timer > 0:
                    result_timer -= dt
                if time_left <= 0 and result_timer <= 0:
                    # timeout
                    player_hp   = max(0, player_hp - DAMAGE_TO_PLAYER)
                    last_result = "timeout"
                    result_timer = 0.8
                    typed        = ""
                    line_idx    += 1
                    shake_frames = 14
                    if line_idx >= len(line_queue):
                        state = "RESULT"
                    else:
                        time_left = line_queue[line_idx][1]
                        current_round_label = line_queue[line_idx][2]

            if shake_frames > 0:
                shake_frames -= 1

            if player_hp <= 0 or cazarog_hp <= 0:
                state = "RESULT"

        # ── Draw ───────────────────────────────────────────────────────────
        # animated BG
        screen.fill(DEEP_PURPLE)
        for i in range(8):
            alpha = int(30 + 20 * math.sin(bg_tick * 1.2 + i))
            r     = int(60 + 40 * math.sin(bg_tick * 0.7 + i * 0.8))
            col   = (max(0,min(255,50+r)), 0, max(0,min(255,80+r)))
            pygame.draw.circle(screen, col,
                               (int(W * (i / 8.0) + 80 * math.sin(bg_tick * 0.4 + i)),
                                int(H // 2 + 150 * math.cos(bg_tick * 0.3 + i * 1.1))),
                               int(120 + 40 * math.sin(bg_tick + i)))

        ox, oy = shake_offset(pygame.time.get_ticks() // 16, shake_frames * 1.5)

        surf = pygame.Surface((W, H), pygame.SRCALPHA)

        if state == "INTRO":
            t = 1.0 - max(0, intro_timer / 3.0)
            col = lerp_colour(WHITE, NEON_YELLOW, abs(math.sin(pulse * 4)))
            draw_text_centered(surf, "CAZAROG CHALLENGES YOU IN A RAP BATTLE!", font_big, NEON_PINK, W // 2, 200, BLACK)
            draw_text_centered(surf, "RAP BATTLE", font_huge, col, W // 2, 250, BLACK)
            draw_text_centered(surf, "Type the response line before time runs out!", font_med, NEON_CYAN, W // 2, 370)
            draw_text_centered(surf, f"Starting in {max(0, int(intro_timer)+1)}...", font_big, NEON_ORANGE, W // 2, 430, BLACK)

        elif state == "BATTLE" and line_idx < len(line_queue):
            _, timer_sec, r_label, (caz_line, resp_line) = line_queue[line_idx]

            # Round label
            pulse_col = lerp_colour(NEON_YELLOW, NEON_PINK, 0.5 + 0.5 * math.sin(pulse * 3))
            draw_text_centered(surf, r_label, font_big, pulse_col, W // 2, 18, BLACK)

            # Health bars
            draw_health_bar(surf, 60, 70, 420, 24, player_hp, PLAYER_START_HP,
                            PLAYER_COL, font_small, player_fighter_name, PLAYER_COL)
            draw_health_bar(surf, W - 480, 70, 420, 24, cazarog_hp, CAZAROG_START_HP,
                            CAZAROG_COL, font_small, "CAZAROG", CAZAROG_COL)

            # Timer bar
            frac   = max(0, time_left / timer_sec)
            t_col  = TIMER_OK if frac > 0.5 else (TIMER_WARN if frac > 0.25 else TIMER_CRIT)
            t_w    = int((W - 120) * frac)
            pygame.draw.rect(surf, (30, 10, 50), (60, 112, W - 120, 18), border_radius=5)
            if t_w > 0:
                pygame.draw.rect(surf, t_col, (60, 112, t_w, 18), border_radius=5)
            pygame.draw.rect(surf, WHITE, (60, 112, W - 120, 18), 1, border_radius=5)
            t_txt = font_timer.render(f"{max(0, time_left):.1f}s", True, t_col)
            surf.blit(t_txt, (W // 2 - t_txt.get_width() // 2, 132))

            # Cazarog's line (top section)
            caz_col = lerp_colour(CAZAROG_COL, NEON_PINK, 0.4 + 0.4 * math.sin(pulse * 2.5))
            draw_text_centered(surf, "CAZAROG:", font_med, CAZAROG_COL, W // 2, 175)
            # word-wrap Cazarog's line if long
            _render_wrapped(surf, caz_line, font_big, caz_col, W // 2, 205, W - 100, BLACK)

            # Divider
            pygame.draw.line(surf, MID_PURPLE, (100, 290), (W - 100, 290), 2)

            # Response line to type
            draw_text_centered(surf, "YOUR COMEBACK:", font_med, NEON_GREEN, W // 2, 305)
            _render_wrapped(surf, resp_line, font_big, NEON_YELLOW, W // 2, 335, W - 100, BLACK)

            # Input box
            input_rect = pygame.Rect(100, 430, W - 200, 54)
            pygame.draw.rect(surf, INPUT_BG, input_rect, border_radius=8)
            if last_result == "correct" and result_timer > 0:
                border_col = CORRECT_COL
            elif last_result in ("wrong", "timeout") and result_timer > 0:
                border_col = WRONG_COL
            else:
                border_col = INPUT_BORDER
            pygame.draw.rect(surf, border_col, input_rect, 3, border_radius=8)
            typed_surf = font_med.render(typed + ("_" if int(pulse * 4) % 2 == 0 else " "), True, WHITE)
            surf.blit(typed_surf, (input_rect.x + 14, input_rect.y + 13))

            # Feedback flash
            if result_timer > 0:
                if last_result == "correct":
                    draw_text_centered(surf, "FIRE!  +2 DMG TO CAZAROG", font_big, NEON_GREEN, W // 2, 498, BLACK)
                elif last_result == "wrong":
                    draw_text_centered(surf, "WRONG!  -1 HP", font_big, WRONG_COL, W // 2, 498, BLACK)
                elif last_result == "timeout":
                    draw_text_centered(surf, "TIME'S UP!  -1 HP", font_big, WRONG_COL, W // 2, 498, BLACK)

            # Hint
            draw_text_centered(surf, "Press ENTER to submit", font_small, (160, 120, 200), W // 2, 560)

            # Progress
            prog = font_small.render(f"Line {line_idx + 1} / {len(line_queue)}", True, (140, 100, 180))
            surf.blit(prog, (W - prog.get_width() - 20, H - 30))

        elif state == "RESULT":
            won = cazarog_hp <= 0 or (cazarog_hp < player_hp)
            if player_hp <= 0 and cazarog_hp > 0:
                won = False

            title_col = NEON_GREEN if won else NEON_PINK
            title_txt = "YOU BODIED IT!" if won else "CAZAROG WINS THE BATTLE"
            draw_text_centered(surf, title_txt, font_huge, title_col, W // 2, 180, BLACK)

            p_dmg = CAZAROG_START_HP - cazarog_hp
            c_dmg = PLAYER_START_HP  - player_hp
            draw_text_centered(surf, f"Damage dealt to Cazarog: {p_dmg}", font_big, NEON_YELLOW, W // 2, 280, BLACK)
            draw_text_centered(surf, f"Damage taken: {c_dmg}", font_big, NEON_ORANGE, W // 2, 330, BLACK)
            draw_text_centered(surf, "These carry into the boss fight!", font_med, NEON_CYAN, W // 2, 395)
            draw_text_centered(surf, "Press ENTER to continue", font_med, WHITE, W // 2, 460)

        elif state == "DONE":
            running = False

        screen.blit(surf, (ox, oy))
        pygame.display.flip()

    won = cazarog_hp < player_hp or cazarog_hp == 0
    return {
        "player_hp":   player_hp,
        "cazarog_hp":  cazarog_hp,
        "won":         won,
    }


def _render_wrapped(surf, text, font, colour, cx, y, max_w, shadow=None):
    """Render text centred, wrapping to a second line if wider than max_w."""
    words  = text.split()
    lines  = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if font.size(test)[0] <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    lh = font.get_linesize()
    for i, line in enumerate(lines):
        draw_text_centered(surf, line, font, colour, cx, y + i * lh, shadow)


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock  = pygame.time.Clock()
    result = run_rap_battle(screen, clock, "Pistachio")
    print("Result:", result)
    pygame.quit()
