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

- 3 dungeon rooms + a final boss room
- Melee and ranged enemies
- Arrow projectiles
- Powerups and health items
- High score leaderboard

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

## Code Architecture Rules

- Always keep code modular — separate files for player, enemies, dungeon, UI, items, projectiles
- Never put everything in one file
- Each module should be independently readable and testable
- Use clear, descriptive variable and function names
- Add a brief comment above any non-obvious logic
- Always check for and fix any existing bugs before adding new features

---

## Art & Music

- All pixel art is **human-made** by the developer — do not suggest or use AI-generated art
- All music is **human-made** by the developer — do not suggest or use AI-generated music
- Placeholder art should use simple coloured rectangles with a warm colour palette
- Warm palette reference: soft greens, warm yellows, earthy browns, muted reds

---

## Placeholder Art Colour Palette

| Element        | Colour (RGB)         |
|----------------|----------------------|
| Player         | (100, 180, 100) green|
| Melee enemy    | (180, 80, 80) red    |
| Ranged enemy   | (180, 120, 60) orange|
| Boss           | (140, 60, 140) purple|
| Health item    | (220, 80, 80) bright red |
| Powerup        | (80, 160, 220) blue  |
| Arrow          | (220, 200, 80) yellow|
| Floor          | (60, 50, 40) dark brown |
| Walls          | (40, 35, 30) darker brown |

---

## Current Feature Roadmap

### Done ✅
- [x] Player movement (8-directional WASD)
- [x] Melee combat
- [x] 3 dungeon rooms + boss room
- [x] Ranged enemies with arrow projectiles
- [x] Health items and powerups
- [x] High score leaderboard

### Up Next 🔧
- [ ] Main menu screen
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
