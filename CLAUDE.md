# CLAUDE.md — Cozy Roguelike (czrg)

This file is read automatically by Claude Code at the start of every session.
Always refer to this document before making any changes to the codebase.

---

## Project Overview

A cozy top-down action roguelike built in Python and Pygame. The aesthetic is warm
and charming (inspired by Garden Story), but the gameplay is mechanically deep and
replayable (inspired by Hades). Target platform is desktop, with a potential future
release on itch.io.

---

## Current State of the Game

9 rooms total, structured as:

| Room | Type        | Notes                                      |
|------|-------------|--------------------------------------------|
| 1    | Normal      | 5 enemies, mixed melee/ranged              |
| 2    | Normal      | 7 enemies, more ranged                     |
| 3    | Miniboss    | Bambie the Witch                           |
| 4    | Normal      | 8 enemies, harder stats                    |
| 5    | Normal      | 9 enemies                                  |
| 6    | Miniboss    | Salomon the Stone Golem                    |
| 7    | Normal      | 9 enemies, harder stats                    |
| 8    | Normal      | 10 enemies, hardest regular room           |
| 9    | Final Boss  | Cazarog                                    |

**Selectable fighters** (chosen at character select before each run):

| Fighter   | Colour                   | HP  | Melee DMG | Melee Range | Arrow DMG | Arrows | Bomb DMG |
|-----------|--------------------------|-----|-----------|-------------|-----------|--------|----------|
| Pistachio | (95, 200, 130) green     | 10  | 1         | 36 / 54 px  | 2         | 3      | 8        |
| Cashew    | (215, 195, 155) beige    | 14  | 2         | 46 / 66 px  | 1         | 3      | 5        |
| Almond    | (190, 162, 118) brown    | 8   | 1         | 26 / 40 px  | 3         | 3      | 13       |
| NUT       | (172, 130, 58) dark gold | 100 | 10        | 36 / 54 px  | 10        | 10     | 2        |

(Melee range: base / with Attack powerup. NUT's `max_arrows` is stored in FIGHTERS and read per-instance in `Player.__init__`.)

**Player abilities:**
- 8-directional WASD movement
- SPACE — melee attack (AoE size varies by fighter, boosted further by Attack powerup)
- E — shoot arrow (up to 3 normally, 10 for NUT; recharge over time; damage varies by fighter)
- Q — throw bomb (AoE, 1 charge, slow recharge; damage varies by fighter)

**Enemy types:**
- Melee enemy — chases and deals contact damage
- Ranged enemy — keeps distance, fires fireballs
- Bambie (miniboss, room 3) — see below
- Salomon (miniboss, room 6) — see below
- Cazarog (final boss, room 9) — pre-fight **Rap Battle** (`minigame_rap.py`): 3 lines at 7s each; shows "CAZAROG CHALLENGES YOU IN A RAP BATTLE!" intro; type the response line correctly → −2 HP Cazarog, wrong/timeout → −1 HP player; damage carries into the boss fight. Boss fires fireballs and homing missiles; enrages at 50% HP spawning 4 minions

**Bambie the Witch (room 3):**
- Pre-fight: **Dance Battle** (`minigame_dance.py`) — 3 WASD sequence rounds; shows "BAMBIE CHALLENGES YOU!" intro; correct → −2 HP Bambie, wrong → −2 HP player
- Fast movement, prefers to keep distance and strafe
- Triple bolt attack: fires 3 witch bolts in a spread (−18°, 0°, +18°) toward the player
- Beam attack: freezes in place, telegraphs direction for 1.5s (glowing purple line), then fires a full-room beam dealing 2 damage — interval shortens in phase 2
- Phase 2 (50% HP): faster movement, shorter attack cooldowns, spawns 2 ranged minions

**Salomon the Stone Golem (room 6):**
- Pre-fight: **Trivia Battle** (`minigame_trivia.py`) — 3 questions; shows "SALOMON CHALLENGES YOU IN A TRIVIA BATTLE!" intro; correct → −2 HP Salomon, wrong → −1 HP player
- Slow, heavy movement
- Earthquake ability: every ~4.7s spawns 9 cracked floor tiles (orange glow) that deal 1 damage on contact; tiles last ~3.3s
- Proximity slam: if the player stays within 88px for 3 continuous seconds, Salomon fires an expanding AoE ring (130px radius, 2 damage); a red warning ring grows as the timer builds; 6s cooldown after each slam
- Phase 2 (50% HP): earthquakes escalate (14 tiles, ~2.7s interval), speed increases, spawns 2 reinforcements

**Items:**
- Health — restores 4 HP
- Speed — movement boost for ~6s
- Attack — enlarged melee hitbox for ~6s
- Invuln — brief invincibility

**Game systems:**
- Character select screen before each run (Pistachio / Cashew / Almond / NUT)
- High score leaderboard (top 20, saved to highscores.json); each entry records the fighter used, shown as a colour dot in the scores table
- Score = speed bonus + survival bonus; max 100,000 (speed 60k + survival 40k)
  - Speed bonus: 60,000 − 38 × seconds (zeroes at ~26 min)
  - Survival bonus: 40,000 − 800 × damage taken (zeroes at 50 damage)
- Pause menu (ESC during play): Resume / Restart / Quit to Menu
- Portal spawns after each non-boss room is cleared; boss rooms trigger win/next-room directly

---

## Game Design Pillars

1. **Cozy but challenging** — warm visuals, satisfying permadeath loop
2. **Replayable** — procedural generation, varied runs
3. **Readable** — the player always understands what is happening and why
4. **Juicy** — every action should have clear visual and audio feedback

---

## Tech Stack

- **Language:** Python 3
- **Framework:** Pygame
- **Version Control:** Git / GitHub (repo: ManolisNikolakakis/czrg)
- **Target:** Desktop (Mac + Windows), potential Pygbag web export for itch.io

---

## Code Architecture

| File               | Responsibility                                           |
|--------------------|----------------------------------------------------------|
| `cozy_roguelike.py`| Main game loop, state machine, score helpers             |
| `player.py`        | Player class (movement, combat, items, draw); reads fighter stats from FIGHTERS |
| `enemies.py`       | Enemy, RangedEnemy, Bambie, Salomon, Boss classes        |
| `dungeon.py`       | Room drawing, wall building, spawning, Portal class      |
| `items.py`         | Item class                                               |
| `projectiles.py`   | Projectile, PlayerArrow, Bomb classes (damage per-instance) |
| `ui.py`            | All draw functions (HUD, menus, char select, panels)     |
| `constants.py`     | All shared constants, colours, room configs, FIGHTERS    |

**Game states:** `MENU` → `CHAR_SELECT` → `PLAYING` ↔ `PAUSED` → `NAME_ENTRY` → `SCORES`

**Boss interface** — Bambie, Salomon, and Boss all share: `alive`, `hp`, `MAX_HP`, `lag_hp`,
`phase2`, `phase2_just_triggered`, `name`, `hp_bar_col`, `rect`, `cx`, `cy`,
`projectiles`, `update(player, walls)`, `take_damage(n)`, `draw(surf, tick)`,
`draw_projectiles(surf, tick)`.

**Fighter system** — `FIGHTERS` list in `constants.py` is the single source of truth for all
per-fighter stats. `Player.__init__(fighter_name)` looks up its stats from there.
`PlayerArrow` and `Bomb` accept a `damage` parameter at construction time so per-fighter
ranged damage flows through without touching the projectile classes.
`MAX_ARROWS` is set per-instance in `Player.__init__` via `f.get('max_arrows', 3)` — only
fighters that need a non-default arrow count (e.g. NUT = 10) need the key in FIGHTERS.

**Rules:**
- Always keep code modular — separate files per domain
- Never put everything in one file
- Use clear, descriptive names
- Add a comment only when the WHY is non-obvious
- Always check for and fix existing bugs before adding new features

---

## Art & Music

- All pixel art is **human-made** by the developer — do not suggest or use AI-generated art
- All music is **human-made** by the developer — do not suggest or use AI-generated music
- Placeholder art should use simple coloured rectangles with a warm colour palette

---

## Placeholder Art Colour Palette

| Element          | Colour (RGB)               |
|------------------|----------------------------|
| Pistachio player | (95, 200, 130) green       |
| Cashew player    | (215, 195, 155) beige      |
| Almond player    | (190, 162, 118) light brown|
| NUT player       | (172, 130, 58) dark gold   |
| Melee enemy      | (210, 75, 75) red          |
| Ranged enemy     | (200, 155, 40) orange      |
| Bambie           | (130, 55, 190) purple      |
| Salomon          | (108, 96, 84) stone grey   |
| Cazarog          | (120, 40, 170) purple      |
| Health item      | (220, 80, 80) bright red   |
| Powerup          | (80, 160, 220) blue        |
| Arrow            | (190, 245, 80) yellow-green|
| Witch bolt       | (180, 70, 230) purple      |
| Hazard tile      | (200, 75, 15) lava orange  |
| Floor            | (42, 36, 30) dark brown    |
| Walls            | (78, 70, 62) brown         |
| Bambie's room    | (28, 22, 38) dark purple   |
| Salomon's room   | (46, 41, 35) stone floor   |
| Cazarog's room   | (38, 28, 28) blood floor   |

---

## Current Feature Roadmap

### Done ✅
- [x] Player movement (8-directional WASD)
- [x] Melee combat (AoE and damage vary by fighter)
- [x] Arrow and bomb projectiles (damage varies by fighter)
- [x] Character select screen — Pistachio, Cashew, Almond, NUT
- [x] 9-room structure with 3 boss rooms
- [x] Ranged enemies with fireballs
- [x] Bambie the Witch (miniboss, room 3) — triple bolts + telegraphed beam
- [x] Salomon the Stone Golem (miniboss, room 6)
- [x] Cazarog (final boss, room 9, 40 HP) with phase 2
- [x] Health items and powerups
- [x] High score leaderboard (top 20) — records fighter used
- [x] Score formula: max 100,000 (speed 60k + survival 40k)
- [x] Win screen with score calculation and name entry
- [x] Pause menu
- [x] 1280×720 resolution (40×22 tile room)

### Up Next 🔧
- [ ] Procedural dungeon generation
- [ ] More enemy variety
- [ ] Player character progression between rooms
- [ ] Sound effects and music hooks
- [ ] Polish pass (screenshake, hit flash, particles)
- [ ] Pygbag web export for itch.io

---

## Session Workflow

When starting a new session:
1. Read this file fully
2. Run the game to check current state
3. Fix any bugs noticed before adding new features
4. Work on the next unchecked item in the roadmap above, unless instructed otherwise

When finishing a session:
1. Make sure the game runs without errors
2. Commit all changes with a descriptive git commit message
3. Update the roadmap checkboxes in this file if features were completed

---

## Important Don'ts

- Don't break existing features when adding new ones — always test after changes
- Don't use external assets or libraries beyond Pygame and Python standard library
- Don't generate large monolithic files — keep modules small and focused
- Don't add features not discussed with the developer without flagging them first
