import pygame
from pygame.locals import *
import sys
import os
import random
from open_1 import StartScreen

pygame.init()
size = width, height = 800, 700
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Catcher(pygame.sprite.Sprite):
    image = load_image('car2.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Catcher.image
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 550

    def update(self, *args):
        if args and (pygame.key.get_pressed()[pygame.K_RIGHT]):
            self.rect = self.rect.move(10, 0)
        if args and (pygame.key.get_pressed()[pygame.K_LEFT]):
            self.rect = self.rect.move(-10, 0)


class Faller(pygame.sprite.Sprite):
    image = load_image('bomb.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Faller.image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(self.rect[2], width - self.rect[2])
        self.y = 0

    def update(self):
        self.rect = self.rect.move(0, 20)

StartScreen('black_fon.jpg') # fon_for_pg1.jpeg
if __name__ == '__main__':
    screen.fill((20, 20, 240))
    screen.fill((0, 255, 0), pygame.Rect(0, 500, width, 200))
    clock = pygame.time.Clock()
    running = True
    timer = pygame.USEREVENT + 1
    gamer_spr = pygame.sprite.Group()
    Catcher(gamer_spr)
    faller_spr = pygame.sprite.Group()
    pygame.time.set_timer(timer, 100)
    Faller(faller_spr)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                gamer_spr.update(event)
            if event.type == timer:
                Faller(faller_spr)
                faller_spr.draw(screen)
                faller_spr.update()

        pygame.display.flip()
        faller_spr.draw(screen)
        faller_spr.update()
        screen.fill((0, 0, 255))
        screen.fill((0, 255, 0), pygame.Rect(0, 500, width, 200))
        gamer_spr.draw(screen)
        clock.tick(30)
    pygame.quit()