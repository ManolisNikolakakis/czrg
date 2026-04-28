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

# ── Question pools ────────────────────────────────────────────────────────────
# Each entry: {'q': str, 'opts': [A, B, C, D], 'answer': int (0-indexed)}
VIDEOGAME_POOL = [
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

SPORTS_POOL = [
    {'q': "How many players from each team are on a basketball court at one time?",
     'opts': ["4", "5", "6", "7"], 'answer': 1},

    {'q': "How many players are on each team in a soccer match?",
     'opts': ["9", "10", "11", "12"], 'answer': 2},

    {'q': "How many innings are in a standard MLB baseball game?",
     'opts': ["7", "8", "9", "10"], 'answer': 2},

    {'q': "What sport uses a shuttlecock?",
     'opts': ["Tennis", "Squash", "Badminton", "Pickleball"], 'answer': 2},

    {'q': "How many events make up a decathlon?",
     'opts': ["8", "9", "10", "12"], 'answer': 2},

    {'q': "Which country hosted the 2016 Summer Olympics?",
     'opts': ["China", "UK", "Brazil", "Australia"], 'answer': 2},

    {'q': "In tennis, what is the name for a 40-40 score?",
     'opts': ["Tie", "Deuce", "Draw", "Level"], 'answer': 1},

    {'q': "Who has won the most Olympic gold medals in history?",
     'opts': ["Usain Bolt", "Carl Lewis", "Michael Phelps", "Mark Spitz"], 'answer': 2},

    {'q': "In American football, how many points is a touchdown worth?",
     'opts': ["4", "5", "6", "7"], 'answer': 2},

    {'q': "In which sport would you perform a 'slam dunk'?",
     'opts': ["Volleyball", "Basketball", "Handball", "Water Polo"], 'answer': 1},

    {'q': "How many holes are in a standard round of golf?",
     'opts': ["9", "12", "18", "21"], 'answer': 2},

    {'q': "In golf, what is completing a hole one stroke under par called?",
     'opts': ["Eagle", "Birdie", "Albatross", "Bogey"], 'answer': 1},

    {'q': "How long is an Olympic swimming pool in metres?",
     'opts': ["25", "50", "75", "100"], 'answer': 1},

    {'q': "Which sport is played at Wimbledon?",
     'opts': ["Squash", "Golf", "Tennis", "Badminton"], 'answer': 2},

    {'q': "In American football, how many points is a field goal worth?",
     'opts': ["1", "2", "3", "4"], 'answer': 2},

    {'q': "How many players are on a volleyball team on the court?",
     'opts': ["4", "5", "6", "7"], 'answer': 2},

    {'q': "In boxing, how many rounds are in a world championship fight?",
     'opts': ["10", "12", "15", "20"], 'answer': 1},

    {'q': "Which country has won the most FIFA World Cup titles?",
     'opts': ["Germany", "Argentina", "Italy", "Brazil"], 'answer': 3},

    {'q': "How far is a marathon in kilometres (approximate)?",
     'opts': ["38", "40", "42", "45"], 'answer': 2},

    {'q': "In cricket, how many runs is a 'six' worth?",
     'opts': ["3", "4", "5", "6"], 'answer': 3},

    {'q': "Which sport uses the term 'love' to mean zero?",
     'opts': ["Badminton", "Squash", "Tennis", "Table Tennis"], 'answer': 2},

    {'q': "In American football, how many points is a safety worth?",
     'opts': ["1", "2", "3", "4"], 'answer': 1},

    {'q': "How many players are on a baseball team on the field?",
     'opts': ["7", "8", "9", "10"], 'answer': 2},

    {'q': "Who invented basketball in 1891?",
     'opts': ["James Naismith", "Bill Bowerman", "Walter Camp", "Abner Doubleday"], 'answer': 0},

    {'q': "In tennis, what is a serve that lands in and cannot be returned called?",
     'opts': ["Ace", "Let", "Fault", "Winner"], 'answer': 0},

    {'q': "How many Grand Slam tournaments are there in tennis?",
     'opts': ["2", "3", "4", "5"], 'answer': 2},

    {'q': "Which Grand Slam tennis tournament is played on clay?",
     'opts': ["Wimbledon", "US Open", "Australian Open", "French Open"], 'answer': 3},

    {'q': "In rugby union, how many players are on each team?",
     'opts': ["13", "14", "15", "16"], 'answer': 2},

    {'q': "What is the name of the trophy awarded to the NHL champion?",
     'opts': ["The Cup", "Stanley Cup", "The Gretzky Cup", "The Maple Cup"], 'answer': 1},

    {'q': "In the Tour de France, what does the yellow jersey represent?",
     'opts': ["Best climber", "Overall leader", "Best sprinter", "Most aggressive rider"], 'answer': 1},

    {'q': "In Formula 1, how many points does the race winner receive?",
     'opts': ["20", "25", "30", "50"], 'answer': 1},

    {'q': "How many gold medals did Usain Bolt win at the Olympics in total?",
     'opts': ["6", "7", "8", "9"], 'answer': 2},

    {'q': "Which country has won the most Olympic gold medals of all time?",
     'opts': ["Russia", "China", "Germany", "United States"], 'answer': 3},

    {'q': "What is the standard height of a basketball hoop in feet?",
     'opts': ["8", "9", "10", "11"], 'answer': 2},

    {'q': "In which year did women's boxing debut at the Olympic Games?",
     'opts': ["2004", "2008", "2012", "2016"], 'answer': 2},

    {'q': "What is a 'love game' in tennis?",
     'opts': ["A tie", "A game won without opponent scoring", "An advantage game", "A penalty game"], 'answer': 1},

    {'q': "How many points is a red ball worth in snooker?",
     'opts': ["1", "2", "3", "4"], 'answer': 0},

    {'q': "In soccer, what colour card results in a player being sent off?",
     'opts': ["Yellow", "Red", "Orange", "Black"], 'answer': 1},

    {'q': "Who holds the record for most career home runs in MLB?",
     'opts': ["Babe Ruth", "Hank Aaron", "Barry Bonds", "Willie Mays"], 'answer': 2},

    {'q': "In which country did the sport of sumo wrestling originate?",
     'opts': ["China", "Korea", "Japan", "Mongolia"], 'answer': 2},

    {'q': "In Formula 1, what does DRS stand for?",
     'opts': ["Drag Reduction System", "Direct Racing Speed", "Driver Reaction System", "Dynamic Rear Spoiler"], 'answer': 0},

    {'q': "How many minutes are in a standard soccer match?",
     'opts': ["80", "85", "90", "95"], 'answer': 2},

    {'q': "In golf, what is completing a hole two strokes under par called?",
     'opts': ["Birdie", "Eagle", "Albatross", "Hole-in-one"], 'answer': 1},

    {'q': "Which Grand Slam tennis tournament is played on grass?",
     'opts': ["US Open", "Australian Open", "French Open", "Wimbledon"], 'answer': 3},

    {'q': "How many players are on a water polo team in the pool?",
     'opts': ["5", "6", "7", "8"], 'answer': 2},

    {'q': "In American football, what separates the two teams at the start of each play?",
     'opts': ["Goal line", "Line of scrimmage", "First down line", "Red zone"], 'answer': 1},

    {'q': "Who has won the men's singles at Wimbledon the most times?",
     'opts': ["Pete Sampras", "Roger Federer", "Novak Djokovic", "Rafael Nadal"], 'answer': 1},

    {'q': "In ice hockey, how many players (including goalie) does each team have in normal play?",
     'opts': ["4", "5", "6", "7"], 'answer': 2},

    {'q': "What is the highest possible score in a game of ten-pin bowling?",
     'opts': ["240", "270", "300", "330"], 'answer': 2},

    {'q': "Which country has won the Rugby Union World Cup the most times?",
     'opts': ["England", "Australia", "South Africa", "New Zealand"], 'answer': 3},

    {'q': "In the Tour de France, what does the polka-dot jersey represent?",
     'opts': ["Overall leader", "Best sprinter", "Best young rider", "Best climber"], 'answer': 3},

    {'q': "How long is a standard NBA basketball game in minutes?",
     'opts': ["40", "48", "50", "60"], 'answer': 1},

    {'q': "What is the distance of a marathon in miles?",
     'opts': ["24.2", "25.2", "26.2", "27.2"], 'answer': 2},

    {'q': "In tennis, what is the name for a serve that clips the net but lands in?",
     'opts': ["Ace", "Let", "Fault", "Replay"], 'answer': 1},

    {'q': "Which American swimmer won 8 gold medals at the 2008 Beijing Olympics?",
     'opts': ["Mark Spitz", "Ryan Lochte", "Michael Phelps", "Nathan Adrian"], 'answer': 2},

    {'q': "In soccer, how many minutes are in each half?",
     'opts': ["40", "45", "50", "55"], 'answer': 1},

    {'q': "What is the name of the annual American football championship game?",
     'opts': ["The Final Bowl", "Super Bowl", "Championship Game", "The Grid Iron Cup"], 'answer': 1},

    {'q': "In a Grand Slam men's final, how many sets must a player win?",
     'opts': ["2", "3", "4", "5"], 'answer': 1},

    {'q': "In which sport is the 'Fosbury Flop' technique used?",
     'opts': ["Long Jump", "Pole Vault", "High Jump", "Triple Jump"], 'answer': 2},

    {'q': "What is the term for scoring three goals in a single soccer match?",
     'opts': ["Hat-trick", "Triple score", "Triple crown", "Brace"], 'answer': 0},

    {'q': "How many players are on a handball team on the court?",
     'opts': ["5", "6", "7", "8"], 'answer': 2},

    {'q': "Which sprinter is known as 'The Lightning Bolt'?",
     'opts': ["Carl Lewis", "Usain Bolt", "Florence Griffith-Joyner", "Tyson Gay"], 'answer': 1},

    {'q': "In tennis, how many points do you need to win a tiebreak?",
     'opts': ["5", "6", "7", "8"], 'answer': 2},

    {'q': "What sport is played in the NHL?",
     'opts': ["Basketball", "Baseball", "Ice Hockey", "American Football"], 'answer': 2},

    {'q': "In cricket, how many balls make up one over?",
     'opts': ["4", "5", "6", "7"], 'answer': 2},

    {'q': "How high is the net in the middle of a standard tennis court (in feet)?",
     'opts': ["2.5", "3", "3.5", "4"], 'answer': 1},

    {'q': "What is the term for a perfect game in baseball (27 batters up, 27 out)?",
     'opts': ["No-hitter", "Perfect game", "Shutout", "Clean sweep"], 'answer': 1},

    {'q': "In which city is the famous Maracanã stadium located?",
     'opts': ["São Paulo", "Buenos Aires", "Rio de Janeiro", "Montevideo"], 'answer': 2},

    {'q': "What is the term for hitting a golf ball into the hole in one shot?",
     'opts': ["Eagle", "Ace", "Birdie", "Condor"], 'answer': 1},

    {'q': "How many players are on an American football team on the field?",
     'opts': ["9", "10", "11", "12"], 'answer': 2},

    {'q': "In which year did Roger Federer win his first Wimbledon title?",
     'opts': ["2001", "2002", "2003", "2004"], 'answer': 2},

    {'q': "In which sport is 'the Green Jacket' awarded at a prestigious annual tournament?",
     'opts': ["Tennis", "Horse Racing", "Golf", "Cycling"], 'answer': 2},

    {'q': "How many players are on the field in a rugby league match per team?",
     'opts': ["13", "14", "15", "16"], 'answer': 0},

    {'q': "In table tennis, how many points do you need to win a game?",
     'opts': ["7", "9", "11", "15"], 'answer': 2},

    {'q': "Who won the 2022 FIFA World Cup?",
     'opts': ["France", "Brazil", "Germany", "Argentina"], 'answer': 3},

    {'q': "In which sport is the term 'en garde' used?",
     'opts': ["Karate", "Fencing", "Judo", "Boxing"], 'answer': 1},

    {'q': "How many events are in a modern pentathlon?",
     'opts': ["3", "4", "5", "6"], 'answer': 2},

    {'q': "What is the lowest score possible in a single hole of golf?",
     'opts': ["1", "2", "3", "4"], 'answer': 0},

    {'q': "In which city are the NBA's Lakers based?",
     'opts': ["Chicago", "Miami", "Los Angeles", "Dallas"], 'answer': 2},

    {'q': "In Australian Rules Football, how many points is a behind worth?",
     'opts': ["1", "2", "3", "4"], 'answer': 0},

    {'q': "Who became the NBA's all-time leading scorer in 2023?",
     'opts': ["Michael Jordan", "Kareem Abdul-Jabbar", "LeBron James", "Kobe Bryant"], 'answer': 2},

    {'q': "In cricket, what is the term for a batsman scoring 100 runs?",
     'opts': ["Half-century", "Century", "Double hundred", "Triple"], 'answer': 1},

    {'q': "In which city is the Roland Garros tennis stadium located?",
     'opts': ["London", "Rome", "Melbourne", "Paris"], 'answer': 3},

    {'q': "What is the maximum number of sets in a women's Grand Slam final?",
     'opts': ["3", "4", "5", "6"], 'answer': 0},

    {'q': "How many laps make up the Monaco Grand Prix?",
     'opts': ["50", "56", "60", "78"], 'answer': 3},

    {'q': "In which sport would you find positions like 'wicketkeeper' and 'slip fielder'?",
     'opts': ["Baseball", "Rounders", "Cricket", "Softball"], 'answer': 2},

    {'q': "What is the term for three consecutive strikes in bowling?",
     'opts': ["Triple", "Turkey", "Hat-trick", "Three-bagger"], 'answer': 1},

    {'q': "How many rings are on the Olympic flag?",
     'opts': ["4", "5", "6", "7"], 'answer': 1},

    {'q': "In which year did Tiger Woods first win the Masters?",
     'opts': ["1995", "1996", "1997", "1998"], 'answer': 2},

    {'q': "In American football, what is a 'Hail Mary' pass?",
     'opts': ["A short pass near the goal line", "A long desperate forward pass", "A lateral pass", "A fake punt"], 'answer': 1},

    {'q': "How many players are on a polo team?",
     'opts': ["2", "3", "4", "5"], 'answer': 2},

    {'q': "In soccer, what is the term for a deliberate punch of the ball away by the goalkeeper?",
     'opts': ["Clearance", "Save", "Punch", "Distribution"], 'answer': 0},

    {'q': "What year did the first modern Olympic Games take place?",
     'opts': ["1892", "1894", "1896", "1900"], 'answer': 2},

    {'q': "In which sport is a 'birdie' scored?",
     'opts': ["Tennis", "Badminton", "Golf", "Cricket"], 'answer': 2},

    {'q': "How many players from each team are on the field in a hurling match?",
     'opts': ["13", "14", "15", "16"], 'answer': 2},

    {'q': "What is the name of the trophy awarded to the winner of the US football league each year?",
     'opts': ["Vince Lombardi Trophy", "Pete Rozelle Trophy", "NFL Cup", "Champions Bowl"], 'answer': 0},

    {'q': "Which country introduced the sport of baseball to Japan?",
     'opts': ["UK", "Canada", "USA", "Cuba"], 'answer': 2},

    {'q': "What year was the first FIFA World Cup held?",
     'opts': ["1926", "1928", "1930", "1934"], 'answer': 2},

    {'q': "How many players are on a netball team on the court?",
     'opts': ["5", "6", "7", "8"], 'answer': 2},

    {'q': "In which sport would you find a 'pommel horse'?",
     'opts': ["Athletics", "Gymnastics", "Equestrian", "Acrobatics"], 'answer': 1},
]

POP_CULTURE_POOL = [
    {'q': "Who sang the hit single 'Rolling in the Deep'?",
     'opts': ["Rihanna", "Beyoncé", "Adele", "Taylor Swift"], 'answer': 2},

    {'q': "In which TV show would you find Ross, Rachel, Monica, Chandler, Joey, and Phoebe?",
     'opts': ["Seinfeld", "How I Met Your Mother", "Friends", "The Big Bang Theory"], 'answer': 2},

    {'q': "What year was the original Star Wars (Episode IV) released?",
     'opts': ["1975", "1976", "1977", "1978"], 'answer': 2},

    {'q': "Which band performed 'Bohemian Rhapsody'?",
     'opts': ["The Beatles", "Led Zeppelin", "Queen", "The Rolling Stones"], 'answer': 2},

    {'q': "Who played Iron Man in the Marvel Cinematic Universe?",
     'opts': ["Chris Evans", "Chris Pratt", "Robert Downey Jr.", "Mark Ruffalo"], 'answer': 2},

    {'q': "Which Disney princess sings 'Let It Go'?",
     'opts': ["Rapunzel", "Merida", "Moana", "Elsa"], 'answer': 3},

    {'q': "What is the name of Harry Potter's owl?",
     'opts': ["Crookshanks", "Scabbers", "Hedwig", "Errol"], 'answer': 2},

    {'q': "Which TV show features Walter White?",
     'opts': ["Dexter", "Breaking Bad", "Ozark", "Better Call Saul"], 'answer': 1},

    {'q': "What year did Michael Jackson release 'Thriller'?",
     'opts': ["1980", "1981", "1982", "1983"], 'answer': 2},

    {'q': "Which film features the quote 'Here's looking at you, kid'?",
     'opts': ["Gone with the Wind", "Casablanca", "The Godfather", "Citizen Kane"], 'answer': 1},

    {'q': "What is the name of the coffee shop in Friends?",
     'opts': ["Café Central", "Central Perk", "The Coffee Bean", "Java Joe's"], 'answer': 1},

    {'q': "Who directed the film Titanic (1997)?",
     'opts': ["Steven Spielberg", "Ridley Scott", "James Cameron", "Peter Jackson"], 'answer': 2},

    {'q': "Which artist released the album '1989'?",
     'opts': ["Katy Perry", "Lady Gaga", "Ariana Grande", "Taylor Swift"], 'answer': 3},

    {'q': "Which fictional kingdom does Elsa rule in Frozen?",
     'opts': ["Agrabah", "Arendelle", "Dunbroch", "Motunui"], 'answer': 1},

    {'q': "Which TV show features the fictional Dunder Mifflin Paper Company?",
     'opts': ["Parks and Recreation", "Brooklyn Nine-Nine", "The Office", "30 Rock"], 'answer': 2},

    {'q': "What is the highest-grossing film of all time worldwide?",
     'opts': ["The Avengers", "Avatar", "Avengers: Endgame", "Titanic"], 'answer': 1},

    {'q': "Who is the lead vocalist of the band U2?",
     'opts': ["The Edge", "Bono", "Larry Mullen Jr.", "Adam Clayton"], 'answer': 1},

    {'q': "Which movie features the line 'I'll be back'?",
     'opts': ["RoboCop", "Predator", "The Terminator", "Total Recall"], 'answer': 2},

    {'q': "What year did the first iPhone go on sale?",
     'opts': ["2005", "2006", "2007", "2008"], 'answer': 2},

    {'q': "Which animated show features the Griffin family?",
     'opts': ["The Simpsons", "American Dad", "Family Guy", "Bob's Burgers"], 'answer': 2},

    {'q': "Who played Katniss Everdeen in The Hunger Games films?",
     'opts': ["Emma Watson", "Shailene Woodley", "Jennifer Lawrence", "Kristen Stewart"], 'answer': 2},

    {'q': "Which actor played the Joker in The Dark Knight (2008)?",
     'opts': ["Jack Nicholson", "Jared Leto", "Joaquin Phoenix", "Heath Ledger"], 'answer': 3},

    {'q': "Which pop star is known as the 'Queen of Pop'?",
     'opts': ["Beyoncé", "Madonna", "Lady Gaga", "Whitney Houston"], 'answer': 1},

    {'q': "Which film series is set in a world called Middle-earth?",
     'opts': ["Harry Potter", "The Lord of the Rings", "Narnia", "Game of Thrones"], 'answer': 1},

    {'q': "What does 'MCU' stand for in entertainment?",
     'opts': ["Movie Cinema Universe", "Marvel Cinematic Universe", "Major Creative Unlimited", "Mega Comics Universe"], 'answer': 1},

    {'q': "Which TV show is set in Westeros?",
     'opts': ["Vikings", "The Witcher", "Game of Thrones", "The Last Kingdom"], 'answer': 2},

    {'q': "Who sang 'Baby One More Time' in 1999?",
     'opts': ["Christina Aguilera", "Britney Spears", "Mandy Moore", "Jessica Simpson"], 'answer': 1},

    {'q': "Which movie studio created the animated film Toy Story (1995)?",
     'opts': ["DreamWorks", "Universal", "Pixar", "Warner Bros."], 'answer': 2},

    {'q': "What is the real name of the rapper known as Eminem?",
     'opts': ["Marshall Mathers", "Curtis Jackson", "Shawn Carter", "Calvin Broadus"], 'answer': 0},

    {'q': "Which superhero is also known as the Caped Crusader?",
     'opts': ["Superman", "Batman", "Spider-Man", "Flash"], 'answer': 1},

    {'q': "Who starred as Jack Dawson in Titanic (1997)?",
     'opts': ["Brad Pitt", "Matt Damon", "Leonardo DiCaprio", "Tom Hanks"], 'answer': 2},

    {'q': "What was the first feature-length animated film produced by Disney?",
     'opts': ["Pinocchio", "Bambi", "Snow White and the Seven Dwarfs", "Fantasia"], 'answer': 2},

    {'q': "What is Sherlock Holmes' famous address in London?",
     'opts': ["10 Downing Street", "221B Baker Street", "12 Grimmauld Place", "4 Privet Drive"], 'answer': 1},

    {'q': "Which boy band released the song 'Bye Bye Bye' in 2000?",
     'opts': ["Backstreet Boys", "*NSYNC", "Boyz II Men", "New Kids on the Block"], 'answer': 1},

    {'q': "What is the name of the fictional country in Black Panther?",
     'opts': ["Narobia", "Wakanda", "Genosha", "Sokovia"], 'answer': 1},

    {'q': "Which artist released the album 'Lemonade' in 2016?",
     'opts': ["Rihanna", "Cardi B", "Beyoncé", "Nicki Minaj"], 'answer': 2},

    {'q': "In which movie does a wizard say 'You shall not pass!'?",
     'opts': ["Harry Potter", "The Lord of the Rings", "Narnia", "The Hobbit"], 'answer': 1},

    {'q': "Which actress played Hermione Granger in the Harry Potter films?",
     'opts': ["Keira Knightley", "Natalie Portman", "Emma Watson", "Lily James"], 'answer': 2},

    {'q': "Which music artist has the most Grammy Awards won (as of 2024)?",
     'opts': ["Taylor Swift", "Beyoncé", "Georg Solti", "Quincy Jones"], 'answer': 1},

    {'q': "What fictional town is the setting for Stranger Things?",
     'opts': ["Hawkins, Indiana", "Derry, Maine", "Castle Rock, Maine", "Springfield, Illinois"], 'answer': 0},

    {'q': "Who played James Bond in Casino Royale (2006)?",
     'opts': ["Pierce Brosnan", "Timothy Dalton", "Daniel Craig", "Roger Moore"], 'answer': 2},

    {'q': "What year did Elvis Presley die?",
     'opts': ["1975", "1976", "1977", "1978"], 'answer': 2},

    {'q': "Which film features the quote 'Life is like a box of chocolates'?",
     'opts': ["Rain Man", "Jerry Maguire", "Cast Away", "Forrest Gump"], 'answer': 3},

    {'q': "Which animated series features Homer, Marge, Bart, and Lisa?",
     'opts': ["Futurama", "King of the Hill", "The Simpsons", "South Park"], 'answer': 2},

    {'q': "What is the name of the wizard school in Harry Potter?",
     'opts': ["Durmstrang", "Beauxbatons", "Hogwarts", "Castelobruxo"], 'answer': 2},

    {'q': "Which movie franchise includes the 'Kessel Run' storyline?",
     'opts': ["Star Trek", "Guardians of the Galaxy", "Star Wars", "Dune"], 'answer': 2},

    {'q': "Who played the Joker in Joker (2019)?",
     'opts': ["Jared Leto", "Heath Ledger", "Mark Hamill", "Joaquin Phoenix"], 'answer': 3},

    {'q': "In which TV show would you find Daenerys Targaryen?",
     'opts': ["The Witcher", "Outlander", "Game of Thrones", "Vikings"], 'answer': 2},

    {'q': "Which animated Disney film features the song 'Under the Sea'?",
     'opts': ["The Little Mermaid", "Finding Nemo", "Moana", "Aladdin"], 'answer': 0},

    {'q': "What is the name of the toy cowboy in Toy Story?",
     'opts': ["Buzz Lightyear", "Woody", "Rex", "Hamm"], 'answer': 1},

    {'q': "Which pop group performed 'Wannabe' in 1996?",
     'opts': ["The Sugababes", "Destiny's Child", "Spice Girls", "TLC"], 'answer': 2},

    {'q': "Who wrote the Harry Potter book series?",
     'opts': ["Suzanne Collins", "Stephenie Meyer", "J.K. Rowling", "Philip Pullman"], 'answer': 2},

    {'q': "What is the name of Tony Stark's AI assistant in the original Iron Man films?",
     'opts': ["Friday", "Vision", "JARVIS", "Ultron"], 'answer': 2},

    {'q': "In which show do characters say 'How you doin'?",
     'opts': ["Seinfeld", "Friends", "How I Met Your Mother", "Cheers"], 'answer': 1},

    {'q': "Which film franchise features the secret agent known as '007'?",
     'opts': ["Mission: Impossible", "James Bond", "Bourne", "Jack Ryan"], 'answer': 1},

    {'q': "What was the first music video ever played on MTV?",
     'opts': ["Video Killed the Radio Star", "Billie Jean", "Money for Nothing", "Jump"], 'answer': 0},

    {'q': "Which actor played Bruce Wayne in The Dark Knight trilogy?",
     'opts': ["George Clooney", "Michael Keaton", "Val Kilmer", "Christian Bale"], 'answer': 3},

    {'q': "Which song by Pharrell Williams stayed at number one in the US for 24 weeks?",
     'opts': ["Get Lucky", "Happy", "Blurred Lines", "Uptown Funk"], 'answer': 1},

    {'q': "What is the name of the island in Jurassic Park?",
     'opts': ["Isla Sorna", "Isla Nublar", "Isla de Muertes", "Isla Cabra"], 'answer': 1},

    {'q': "Which TV show features the fictional Bluth family?",
     'opts': ["Arrested Development", "Succession", "Schitt's Creek", "Modern Family"], 'answer': 0},

    {'q': "What was the best-selling album of the 20th century?",
     'opts': ["Abbey Road", "Thriller", "Back in Black", "The Dark Side of the Moon"], 'answer': 1},

    {'q': "Who created the cartoon character Mickey Mouse?",
     'opts': ["Walt Disney", "Chuck Jones", "Tex Avery", "Max Fleischer"], 'answer': 0},

    {'q': "Which actress played Black Widow in the MCU?",
     'opts': ["Brie Larson", "Gal Gadot", "Scarlett Johansson", "Zoe Saldana"], 'answer': 2},

    {'q': "What is the name of SpongeBob's best friend?",
     'opts': ["Squidward", "Sandy", "Patrick", "Gary"], 'answer': 2},

    {'q': "Which music genre did Elvis Presley help popularise in the 1950s?",
     'opts': ["Jazz", "Blues", "Rock and Roll", "Country"], 'answer': 2},

    {'q': "Which 2010 film features characters navigating levels of dreams?",
     'opts': ["Interstellar", "The Matrix", "Inception", "Eternal Sunshine"], 'answer': 2},

    {'q': "Who voiced Mufasa in The Lion King (1994)?",
     'opts': ["James Earl Jones", "Morgan Freeman", "Denzel Washington", "Samuel L. Jackson"], 'answer': 0},

    {'q': "Which TV show is set in the fictional town of Pawnee, Indiana?",
     'opts': ["The Office", "Parks and Recreation", "Community", "Brooklyn Nine-Nine"], 'answer': 1},

    {'q': "What is the subtitle of the fourth Avengers film?",
     'opts': ["Infinity War", "Age of Ultron", "Civil War", "Endgame"], 'answer': 3},

    {'q': "Who sang the James Bond theme for Skyfall?",
     'opts': ["Shirley Bassey", "Duran Duran", "Adele", "Sam Smith"], 'answer': 2},

    {'q': "Who wrote the 'A Song of Ice and Fire' novels that Game of Thrones is based on?",
     'opts': ["J.R.R. Tolkien", "George R.R. Martin", "Brandon Sanderson", "Robert Jordan"], 'answer': 1},

    {'q': "Which film features the memorable dance scene between Uma Thurman and John Travolta?",
     'opts': ["Natural Born Killers", "Pulp Fiction", "Reservoir Dogs", "Jackie Brown"], 'answer': 1},

    {'q': "What year did the final episode of Seinfeld air?",
     'opts': ["1996", "1997", "1998", "1999"], 'answer': 2},

    {'q': "Who plays Eleven in Stranger Things?",
     'opts': ["Sadie Sink", "Millie Bobby Brown", "Natalia Dyer", "Maya Hawke"], 'answer': 1},

    {'q': "Which animated Pixar film features a rat who wants to become a chef in Paris?",
     'opts': ["Chef", "Ratatouille", "WALL-E", "A Bug's Life"], 'answer': 1},

    {'q': "What year was the first Shrek film released?",
     'opts': ["1999", "2000", "2001", "2002"], 'answer': 2},

    {'q': "Which iconic rock band featured members Mick Jagger and Keith Richards?",
     'opts': ["The Who", "Led Zeppelin", "The Rolling Stones", "Aerosmith"], 'answer': 2},

    {'q': "In which TV show does the character Don Draper work?",
     'opts': ["The Wire", "Mad Men", "Suits", "Billions"], 'answer': 1},

    {'q': "Which actress starred in Legally Blonde (2001)?",
     'opts': ["Cameron Diaz", "Reese Witherspoon", "Julia Roberts", "Sandra Bullock"], 'answer': 1},

    {'q': "Which pop star had a famous wardrobe malfunction at the 2004 Super Bowl halftime show?",
     'opts': ["Beyoncé", "Britney Spears", "Janet Jackson", "Jennifer Lopez"], 'answer': 2},

    {'q': "What year was the TV show Lost first aired?",
     'opts': ["2002", "2003", "2004", "2005"], 'answer': 2},

    {'q': "What is the name of the killer in the Scream film franchise?",
     'opts': ["Ghostface", "Jason Voorhees", "Michael Myers", "Freddy Krueger"], 'answer': 0},

    {'q': "Who played Neo in The Matrix (1999)?",
     'opts': ["Will Smith", "Brad Pitt", "Tom Cruise", "Keanu Reeves"], 'answer': 3},

    {'q': "What famous TV show features the fictional town of Springfield?",
     'opts': ["South Park", "Futurama", "The Simpsons", "King of the Hill"], 'answer': 2},

    {'q': "What is the name of Moe's bar in The Simpsons?",
     'opts': ["The Rusty Nail", "Paddy's Pub", "Moe's Tavern", "McLaren's Pub"], 'answer': 2},

    {'q': "Which singer is known as 'The King of Pop'?",
     'opts': ["Prince", "Elvis Presley", "Michael Jackson", "David Bowie"], 'answer': 2},

    {'q': "Which film series features the fictional wizard Dumbledore?",
     'opts': ["Narnia", "The Lord of the Rings", "Harry Potter", "Merlin"], 'answer': 2},

    {'q': "Who sang 'We Are the World' (1985)?",
     'opts': ["USA for Africa — various artists", "Michael Jackson solo", "The Beatles", "Prince"], 'answer': 0},

    {'q': "In which year did the final episode of Game of Thrones air?",
     'opts': ["2017", "2018", "2019", "2020"], 'answer': 2},

    {'q': "Which Netflix show is set in a dystopian future where people are matched by algorithm?",
     'opts': ["Altered Carbon", "Black Mirror", "Love, Death & Robots", "Westworld"], 'answer': 1},

    {'q': "What is the name of the fictional high school in Grease (1978)?",
     'opts': ["Jefferson High", "Rydell High", "West Beverly High", "Bayside High"], 'answer': 1},

    {'q': "Which animated film features the character Simba?",
     'opts': ["The Jungle Book", "Bambi", "Tarzan", "The Lion King"], 'answer': 3},

    {'q': "What is the name of the fictional spaceship in Star Trek: The Next Generation?",
     'opts': ["USS Voyager", "USS Enterprise", "USS Defiant", "Millennium Falcon"], 'answer': 1},

    {'q': "Which actor played Forrest Gump?",
     'opts': ["Tom Cruise", "Tom Hanks", "Kevin Costner", "Brad Pitt"], 'answer': 1},

    {'q': "Which band sang 'Smells Like Teen Spirit'?",
     'opts': ["Pearl Jam", "Soundgarden", "Nirvana", "Alice in Chains"], 'answer': 2},

    {'q': "What year was the social network Facebook launched to the public?",
     'opts': ["2004", "2005", "2006", "2007"], 'answer': 2},

    {'q': "Which reality TV show features the catchphrase 'You're fired'?",
     'opts': ["Big Brother", "Survivor", "The Apprentice", "The Amazing Race"], 'answer': 2},

    {'q': "What is the name of the robot in the film WALL-E?",
     'opts': ["EVE", "R2-D2", "WALL-E", "HAL"], 'answer': 2},

    {'q': "Which TV show features the fictional town of Hawkins in the 1980s?",
     'opts': ["Dark", "Stranger Things", "The Americans", "Dark Angel"], 'answer': 1},

    {'q': "Who sang 'Shape of You' in 2017?",
     'opts': ["Sam Smith", "Ed Sheeran", "Harry Styles", "Shawn Mendes"], 'answer': 1},

    {'q': "Which film sequel featured the tagline 'Just when you thought it was safe to go back in the water'?",
     'opts': ["Jaws 2", "The Deep", "Piranha II", "Open Water"], 'answer': 0},
]

ALL_POOLS = [
    ('Video Games', VIDEOGAME_POOL),
    ('Sports',      SPORTS_POOL),
    ('Pop Culture', POP_CULTURE_POOL),
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
        cat_name, pool     = random.choice(ALL_POOLS)
        self.category      = cat_name
        self.questions     = random.sample(pool, 3)
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
            surf.blit(t, (cx - t.get_width() // 2, 220))
            t = font_big.render(f'Category:  {self.category.upper()}',
                                True, c(GOLD_COL))
            surf.blit(t, (cx - t.get_width() // 2, 290))
            t = font_big.render('Answer 3 questions correctly to proceed.',
                                True, c(UI_MUTED))
            surf.blit(t, (cx - t.get_width() // 2, 330))
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
            msg, sub, col = "SALOMON YIELDS!", "Salomon thinks your IQ is over 9000.", CORRECT_COL
        else:
            msg, sub, col = "SALOMON PREVAILS!", "Salomon wonders if you've completed preschool.", WRONG_COL

        t1 = font_title.render(msg, True, col)
        t2 = font_big.render(sub, True, UI_WHITE)
        t3 = font.render("Press ENTER to continue", True, UI_MUTED)
        surf.blit(t1, (cx - t1.get_width() // 2, SCREEN_H // 2 - 65))
        surf.blit(t2, (cx - t2.get_width() // 2, SCREEN_H // 2 - 12))
        surf.blit(t3, (cx - t3.get_width() // 2, SCREEN_H // 2 + 38))
