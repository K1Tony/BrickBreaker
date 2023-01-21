import random
from abc import ABC, abstractmethod
import pygame as pg
import constants as c
import os


class Upgrade(ABC):

    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.color = None
        self.rect = pg.Rect(x, y, image.get_width(), image.get_height())
        self.duration = 1500

    def place(self):
        c.WIN.blit(self.image, (self.rect.x, self.rect.y))

    def catch(self) -> bool:
        return self.rect.colliderect(c.PLATFORM)

    @abstractmethod
    def utilise(self):
        pass

    @abstractmethod
    def finish(self):
        pass


class SuperBall(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'super.png')), c.DROP_)):
        super(SuperBall, self).__init__(x, y, image)
        self.color = c.GREEN

    def utilise(self):
        c.SUPER_BALL = True

    def finish(self):
        c.SUPER_BALL = False


class DmgUp(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'dmg+.png')), c.DROP_)):
        super(DmgUp, self).__init__(x, y, image)
        self.color = c.RED

    def utilise(self):
        c.DAMAGE += 150
        c.B_RAD += 5

    def finish(self):
        c.DAMAGE -= 150
        c.B_RAD -= 5


class SlowBall(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'SlowBall.png')), c.DROP_)):
        super(SlowBall, self).__init__(x, y, image)
        self.utilised = False
        self.color = c.BLUE

    def utilise(self):
        if c.B_SPEED > 1:
            c.B_SPEED -= 1
            self.utilised = True

    def finish(self):
        if self.utilised:
            c.B_SPEED += 1
            self.utilised = False


class LongPlatform(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets',
                                                                                 'LongPlatform.png')), c.DROP_)):
        super(LongPlatform, self).__init__(x, y, image)

    def utilise(self):
        c.PLATFORM.width += 100
        c.P_WIDTH += 100

    def finish(self):
        c.PLATFORM.width -= 100
        c.P_WIDTH -= 100


class FastPlatform(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets',
                                                                                 'FastPlatform.png')), c.DROP_)):
        super(FastPlatform, self).__init__(x, y, image)

    def utilise(self):
        c.P_SPEED += 5

    def finish(self):
        c.P_SPEED -= 5


class Fireball(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'Fireball.png')),
                                                      c.DROP_)):
        super(Fireball, self).__init__(x, y, image)
        self.color = c.ORANGE

    def utilise(self):
        c.DAMAGE -= 10
        c.FIREBALL = True

    def finish(self):
        c.DAMAGE += 10
        c.FIREBALL = False
        
        
class BedrockCrusher(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'BedrockCrusher.png')),
                                                      c.DROP_)):
        super(BedrockCrusher, self).__init__(x, y, image)
        self.color = 66, 21, 115

    def utilise(self):
        c.BEDROCK_CRUSHER = True

    def finish(self):
        c.BEDROCK_CRUSHER = False
        
        
class Nuke(Upgrade):
    def __init__(self, x, y, image=None):
        super(Nuke, self).__init__(x, y, image)

"""
DOWNGRADES
"""


class FastBall(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'FastBall.png')), c.DROP_)):
        super(FastBall, self).__init__(x, y, image)
        self.color = 3, 236, 252

    def utilise(self):
        c.B_SPEED += 1

    def finish(self):
        c.B_SPEED -= 1


class SlowPlatform(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'SlowPlatform.png')),
                                                      c.DROP_)):
        super(SlowPlatform, self).__init__(x, y, image)
        self.utilised = False

    def utilise(self):
        if c.P_SPEED > 4:
            c.P_SPEED -= 4
            self.utilised = True

    def finish(self):
        if self.utilised:
            c.P_SPEED += 4
            self.utilised = False


class ShortPlatform(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'ShortPlatform.png')),
                                                      c.DROP_)):
        super(ShortPlatform, self).__init__(x, y, image)
        self.utilised = False

    def utilise(self):
        if c.P_WIDTH > 50 and c.PLATFORM.width > 50:
            c.P_WIDTH -= 40
            c.PLATFORM.width -= 40
            self.utilised = True

    def finish(self):
        if self.utilised:
            c.P_WIDTH += 40
            c.PLATFORM.width += 40
            self.utilised = False


class DmgDown(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'dmg-.png')), c.DROP_)):
        super(DmgDown, self).__init__(x, y, image)
        self.utilised = False
        self.color = c.WHITE

    def utilise(self):
        if c.DAMAGE > 10:
            c.DAMAGE -= 10
            self.utilised = True

    def finish(self):
        if self.utilised:
            c.DAMAGE += 10


class ToughBricks(Upgrade):
    def __init__(self, x, y, image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'ToughBrick.png')),
                                                              c.DROP_)):
        super(ToughBricks, self).__init__(x, y, image)

    def utilise(self):
        for brick in c.bricks:
            brick.health += 100

    def finish(self):
        for brick in c.bricks:
            if brick.health > 100:
                brick.health -= 100
            else:
                brick.health = 10


class ExtraBricks(Upgrade):
    def __init__(self, x, y, types,
                 image=pg.transform.scale(pg.image.load(os.path.join('Assets', 'ExtraBricks.png')), c.DROP_)):
        super(ExtraBricks, self).__init__(x, y, image)
        self.types = types
        self.duration = 0

    def utilise(self):
        for bricks in c.BRICKS:
            for brick in bricks:
                brick.rect.y += (brick.height + c.PAD)
                brick.y += (brick.height + c.PAD)
        range_ = list(range(c.COLS))
        bedrocks, bombs, shields, basics = [], [], [], []
        for _ in range(2):
            r = random.choice(range_)
            bedrocks.append(r)
            range_.remove(r)
        for _ in range(3):
            r = random.choice(range_)
            bombs.append(r)
            range_.remove(r)
        for _ in range(5):
            r = random.choice(range_)
            shields.append(r)
            range_.remove(r)
        basics = range_
        extra_bricks = []
        for bedrock in bedrocks:
            extra_bricks.append(self.types[0](bedrock * (c.BRICK_WIDTH + c.PAD), 0))
        for bomb in bombs:
            extra_bricks.append(self.types[1](bomb * (c.BRICK_WIDTH + c.PAD), 0))
        for shield in shields:
            extra_bricks.append(self.types[2](shield * (c.BRICK_WIDTH + c.PAD), 0))
        for basic in basics:
            extra_bricks.append(self.types[3](basic * (c.BRICK_WIDTH + c.PAD), 0))
        extra_bricks.sort(key=lambda x: x.x)
        c.BRICKS.insert(0, extra_bricks)
        c.bricks += extra_bricks

    def finish(self):
        pass


POWERS =\
        {
            SuperBall: pg.transform.scale(pg.image.load(os.path.join('Assets', 'super.png')), c.DROP_),
            DmgUp: pg.transform.scale(pg.image.load(os.path.join('Assets', 'dmg+.png')), c.DROP_),
            SlowBall: pg.transform.scale(pg.image.load(os.path.join('Assets', 'SlowBall.png')), c.DROP_),
            FastPlatform: pg.transform.scale(pg.image.load(os.path.join('Assets', 'FastPlatform.png')), c.DROP_),
            LongPlatform: pg.transform.scale(pg.image.load(os.path.join('Assets', 'LongPlatform.png')), c.DROP_),
            Fireball: pg.transform.scale(pg.image.load(os.path.join('Assets', 'Fireball.png')), c.DROP_),
            BedrockCrusher: pg.transform.scale(pg.image.load(os.path.join('Assets', 'BedrockCrusher.png')), c.DROP_),
            FastBall: pg.transform.scale(pg.image.load(os.path.join('Assets', 'FastBall.png')), c.DROP_),
            SlowPlatform: pg.transform.scale(pg.image.load(os.path.join('Assets', 'SlowPlatform.png')), c.DROP_),
            ShortPlatform: pg.transform.scale(pg.image.load(os.path.join('Assets', 'ShortPlatform.png')), c.DROP_),
            DmgDown: pg.transform.scale(pg.image.load(os.path.join('Assets', 'dmg-.png')), c.DROP_),
            ToughBricks: pg.transform.scale(pg.image.load(os.path.join('Assets', 'ToughBrick.png')), c.DROP_),
            ExtraBricks: pg.transform.scale(pg.image.load(os.path.join('Assets', 'ExtraBricks.png')), c.DROP_)
        }
