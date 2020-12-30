import os
import sys

import pygame
import random

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Герой двигается!')
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)

    def load_image(name, colorkey=None):
        fullname = '/'.join(['data', name])
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        return image

    running = True
    fps = 60
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()

    class Landing(pygame.sprite.Sprite):
        image = load_image("landing.png")

        def __init__(self, pos):
            super().__init__(all_sprites)
            self.image = Landing.image
            self.image = pygame.transform.scale(self.image, (30, 30))
            self.rect = self.image.get_rect()
            self.width = self.rect.size[0]
            # вычисляем маску для эффективного сравнения
            self.mask = pygame.mask.from_surface(self.image)
            self.rect.x = pos[0] - self.width / 2
            self.rect.y = pos[1]

        def update(self):
            if not pygame.sprite.collide_mask(self, mountain):
                self.rect = self.rect.move(0, 2)

    class Mountain(pygame.sprite.Sprite):
        image = load_image("mountain.png")

        def __init__(self):
            super().__init__(all_sprites)
            self.image = Mountain.image
            self.image = pygame.transform.scale(self.image, (600, 200))
            self.rect = self.image.get_rect()
            # вычисляем маску для эффективного сравнения
            self.mask = pygame.mask.from_surface(self.image)
            # располагаем горы внизу
            self.rect.bottom = height

    mountain = Mountain()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                Landing(event.pos)
        screen.fill((255, 255, 255))
        all_sprites.update()
        all_sprites.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()


