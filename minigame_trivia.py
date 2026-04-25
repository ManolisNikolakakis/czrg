import pygame
import random
import math

from constants import (
    SCREEN_W, SCREEN_H,
    UI_WHITE, UI_MUTED, GOLD_COL, HP_BG, HP_FG,
    ATTACK_BCOL, PLAYER_ARROW_C, BOMB_COL,
)

# ── Colours ───────────────────────────────────────────────────────────────────
CORRECT_COL  = (75,  200, 100)
WRONG_COL    = (210, 60,  60)
OPTION_BG    = (38,  32,  26)
STONE_BG     = (46,  41,  35)
STONE_GRID   = (58,  52,  44)
SALOMON_DARK = (108, 96,  84)
SALOMON_OUT  = (158, 142, 125)
BUBBLE_BG    = (30,  26,  22)
BUBBLE_EDGE  = (125, 105, 78)

# ── 100-question pool ─────────────────────────────────────────────────────────
# Each entry: {'q': str, 'opts': [A, B, C, D], 'answer': int (0-indexed)}
QUESTION_POOL = [
    {'q': "What year was Pong first released?",
     'opts': ["1968", "1970", "1972", "1975"], 'answer': 2},

    {'q': "Who is the playable hero in The Legend of Zelda?",
     'opts': ["Zelda", "Ganondorf", "Impa", "Link"], 'answer': 3},

    {'q': "What colour is Sonic the Hedgehog?",
     'opts': ["Red", "Blue", "Green", "Yellow"], 'answer': 1},

    {'q': "Which company created the Mario franchise?",
     'opts': ["Sega", "Atari", "Capcom", "Nintendo"], 'answer': 3},

    {'q': "In which game do you play as Gordon Freeman?",
     'opts': ["Quake", "Doom", "Half-Life", "Duke Nukem"], 'answer': 2},

    {'q': "What types is Charizard in the original Pokémon games?",
     'opts': ["Fire/Dragon", "Fire only", "Fire/Ground", "Fire/Flying"], 'answer': 3},

    {'q': "What is the name of the princess kidnapped in Donkey Kong (1981)?",
     'opts': ["Peach", "Zelda", "Pauline", "Rosalina"], 'answer': 2},

    {'q': "Which company developed the original Sonic the Hedgehog?",
     'opts': ["Nintendo", "Sega", "Atari", "Namco"], 'answer': 1},

    {'q': "What year was Space Invaders first released?",
     'opts': ["1975", "1976", "1978", "1980"], 'answer': 2},

    {'q': "What are the Dragonborn's special voice powers called in Skyrim?",
     'opts': ["Spells", "Blessings", "Powers", "Shouts"], 'answer': 3},

    {'q': "What game features the underwater city of Rapture?",
     'opts': ["SOMA", "Subnautica", "BioShock", "Aquaria"], 'answer': 2},

    {'q': "What year was the original Super Mario Bros. released?",
     'opts': ["1983", "1984", "1985", "1986"], 'answer': 2},

    {'q': "Which green enemy from Minecraft explodes when near the player?",
     'opts': ["Spider", "Creeper", "Zombie", "Skeleton"], 'answer': 1},

    {'q': "What is the name of Link's fairy companion in Ocarina of Time?",
     'opts': ["Navi", "Tatl", "Fi", "Midna"], 'answer': 0},

    {'q': "In Street Fighter II, which character uses the 'Yoga Fire'?",
     'opts': ["Ryu", "Guile", "Dhalsim", "Blanka"], 'answer': 2},

    {'q': "What game popularised the battle royale genre on PC?",
     'opts': ["Fortnite", "Apex Legends", "PUBG", "H1Z1"], 'answer': 2},

    {'q': "How many Pokémon are in the original Generation I Pokédex?",
     'opts': ["149", "150", "151", "152"], 'answer': 2},

    {'q': "What year was Halo: Combat Evolved released?",
     'opts': ["1999", "2000", "2001", "2002"], 'answer': 2},

    {'q': "Which game features the spaceship Normandy SR-2?",
     'opts': ["Star Wars: KOTOR", "Mass Effect", "No Man's Sky", "Halo"], 'answer': 1},

    {'q': "What is the name of the AI villain in Portal?",
     'opts': ["SHODAN", "HAL", "GLaDOS", "ARIA"], 'answer': 2},

    {'q': "What year was Pac-Man first released?",
     'opts': ["1978", "1979", "1980", "1981"], 'answer': 2},

    {'q': "What material is used to build a Nether portal in Minecraft?",
     'opts': ["Iron Blocks", "Gold Blocks", "Obsidian", "Diamond Blocks"], 'answer': 2},

    {'q': "Which studio made the original Doom (1993)?",
     'opts': ["Valve", "Rare", "id Software", "Epic Games"], 'answer': 2},

    {'q': "Who is the main antagonist in Final Fantasy VII?",
     'opts': ["Kefka", "Sephiroth", "Golbez", "Exdeath"], 'answer': 1},

    {'q': "What is the name of the spaceship in Dead Space?",
     'opts': ["USG Ishimura", "Nostromo", "Sulaco", "Sevastopol"], 'answer': 0},

    {'q': "'It's dangerous to go alone! Take this.' is from which game?",
     'opts': ["Super Mario Bros.", "Mega Man", "The Legend of Zelda", "Castlevania"], 'answer': 2},

    {'q': "What is the highest rank in CS:GO?",
     'opts': ["Global Elite", "Supreme Master", "Legendary Eagle", "Grand Master"], 'answer': 0},

    {'q': "How many players start a standard Fortnite solo match?",
     'opts': ["50", "75", "100", "125"], 'answer': 2},

    {'q': "What year was the first Grand Theft Auto released?",
     'opts': ["1996", "1997", "1998", "1999"], 'answer': 1},

    {'q': "What is the name of the AI companion in Halo?",
     'opts': ["Aria", "Cortana", "IRIS", "Oracle"], 'answer': 1},

    {'q': "Which studio developed The Last of Us?",
     'opts': ["Santa Monica Studio", "Insomniac Games", "Naughty Dog", "Sucker Punch"], 'answer': 2},

    {'q': "What is the name of the main character in the God of War series?",
     'opts': ["Ares", "Atlas", "Kratos", "Heracles"], 'answer': 2},

    {'q': "In Super Smash Bros., what does picking up a Smash Ball allow you to do?",
     'opts': ["Become invisible", "Use your Final Smash", "Triple your speed", "Heal fully"], 'answer': 1},

    {'q': "What year was Tetris originally created?",
     'opts': ["1982", "1983", "1984", "1985"], 'answer': 2},

    {'q': "Which game is set in the futuristic city of Night City?",
     'opts': ["Deus Ex", "Watch Dogs", "Cyberpunk 2077", "Mirror's Edge"], 'answer': 2},

    {'q': "What is the name of the currency in Dark Souls?",
     'opts': ["Runes", "Gold", "Souls", "Echoes"], 'answer': 2},

    {'q': "Which game features 'Fatality' finishing moves?",
     'opts': ["Street Fighter", "Tekken", "Mortal Kombat", "Dead or Alive"], 'answer': 2},

    {'q': "In Mario Kart, what colour shell targets the player in first place?",
     'opts': ["Red", "Green", "Blue", "Yellow"], 'answer': 2},

    {'q': "What year was the PlayStation 4 released in North America?",
     'opts': ["2011", "2012", "2013", "2014"], 'answer': 2},

    {'q': "In game terminology, what does 'RPG' stand for?",
     'opts': ["Rapid Progression Game", "Role Playing Game", "Random Player Game", "Reactive Play Game"], 'answer': 1},

    {'q': "In Stardew Valley, who leaves you the farm at the start?",
     'opts': ["Your father", "Your mother", "Your grandfather", "Your uncle"], 'answer': 2},

    {'q': "Who is the protagonist in Red Dead Redemption 2?",
     'opts': ["John Marston", "Arthur Morgan", "Dutch van der Linde", "Bill Williamson"], 'answer': 1},

    {'q': "Which studio developed the BioShock series?",
     'opts': ["Irrational Games", "Obsidian", "Eidos", "2K Marin"], 'answer': 0},

    {'q': "What is Pikachu's evolved form in Pokémon?",
     'opts': ["Raichu", "Jolteon", "Electabuzz", "Plusle"], 'answer': 0},

    {'q': "Which game features the protagonist Geralt of Rivia?",
     'opts': ["Dragon Age", "The Witcher", "Divinity", "Pillars of Eternity"], 'answer': 1},

    {'q': "What is the primary enemy faction in the original Halo?",
     'opts': ["The Flood", "The Covenant", "The Prometheans", "The Banished"], 'answer': 1},

    {'q': "In which game do you play as Joel and Ellie?",
     'opts': ["Uncharted", "The Last of Us", "Days Gone", "Ghost of Tsushima"], 'answer': 1},

    {'q': "What year was Minecraft officially released out of beta?",
     'opts': ["2010", "2011", "2012", "2013"], 'answer': 1},

    {'q': "Which real-world city is GTA: Vice City primarily based on?",
     'opts': ["New York", "Chicago", "Miami", "Las Vegas"], 'answer': 2},

    {'q': "What is the protagonist's name in Celeste?",
     'opts': ["Madeline", "Celeste", "Claire", "Maya"], 'answer': 0},

    {'q': "What is the common name for the player character in Hollow Knight?",
     'opts': ["The Hollow Knight", "Hornet", "The Knight", "Ghost"], 'answer': 2},

    {'q': "Which Overwatch hero has the ability called 'Blink'?",
     'opts': ["Tracer", "Genji", "Reaper", "Widowmaker"], 'answer': 0},

    {'q': "What is the name of the main playable character in Cuphead?",
     'opts': ["Mugman", "Cuphead", "Elder Kettle", "The Devil"], 'answer': 1},

    {'q': "What year was the Game Boy released in Japan?",
     'opts': ["1987", "1988", "1989", "1990"], 'answer': 2},

    {'q': "In Undertale, which character says 'You're going to have a bad time'?",
     'opts': ["Papyrus", "Sans", "Toriel", "Undyne"], 'answer': 1},

    {'q': "Which game features the protagonist Solid Snake?",
     'opts': ["Splinter Cell", "Metal Gear", "Hitman", "Deus Ex"], 'answer': 1},

    {'q': "What planet does Kirby live on?",
     'opts': ["Dream Land", "Pop Star", "Kirby World", "Nova"], 'answer': 1},

    {'q': "'The cake is a lie' originates from which game?",
     'opts': ["BioShock", "Portal", "Borderlands", "Mirror's Edge"], 'answer': 1},

    {'q': "What is the best-selling game on Nintendo Switch?",
     'opts': ["Animal Crossing: New Horizons", "Super Smash Bros. Ultimate", "Mario Kart 8 Deluxe", "Breath of the Wild"], 'answer': 2},

    {'q': "What year was the NES released in North America?",
     'opts': ["1983", "1984", "1985", "1986"], 'answer': 2},

    {'q': "Who is the demon lord that gives the Diablo franchise its name?",
     'opts': ["Mephisto", "Baal", "Diablo", "Belial"], 'answer': 2},

    {'q': "What is the name of the protagonist in NieR: Automata?",
     'opts': ["2A", "2B", "A2", "9S"], 'answer': 1},

    {'q': "In which game does Sackboy appear?",
     'opts': ["LittleBigPlanet", "Dreams", "Knack", "Tearaway"], 'answer': 0},

    {'q': "What is the name of the first assassin playable in Assassin's Creed (2007)?",
     'opts': ["Ezio", "Connor", "Altaïr", "Bayek"], 'answer': 2},

    {'q': "What year was the Nintendo Wii launched in North America?",
     'opts': ["2004", "2005", "2006", "2007"], 'answer': 2},

    {'q': "What is Magikarp's evolved form in Pokémon?",
     'opts': ["Gyarados", "Dragonite", "Kingdra", "Seadra"], 'answer': 0},

    {'q': "Which Fallout game introduced Settlement building?",
     'opts': ["Fallout 3", "Fallout: New Vegas", "Fallout 4", "Fallout 76"], 'answer': 2},

    {'q': "In which Persona game does 'Joker' lead the Phantom Thieves?",
     'opts': ["Persona 4", "Persona 5", "Persona 3", "Persona 4 Golden"], 'answer': 1},

    {'q': "In Fortnite, what is the closing purple zone called?",
     'opts': ["The Surge", "The Wall", "The Storm", "The Zone"], 'answer': 2},

    {'q': "Which game popularised the 'bullet time' slow-motion mechanic?",
     'opts': ["Max Payne", "Wanted", "Stranglehold", "SUPERHOT"], 'answer': 0},

    {'q': "How many Divine Beasts are there in Zelda: Breath of the Wild?",
     'opts': ["3", "4", "5", "6"], 'answer': 1},

    {'q': "Who is the main villain in the Mega Man series?",
     'opts': ["Dr. Wily", "Dr. Light", "Dr. Cossack", "King"], 'answer': 0},

    {'q': "Which studio developed God of War (2018)?",
     'opts': ["Naughty Dog", "Sony Bend", "Santa Monica Studio", "Guerrilla Games"], 'answer': 2},

    {'q': "In which game does the merchant say 'What are ya buyin'?",
     'opts': ["Resident Evil 4", "Resident Evil 5", "Resident Evil 7", "Resident Evil Village"], 'answer': 0},

    {'q': "Who is the final boss in the original Dark Souls?",
     'opts': ["Ornstein", "Seath the Scaleless", "Gwyn, Lord of Cinder", "Bed of Chaos"], 'answer': 2},

    {'q': "What is the protagonist's name in Assassin's Creed II?",
     'opts': ["Ezio Auditore", "Altaïr", "Connor", "Edward Kenway"], 'answer': 0},

    {'q': "In which game do you play as the agent 'Joanna Dark'?",
     'opts': ["GoldenEye 007", "Perfect Dark", "TimeSplitters", "Killzone"], 'answer': 1},

    {'q': "In game genre terminology, what does 'FPS' stand for?",
     'opts': ["Fast Play System", "First-Person Shooter", "Full Polygon Simulation", "Frame Performance Standard"], 'answer': 1},

    {'q': "What is the main collectible in Donkey Kong Country?",
     'opts': ["Bananas", "Stars", "Coins", "Gems"], 'answer': 0},

    {'q': "In which game series does Commander Shepard appear?",
     'opts': ["Halo", "Gears of War", "Mass Effect", "Killzone"], 'answer': 2},

    {'q': "What year was The Legend of Zelda: Ocarina of Time released?",
     'opts': ["1996", "1997", "1998", "1999"], 'answer': 2},

    {'q': "What is the name of the protagonist in Horizon Zero Dawn?",
     'opts': ["Yara", "Aloy", "Talanah", "Erend"], 'answer': 1},

    {'q': "In Final Fantasy, which summon is known as the Dragon King?",
     'opts': ["Ifrit", "Shiva", "Bahamut", "Alexander"], 'answer': 2},

    {'q': "What year was Grand Theft Auto V released?",
     'opts': ["2011", "2012", "2013", "2014"], 'answer': 2},

    {'q': "What is the in-game currency in The Sims?",
     'opts': ["Credits", "Bits", "Simoleons", "Ducats"], 'answer': 2},

    {'q': "Which game features open-world survival with dinosaurs?",
     'opts': ["The Forest", "Subnautica", "ARK: Survival Evolved", "Conan Exiles"], 'answer': 2},

    {'q': "What year was the original Xbox released in North America?",
     'opts': ["1999", "2000", "2001", "2002"], 'answer': 2},

    {'q': "In Among Us, how many Impostors are there by default?",
     'opts': ["1", "2", "3", "4"], 'answer': 0},

    {'q': "What year was the original Doom released?",
     'opts': ["1991", "1992", "1993", "1994"], 'answer': 2},

    {'q': "In Apex Legends, how many players are in a standard squad?",
     'opts': ["2", "3", "4", "5"], 'answer': 1},

    {'q': "What is the name of Link's horse in Ocarina of Time?",
     'opts': ["Shadowmere", "Epona", "Pegasus", "Agro"], 'answer': 1},

    {'q': "What is the full name of the studio that made Dark Souls?",
     'opts': ["From Studios", "FromSoftware", "SoftFrom Inc.", "Namco Origins"], 'answer': 1},

    {'q': "What is Geralt's profession in The Witcher series?",
     'opts': ["Witcher", "Sorcerer", "Knight", "Assassin"], 'answer': 0},

    {'q': "What type of creature is Yoshi in the Mario series?",
     'opts': ["Dragon", "Dinosaur", "Turtle", "Lizard"], 'answer': 1},

    {'q': "Which Mario game introduced the Tanooki Suit and Frog Suit?",
     'opts': ["Super Mario World", "Super Mario Bros. 3", "Super Mario Land", "Super Mario 64"], 'answer': 1},

    {'q': "What year was Counter-Strike originally released?",
     'opts': ["1999", "2000", "2001", "2002"], 'answer': 1},

    {'q': "In Rocket League, how many players are on each team in standard mode?",
     'opts': ["2", "3", "4", "5"], 'answer': 1},

    {'q': "Which game features a ghost companion that guides the player?",
     'opts': ["Warframe", "Destiny", "Halo", "Anthem"], 'answer': 1},

    {'q': "Which game features the protagonist BJ Blazkowicz?",
     'opts': ["Doom", "Wolfenstein", "Quake", "Duke Nukem"], 'answer': 1},

    {'q': "In which Zelda game does Link first transform into a wolf?",
     'opts': ["Majora's Mask", "Twilight Princess", "Skyward Sword", "Wind Waker"], 'answer': 1},

    {'q': "Which game was originally a Half-Life mod?",
     'opts': ["Team Fortress 2", "Counter-Strike", "Left 4 Dead", "Portal"], 'answer': 1},

    {'q': "What is the name of the settlement currency in Fallout: New Vegas?",
     'opts': ["Gold", "Dollars", "Caps", "Credits"], 'answer': 2},

    {'q': "In which game does the phrase 'Stay a while and listen' appear?",
     'opts': ["World of Warcraft", "Diablo II", "StarCraft", "Warcraft III"], 'answer': 1},

    {'q': "What company makes the PlayStation consoles?",
     'opts': ["Microsoft", "Nintendo", "Sony", "Sega"], 'answer': 2},

    {'q': "Which of these games was developed by Valve?",
     'opts': ["Minecraft", "Portal", "Cuphead", "Hollow Knight"], 'answer': 1},

    {'q': "In Pokémon, what is the evolved form of Eevee using a Fire Stone?",
     'opts': ["Vaporeon", "Flareon", "Jolteon", "Espeon"], 'answer': 1},
]


# ── Trivia minigame class ─────────────────────────────────────────────────────

class TriviaMinigame:
    """3-question trivia duel against Salomon. Correct = 2 dmg to him. Wrong = 1 dmg to player."""

    SALOMON_MAX_HP = 6
    FEEDBACK_DUR   = 100   # ~1.7 s

    INTRO_DUR = 210   # ~3.5 s auto-advance

    def __init__(self, player):
        self.player_hp     = player.hp
        self.player_max_hp = player.max_hp
        self.player_col    = player.col
        self.player_name   = player.fighter
        self.salomon_hp    = self.SALOMON_MAX_HP
        self.questions     = random.sample(QUESTION_POOL, 3)
        self.current_q     = 0
        self.phase         = 'intro'      # 'intro' | 'question' | 'feedback' | 'done'
        self.intro_timer   = self.INTRO_DUR
        self.feedback_timer = 0
        self.last_correct  = None
        self.chosen        = -1
        self.result        = None         # 'win' | 'lose'
        self._done_ready   = False        # True once ENTER can advance

    # ── Public interface ──────────────────────────────────────────────────────

    def handle_key(self, key):
        if self.phase == 'intro' and key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                                              pygame.K_SPACE):
            self.phase = 'question'
            return True
        if self.phase == 'done' and key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._done_ready = True
            return True
        if self.phase != 'question':
            return False
        idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}.get(key)
        if idx is None:
            return False
        self.chosen        = idx
        q                  = self.questions[self.current_q]
        self.last_correct  = (idx == q['answer'])
        if self.last_correct:
            self.salomon_hp    = max(0, self.salomon_hp - 2)
        else:
            self.player_hp     = max(0, self.player_hp - 1)
        self.phase          = 'feedback'
        self.feedback_timer = self.FEEDBACK_DUR
        return True

    def update(self):
        if self.phase == 'intro':
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.phase = 'question'
            return
        if self.phase != 'feedback':
            return
        self.feedback_timer -= 1
        if self.feedback_timer > 0:
            return
        if self.player_hp <= 0:
            self.phase  = 'done'
            self.result = 'lose'
            return
        self.current_q += 1
        if self.current_q >= 3:
            self.phase  = 'done'
            self.result = 'win'
        else:
            self.phase  = 'question'
            self.chosen = -1

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self, surf, font, font_big, font_title, tick):
        # Stone floor
        surf.fill(STONE_BG)
        for x in range(0, SCREEN_W, 32):
            pygame.draw.line(surf, STONE_GRID, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 32):
            pygame.draw.line(surf, STONE_GRID, (0, y), (SCREEN_W, y))

        cx = SCREEN_W // 2

        # ── Intro overlay ─────────────────────────────────────────────────────
        if self.phase == 'intro':
            fade = min(255, (self.INTRO_DUR - self.intro_timer) * 5)
            c    = lambda base: tuple(int(b * fade / 255) for b in base)
            t = font_title.render('SALOMON CHALLENGES YOU IN A TRIVIA BATTLE!',
                                  True, c(SALOMON_OUT))
            surf.blit(t, (cx - t.get_width() // 2, 240))
            t = font_big.render('Answer 3 questions correctly to proceed.',
                                True, c(UI_MUTED))
            surf.blit(t, (cx - t.get_width() // 2, 320))
            if self.INTRO_DUR - self.intro_timer > 55:
                t = font.render('PRESS ENTER or SPACE to start',
                                True, c((200, 170, 110)))
                surf.blit(t, (cx - t.get_width() // 2, 390))
            return

        q_idx = min(self.current_q, 2)
        q     = self.questions[q_idx]
        cx    = SCREEN_W // 2

        # ── Round indicator ───────────────────────────────────────────────────
        q_num = min(self.current_q + 1, 3)
        rt = font_big.render(f"Question  {q_num} / 3", True, GOLD_COL)
        surf.blit(rt, (cx - rt.get_width() // 2, 12))

        # ── Player sprite + HP (left) ─────────────────────────────────────────
        PW, PH = 56, 56
        px, py = 40, 52
        pygame.draw.rect(surf, self.player_col, (px, py, PW, PH))
        pygame.draw.rect(surf, UI_WHITE, (px, py, PW, PH), 2)
        pygame.draw.circle(surf, (30, 30, 30),    (px + PW - 10, py + PH // 2), 5)
        pygame.draw.circle(surf, (240, 240, 240), (px + PW - 10, py + PH // 2), 2)
        nt = font.render(self.player_name.upper(), True, UI_WHITE)
        surf.blit(nt, (px + PW // 2 - nt.get_width() // 2, py + PH + 4))
        self._hbar(surf, font, px, py + PH + 22, PW + 60, 14,
                   self.player_hp / self.player_max_hp,
                   HP_BG, HP_FG, f"{self.player_hp}/{self.player_max_hp}")

        # ── Salomon sprite + HP (right) ───────────────────────────────────────
        SW, SH = 72, 72
        sx     = SCREEN_W - 40 - SW
        sy     = 46
        p2     = self.salomon_hp <= self.SALOMON_MAX_HP // 2
        s_col  = (155, 120, 78) if p2 else SALOMON_DARK
        s_out  = (220, 160, 70) if p2 else SALOMON_OUT
        pygame.draw.rect(surf, s_col, (sx, sy, SW, SH))
        pygame.draw.rect(surf, s_out, (sx, sy, SW, SH), 3)
        ey_col = (220, 80, 30) if p2 else (195, 175, 95)
        for ex in (sx + 18, sx + SW - 18):
            pygame.draw.circle(surf, ey_col,          (ex, sy + 28), 6)
            pygame.draw.circle(surf, (255, 255, 200), (ex, sy + 28), 2)
        snt = font.render("SALOMON", True, UI_WHITE)
        surf.blit(snt, (sx + SW // 2 - snt.get_width() // 2, sy + SH + 4))
        self._hbar(surf, font, sx - 60, sy + SH + 22, SW + 60, 14,
                   self.salomon_hp / self.SALOMON_MAX_HP,
                   (55, 45, 35), (125, 105, 78), f"{self.salomon_hp}/{self.SALOMON_MAX_HP}")

        # ── Speech bubble (centred, below round label) ─────────────────────
        bub_y = 155
        self._speech_bubble(surf, font_big, q['q'], cx, bub_y)

        # ── Answer options (2 × 2 grid) ───────────────────────────────────────
        OPT_W, OPT_H = 555, 54
        GAP           = 20
        OPT_Y         = 390
        for i, opt in enumerate(q['opts']):
            col_i = i % 2
            row_i = i // 2
            ox    = cx - OPT_W - GAP // 2 + col_i * (OPT_W + GAP)
            oy    = OPT_Y + row_i * (OPT_H + GAP)
            self._option_box(surf, font, font_big,
                             ox, oy, OPT_W, OPT_H,
                             str(i + 1), opt, i, q['answer'])

        # ── Feedback overlay ──────────────────────────────────────────────────
        if self.phase == 'feedback':
            frac  = self.feedback_timer / self.FEEDBACK_DUR
            alpha = int(230 * min(1.0, frac * 2.5))
            msg   = "CORRECT!" if self.last_correct else "WRONG!"
            col   = CORRECT_COL if self.last_correct else WRONG_COL
            sub   = ("−2 HP to Salomon!" if self.last_correct
                     else "−1 HP to you!")
            t1 = font_title.render(msg, True, col)
            t2 = font_big.render(sub, True, UI_WHITE)
            for surf_t, dy in ((t1, -55), (t2, 0)):
                bg = pygame.Surface(
                    (surf_t.get_width() + 20, surf_t.get_height() + 8),
                    pygame.SRCALPHA)
                bg.fill((0, 0, 0, min(200, alpha)))
                bx = cx - surf_t.get_width() // 2 - 10
                surf.blit(bg, (bx, SCREEN_H // 2 + dy - 4))
                surf.blit(surf_t, (cx - surf_t.get_width() // 2, SCREEN_H // 2 + dy))

        # ── Done overlay ──────────────────────────────────────────────────────
        if self.phase == 'done':
            self._done_overlay(surf, font, font_big, font_title, cx)

        # ── Hint ─────────────────────────────────────────────────────────────
        if self.phase == 'question':
            hint = font.render("Press  1 · 2 · 3 · 4  to answer", True, (78, 68, 56))
            surf.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 22))

    # ── Private helpers ───────────────────────────────────────────────────────

    def _hbar(self, surf, font, x, y, w, h, frac, bg, fg, label):
        pygame.draw.rect(surf, bg, (x, y, w, h))
        fw = max(0, int(w * frac))
        if fw:
            pygame.draw.rect(surf, fg, (x, y, fw, h))
        pygame.draw.rect(surf, (80, 70, 60), (x, y, w, h), 1)
        t = font.render(label, True, UI_WHITE)
        surf.blit(t, (x + 4, y + 1))

    def _speech_bubble(self, surf, font_big, text, cx, y):
        max_w = 860
        words = text.split()
        lines, line = [], ""
        for word in words:
            test = (line + " " + word).strip()
            if font_big.size(test)[0] <= max_w:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)

        lh  = font_big.get_height() + 4
        bw  = max_w + 48
        bh  = len(lines) * lh + 32
        bx  = cx - bw // 2

        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((*BUBBLE_BG, 230))
        surf.blit(bg, (bx, y))
        pygame.draw.rect(surf, BUBBLE_EDGE, (bx, y, bw, bh), 2)

        ty = y + 16
        for ln in lines:
            t = font_big.render(ln, True, UI_WHITE)
            surf.blit(t, (cx - t.get_width() // 2, ty))
            ty += lh

    def _option_box(self, surf, font, font_big, x, y, w, h,
                    label, text, idx, correct):
        if self.phase == 'feedback':
            if idx == correct:
                bg, border = (34, 82, 44), CORRECT_COL
            elif idx == self.chosen:
                bg, border = (82, 32, 32), WRONG_COL
            else:
                bg, border = OPTION_BG, (58, 50, 40)
        else:
            bg, border = OPTION_BG, (85, 74, 60)

        pygame.draw.rect(surf, bg, (x, y, w, h))
        pygame.draw.rect(surf, border, (x, y, w, h), 2)

        # Key badge
        badge_w = 34
        bgy     = y + h // 2 - 13
        pygame.draw.rect(surf, (60, 52, 42), (x + 8, bgy, badge_w, 26))
        pygame.draw.rect(surf, border, (x + 8, bgy, badge_w, 26), 1)
        lt = font_big.render(label, True, GOLD_COL)
        surf.blit(lt, (x + 8 + badge_w // 2 - lt.get_width() // 2,
                       y + h // 2 - lt.get_height() // 2))

        # Option text (clipped so it doesn't overflow the box)
        ot   = font_big.render(text, True, UI_WHITE)
        tx   = x + badge_w + 20
        clip = pygame.Rect(tx, y + 2, w - badge_w - 28, h - 4)
        surf.set_clip(clip)
        surf.blit(ot, (tx, y + h // 2 - ot.get_height() // 2))
        surf.set_clip(None)

    def _done_overlay(self, surf, font, font_big, font_title, cx):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surf.blit(overlay, (0, 0))

        if self.result == 'win':
            msg, sub, col = "SALOMON YIELDS!", "The battle begins…", CORRECT_COL
        else:
            msg, sub, col = "SALOMON PREVAILS!", "You have been defeated…", WRONG_COL

        t1 = font_title.render(msg, True, col)
        t2 = font_big.render(sub, True, UI_WHITE)
        t3 = font.render("Press ENTER to continue", True, UI_MUTED)
        surf.blit(t1, (cx - t1.get_width() // 2, SCREEN_H // 2 - 65))
        surf.blit(t2, (cx - t2.get_width() // 2, SCREEN_H // 2 - 12))
        surf.blit(t3, (cx - t3.get_width() // 2, SCREEN_H // 2 + 38))
