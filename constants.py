import os.path
import random

import pygame as pg
import pyautogui as pag
pg.font.init()
pg.mixer.init()
"""
GAME PARAMETERS
"""
FPS = 60
SUPER_BALL = False
FIREBALL = False
BEDROCK_CRUSHER = False
ROWS, COLS = 10, 20
BRICKS, bricks = [[] for i in range(10)], []

"""
DIMENSIONS
"""
P_WIDTH, P_HEIGHT = 120, 20
BOTTOM = 170
B_RAD = 15
B_D = 2 * B_RAD
PAD = 2
BRICK_WIDTH, BRICK_HEIGHT = pag.size()[0] // COLS - PAD, 30 - PAD
DROP_ = 53, 37

"""
PROPERTIES
"""
P_SPEED = 10
PRE_B_SPEED = 6
B_SPEED = 4
DAMAGE = 50
BOMB_DAMAGE = 200

"""
FONTS
"""
FONT = pg.font.SysFont('Arial', 120)
FONT_1 = pg.font.SysFont('Impact', 150)

"""
COLORS
"""
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
YELLOW, CYAN, PINK = (255, 255, 0), (0, 255, 255), (255, 0, 255)
GREY = (128, 128, 128)
ORANGE = (255, 128, 0)

BALL_COLOR = YELLOW
PLATFORM_COLOR = GREY

"""
SURFACES
"""
WIN = pg.display.set_mode(pag.size())
PLATFORM_X, PLATFORM_Y = WIN.get_width() // 2 - P_WIDTH // 2, WIN.get_height() - BOTTOM - P_HEIGHT
PLATFORM = pg.Rect(PLATFORM_X, PLATFORM_Y, P_WIDTH, P_HEIGHT)
BALL_X, BALL_Y = WIN.get_width() // 2 - B_RAD, WIN.get_height() - BOTTOM - P_HEIGHT - B_D
BALL = pg.Rect(BALL_X, BALL_Y, B_D, B_D)

"""
EVENTS
"""
GAME_OVER = pg.USEREVENT + 1
DROP = pg.USEREVENT + 2
DROP_CAUGHT = pg.USEREVENT + 3
CLICK_PLAY = pg.USEREVENT + 4
BOMB_EXPLOSION = pg.USEREVENT + 5

"""
SOUNDS
"""
BOMB_SOUND = pg.mixer.Sound(os.path.join('Assets', 'sound.wav'))
SHIELD_SOUND = pg.mixer.Sound(os.path.join('Assets', 'zap.wav'))
END_SHIELD_SOUND = pg.mixer.Sound(os.path.join('Assets', 'zap1.wav'))
HIT = pg.mixer.Sound(os.path.join('Assets', 'hit.wav'))

"""
OTHERS
"""
UP, RIGHT = 1, 1
BEDROCKS = random.randint(10, 15)
BOMBS = random.randint(20, 25)
SHIELDS = random.randint(30, 40)
BASICS = 200 - BEDROCKS - BOMBS - SHIELDS
