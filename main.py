import pygame as pg
import constants as c
import os
import random
from abc import ABC
import Upgrades as u
pg.init()
pg.mixer.init()

drop_coords = []


class Brick(ABC):
    def __init__(self, x, y, health, color, width=c.BRICK_WIDTH, height=c.BRICK_HEIGHT):
        self.x = x
        self.y = y
        self.health = health
        self.color = color
        self.width = width
        self.height = height
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.flame_index = 0

    def __call__(self):
        if self.health > 0:
            pg.draw.rect(c.WIN, self.color, self.rect, border_radius=c.PAD)

    def collide(self) -> int:
        if ((c.BALL.x + c.B_SPEED < self.x + self.width < c.BALL.x + c.B_D + c.B_SPEED and c.RIGHT == -1) or
            (c.BALL.x + c.B_D + c.B_SPEED > self.x > c.BALL.x + c.B_SPEED and c.RIGHT == 1)) and\
                (self.y < c.BALL.y + c.BALL.width and c.BALL.y < self.y + self.height):
            return 1
        if ((c.BALL.y - c.B_SPEED < self.y + self.height < c.BALL.y + c.B_D - c.B_SPEED and c.UP == 1) or
            (c.BALL.y + c.B_D + c.B_SPEED > self.y > c.BALL.y + c.B_SPEED and c.UP == -1)) and\
                (self.x < c.BALL.x + c.BALL.width and c.BALL.x < self.x + self.width):
            return 2
        return 0

    def take_hit(self, damage):
        pg.draw.rect(c.WIN, c.RED, self.rect, border_radius=c.PAD)
        self.health -= damage

    def dead(self) -> bool:
        return self.health <= 0

    def __repr__(self):
        return f'{self.x // (c.BRICK_WIDTH + c.PAD), self.y // (c.BRICK_HEIGHT + c.PAD)}'

    def flaming(self):
        if self.flame_index < 50:
            self.take_hit(1)
        else:
            self.flame_index = 0


class Basic(Brick):
    def __init__(self, x, y, health=50, color=(140, 140, 140), width=c.BRICK_WIDTH, height=c.BRICK_HEIGHT):
        super(Basic, self).__init__(x, y, health, color, width, height)


class Shielded(Brick):
    def __init__(self, x, y, health=20, color=c.WHITE, width=c.BRICK_WIDTH, height=c.BRICK_HEIGHT):
        super(Shielded, self).__init__(x, y, health, color, width, height)
        self.shield = 200

    def __call__(self):
        if self.shield > 0:
            pg.draw.rect(c.WIN, c.CYAN, self.rect, border_radius=c.PAD)
        else:
            pg.draw.rect(c.WIN, self.color, self.rect, border_radius=c.PAD)

    def take_hit(self, damage):
        if self.shield <= 0:
            pg.draw.rect(c.WIN, c.RED, self.rect, border_radius=c.PAD)
            self.health -= damage
        else:
            pg.draw.rect(c.WIN, c.RED, self.rect, border_radius=c.PAD)
            self.shield -= damage


class Bombed(Brick):
    def __init__(self, x, y, other=None, health=50, color=(60, 60, 60), width=c.BRICK_WIDTH, height=c.BRICK_HEIGHT):
        super(Bombed, self).__init__(x, y, health, color, width, height)
        self.other = other


class Bedrock(Brick):
    def __init__(self, x, y, health=float('inf'), color=c.BLACK, width=c.BRICK_WIDTH, height=c.BRICK_HEIGHT):
        super(Bedrock, self).__init__(x, y, health, color, width, height)

    def take_hit(self, damage):
        if c.BEDROCK_CRUSHER:
            self.health = 0


def others(obj: object, itr: list[list[object]]) -> list[tuple[int, int]]:
    end_x = len(itr[0]) - 1
    end_y = len(itr) - 1
    transpose = [[itr[i][j] for i in range(end_y + 1)] for j in range(end_x + 1)]
    if itr[0][0] == obj:
        return [(0, 1), (1, 0), (1, 1)]
    elif itr[0][end_x] == obj:
        return [(0, end_x - 1), (1, end_x), (1, end_x - 1)]
    elif itr[end_y][0] == obj:
        return [(end_y - 1, 0), (end_y, 1), (end_y - 1, 1)]
    elif itr[end_y][end_x] == obj:
        return [(end_y, end_x - 1), (end_y - 1, end_x), (end_y - 1, end_x - 1)]
    elif obj in itr[0]:
        idx = itr[0].index(obj)
        return [(0, idx - 1), (0, idx + 1), (1, idx - 1), (1, idx), (1, idx + 1)]
    elif obj in itr[end_y]:
        idx = itr[end_y].index(obj)
        return [(end_y, idx - 1), (end_y, idx + 1), (end_y - 1, idx - 1), (end_y - 1, idx), (end_y - 1, idx + 1)]
    elif obj in transpose[0]:
        idx = transpose[0].index(obj)
        return [(idx - 1, 0), (idx + 1, 0), (idx - 1, 1), (idx, 1), (idx + 1, 1)]
    elif obj in transpose[end_x]:
        idx = transpose[end_x].index(obj)
        return [(idx - 1, end_x), (idx + 1, end_x), (idx - 1, end_x - 1), (idx, end_x - 1), (idx + 1, end_x - 1)]
    found = []
    for i in itr:
        if obj in i:
            found += i
    idx_x = found.index(obj)
    idx_y = itr.index(found)
    return [(idx_y - 1, idx_x - 1), (idx_y - 1, idx_x), (idx_y - 1, idx_x + 1), (idx_y, idx_x - 1), (idx_y, idx_x + 1),
            (idx_y + 1, idx_x - 1), (idx_y + 1, idx_x), (idx_y + 1, idx_x + 1)]


def create_bricks():
    coordinates = []

    def set_(key):
        position = (random.randint(0, 19) * (c.BRICK_WIDTH + c.PAD), random.randint(0, 9) * (c.BRICK_HEIGHT + c.PAD))
        while position in coordinates:
            position = (random.randint(0, 19) * (c.BRICK_WIDTH + c.PAD), random.randint(0, 9) * (c.BRICK_HEIGHT + c.PAD)
                        )
        coordinates.append(position)
        c.bricks.append(key(*position))

    for i in range(c.BEDROCKS):
        set_(Bedrock)
    for i in range(c.BOMBS):
        set_(Bombed)
    for i in range(c.SHIELDS):
        set_(Shielded)
    for i in range(c.BASICS):
        set_(Basic)
    c.bricks = sorted(c.bricks, key=lambda x: x.y)
    index = 0
    for idx, val in enumerate(c.bricks):
        c.BRICKS[index].append(val)
        if (idx + 1) % c.COLS == 0:
            index += 1
    for i in c.BRICKS:
        i.sort(key=lambda x: x.x)


def set_menu_background(cursor: tuple[int, int]):
    c.WIN.fill(c.GREEN)
    text = c.FONT_1.render('BRICK BREAKER', True, c.BLACK)
    play = pg.font.SysFont('Arial', 50).render('Play', True, c.BLACK)
    text_x = (c.WIN.get_width() - play.get_width()) // 2
    c.WIN.blit(text, ((c.WIN.get_width() - text.get_width()) // 2, (c.WIN.get_height() - text.get_height()) // 2))
    pg.draw.rect(c.WIN, c.PLATFORM_COLOR, c.PLATFORM)
    pg.draw.circle(c.WIN, c.BALL_COLOR, (c.BALL.x + c.B_RAD, c.BALL.y + c.B_RAD), c.B_RAD)
    pg.draw.rect(c.WIN, c.WHITE, pg.Rect(text_x, c.BOTTOM, play.get_width(), play.get_height()))
    c.WIN.blit(play, ((c.WIN.get_width() - play.get_width()) // 2, c.BOTTOM))
    if text_x <= cursor[0] <= text_x + play.get_width() and c.BOTTOM <= cursor[1] <= c.BOTTOM + play.get_height():
        pg.event.post(pg.event.Event(c.CLICK_PLAY))
    pg.display.update()


def set_background(game_over: bool, drops: list[u.Upgrade], upgrades: dict[u.Upgrade: bool]):
    global drop_coords
    c.WIN.blit(pg.transform.scale(pg.image.load(os.path.join('Assets', 'webbs.jpg')), (c.WIN.get_width(),
                                                                                       c.WIN.get_height())), (0, 0))
    x_position = 0
    for key, value in upgrades.items():
        if value > 0:
            c.WIN.blit(u.POWERS[key], (x_position, c.WIN.get_height() - u.POWERS[key].get_height()))
            x_position += u.POWERS[key].get_width()
    pg.draw.rect(c.WIN, c.PLATFORM_COLOR, c.PLATFORM)
    pg.draw.circle(c.WIN, c.BALL_COLOR, (c.BALL.x + c.B_RAD, c.BALL.y + c.B_RAD), c.B_RAD)
    if game_over:
        text = c.FONT.render('GAME OVER', True, c.RED)
        c.WIN.blit(text, (c.WIN.get_width() // 2 - text.get_width() // 2, c.WIN.get_height() // 2 -
                          text.get_height() // 2))
    for brick in c.bricks:
        if brick.dead():
            c.bricks.remove(brick)
            r = random.randint(1, 10)
            if r in [1, 2, 3, 4, 5]:
                pg.event.post(pg.event.Event(c.DROP))
                drop_coords.append((brick.x, brick.y))
            if isinstance(brick, Bombed):
                brick.other = others(brick, c.BRICKS)
                for i in brick.other:
                    target = c.BRICKS[i[0]][i[1]]
                    if target in c.bricks:
                        target.take_hit(c.BOMB_DAMAGE)
                c.BOMB_SOUND.play(0, 0, 100)
                for i in range(100):
                    pg.draw.rect(c.WIN, c.ORANGE, pg.Rect(brick.x - brick.width, brick.y - brick.height,
                                                          brick.width * 3, brick.height * 3), border_radius=c.PAD)
        else:
            brick()
    for idx, brick in enumerate(c.bricks):
        if brick.collide() == 1:
            if isinstance(brick, Shielded) and brick.shield - c.DAMAGE <= 0:
                c.END_SHIELD_SOUND.play()
            elif isinstance(brick, Shielded) and brick.shield > 0:
                c.SHIELD_SOUND.play()
            elif isinstance(brick, Basic) or isinstance(brick, Shielded) and brick.shield <= 0:
                c.HIT.play()
            brick.take_hit(c.DAMAGE)
            if not c.SUPER_BALL:
                if idx < len(c.bricks) - 20 and c.bricks[idx + 20].collide() == 1:
                    c.RIGHT *= -1
                elif idx > 19 and c.bricks[idx - 20].collide() == 1:
                    pass
                else:
                    c.RIGHT *= -1
            if c.FIREBALL:
                brick.flame_index += 1
        if brick.collide() == 2:
            if isinstance(brick, Shielded) and brick.shield > 0 and brick.shield - c.DAMAGE <= 0:
                c.END_SHIELD_SOUND.play()
            elif isinstance(brick, Shielded) and brick.shield > 0:
                c.SHIELD_SOUND.play()
            elif isinstance(brick, Basic) or isinstance(brick, Shielded) and brick.shield <= 0:
                c.HIT.play()
            brick.take_hit(c.DAMAGE)
            if not c.SUPER_BALL:
                if idx < len(c.bricks) - 1 and c.bricks[idx + 1].collide() == 2:
                    c.UP *= -1
                elif idx > 0 and c.bricks[idx - 1].collide() == 2:
                    pass
                else:
                    c.UP *= -1
            if c.FIREBALL:
                brick.flame_index += 1
        if brick.flame_index > 0:
            brick.flaming()
    for i in drops:
        i.place()

    pg.display.update()


def manage_ball(state: bool, super_speed: bool):
    speed = c.B_SPEED
    if super_speed:
        speed = c.PRE_B_SPEED
    if state:
        if c.BALL.y - speed * c.UP < 0 or (c.PLATFORM.y + c.P_HEIGHT > c.BALL.y - speed * c.UP + c.B_D >
                                           c.PLATFORM.y and c.PLATFORM.x <= c.BALL.x
                                           + c.BALL.width and c.BALL.x <= c.PLATFORM.x + c.P_WIDTH):
            c.UP *= -1
        if c.BALL.x + speed * c.RIGHT < 0 or c.BALL.x + speed * c.RIGHT + c.B_D > c.WIN.get_width():
            c.RIGHT *= -1

        c.BALL.x += speed * c.RIGHT
        c.BALL.y -= speed * c.UP

        if c.BALL.y + c.B_D >= c.WIN.get_height():
            pg.event.post(pg.event.Event(c.GAME_OVER))


def manage_drops(drops, game_over):
    if not game_over:
        for i in drops:
            if c.PLATFORM.colliderect(i.rect):
                i.utilise()
                pg.event.post(pg.event.Event(c.DROP_CAUGHT))
            else:
                i.rect.y += 2


def main():
    create_bricks()
    print(c.BRICKS, c.bricks, sep='\n')
    pre_run = True
    run = True
    clock = pg.time.Clock()
    ball_stationed = True
    game_over = False
    drops = []
    counter = []

    upgrades = {
        u.SuperBall: 0,
        u.DmgUp: 0,
        u.SlowBall: 0,
        u.FastPlatform: 0,
        u.LongPlatform: 0,
        u.Fireball: 0,
        u.BedrockCrusher: 0,
        u.FastBall: 0,
        u.SlowPlatform: 0,
        u.ShortPlatform: 0,
        u.DmgDown: 0,
        u.ToughBricks: 0,
        u.ExtraBricks: 0
    }
    while pre_run:
        clock.tick(c.FPS)
        cursor = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                run = False
                pre_run = False
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                c.BALL.x = c.WIN.get_width() // 2 - c.B_RAD
                c.BALL.y = c.WIN.get_height() - c.BOTTOM - c.P_HEIGHT - c.B_D
                c.PLATFORM.x = c.WIN.get_width() // 2 - c.P_WIDTH // 2
                c.PLATFORM.y = c.WIN.get_height() - c.BOTTOM - c.P_HEIGHT
                pre_run = False
                break
            if event.type == pg.MOUSEBUTTONDOWN and event.type == c.CLICK_PLAY:
                pre_run = False
                break
        if not pre_run:
            break
        set_menu_background(cursor)
        manage_ball(True, True)
        c.PLATFORM.x = c.BALL.x - c.P_WIDTH // 2
    while run:
        clock.tick(c.FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run = False
                    break
                if event.key == pg.K_LALT and ball_stationed:
                    ball_stationed = False
                    c.RIGHT = -1
                if event.key == pg.K_RALT and ball_stationed:
                    ball_stationed = False
                if game_over and event.key == pg.K_SPACE:
                    for i in counter:
                        i[1].finish()
                    c.bricks.clear()
                    c.BRICKS = [[] for _ in range(10)]
                    create_bricks()
                    drops.clear()
                    counter.clear()
                    upgrades = {key: 0 for key in upgrades}

                    c.BALL.x = c.WIN.get_width() // 2 - c.B_RAD
                    c.BALL.y = c.WIN.get_height() - c.BOTTOM - c.P_HEIGHT - c.B_D
                    c.PLATFORM.x = c.WIN.get_width() // 2 - c.P_WIDTH // 2
                    c.PLATFORM.y = c.WIN.get_height() - c.BOTTOM - c.P_HEIGHT
                    game_over = False
                    ball_stationed = True
                    break
            if event.type == c.GAME_OVER:
                game_over = True
            if event.type == c.DROP:
                for drop in drop_coords:
                    chance = random.randint(1, 100)
                    if chance in range(1, 3):
                        drops.append(u.SuperBall(*drop))
                    elif chance in range(3, 18):
                        drops.append(u.DmgUp(*drop))
                    elif chance in range(18, 28):
                        drops.append(u.SlowBall(*drop))
                    elif chance in range(28, 38):
                        drops.append(u.FastPlatform(*drop))
                    elif chance in range(38, 43):
                        drops.append(u.LongPlatform(*drop))
                    elif chance in range(43, 48):
                        drops.append(u.Fireball(*drop))
                    elif chance in range(48, 51):
                        drops.append(u.BedrockCrusher(*drop))
                    elif chance in range(51, 61):
                        drops.append(u.FastBall(*drop))
                    elif chance in range(61, 71):
                        drops.append(u.SlowPlatform(*drop))
                    elif chance in range(71, 76):
                        drops.append(u.ShortPlatform(*drop))
                    elif chance in range(76, 86):
                        drops.append(u.DmgDown(*drop))
                    elif chance in range(86, 91):
                        drops.append(u.ToughBricks(*drop))
                    else:
                        drops.append(u.ExtraBricks(*drop, (Bedrock, Bombed, Shielded, Basic)))
                drop_coords.clear()
            if event.type == c.DROP_CAUGHT:
                for i in drops:
                    if i.catch():
                        if not isinstance(i, u.ExtraBricks):
                            upgrades[type(i)] += 1
                            counter.append([0, i])
                        drops.remove(i)
        for drop in drops:
            if drop.rect.y >= c.WIN.get_height():
                drops.remove(drop)
        for i in counter:
            if i[0] < i[1].duration:
                if i[1].color is not None:
                    c.BALL_COLOR = i[1].color
                else:
                    c.BALL_COLOR = c.YELLOW
                i[0] += 1
                print(i[0])
            else:
                if upgrades[type(i[1])] == 0:
                    i[1].finish()
                    counter.remove(i)
                else:
                    upgrades[type(i[1])] -= 1
                print(upgrades[type(i[1])])
                k = []
                for j in c.BRICKS:
                    if j:
                        k = j
                r = random.choice(k)
                if ((isinstance(i[1], u.SuperBall) and upgrades[u.SuperBall] == 0) or isinstance(i[1], u.ExtraBricks))\
                        and c.BALL.y - c.B_SPEED * c.UP <= r.y + r.height:
                    ball_stationed = True
                    c.BALL.x = c.PLATFORM.x + c.P_WIDTH // 2 - c.B_RAD
                    c.BALL.y = c.PLATFORM.y - c.B_D
        if not counter:
            c.BALL_COLOR = c.YELLOW
        if not game_over:
            pressed = pg.key.get_pressed()
            if (pressed[pg.K_a] or pressed[pg.K_LEFT]) and c.PLATFORM.x > 0:
                c.PLATFORM.x -= c.P_SPEED
                if ball_stationed:
                    c.BALL.x -= c.P_SPEED
            if (pressed[pg.K_d] or pressed[pg.K_RIGHT]) and c.PLATFORM.x + c.P_WIDTH < c.WIN.get_width():
                c.PLATFORM.x += c.P_SPEED
                if ball_stationed:
                    c.BALL.x += c.P_SPEED
        if not c.bricks or False not in map(lambda x: isinstance(x, Bedrock), c.bricks):
            run = False
        set_background(game_over, drops, upgrades)
        manage_ball(not ball_stationed, False)
        manage_drops(drops, game_over)
    if run:
        main()


if __name__ == '__main__':
    main()
