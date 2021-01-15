import os
import random
import sys
import warnings
import time

import pygame

from sklearn import preprocessing

warnings.filterwarnings("ignore")

G_Player_position = [0, 0]
G_Mouse_position = [0, 0]

pygame.init()
pygame.display.set_caption('Моя игра')
size = width, height = 1080, 720
screen = pygame.display.set_mode(size,  pygame.FULLSCREEN)
screen_rect = screen.get_rect()

clock = pygame.time.Clock()

current_time = 0
flash_button_press_time = 0

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
mobs = pygame.sprite.Group()
player_group = pygame.sprite.Group()

fps = 60
score = 0

GRAVITY = 1

running = True
mobs_spawn = True
state = 'menu'

spawn_stumps_timer = 0

attack_player_sound = pygame.mixer.Sound('data/sounds/shot-of-the-player.wav')
attack_player_sound.set_volume(0.5)
slime_splat_sound = pygame.mixer.Sound('data/sounds/slime-splat.wav')
slime_splat_sound.set_volume(0.5)
shooter_heath_sound = pygame.mixer.Sound('data/sounds/shooter_death.wav')
shooter_shoot_sound = pygame.mixer.Sound('data/sounds/shooter_shoot.wav')
boom_bomb_sound = pygame.mixer.Sound('data/sounds/shot-of-the-player2.wav')

#pygame.mixer.music.load('data/sounds/Music_3.mp3')
#pygame.mixer.music.play(-1)


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


def hit():
    global state
    hits = pygame.sprite.spritecollide(player, mobs, False)
    if hits:
        state = 'death'


def create_particles(position, name_img):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    numbers_y = range(-2, 3)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers_y), name_img)


def restart():
    global score
    score = 95
    player.rect.x = width // 2
    player.rect.y = height // 3
    player.flash_ready = True
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
        text = font.render(str(score), True, (255, 255, 100))
        text_x = width - text.get_width()
        text_y = 10
        screen.blit(text, (text_x, text_y))
        self.spells()

    def spells(self):
        flash_img = load_image('flash.png')
        if player.flash_ready:
            screen.blit(flash_img, (width // 2 - 80, height - 60))


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
        if current_time - self.flash_button_press_time > 10000:
            self.flash_ready = True
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
            pygame.mixer.Sound.stop(attack_player_sound)
            pygame.mixer.Sound.play(attack_player_sound)
            bullet = Bullet(G_Mouse_position, self.rect)
            all_sprites.add(bullet)
            bullets.add(bullet)
            self.attack_cooldown_time = 0

    def animation_player(self):
        if G_Player_position[0] - G_Mouse_position[0] > 100 and G_Player_position[1] - G_Mouse_position[1] < 100:
            self.direction = 'left'
        elif G_Player_position[0] - G_Mouse_position[0] < -100 and G_Player_position[1] - G_Mouse_position[1] < 100:
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
        self.image = load_image('shooter/shooter_run_down1.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([-50, width // 2, width + 50])
        self.rect.y = random.choice([-50, height + 50])

        self.bullet_rect = [self.rect.x, self.rect.y]

        self.animation_run_up = ['shooter_run_up1.png', 'shooter_run_up2.png', 'shooter_run_up3.png', 'shooter_run_up4.png', 'shooter_run_up5.png']
        self.animation_run_down = ['shooter_run_down1.png', 'shooter_run_down2.png', 'shooter_run_down3.png', 'shooter_run_down4.png', 'shooter_run_down5.png']
        self.animation_run_left = ['shooter_run_left1.png', 'shooter_run_left2.png', 'shooter_run_left3.png', 'shooter_run_left4.png', 'shooter_run_left5.png']
        self.animation_run_right = ['shooter_run_right1.png', 'shooter_run_right2.png', 'shooter_run_right3.png', 'shooter_run_right4.png', 'shooter_run_right5.png']

        self.direction = None

        self.mask = pygame.mask.from_surface(self.image)

        self.SPEED = 1.2

        self.cooldown_attack_timer = 0
        self.animation_timer = 0
        self.sprite_number = 0

    def shoot(self):
        pygame.mixer.Sound.play(shooter_shoot_sound)
        if score < 100:
            bullet = EnemyBullet(self.bullet_rect, G_Player_position)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
        else:
            bullet = EnemyBulletExploding(self.bullet_rect, G_Player_position)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def animation(self):
        if self.direction == 'down':
            self.image = load_image('shooter/' + self.animation_run_down[self.sprite_number])
        elif self.direction == 'up':
            self.image = load_image('shooter/' + self.animation_run_up[self.sprite_number])
        elif self.direction == 'right':
            self.image = load_image('shooter/' + self.animation_run_right[self.sprite_number])
        elif self.direction == 'left':
            self.image = load_image('shooter/' + self.animation_run_left[self.sprite_number])

        if self.sprite_number == len(self.animation_run_up) - 1:
            self.sprite_number = 0
        else:
            self.sprite_number += 1

    def update(self, *args):
        self.animation_timer += 1
        self.cooldown_attack_timer += 1

        if self.cooldown_attack_timer > 150:
            self.shoot()
            self.cooldown_attack_timer = 0

        arr = preprocessing.normalize([[G_Player_position[0] - self.rect.x, G_Player_position[1] - self.rect.y]])
        self.rect.x += arr[0][0] * self.SPEED
        self.rect.y += arr[0][1] * self.SPEED

        if arr[0][1] > arr[0][0] < 0:
            self.direction = 'left'
            self.bullet_rect[0] = self.rect.x - 15
            self.bullet_rect[1] = self.rect.y + 15
        elif arr[0][1] < arr[0][0] > 0:
            self.direction = 'right'
            self.bullet_rect[0] = self.rect.x + 45
            self.bullet_rect[1] = self.rect.y + 15
        elif arr[0][0] < arr[0][1] > 0:
            self.direction = 'down'
            self.bullet_rect[0] = self.rect.x + 15
            self.bullet_rect[1] = self.rect.y + 30
        elif arr[0][0] > arr[0][1] < 0:
            self.direction = 'up'
            self.bullet_rect[0] = self.rect.x + 20
            self.bullet_rect[1] = self.rect.y - 4

        if self.animation_timer > 8:
            self.animation()
            self.animation_timer = 0

        hit()


class Slime(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image('slime/slime_up_run1.png')
        self.animation_run_up = ['slime_up_run1.png', 'slime_up_run2.png', 'slime_up_run3.png', 'slime_up_run4.png',
                                 'slime_up_run5.png']
        self.animation_run_down = ['slime_down_run1.png', 'slime_down_run2.png', 'slime_down_run3.png',
                                   'slime_down_run4.png', 'slime_down_run5.png']
        self.animation_run_left = ['slime_left_run1.png', 'slime_left_run2.png', 'slime_left_run3.png',
                                   'slime_left_run4.png', 'slime_left_run5.png']
        self.animation_run_right = ['slime_right_run1.png', 'slime_right_run2.png', 'slime_right_run3.png',
                                    'slime_right_run4.png', 'slime_right_run5.png']
        self.rect = self.image.get_rect()
        self.rect.x = random.choice(
            [-50, -10, width // 2, width // 2 + 100, width // 2 - 100, width // 3, width + 50, width + 80])
        self.rect.y = random.choice([-50, height + 50])

        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 'down'

        self.SPEED = 2
        self.sprite_number = 0

        self.animation_timer = 0

    def animation(self):
        if self.direction == 'down':
            self.image = load_image('slime/' + self.animation_run_down[self.sprite_number])
        elif self.direction == 'up':
            self.image = load_image('slime/' + self.animation_run_up[self.sprite_number])
        elif self.direction == 'right':
            self.image = load_image('slime/' + self.animation_run_right[self.sprite_number])
        elif self.direction == 'left':
            self.image = load_image('slime/' + self.animation_run_left[self.sprite_number])

        if self.sprite_number == len(self.animation_run_up) - 1:
            self.sprite_number = 0
        else:
            self.sprite_number += 1

    def update(self, *args):
        self.animation_timer += 1
        arr = preprocessing.normalize([[G_Player_position[0] - self.rect.x, G_Player_position[1] - self.rect.y]])
        if arr[0][0] < 0 and arr[0][1] < 0:
            self.direction = 'left'
        elif arr[0][0] > 0 and arr[0][1] > 0:
            self.direction = 'right'
        elif arr[0][1] > 0 and arr[0][0] < 0:
            self.direction = 'down'
        elif arr[0][1] < 0 and arr[0][0] > 0:
            self.direction = 'up'

        if self.sprite_number != 4:
            self.rect.x += arr[0][0] * self.SPEED
            self.rect.y += arr[0][1] * self.SPEED

        if self.animation_timer > 8:
            self.animation()
            self.animation_timer = 0

        hit()


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
        global state
        hits = pygame.sprite.spritecollide(player, enemy_bullets, False)
        if hits:
            state = 'death'


class EnemyBulletExploding(EnemyBullet):
    def __init__(self, enemy_pos, player_pos):
        super().__init__(enemy_pos, player_pos)
        self.player_pos = player_pos
        self.image = pygame.transform.scale(load_image('shooter/death_particles.png'), (30, 30))
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
            pygame.mixer.Sound.play(boom_bomb_sound)
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
        self.arr = preprocessing.normalize(
            [[self.mouse_pos[0] + self.SPEED - self.rect.x, self.mouse_pos[1] + self.SPEED - self.rect.y]])

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
            if 'Shooter' in str(type(hit)):
                pygame.mixer.Sound.play(shooter_heath_sound)
                create_particles([hit.rect.x, hit.rect.y], 'shooter/death_particles.png')
            elif 'Slime' in str(type(hit)):
                pygame.mixer.Sound.play(slime_splat_sound)
                create_particles([hit.rect.x, hit.rect.y], 'slime/death_particles.png')
            hit.kill()
            score += 1


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy, name_img):
        super().__init__(all_sprites)
        self.fire = [load_image(name_img)]
        for scale in (5, 10, 20):
            self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = [pos[0], pos[1] - 10]

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY / 2

        self.kill_timer = 0

    def update(self):
        self.kill_timer += 1
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        if self.kill_timer <= 20:
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if self.kill_timer >= 40:
            self.kill()


UI = UI()
player = Player()
player_group.add(player)

back_ground = load_image('back_ground.png')
back_ground_rect = back_ground.get_rect()

play_button = load_image('buttons/play.png')
play_set_button = load_image('buttons/play_set.png')
records_button = load_image('buttons/records.png')
records_set_button = load_image('buttons/records_set.png')

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            G_Mouse_position = event.pos

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.player_shoots = True
                player.attack_cooldown_time = 10
                if state == 'running':
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
                state = 'menu'
            elif event.key == pygame.K_f:
                if state == 'running':
                    state = 'pause'
                    #pygame.mixer.music.stop()
                elif state == 'pause':
                    state = 'running'
                    #pygame.mixer.music.play(-1)
            elif event.key == pygame.K_1:
                pygame.display.quit()
                size = width, height = (1080, 720)
                screen = pygame.display.set_mode(size)
            elif event.key == pygame.K_2:
                pygame.display.quit()
                size = width, height = 1080, 720
                screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
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

    if state == 'running':
        spawn_stumps_timer += 1
        screen.blit(back_ground, (0, 0))
        if mobs_spawn:
            if spawn_stumps_timer > 100:
                for _ in range(1):
                    mobs.add(Slime())
                if len(mobs) < 8:
                    mobs.add(Shooter())
                spawn_stumps_timer = 0

        current_time = pygame.time.get_ticks()
        all_sprites.update()
        all_sprites.draw(screen)
        UI.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
    elif state == 'death':
        screen.fill((0, 0, 0))
        screen.blit(load_image('game over.png'), (-20, 0))
        screen.blit(load_image('score.png'), (320, 450))
        font = pygame.font.Font(None, 50)
        text = font.render(str(score), True, (255, 255, 100))
        screen.blit(text, (600, 445))
        text = font.render('Нажмите кнопку ESCAPE', True, (255, 100, 100))
        screen.blit(text, (width / 4 + 50, 545))
        pygame.display.flip()
    elif state == 'menu':
        screen.fill((200, 200, 255))
        if width / 2 - 128 < G_Mouse_position[0] < width / 2 - 128 + 256 and 200 < G_Mouse_position[1] < 264:
            screen.blit(play_set_button, (width / 2 - 128, 200))
        else:
            screen.blit(play_button, (width / 2 - 128, 200))

        if width / 2 - 128 < G_Mouse_position[0] < width / 2 - 128 + 256 and 300 < G_Mouse_position[1] < 364:
            screen.blit(load_image('buttons/exit_set.png'), (width / 2 - 128, 300))
        else:
            screen.blit(load_image('buttons/exit.png'), (width / 2 - 128, 300))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if width / 3 < G_Mouse_position[0] < width / 3 + 256 and 200 < G_Mouse_position[1] < 264:
                        state = 'running'
                        restart()
                    if width / 2 - 128 < G_Mouse_position[0] < width / 2 - 128 + 256 and 300 < G_Mouse_position[1] < 364:
                        running = False
        pygame.display.flip()
    elif state == 'pause':
        screen.blit(load_image('pause.png'), (width / 2.5, height / 3))
        pygame.display.flip()
pygame.quit()
