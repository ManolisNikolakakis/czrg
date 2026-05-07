import pygame
import sys
import json
import random
import math

from constants import (
    SCREEN_W, SCREEN_H, FPS, TOTAL_ROOMS,
    SCORES_FILE, MENU, CHAR_SELECT, PLAYING, TRIVIA, PAUSED, NAME_ENTRY, SCORES, CREDITS,
    CONTROLS,
    OVERLAY_R, OVERLAY_W, SPEED_COL, FIGHTERS,
)
from minigame_trivia   import TriviaMinigame
from minigame_dance    import run_dance_battle
from minigame_fishing  import run_fishing_battle
from minigame_shooting import run_shooting_battle
from minigame_rap      import (run_rap_battle,
                              PLAYER_START_HP as RAP_PLAYER_HP,
                              CAZAROG_START_HP as RAP_CAZ_HP)
from hub import run_hub
from dungeon  import (Portal, build_walls, draw_room,
                      spawn_boss_minions, spawn_salomon_minions,
                      spawn_bambie_minions,
                      spawn_items, setup_room, new_game)
from enemies  import Salomon, Bambie
from ui       import (NameEntry, draw_hud, draw_boss_bar, draw_end_panel,
                      draw_room_banner, draw_menu, draw_scores_screen,
                      draw_name_entry_screen, draw_pause_screen,
                      draw_char_select, draw_credits_screen,
                      draw_controls_screen)

pygame.init()


# ── Score helpers ─────────────────────────────────────────────────────────────

def load_scores():
    try:
        with open(SCORES_FILE) as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x['score'], reverse=True)[:20]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return []

def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f)

def is_top20(score, scores):
    return len(scores) < 20 or score > scores[-1]['score']

def insert_score(name, score, scores, fighter='Pistachio'):
    entry    = {'name': name[:20] or 'PLAYER', 'score': score, 'fighter': fighter}
    combined = scores + [entry]
    combined.sort(key=lambda x: x['score'], reverse=True)
    combined = combined[:20]
    idx = next((i for i, s in enumerate(combined) if s is entry), -1)
    return combined, idx

def calculate_score(elapsed_ticks, damage_taken):
    secs           = elapsed_ticks / FPS
    speed_bonus    = max(0, 60000 - int(secs * 38))   # zeroes out after ~26 min
    survival_bonus = max(0, 40000 - damage_taken * 800) # zeroes out after 50 dmg
    return speed_bonus + survival_bonus, speed_bonus, survival_bonus


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    screen     = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Cozy Roguelike")
    clock      = pygame.time.Clock()
    font       = pygame.font.SysFont(None, 22)
    font_big   = pygame.font.SysFont(None, 40)
    font_title = pygame.font.SysFont(None, 58)

    scores = load_scores()
    state  = MENU
    menu_sel = 0
    char_sel = 0
    selected_fighter  = FIGHTERS[0]['name']
    scores_from_game  = False

    walls = player = enemies = items = boss = None
    game_over = won = False
    elapsed      = 0
    final_score  = speed_bonus = survival_bonus = 0
    session_best = 0
    room_num     = 1
    portal       = None
    banner_timer = 0
    banner_text  = ""
    player_arrows = []
    player_bombs  = []

    ne             = None
    highlight_idx  = -1
    tick           = 0
    pause_sel      = 0
    trivia         = None
    controls_from  = MENU

    # Minigame assignment: picked fresh each run (pre-generated before the hub so
    # the hub NPCs can hint at what's coming next).
    bambie_minigame  = 'dance'    # 'dance' | 'fishing' | 'shooting'
    salomon_minigame = 'trivia'   # 'trivia' | 'fishing' | 'shooting'
    pending_minigames = None      # (bambie_game, salomon_game) pre-generated for next run

    def _pick_minigames():
        """Pick one minigame for Bambie and one for Salomon with no shared game."""
        b_pool = ['dance', 'fishing', 'shooting']
        b      = random.choice(b_pool)
        s_pool = ['trivia', 'fishing', 'shooting']
        if b in s_pool:
            s_pool = [g for g in s_pool if g != b]
        return b, random.choice(s_pool)

    def _reset():
        nonlocal walls, player, enemies, items, boss
        nonlocal player_arrows, player_bombs
        nonlocal game_over, won, elapsed, room_num, portal
        nonlocal final_score, speed_bonus, survival_bonus, session_best
        nonlocal banner_timer, banner_text
        nonlocal bambie_minigame, salomon_minigame, pending_minigames
        if pending_minigames is not None:
            bambie_minigame, salomon_minigame = pending_minigames
            pending_minigames = None
        else:
            bambie_minigame, salomon_minigame = _pick_minigames()
        walls, player, enemies, items, boss = new_game(selected_fighter)
        player_arrows = []
        player_bombs  = []
        game_over = won = False
        elapsed   = 0
        room_num  = 1
        portal    = None
        final_score = speed_bonus = survival_bonus = 0
        session_best = scores[0]['score'] if scores else 0
        banner_timer = 0
        banner_text  = ""

    while True:
        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if state == MENU:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        menu_sel = (menu_sel - 1) % 5
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        menu_sel = (menu_sel + 1) % 5
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if menu_sel == 0:
                            pending_minigames = _pick_minigames()
                            run_hub(screen, clock, font, font_big, font_title,
                                    next_minigames={'bambie':  pending_minigames[0],
                                                    'salomon': pending_minigames[1]})
                            state = CHAR_SELECT
                        elif menu_sel == 1:
                            highlight_idx    = -1
                            scores_from_game = False
                            state            = SCORES
                        elif menu_sel == 2:
                            controls_from = MENU
                            state         = CONTROLS
                        elif menu_sel == 3:
                            state = CREDITS
                        else:
                            pygame.quit()
                            sys.exit()

                elif state == CHAR_SELECT:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        char_sel = (char_sel - 1) % len(FIGHTERS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        char_sel = (char_sel + 1) % len(FIGHTERS)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        selected_fighter = FIGHTERS[char_sel]['name']
                        _reset()
                        state = PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        state = MENU

                elif state == TRIVIA:
                    trivia.handle_key(event.key)
                    if trivia._done_ready:
                        player.hp = trivia.player_hp
                        if trivia.result == 'win':
                            state = PLAYING
                            banner_text  = "SALOMON AWAITS…"
                            banner_timer = 100
                        else:
                            player.hp = 0
                            game_over  = True
                            final_score, speed_bonus, survival_bonus = calculate_score(
                                elapsed, player.total_damage)
                            state = PLAYING

                elif state == PLAYING:
                    if not game_over and not won:
                        if event.key == pygame.K_SPACE:
                            player.attack()
                        elif event.key == pygame.K_e:
                            a = player.shoot_arrow()
                            if a:
                                player_arrows.append(a)
                        elif event.key == pygame.K_q:
                            b = player.shoot_bomb()
                            if b:
                                player_bombs.append(b)
                        elif event.key == pygame.K_r:
                            if player.use_superpower():
                                if player.fighter == 'NUT':
                                    for e in enemies:
                                        e.alive = False
                                    enemies = []
                                    if boss and boss.alive:
                                        boss.take_damage(9999)
                        elif event.key == pygame.K_ESCAPE:
                            pause_sel = 0
                            state = PAUSED
                    else:
                        if event.key == pygame.K_r:
                            if won and is_top20(final_score, scores):
                                ne               = NameEntry(final_score)
                                scores_from_game = True
                                state            = NAME_ENTRY
                            else:
                                pending_minigames = _pick_minigames()
                                run_hub(screen, clock, font, font_big, font_title,
                                        next_minigames={'bambie':  pending_minigames[0],
                                                        'salomon': pending_minigames[1]})
                                state = CHAR_SELECT
                        elif event.key == pygame.K_ESCAPE:
                            state = MENU

                elif state == PAUSED:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        pause_sel = (pause_sel - 1) % 4
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        pause_sel = (pause_sel + 1) % 4
                    elif event.key == pygame.K_ESCAPE:
                        state = PLAYING
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if pause_sel == 0:
                            state = PLAYING
                        elif pause_sel == 1:
                            _reset()
                            state = PLAYING
                        elif pause_sel == 2:
                            controls_from = PAUSED
                            state         = CONTROLS
                        else:
                            state = MENU

                elif state == NAME_ENTRY:
                    if event.key == pygame.K_ESCAPE:
                        state = MENU
                    elif ne.handle(event):
                        scores, highlight_idx = insert_score(
                            ne.name, ne.score, scores, player.fighter)
                        save_scores(scores)
                        state = SCORES

                elif state == SCORES:
                    if event.key == pygame.K_ESCAPE:
                        highlight_idx = -1
                        state = MENU
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r):
                        highlight_idx = -1
                        if scores_from_game:
                            scores_from_game = False
                            pending_minigames = _pick_minigames()
                            run_hub(screen, clock, font, font_big, font_title,
                                    next_minigames={'bambie':  pending_minigames[0],
                                                    'salomon': pending_minigames[1]})
                            state = CHAR_SELECT
                        else:
                            state = MENU

                elif state == CREDITS:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                        state = MENU

                elif state == CONTROLS:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                        state = controls_from

        # ── Game update ───────────────────────────────────────────────────────
        if state == PLAYING and not game_over and not won:
            keys = pygame.key.get_pressed()
            dx = (int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
                  - int(keys[pygame.K_a] or keys[pygame.K_LEFT]))
            dy = (int(keys[pygame.K_s] or keys[pygame.K_DOWN])
                  - int(keys[pygame.K_w] or keys[pygame.K_UP]))

            player.move(dx, dy, walls)
            player.update()
            player_arrows.extend(player.sp_arrows_pending)

            # Item pickup
            for item in items[:]:
                if player.rect.inflate(4, 4).colliderect(item.rect):
                    player.apply_item(item.kind)
                    items.remove(item)

            # Pistachio freeze: non-friendly enemies and boss are paused
            pistachio_freeze = (player.fighter == 'Pistachio' and player.sp_timer > 0)

            # Enemy updates + melee attack hits
            for e in enemies:
                if e.friendly:
                    # Chase nearest non-friendly enemy and deal contact damage
                    if e.iframes:
                        e.iframes -= 1
                    targets = [t for t in enemies
                               if t is not e and t.alive and not t.friendly]
                    if targets:
                        t = min(targets,
                                key=lambda t: math.hypot(t.cx - e.cx, t.cy - e.cy))
                        dx = t.cx - e.cx
                        dy = t.cy - e.cy
                        dist = math.hypot(dx, dy)
                        if dist > 4:
                            nx, ny = dx / dist, dy / dist
                            e.x += nx * e.speed
                            for w in walls:
                                if e.rect.colliderect(w):
                                    e.x = w.right if nx < 0 else w.left - e.W
                            e.y += ny * e.speed
                            for w in walls:
                                if e.rect.colliderect(w):
                                    e.y = w.bottom if ny < 0 else w.top - e.H
                        if e.rect.colliderect(t.rect):
                            t.take_damage(1)
                elif pistachio_freeze:
                    if e.iframes:
                        e.iframes -= 1
                else:
                    e.update(player, walls)
                    # Non-friendly enemies deal contact damage to friendly ones
                    for f in enemies:
                        if f.friendly and f.alive and e.rect.colliderect(f.rect):
                            f.take_damage(1)

                # Melee hit
                if player.attack_rect and e.alive and player.attack_rect.colliderect(e.rect):
                    if not e.friendly:
                        if pistachio_freeze and player.sp_converts_left > 0:
                            e.friendly = True
                            if hasattr(e, 'projectiles'):
                                e.projectiles.clear()
                            player.sp_converts_left -= 1
                        else:
                            e.take_damage(player.eff_melee_dmg)
            enemies = [e for e in enemies if e.alive]

            # Player projectiles
            for a in player_arrows:
                a.update(enemies, boss)
            player_arrows = [a for a in player_arrows if a.alive]

            for b in player_bombs:
                b.update(enemies, boss)
            player_bombs = [b for b in player_bombs if b.alive]

            # Boss
            if boss and boss.alive:
                if not pistachio_freeze:
                    boss.update(player, walls)
                    # Boss deals contact damage to friendly enemies
                    for f in enemies:
                        if f.friendly and f.alive and boss.rect.colliderect(f.rect):
                            f.take_damage(1)
                if player.attack_rect and player.attack_rect.colliderect(boss.rect):
                    boss.take_damage(player.eff_melee_dmg)
                if boss.phase2_just_triggered:
                    boss.phase2_just_triggered = False
                    if isinstance(boss, Salomon):
                        enemies.extend(spawn_salomon_minions())
                        banner_text = "SALOMON ENRAGED!"
                    elif isinstance(boss, Bambie):
                        enemies.extend(spawn_bambie_minions())
                        banner_text = "BAMBIE ENRAGED!"
                    else:
                        enemies.extend(spawn_boss_minions())
                        banner_text = "CAZAROG ENRAGED!"
                    banner_timer = 100
            # Nullify boss regardless of how it died (melee OR projectile kill)
            if boss and not boss.alive:
                boss = None

            # Portal spawns when no hostile enemies remain (friendlies don't block it)
            if all(e.friendly for e in enemies) and boss is None and portal is None:
                if room_num < TOTAL_ROOMS:
                    portal = Portal()
                elif not won:
                    won = True
                    final_score, speed_bonus, survival_bonus = calculate_score(
                        elapsed, player.total_damage)

            # Portal entry
            if portal and player.rect.inflate(4, 4).colliderect(portal.rect):
                room_num      += 1
                enemies, boss  = setup_room(room_num)
                items          = spawn_items()
                portal         = None
                player.place_at_center()
                player.reset_superpower()
                if room_num == 3:
                    # Pre-fight minigame for Bambie (blocking)
                    if bambie_minigame == 'dance':
                        survived = run_dance_battle(
                            screen, clock, font, font_big, font_title, player, boss)
                    elif bambie_minigame == 'fishing':
                        survived = run_fishing_battle(
                            screen, clock, font, font_big, font_title, player, boss)
                    else:  # shooting
                        survived = run_shooting_battle(
                            screen, clock, font, font_big, font_title, player, boss)
                    if not survived:
                        game_over = True
                        final_score, speed_bonus, survival_bonus = calculate_score(
                            elapsed, player.total_damage)
                    else:
                        banner_text  = "BAMBIE AWAITS…"
                        banner_timer = 100
                elif room_num == 6:
                    # Pre-fight minigame for Salomon
                    if salomon_minigame == 'trivia':
                        trivia       = TriviaMinigame(player)
                        state        = TRIVIA
                        banner_timer = 0
                    else:
                        if salomon_minigame == 'fishing':
                            survived = run_fishing_battle(
                                screen, clock, font, font_big, font_title, player, boss)
                        else:  # shooting
                            survived = run_shooting_battle(
                                screen, clock, font, font_big, font_title, player, boss)
                        if not survived:
                            game_over = True
                            final_score, speed_bonus, survival_bonus = calculate_score(
                                elapsed, player.total_damage)
                        else:
                            banner_text  = "SALOMON AWAITS…"
                            banner_timer = 100
                elif room_num == TOTAL_ROOMS:
                    # Rap battle before Cazarog fight
                    result = run_rap_battle(screen, clock, player.fighter)
                    rap_player_dmg = RAP_PLAYER_HP - result["player_hp"]
                    rap_caz_dmg    = RAP_CAZ_HP    - result["cazarog_hp"]
                    player.hp          -= rap_player_dmg
                    player.total_damage += rap_player_dmg
                    if boss:
                        boss.take_damage(rap_caz_dmg)
                    if player.hp <= 0:
                        game_over = True
                        final_score, speed_bonus, survival_bonus = calculate_score(
                            elapsed, player.total_damage)
                    else:
                        banner_text  = "CAZAROG AWAITS…"
                        banner_timer = 100
                else:
                    banner_text  = f"Room {room_num} / {TOTAL_ROOMS}"
                    banner_timer = 100

            if player.hp <= 0:
                game_over = True
                final_score, speed_bonus, survival_bonus = calculate_score(
                    elapsed, player.total_damage)

            elapsed      += 1
            banner_timer  = max(0, banner_timer - 1)

        # ── Trivia update ─────────────────────────────────────────────────────
        if state == TRIVIA and trivia:
            trivia.update()

        # ── Draw ──────────────────────────────────────────────────────────────
        tick += 1

        if state == MENU:
            draw_menu(screen, font, font_big, font_title, menu_sel, scores)

        elif state == CHAR_SELECT:
            draw_char_select(screen, font, font_big, font_title, FIGHTERS, char_sel)

        elif state == TRIVIA:
            if trivia:
                trivia.draw(screen, font, font_big, font_title, tick)

        elif state == PLAYING:
            screen.fill((10, 8, 12))
            draw_room(screen, walls, room_num)

            for item in items:        item.draw(screen, tick)
            for a in player_arrows:   a.draw(screen)
            for e in enemies:         e.draw_projectiles(screen, tick)
            if boss:                  boss.draw_projectiles(screen, tick)
            for b in player_bombs:    b.draw(screen, tick)
            if portal:                portal.draw(screen, tick)
            for e in enemies:         e.draw(screen)
            if boss:                  boss.draw(screen, tick)
            player.draw(screen)

            draw_hud(screen, font, player, enemies, elapsed,
                     scores[0]['score'] if scores else 0,
                     room_num, portal, boss)
            draw_boss_bar(screen, font, font_big, boss)

            best_sc = scores[0]['score'] if scores else 0
            if game_over:
                draw_end_panel(screen, font, font_big, "GAME OVER", OVERLAY_R,
                               elapsed, player.total_damage,
                               final_score, speed_bonus, survival_bonus, best_sc)
            elif won:
                win_hint = ("R enter name   ESC menu"
                            if is_top20(final_score, scores) else "R restart   ESC menu")
                draw_end_panel(screen, font, font_big, "YOU WIN!", OVERLAY_W,
                               elapsed, player.total_damage,
                               final_score, speed_bonus, survival_bonus, best_sc, win_hint)

            draw_room_banner(screen, font_big, banner_text, banner_timer)

        elif state == PAUSED:
            # Draw frozen game world underneath the overlay
            screen.fill((10, 8, 12))
            draw_room(screen, walls, room_num)
            for item in items:        item.draw(screen, tick)
            for a in player_arrows:   a.draw(screen)
            for e in enemies:         e.draw_projectiles(screen, tick)
            if boss:                  boss.draw_projectiles(screen, tick)
            for b in player_bombs:    b.draw(screen, tick)
            if portal:                portal.draw(screen, tick)
            for e in enemies:         e.draw(screen)
            if boss:                  boss.draw(screen, tick)
            player.draw(screen)
            draw_hud(screen, font, player, enemies, elapsed,
                     scores[0]['score'] if scores else 0,
                     room_num, portal, boss)
            draw_boss_bar(screen, font, font_big, boss)
            draw_pause_screen(screen, font, font_big, pause_sel)

        elif state == NAME_ENTRY:
            draw_name_entry_screen(screen, font, font_big, ne, tick)

        elif state == SCORES:
            draw_scores_screen(screen, font, font_big, scores, highlight_idx)

        elif state == CREDITS:
            draw_credits_screen(screen, font, font_big, font_title)

        elif state == CONTROLS:
            draw_controls_screen(screen, font, font_big, font_title,
                                 from_pause=(controls_from == PAUSED))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
