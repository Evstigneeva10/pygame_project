import pygame
import os
from random import choice, randrange
import math

BALLS = 20
FPS = 100
R = randrange(50, 255)
G = randrange(50, 255)
B = randrange(50, 255)
COLOR = (R, G, B)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('star.png', -1), (14, 14))
        self.rect = self.image.get_rect()
        self.rect.x = width // 2 - self.image.get_width() // 2
        self.rect.y = 0
        self.pos = [self.rect.x, self.rect.y]
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = [0, 0]
        self.in_sea = False
        self.polygon_coords = []
        self.lastx = self.rect.x
        self.lasty = self.rect.y
        self.borders = []

    def get_center_coords(self):
        return self.rect.x + self.image.get_width() // 2, self.rect.y + self.image.get_height() // 2

    def append_coord(self, coord):
        checker = CheckPoint(self.get_center_coords())
        if pygame.sprite.collide_mask(checker, sea):
            self.polygon_coords.append(coord)
        checker.kill()

    def set_last_coords(self, coord):
        x, y = coord
        border = Border(self.lastx, self.lasty, x, y)
        self.borders.append(border)
        self.lastx = x
        self.lasty = y

    def border_check(self):
        if pygame.sprite.spritecollideany(self, ball_sprites):
            return False
        x, y = self.get_center_coords()
        border = Border(self.lastx, self.lasty, x, y)
        if pygame.sprite.spritecollideany(border, white_ball_sprites):
            border.kill()
            return False
        border.kill()
        for el in self.borders:
            if pygame.sprite.spritecollideany(el, white_ball_sprites):
                return False
        return True

    def update(self):
        if not self.border_check():
            self.rect.x = width // 2 - self.image.get_width() // 2
            self.rect.y = 0
            self.pos = [self.rect.x, self.rect.y]
            self.speed = [0, 0]
            self.in_sea = False
            self.polygon_coords = []
            self.lastx = self.rect.x
            self.lasty = self.rect.y
            self.borders = []
            return
        checker = CheckPoint(self.get_center_coords())
        if self.in_sea and pygame.sprite.collide_mask(checker, land):
            self.speed = [0, 0]
            self.in_sea = False
        checker.kill()
        for coord in (0, 1):
            if (self.pos[coord] >= size[coord] - 14 and self.speed[coord] > 0 or
                    self.pos[coord] <= 0 and self.speed[coord] < 0):
                self.speed[coord] = 0
            self.pos[coord] += self.speed[coord]
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        checker = CheckPoint(self.get_center_coords())
        if pygame.sprite.collide_mask(checker, sea) and not self.in_sea:
            self.in_sea = True
            self.append_coord(self.get_center_coords())
        if pygame.sprite.collide_mask(checker, land):
            if len(self.polygon_coords) >= 1:
                start_coord = self.polygon_coords[0]
                finish_coord = self.get_center_coords()
                land.modify(start_coord, finish_coord, self.polygon_coords)
                print(land.get_area())
            self.polygon_coords.clear()
            self.borders.clear()
            self.lastx, self.lasty = self.get_center_coords()
        checker.kill()

    def draw_polygon(self):
        if len(self.polygon_coords) >= 1:
            polygon_coords = self.polygon_coords.copy()
            polygon_coords.append(self.get_center_coords())
            pygame.draw.aalines(screen, (255, 0, 0), False, tuple(polygon_coords), 5)
            del polygon_coords


class CheckPoint(pygame.sprite.Sprite):
    def __init__(self, *coords):
        super().__init__(all_sprites)
        surf = pygame.Surface((1, 1), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 255))
        self.image = surf
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = coords


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            surf = pygame.Surface((5, abs(y1 - y2)), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 255))
            self.image = surf
            self.rect = self.image.get_rect()
            self.rect.x = min(x1, x2) - 2
            self.rect.y = min(y1, y2)
        else:
            surf = pygame.Surface((abs(x1 - x2), 5), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 255))
            self.image = surf
            self.rect = self.image.get_rect()
            self.rect.x = min(x1, x2)
            self.rect.y = min(y1, y2) - 2
        self.mask = pygame.mask.from_surface(self.image)


class WhiteBall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        arr = [-1, -0.9, -0.8, -0.7, -0.6, -0.5, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        self.speed = [choice(arr), choice(arr)]
        self.pos = [randrange(40, width - 40), randrange(40, height - 40)]
        self.delta = [0.0, 0.0]
        self.topleft = (self.pos[0], self.pos[1])
        self.image = pygame.transform.scale(load_image('white-tennis-ball.png', -1), (10, 10))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.flag = [True, True]

    def update(self):
        if pygame.sprite.collide_mask(self, land) and all(self.flag):
            if self.speed[1] < 0:
                check1 = CheckBall(self.rect.x - 1, self.rect.y - 1)
                check2 = CheckBall(self.rect.x + 1, self.rect.y - 1)
                if pygame.sprite.collide_mask(check1, land) and pygame.sprite.collide_mask(check2, land):
                    self.flag[1] = False
                    self.speed[1] = -self.speed[1]
                    self.delta[1] = self.speed[1]
            else:
                check1 = CheckBall(self.rect.x - 1, self.rect.y + 1)
                check2 = CheckBall(self.rect.x + 1, self.rect.y + 1)
                if pygame.sprite.collide_mask(check1, land) and pygame.sprite.collide_mask(check2, land):
                    self.flag[1] = False
                    self.speed[1] = -self.speed[1]
                    self.delta[1] = self.speed[1]
            if self.speed[0] < 0:
                check1 = CheckBall(self.rect.x - 1, self.rect.y - 1)
                check2 = CheckBall(self.rect.x - 1, self.rect.y + 1)
                if pygame.sprite.collide_mask(check1, land) and pygame.sprite.collide_mask(check2, land):
                    self.flag[0] = False
                    self.speed[0] = -self.speed[0]
                    self.delta[0] = self.speed[0]
            else:
                check1 = CheckBall(self.rect.x + 1, self.rect.y - 1)
                check2 = CheckBall(self.rect.x + 1, self.rect.y + 1)
                if pygame.sprite.collide_mask(check1, land) and pygame.sprite.collide_mask(check2, land):
                    self.flag[0] = False
                    self.speed[0] = -self.speed[0]
                    self.delta[0] = self.speed[0]
            check1.kill()
            check2.kill()
        for coord in (0, 1):
            self.delta[coord] += self.speed[coord]
            if not pygame.sprite.collide_mask(self, land):
                self.flag[coord] = True
            if self.delta[coord] >= 1:
                self.pos[coord] += 1
                self.delta[coord] -= 1
            if self.delta[coord] <= -1:
                self.pos[coord] -= 1
                self.delta[coord] += 1
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]


class BlackBall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        arr = [-1, -0.9, -0.8, -0.7, -0.6, -0.5, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        self.speed = [choice(arr), choice(arr)]
        arr1 = [1, 2, 3, 4, 5, width - 15, width - 14, width - 13, width - 12, width - 11]
        arr2 = [1, 2, 3, 4, 5, height - 15, height - 14, height - 13, height - 12, height - 11]
        flag = choice([0, 1])
        if flag:
            self.pos = [choice(arr1), randrange(1, height)]
        else:
            self.pos = [randrange(1, width), choice(arr2)]
        self.delta = [0.0, 0.0]
        self.topleft = (self.pos[0], self.pos[1])
        self.image = pygame.transform.scale(load_image('black-tennis-ball.png', -1), (10, 10))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.flag = [True, True]

    def update(self):
        if pygame.sprite.collide_mask(self, sea) and all(self.flag):
            if self.speed[1] < 0:
                check1 = CheckBall(self.rect.x - 1, self.rect.y - 1)
                check2 = CheckBall(self.rect.x + 1, self.rect.y - 1)
                if pygame.sprite.collide_mask(check1, sea) and pygame.sprite.collide_mask(check2, sea):
                    self.flag[1] = False
                    self.speed[1] = -self.speed[1]
                    self.delta[1] = self.speed[1]
            else:
                check1 = CheckBall(self.rect.x - 1, self.rect.y + 1)
                check2 = CheckBall(self.rect.x + 1, self.rect.y + 1)
                if pygame.sprite.collide_mask(check1, sea) and pygame.sprite.collide_mask(check2, sea):
                    self.flag[1] = False
                    self.speed[1] = -self.speed[1]
                    self.delta[1] = self.speed[1]
            if self.speed[0] < 0:
                check1 = CheckBall(self.rect.x - 1, self.rect.y - 1)
                check2 = CheckBall(self.rect.x - 1, self.rect.y + 1)
                if pygame.sprite.collide_mask(check1, sea) and pygame.sprite.collide_mask(check2, sea):
                    self.flag[0] = False
                    self.speed[0] = -self.speed[0]
                    self.delta[0] = self.speed[0]
            else:
                check1 = CheckBall(self.rect.x + 1, self.rect.y - 1)
                check2 = CheckBall(self.rect.x + 1, self.rect.y + 1)
                if pygame.sprite.collide_mask(check1, sea) and pygame.sprite.collide_mask(check2, sea):
                    self.flag[0] = False
                    self.speed[0] = -self.speed[0]
                    self.delta[0] = self.speed[0]
            check1.kill()
            check2.kill()
        for coord in (0, 1):
            if self.pos[coord] >= size[coord] - 10 or self.pos[coord] <= 0:
                self.flag[coord] = False
                self.speed[coord] = -self.speed[coord]
                self.delta[coord] = self.speed[coord]
            self.delta[coord] += self.speed[coord]
            if not pygame.sprite.collide_mask(self, sea) and (self.delta[coord] >= 1 or self.delta[coord] <= -1):
                self.flag[coord] = True
            if self.delta[coord] >= 1:
                self.pos[coord] += 1
                self.delta[coord] -= 1
            if self.delta[coord] <= -1:
                self.pos[coord] -= 1
                self.delta[coord] += 1
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]


class CheckBall(pygame.sprite.Sprite):
    def __init__(self, *coords):
        super().__init__(all_sprites)
        self.topleft = coords
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.mask = pygame.mask.from_surface(self.image)


class Land(pygame.sprite.Sprite):
    def __init__(self, *coords):
        super().__init__(all_sprites)
        self.coords = [[(20, 20), (width - 20, 20), (width - 20, height - 20), (20, height - 20), (20, 20)]]
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(surf, COLOR, tuple(coords))
        sea.set_image(coords)
        self.image = surf
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = (min(coords))

    def pol1_in_pol2(self, coords1, coords2):
        pol2 = PolygonCheck(coords2)
        for el in coords1:
            cp = CheckPoint(el)
            if not pygame.sprite.collide_mask(cp, pol2):
                cp.kill()
                pol2.kill()
                return False
            cp.kill()
        pol2.kill()
        return True

    def modify(self, start, stop, coords):
        del coords[0]
        start_x, start_y = start
        stop_x, stop_y = stop
        pre_pos1 = None
        pre_pos2 = None
        post_pos1 = None
        post_pos2 = None
        index = None
        for j in range(len(self.coords)):
            for i in range(len(self.coords[j]) - 1):
                x1, y1 = self.coords[j][i]
                x2, y2 = self.coords[j][i + 1]
                if abs(start_x - x1) < 3 and (y1 <= start_y <= y2 or y1 >= start_y >= y2):
                    pre_pos1 = i
                    post_pos1 = i + 1
                    start_x = x1
                if abs(start_y - y1) < 3 and (x1 <= start_x <= x2 or x1 >= start_x >= x2):
                    pre_pos1 = i
                    post_pos1 = i + 1
                    start_y = y1
                if abs(stop_x - x1) < 3 and (y1 <= stop_y <= y2 or y1 >= stop_y >= y2):
                    pre_pos2 = i
                    post_pos2 = i + 1
                    stop_x = x1
                if abs(stop_y - y1) < 3 and (x1 <= stop_x <= x2 or x1 >= stop_x >= x2):
                    pre_pos2 = i
                    post_pos2 = i + 1
                    stop_y = y1
            if pre_pos1 != None and pre_pos2 != None and post_pos1 != None and post_pos2 != None:
                if self.pol1_in_pol2([(start_x, start_y)] + coords + [(stop_x, stop_y)], self.coords[j]):
                    index = j
                    break
        if pre_pos1 == pre_pos2:
            pre_x, pre_y = self.coords[index][pre_pos1]
            if start_x == stop_x and abs(stop_y - pre_y) < abs(start_y - pre_y):
                start_y, stop_y = stop_y, start_y
                coords.reverse()
            if start_y == stop_y and abs(stop_x - pre_x) < abs(start_x - pre_x):
                start_x, stop_x = stop_x, start_x
                coords.reverse()
            polygon1 = PolygonCheck([(start_x, start_y)] + coords + [(stop_x, stop_y)])
            polygon2 = PolygonCheck(self.coords[index][:pre_pos1 + 1] + [(start_x, start_y)] + coords + [(stop_x, stop_y)] +
                                    self.coords[index][post_pos1:])
            count1 = 0
            count2 = 0
            for el in white_ball_sprites:
                if pygame.sprite.collide_mask(el, polygon1):
                    count1 += 1
                if pygame.sprite.collide_mask(el, polygon2):
                    count2 += 1
            if count1 == 0:
                pygame.draw.polygon(self.image, COLOR, tuple([(start_x, start_y)] + coords + [(stop_x, stop_y)]))
                self.mask = pygame.mask.from_surface(self.image)
                self.coords[index] = self.coords[index][:pre_pos1 + 1] + [(start_x, start_y)] + coords + \
                                     [(stop_x, stop_y)] + self.coords[index][post_pos1:]
                sea.set_image([(start_x, start_y)] + coords + [(stop_x, stop_y)])
            elif count2 == 0:
                pygame.draw.polygon(self.image, COLOR, tuple(self.coords[index][:pre_pos1 + 1] + [(start_x, start_y)] +
                                                             coords + [(stop_x, stop_y)] + self.coords[index][post_pos1:]))
                self.mask = pygame.mask.from_surface(self.image)
                sea.set_image(self.coords[index][:pre_pos1 + 1] + [(start_x, start_y)] + coords + [(stop_x, stop_y)] +
                              self.coords[index][post_pos1:])
                self.coords[index] = [(start_x, start_y)] + coords + [(stop_x, stop_y)] + [(start_x, start_y)]
            else:
                pygame.draw.aalines(self.image, COLOR, False, tuple([(start_x, start_y)] + coords + [(stop_x, stop_y)]), 5)
                self.mask = pygame.mask.from_surface(self.image)
                coords1 = coords.copy()
                coords1.reverse()
                pygame.draw.aalines(sea.image, (0, 0, 0, 0), False,
                                    tuple([(start_x, start_y)] + coords + [(stop_x, stop_y)]), 5)
                sea.rect = sea.image.get_rect()
                sea.mask = pygame.mask.from_surface(sea.image)
                self.coords.append(self.coords[index][:pre_pos1 + 1] + [(start_x, start_y)] + coords +
                                   [(stop_x, stop_y)] + self.coords[index][post_pos1:])
                self.coords[index] = [(start_x, start_y)] + coords + [(stop_x, stop_y)] + [(start_x, start_y)]
        else:
            if pre_pos1 > pre_pos2:
                pre_pos1, pre_pos2 = pre_pos2, pre_pos1
                post_pos1, post_pos2 = post_pos2, post_pos1
                start_x, stop_x = stop_x, start_x
                start_y, stop_y = stop_y, start_y
                coords.reverse()
            coords1 = coords.copy()
            coords1.reverse()
            coords_in = [(start_x, start_y)] + self.coords[index][post_pos1:pre_pos2 + 1] + [(stop_x, stop_y)] + \
                        coords1 + [(start_x, start_y)]
            coords_out = self.coords[index][:pre_pos1 + 1] + [(start_x, start_y)] + coords + [(stop_x, stop_y)] + \
                         self.coords[index][post_pos2:]
            coords_mid_draw = [(start_x, start_y)] + coords + [(stop_x, stop_y)]
            polygon1 = PolygonCheck(coords_in)
            polygon2 = PolygonCheck(coords_out)
            count1 = 0
            count2 = 0
            for el in white_ball_sprites:
                if pygame.sprite.collide_mask(el, polygon1):
                    count1 += 1
                if pygame.sprite.collide_mask(el, polygon2):
                    count2 += 1
            if count1 == 0:
                pygame.draw.polygon(self.image, COLOR, tuple(coords_in))
                self.mask = pygame.mask.from_surface(self.image)
                self.coords[index] = coords_out
                sea.set_image(coords_in)
            elif count2 == 0:
                pygame.draw.polygon(self.image, COLOR, tuple(coords_out))
                self.mask = pygame.mask.from_surface(self.image)
                sea.set_image(coords_out)
                self.coords[index] = coords_in
            else:
                pygame.draw.aalines(self.image, COLOR, False, tuple(coords_mid_draw), 5)
                self.mask = pygame.mask.from_surface(self.image)
                pygame.draw.aalines(sea.image, (0, 0, 0, 0), False, tuple(coords_mid_draw), 5)
                sea.rect = sea.image.get_rect()
                sea.mask = pygame.mask.from_surface(sea.image)
                self.coords.append(coords_out)
                self.coords[index] = coords_in
        polygon1.kill()
        polygon2.kill()

    def get_area(self):
        s = 0
        for arr in self.coords:
            s1 = 0
            for i in range(len(arr) - 1):
                x1, y1 = arr[i]
                x2, y2 = arr[i + 1]
                s1 += x1 * y2 - x2 * y1
            s += abs(s1) // 2
        return math.floor((490000 - s) / 490000 * 100)


class PolygonCheck(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__(all_sprites)
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (0, 0, 0, 255), tuple(coords))
        self.image = surf
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()


class Sea(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        surf0 = pygame.Surface((width, height), pygame.SRCALPHA)
        surf0.fill((0, 0, 0, 255))
        self.surface = surf0
        self.image = surf0
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def set_image(self, coords):
        pygame.draw.polygon(self.image, (0, 0, 0, 0), tuple(coords))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)


pygame.init()
size = width, height = 700, 700
screen = pygame.display.set_mode(size)
screen.fill(pygame.Color('black'))
all_sprites = pygame.sprite.Group()
ball_sprites = pygame.sprite.Group()
white_ball_sprites = pygame.sprite.Group()
black_ball_sprites = pygame.sprite.Group()
land_sprites = pygame.sprite.Group()
sea_sprites = pygame.sprite.Group()
player_sprites = pygame.sprite.Group()
sea = Sea()
sea_sprites.add(sea)
for i in range(BALLS):
    ball = WhiteBall()
    ball_sprites.add(ball)
    white_ball_sprites.add(ball)
for i in range(2):
    ball = BlackBall()
    ball_sprites.add(ball)
    black_ball_sprites.add(ball)
land = Land((0, 0), (20, 20), (width - 20, 20), (width - 20, height - 20), (20, height - 20), (20, 20), (0, 0),
            (0, height), (width, height), (width, 0))
land_sprites.add(land)
player = Star()
player_sprites.add(player)
running = True
clock = pygame.time.Clock()
forbidden_speed = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player.speed != [0, 2] and forbidden_speed != [0, 2]:
            forbidden_speed = None
            player.speed = [0, -2]
            player.append_coord(player.get_center_coords())
            player.set_last_coords(player.get_center_coords())
        if keys[pygame.K_DOWN] and player.speed != [0, -2] and forbidden_speed != [0, -2]:
            forbidden_speed = None
            player.speed = [0, 2]
            player.append_coord(player.get_center_coords())
            player.set_last_coords(player.get_center_coords())
        if keys[pygame.K_LEFT] and player.speed != [2, 0] and forbidden_speed != [2, 0]:
            forbidden_speed = None
            player.speed = [-2, 0]
            player.append_coord(player.get_center_coords())
            player.set_last_coords(player.get_center_coords())
        if keys[pygame.K_RIGHT] and player.speed != [-2, 0] and forbidden_speed != [-2, 0]:
            forbidden_speed = None
            player.speed = [2, 0]
            player.append_coord(player.get_center_coords())
            player.set_last_coords(player.get_center_coords())
        if keys[pygame.K_SPACE]:
            if player.in_sea:
                forbidden_speed = player.speed
            player.speed = [0, 0]
    all_sprites.update()
    screen.fill(pygame.Color('black'))
    land_sprites.draw(screen)
    ball_sprites.draw(screen)
    player.draw_polygon()
    player_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
