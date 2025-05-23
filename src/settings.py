# ГРАФИЧЕСКИЕ НАСТРОЙКИ
WIDTH = 960
HEIGHT = 640
FPS = 60

# НАСТРОЙКИ UI И ЕГО ЗВУКОВ
START_SCREEN_PATH = '../img/ui/start_screen.png'
END_SCREEN_PATH = '../img/ui/end_screen.png'
START_SCREEN_MUSIC_PATH = '../sounds/menu.mp3'

# ГЛОБАЛЬНЫЕ НАСТРОЙКИ ФИЗИКИ
GRAVITY_ACCELERATION = 0.2
MAX_FALL_SPEED = 5

# НАСТРОЙКИ ИГРОКА
PLAYER_START_POS = (37, 36.5)

PLAYER_JUMP_SPEED = 5
PLAYER_WALK_SPEED = 1.8

PLAYER_IMAGE = '../img/player/facing/0.png'
PLAYER_FRAMES = [
    '../img/player/walk/0.png',
    '../img/player/walk/1.png',
]
PLAYER_JUMP_SOUND = '../sounds/jump.mp3'
PLAYER_DAMAGED_SOUND = '../sounds/майнрафт смерть.mp3'
PLAYER_ATTACK_SOUND = '../sounds/майнрафт урон.mp3'
PLAYER_ATTACK_FRAMES = [
    '../img/player/attack/0.png',
    '../img/player/attack/1.png',
    '../img/player/attack/2.png',
    '../img/player/attack/3.png',
    '../img/player/attack/4.png',
]

PLAYER_HEALTH = 200
PLAYER_DAMAGE = 100

# НАСТРОЙКИ СЛИЗНЕЙ
SLIME_1_START_POS = (6, 36.5)
SLIME_2_START_POS = (9, 36.5)
SLIME_3_START_POS = (13, 36.5)
SLIME_IMAGE = '../img/NPC/NPC0/idle/idle.png'
# Дополнительные настройки для слаймов
SLIME_JUMP_FORCE = 4  # Сила прыжка слайма
SLIME_SPEED = 1.5     # Скорость передвижения слайма
SLIME_JUMP_COOLDOWN = 1000

SLIME_DEATH_SOUND = '../sounds/майнрафт смерть.mp3'

SLIME_FRAMES = [
    '../img/NPC/NPC0/walk/0.png',
    '../img/NPC/NPC0/walk/1.png',
    '../img/NPC/NPC0/walk/2.png',
]
SLIME_ATTACK_FRAMES = [
    '../img/NPC/NPC0/attack/0.png',
    '../img/NPC/NPC0/attack/1.png',
    '../img/NPC/NPC0/attack/2.png',
    '../img/NPC/NPC0/attack/3.png',
]

SLIME_HEALTH = 20
SLIME_DAMAGE = 50

# НАСТРОЙКИ УРОВНЯ
LEVEL1_PATH = '../maps/level1/level1.tmx'
BACKGROUND_IMAGE_0 = '../img/background/first_door.png'
BACKGROUND_IMAGE_1 = '../img/background/first_without_door.png'

# НАСТРОЙКИ СУНДУКА И АЛМАЗА
diamond_pos = (10, 3.5)
chest_pos = (37.5, 23.2)
diamond_image = '../img/pickups/orangecrystal.png'
chest_image = '../img/sunduk/chest1.png'
