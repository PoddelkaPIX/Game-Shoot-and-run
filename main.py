import os
import random
import sys

import pygame

import warnings
warnings.filterwarnings("ignore")

from sklearn import preprocessing

G_Player_position = [0, 0]
G_Mouse_position = [0, 0]

pygame.init()
pygame.display.set_caption('Моя игра')
size = width, height = 1600, 900
screen = pygame.display.set_mode((size), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
mobs = pygame.sprite.Group()
player_group = pygame.sprite.Group()
mobs_warning = pygame.sprite.Group()

fps = 60
score = 0

running = True

player_shot = False

spawn_stumps_timer = 0

menu_buttons = ['Старт', 'Таблица рекордов']


def load_image(name, colorkey=None):
        fullname = '/'.join(['data', name])
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
        return image


class UI(pygame.sprite.Sprite):
    def draw(self, screen):
        font = pygame.font.Font(None, 50)
        text = font.render(str(score), True, (100, 255, 100))
        text_x = width - (text.get_height() + 15)
        text_y = 10
        screen.blit(text, (text_x, text_y))


class Mob_warning(pygame.sprite.Sprite):
    def __init__(self, enemy_pos):
        super().__init__(all_sprites)
        self.image = load_image('arrow.png')
        self.rect = self.image.get_rect()
        self.enemy_pos = enemy_pos

    def update(self):
        if self.enemy_pos[0] > width:
            self.rect.x = width - 100
            self.rect.y = self.enemy_pos[1]

        if self.enemy_pos[0] < 0:
            self.rect.x = width
            self.rect.y = self.enemy_pos[1]


class Button(pygame.sprite.Sprite):
    def __init__(self, text, x, y, screen):
        super().__init__(all_sprites)
        self.screen = screen
        self.text = str(text)
        self.image = load_image('player/лицом_1.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image('player/лицом_1.png')
        self.rect = self.image.get_rect()
        self.rect.x = width / 2
        self.rect.y = height / 3

        self.MOVE_SPEED = 3

        self.direction = 'right'

        self.width = self.rect.size[0]
        self.height = self.rect.size[1]

        self.move_right = False
        self.move_left = False
        self.move_up = False
        self.move_down = False

        self.is_alive = True
        self.flash = False

    def update(self):
        self.move()
        self.animation_player()

    def move(self):
        global G_Player_position
        G_Player_position = self.rect
        if self.move_left:
            self.rect.x -= self.MOVE_SPEED
        elif self.move_right:
            self.rect.x += self.MOVE_SPEED

        if self.move_up:
            self.rect.y -= self.MOVE_SPEED
        elif self.move_down:
            self.rect.y += self.MOVE_SPEED

        if self.flash:
            self.arr = preprocessing.normalize([[G_Mouse_position[0] - self.rect.x, G_Mouse_position[1] - self.rect.y]])
            self.rect.x += self.arr[0][0] * 200
            self.rect.y += self.arr[0][1] * 200
            self.flash = False

        if self.rect.x > width:
            self.rect.x -= self.MOVE_SPEED
        elif self.rect.x < 0:
            self.rect.x += self.MOVE_SPEED
        elif self.rect.y > height:
            self.rect.y -= self.MOVE_SPEED
        elif self.rect.y < 0:
            self.rect.y += self.MOVE_SPEED


    def shoot(self, mouse_pos):
        bullet = Bullet(mouse_pos, self.rect)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def animation_player(self):
        if G_Player_position[1] - G_Mouse_position[1] == 0:
            self.direction = 'up'
        elif G_Player_position[1] - G_Mouse_position[1] < 0 and (G_Player_position[0] - G_Mouse_position[0]) < 200:
            self.direction = 'down'

        if G_Player_position[0] - G_Mouse_position[0] < 200 and G_Player_position[1] - G_Mouse_position[1] < 300:
            self.direction = 'right'
        elif G_Player_position[0] - G_Mouse_position[0] > 200 and G_Player_position[1] - G_Mouse_position[1] > -300:
            self.direction = 'left'

        if self.direction == 'down':
            self.image = load_image('player/лицом_1.png')
        elif self.direction == 'right':
            self.image = load_image('player/правой_рукой_1.png')
        elif self.direction == 'left':
            self.image = load_image('player/левой_рукой_1.png')


class Shooter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image('boom.png')
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([-50, width // 2,  width + 50])
        self.rect.y = random.choice([-50, height + 50])

        self.mask = pygame.mask.from_surface(self.image)

        self.SPEED = 1

        self.cooldown_attack_timer = 0

    def shoot(self):
        bullet = EnemyBullet(self.rect, G_Player_position)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)

    def update(self, *args):
        self.cooldown_attack_timer += 1

        if self.cooldown_attack_timer > 150:
            self.shoot()
            self.cooldown_attack_timer = 0

        self.arr = preprocessing.normalize([[G_Player_position[0] - self.rect.x, G_Player_position[1] - self.rect.y]])
        self.rect.x += self.arr[0][0] * self.SPEED + 0.4
        self.rect.y += self.arr[0][1] * self.SPEED + 0.4

        self.hit()
        self.visible()

    def restart(self):
        self.rect.x = width / 2
        self.rect.y = height / 3
        for mob in mobs:
            mob.kill()
        for bullet in bullets:
            bullet.kill()
        for enemy_bullet in enemy_bullets:
            enemy_bullet.kill()

    def hit(self):
        hits = pygame.sprite.spritecollide(player, mobs, False)
        if hits:
            self.restart()

    def visible(self):
        if self.rect.x > width:
            mobs_warning.add(Mob_warning(self.rect))
        elif self.rect.x < 0:
            mobs_warning.add(Mob_warning(self.rect))

        else:
            for mob in mobs_warning:
                mob.kill()


class Stump(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image('stump/KRYSTAL_head_bite1.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([-50, -10, width // 2, width // 2 + 100, width // 2 - 100, width // 3,  width + 50, width + 80])
        self.rect.y = random.choice([-50, height + 50])

        self.mask = pygame.mask.from_surface(self.image)

        self.SPEED = 2

    def update(self, *args):
        self.arr = preprocessing.normalize([[G_Player_position[0] - self.rect.x, G_Player_position[1] - self.rect.y]])
        self.rect.x += self.arr[0][0] * self.SPEED
        self.rect.y += self.arr[0][1] * self.SPEED
        self.hit()

    def restart(self):
        self.rect.x = width / 2
        self.rect.y = height / 3
        for mob in mobs:
            mob.kill()
        for bullet in bullets:
            bullet.kill()
        for enemy_bullet in enemy_bullets:
            enemy_bullet.kill()

    def hit(self):
        hits = pygame.sprite.spritecollide(player, mobs, False)
        if hits:
            self.restart()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, enemy_pos, player_pos):
        super().__init__(all_sprites)
        self.image = load_image('bomb.png')
        self.image = pygame.transform.scale(self.image, (20, 20))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = enemy_pos[0]
        self.rect.y = enemy_pos[1]

        self.player_pos = player_pos

        self.SPEED = 5
        self.arr = preprocessing.normalize([[G_Player_position[0] - self.rect.x, G_Player_position[1] - self.rect.y]])

    def update(self):
        self.rect.x += self.arr[0][0] * self.SPEED
        self.rect.y += self.arr[0][1] * self.SPEED

        if self.rect.x >= width or self.rect.x < 0:
            self.kill()
        elif self.rect.y >= height or self.rect.y < 0:
            self.kill()

        self.hit()

    def restart(self):
        self.rect.x = width / 2
        self.rect.y = height / 3
        for mob in mobs:
            mob.kill()
        for bullet in bullets:
            bullet.kill()
        for enemy_bullet in enemy_bullets:
            enemy_bullet.kill()

    def hit(self):
        hits = pygame.sprite.spritecollide(player, enemy_bullets, False)
        if hits:
            self.restart()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, mouse_pos, player_pos):
        super().__init__(all_sprites)
        self.image = load_image('boom.png')
        self.image = pygame.transform.scale(self.image, (10, 10))
        self.size_image_width = self.image.get_width()
        self.size_image_height = self.image.get_height()

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = player_pos[0]
        self.rect.y = player_pos[1]

        self.player_pos = player_pos
        self.mouse_pos = []
        self.mouse_pos.append(mouse_pos[0] - self.image.get_width() // 2)
        self.mouse_pos.append(mouse_pos[1] - self.image.get_height() // 2)

        self.SPEED = 10
        self.arr = preprocessing.normalize([[self.mouse_pos[0] - self.player_pos[0], self.mouse_pos[1] - self.player_pos[1]]])

    def update(self):
        global score
        self.rect.x += self.arr[0][0] * self.SPEED
        self.rect.y += self.arr[0][1] * self.SPEED

        if self.rect.x >= width or self.rect.x < 0:
            self.kill()
        elif self.rect.y >= height or self.rect.y < 0:
            self.kill()

        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            hit.kill()
            score += 1


UI = UI()
player = Player()
player_group.add(player)
button = Button(menu_buttons[0], 10, 10, screen)

while running:
    spawn_stumps_timer += 1

    if spawn_stumps_timer > 150:
        for _ in range(3):
            mobs.add(Stump())
        if len(mobs) < 8:
            mobs.add(Shooter())
        spawn_stumps_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            G_Mouse_position = event.pos

        if event.type == pygame.MOUSEBUTTONDOWN:
            if player.is_alive:
                player.shoot(event.pos)
                G_Mouse_position = event.pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                player.move_left = True
            elif event.key == pygame.K_d:
                player.move_right = True
            elif event.key == pygame.K_w:
                player.move_up = True
            elif event.key == pygame.K_s:
                player.move_down = True
            elif event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_1:
                pygame.display.quit()
                size = width, height = (1080, 720)
                screen = pygame.display.set_mode(size)
            elif event.key == pygame.K_2:
                pygame.display.quit()
                size = width, height = 1520, 880
                screen = pygame.display.set_mode((size), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                player.move_left = False
            elif event.key == pygame.K_d:
                player.move_right = False
            elif event.key == pygame.K_w:
                player.move_up = False
            elif event.key == pygame.K_s:
                player.move_down = False
            elif event.key == pygame.K_SPACE:
                player.flash = True

    screen.fill((0, 0, 0))
    all_sprites.update()
    all_sprites.draw(screen)
    UI.draw(screen)

    clock.tick(fps)
    pygame.display.flip()
pygame.quit()


