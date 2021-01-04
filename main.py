import os
import random
import sys
import warnings

import pygame

from sklearn import preprocessing

warnings.filterwarnings("ignore")

G_Player_position = [0, 0]
G_Mouse_position = [0, 0]

pygame.init()
pygame.display.set_caption('Моя игра')
size = width, height = 1600, 900
screen = pygame.display.set_mode((size), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)

clock = pygame.time.Clock()

current_time = 0
flash_button_press_time = 0

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
mobs = pygame.sprite.Group()
player_group = pygame.sprite.Group()
mobs_warning = pygame.sprite.Group()

fps = 60
score = 0

running = True
mobs_spawn = True

spawn_stumps_timer = 0


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


def restart():
    global score
    score = score
    player.rect.x = width // 2
    player.rect.y = height // 3
    for mob in mobs:
        mob.kill()
    for bullet in bullets:
        bullet.kill()
    for enemy_bullet in enemy_bullets:
        enemy_bullet.kill()


class UI(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.screen = screen

    def draw(self, screen):
        font = pygame.font.Font(None, 50)
        text = font.render(str(score), True, (100, 255, 100))
        text_x = width - text.get_width()
        text_y = 10
        screen.blit(text, (text_x, text_y))
        self.spells()

    def spells(self):
        flash_img = load_image('flash.png').convert(24)
        if player.flash_ready:
            flash_img.set_alpha(100)
        else:
            flash_img.set_alpha(0)

        self.screen.blit(flash_img, (width // 2 - 80, height - 60))


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image('player/лицом_1.png')
        self.rect = self.image.get_rect()
        self.rect.x = width / 2
        self.rect.y = height / 3
        self.mask = pygame.mask.from_surface(self.image)

        self.MOVE_SPEED = 3
        self.flash_button_press_time = 0
        self.attack_cooldown_time = 0

        self.direction = 'right'

        self.width = self.rect.size[0]
        self.height = self.rect.size[1]

        self.move_right = False
        self.move_left = False
        self.move_up = False
        self.move_down = False

        self.is_alive = True
        self.flash_ready = True
        self.flash = False
        self.player_shoots = False

    def update(self):
        if self.player_shoots:
            self.attack_cooldown_time += 1
            self.shoot()
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

        if self.flash and self.flash_ready:
            self.flash_button_press_time = pygame.time.get_ticks()
            arr = preprocessing.normalize([[G_Mouse_position[0] - self.rect.x, G_Mouse_position[1] - self.rect.y]])
            self.rect.x += arr[0][0] * 300
            self.rect.y += arr[0][1] * 300
            self.flash = False
            self.flash_ready = False
        else:
            self.flash = False

        if self.rect.x > width:
            self.rect.x -= self.MOVE_SPEED
        elif self.rect.x < 0:
            self.rect.x += self.MOVE_SPEED
        elif self.rect.y > height:
            self.rect.y -= self.MOVE_SPEED
        elif self.rect.y < 0:
            self.rect.y += self.MOVE_SPEED

    def shoot(self):
        if self.attack_cooldown_time == 10:
            bullet = Bullet(G_Mouse_position, self.rect)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.attack_cooldown_time = 0

    def animation_player(self):
        if G_Player_position[0] - G_Mouse_position[0] > 100 and G_Player_position[1] - G_Mouse_position[1] < 0:
            self.direction = 'left'
        elif G_Player_position[0] - G_Mouse_position[0] < -100 and G_Player_position[1] - G_Mouse_position[1] < 0:
            self.direction = 'right'
        elif G_Player_position[1] - G_Mouse_position[1] > 0:
            self.direction = 'up'
        elif G_Player_position[1] - G_Mouse_position[1] < 0:
            self.direction = 'down'

        if self.direction == 'down':
            self.image = load_image('player/лицом_1.png')
        elif self.direction == 'up':
            self.image = load_image('player/спиной_1.png')
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
        if score < 100:
            bullet = EnemyBullet(self.rect, G_Player_position)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
        else:
            bullet = EnemyBulletExploding(self.rect, G_Player_position)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def update(self, *args):
        self.cooldown_attack_timer += 1

        if self.cooldown_attack_timer > 150:
            self.shoot()
            self.cooldown_attack_timer = 0

        arr = preprocessing.normalize([[G_Player_position[0] - self.rect.x, G_Player_position[1] - self.rect.y]])
        self.rect.x += arr[0][0] * self.SPEED + 0.4
        self.rect.y += arr[0][1] * self.SPEED + 0.4

        self.hit()

    def hit(self):
        hits = pygame.sprite.spritecollide(player, mobs, False)
        if hits:
            restart()


class Slime(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image('slime/slime_up_run1.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([-50, -10, width // 2, width // 2 + 100, width // 2 - 100, width // 3,  width + 50, width + 80])
        self.rect.y = random.choice([-50, height + 50])

        self.mask = pygame.mask.from_surface(self.image)

        self.SPEED = 2

    def update(self, *args):
        arr = preprocessing.normalize([[G_Player_position[0] - self.rect.x, G_Player_position[1] - self.rect.y]])
        self.rect.x += arr[0][0] * self.SPEED
        self.rect.y += arr[0][1] * self.SPEED
        self.hit()

    def hit(self):
        hits = pygame.sprite.spritecollide(player, mobs, False)
        if hits:
            restart()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, enemy_pos, player_pos):
        super().__init__(all_sprites)
        self.image = load_image('bomb.png')
        self.image = pygame.transform.scale(self.image, (20, 20))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = enemy_pos[0]
        self.rect.y = enemy_pos[1]

        self.SPEED = 10
        self.arr = preprocessing.normalize([[player_pos[0] - self.rect.x, (player_pos[1] - self.rect.y) + 10]])

    def update(self):
        self.rect.x += self.arr[0][0] * self.SPEED
        self.rect.y += self.arr[0][1] * self.SPEED

        if self.rect.x >= width or self.rect.x < 0:
            self.kill()
        elif self.rect.y >= height or self.rect.y < 0:
            self.kill()

        self.hit()

    def hit(self):
        hits = pygame.sprite.spritecollide(player, enemy_bullets, False)
        if hits:
            restart()


class EnemyBulletExploding(EnemyBullet):
    def __init__(self, enemy_pos, player_pos):
        super().__init__(enemy_pos, player_pos)
        self.player_pos = player_pos
        self.timer = 0
        self.SPEED = 5

    def update(self):
        self.timer += 1
        self.rect.x += self.arr[0][0] * self.SPEED
        self.rect.y += self.arr[0][1] * self.SPEED

        if self.rect.x >= width or self.rect.x < 0:
            self.kill()
        elif self.rect.y >= height or self.rect.y < 0:
            self.kill()
        if self.timer == 100:
            enemy_bullets.add(EnemyBullet(self.rect, (self.rect.x + 90, self.rect.y - 90)))
            enemy_bullets.add(EnemyBullet(self.rect, (self.rect.x - 90, self.rect.y + 90)))
            enemy_bullets.add(EnemyBullet(self.rect, (self.rect.x - 90, self.rect.y - 90)))
            enemy_bullets.add(EnemyBullet(self.rect, (self.rect.x + 90, self.rect.y + 90)))
            self.kill()

        self.hit()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, mouse_pos, player_pos):
        super().__init__(all_sprites)
        self.image = load_image('boom.png')
        self.image = pygame.transform.scale(self.image, (10, 10))
        self.size_image_width = self.image.get_width()
        self.size_image_height = self.image.get_height()

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()

        if player.direction == 'down':
            self.rect.x = player_pos[0] + 4
            self.rect.y = player_pos[1] + player.height // 2
        elif player.direction == 'up':
            self.rect.x = player_pos[0] + player.width
            self.rect.y = player_pos[1] + 15
        elif player.direction == 'left':
            self.rect.x = player_pos[0]
            self.rect.y = player_pos[1] + player.height // 2
        elif player.direction == 'right':
            self.rect.x = player_pos[0] + player.width
            self.rect.y = player_pos[1] + player.height // 2

        self.player_pos = player_pos
        self.mouse_pos = []
        self.mouse_pos.append(mouse_pos[0] - self.image.get_width() // 2)
        self.mouse_pos.append(mouse_pos[1] - self.image.get_height() // 2)

        self.SPEED = 10
        self.arr = preprocessing.normalize([[self.mouse_pos[0] + self.SPEED - self.rect.x, self.mouse_pos[1] + self.SPEED - self.rect.y]])

    def update(self):
        global score
        self.rect.x += (self.arr[0][0] * self.SPEED)
        self.rect.y += (self.arr[0][1] * self.SPEED)

        if self.rect.x >= width or self.rect.x < 0:
            self.kill()
        elif self.rect.y >= height or self.rect.y < 0:
            self.kill()

        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            hit.kill()
            score += 1

        hits = pygame.sprite.groupcollide(enemy_bullets, bullets, True, True)
        for hit in hits:
            hit.kill()


UI = UI()
player = Player()
player_group.add(player)

while running:
    spawn_stumps_timer += 1

    if mobs_spawn:
        if spawn_stumps_timer > 150:
            for _ in range(3):
                mobs.add(Slime())
            if len(mobs) < 8:
                mobs.add(Shooter())
            spawn_stumps_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            G_Mouse_position = event.pos

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.player_shoots = True
                player.attack_cooldown_time = 10
                player.shoot()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                player.player_shoots = False

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
                size = width, height = 1600, 900
                screen = pygame.display.set_mode(size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
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

    current_time = pygame.time.get_ticks()

    screen.fill((0, 0, 0))
    all_sprites.update()
    all_sprites.draw(screen)
    UI.draw(screen)

    clock.tick(fps)
    pygame.display.flip()
    if current_time - player.flash_button_press_time > 3000:
        player.flash_ready = True
pygame.quit()
