import pygame
import sys
import json

from constants import (
    SCREEN_W, SCREEN_H, FPS, TOTAL_ROOMS,
    SCORES_FILE, MENU, CHAR_SELECT, PLAYING, TRIVIA, PAUSED, NAME_ENTRY, SCORES,
    OVERLAY_R, OVERLAY_W, SPEED_COL, FIGHTERS,
)
from minigame_trivia import TriviaMinigame
from minigame_dance  import run_dance_battle
from minigame_rap    import (run_rap_battle,
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
                      draw_char_select)

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

    ne            = None
    highlight_idx = -1
    tick          = 0
    pause_sel     = 0
    trivia        = None

    def _reset():
        nonlocal walls, player, enemies, items, boss
        nonlocal player_arrows, player_bombs
        nonlocal game_over, won, elapsed, room_num, portal
        nonlocal final_score, speed_bonus, survival_bonus, session_best
        nonlocal banner_timer, banner_text
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
                        menu_sel = (menu_sel - 1) % 3
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        menu_sel = (menu_sel + 1) % 3
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if menu_sel == 0:
                            state = CHAR_SELECT
                        elif menu_sel == 1:
                            highlight_idx    = -1
                            scores_from_game = False
                            state            = SCORES
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
                                run_hub(screen, clock, font, font_big, font_title)
                                state = CHAR_SELECT
                        elif event.key == pygame.K_ESCAPE:
                            state = MENU

                elif state == PAUSED:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        pause_sel = (pause_sel - 1) % 3
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        pause_sel = (pause_sel + 1) % 3
                    elif event.key == pygame.K_ESCAPE:
                        state = PLAYING
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if pause_sel == 0:
                            state = PLAYING
                        elif pause_sel == 1:
                            _reset()
                            state = PLAYING
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
                            run_hub(screen, clock, font, font_big, font_title)
                            state = CHAR_SELECT
                        else:
                            state = MENU

        # ── Game update ───────────────────────────────────────────────────────
        if state == PLAYING and not game_over and not won:
            keys = pygame.key.get_pressed()
            dx = (int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
                  - int(keys[pygame.K_a] or keys[pygame.K_LEFT]))
            dy = (int(keys[pygame.K_s] or keys[pygame.K_DOWN])
                  - int(keys[pygame.K_w] or keys[pygame.K_UP]))

            player.move(dx, dy, walls)
            player.update()

            # Item pickup
            for item in items[:]:
                if player.rect.inflate(4, 4).colliderect(item.rect):
                    player.apply_item(item.kind)
                    items.remove(item)

            # Enemy updates + melee attack hits
            for e in enemies:
                e.update(player, walls)
                if player.attack_rect and e.alive and player.attack_rect.colliderect(e.rect):
                    e.take_damage(player.melee_dmg)
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
                boss.update(player, walls)
                if player.attack_rect and player.attack_rect.colliderect(boss.rect):
                    boss.take_damage(player.melee_dmg)
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

            # Portal spawns when room is cleared (non-final rooms only)
            if not enemies and boss is None and portal is None:
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
                if room_num == 6:
                    # Trivia duel before Salomon fight
                    trivia       = TriviaMinigame(player)
                    state        = TRIVIA
                    banner_timer = 0
                elif room_num == 3:
                    # Dance battle before Bambie fight (blocking inner loop)
                    survived = run_dance_battle(
                        screen, clock, font, font_big, font_title, player, boss)
                    if not survived:
                        game_over = True
                        final_score, speed_bonus, survival_bonus = calculate_score(
                            elapsed, player.total_damage)
                    else:
                        banner_text  = "BAMBIE AWAITS…"
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

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
