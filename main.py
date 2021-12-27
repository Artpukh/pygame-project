import pygame
from pygame.locals import *
import sys
import os
import random

all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
pygame.init()
size = width, height = 800, 700
screen = pygame.display.set_mode(size)
count = 0


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Grass(pygame.sprite.Sprite):
    image = load_image("grass1.png", color_key=None)

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Grass.image
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        # располагаем горы внизу
        self.rect.bottom = height


class Catcher(pygame.sprite.Sprite):
    image = load_image('car2.png', color_key=None)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Catcher.image
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 550

    def update(self, *args):
        if pygame.sprite.spritecollide(self, faller_spr, True):
            global count
            count += 1
        if not pygame.sprite.spritecollideany(self, vertical_borders) and \
           not pygame.sprite.spritecollideany(self, horizontal_borders):
            if args and (pygame.key.get_pressed()[pygame.K_RIGHT]):
                self.rect = self.rect.move(5, 0)
            if args and (pygame.key.get_pressed()[pygame.K_LEFT]):
                self.rect = self.rect.move(-5, 0)
            if args and (pygame.key.get_pressed()[pygame.K_UP]):
                self.rect = self.rect.move(0, -5)
            if args and (pygame.key.get_pressed()[pygame.K_DOWN]):
                self.rect = self.rect.move(0, 5)
        else:
            self.rect.x = 300
            self.rect.y = 550


class Faller(pygame.sprite.Sprite):
    image = load_image('bomb.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Faller.image
        self.rect = self.image.get_rect()
        rand_pos = random.randint(1, 4)
        if not pygame.sprite.spritecollideany(self, vertical_borders) and\
           not pygame.sprite.spritecollideany(self, horizontal_borders):
            # Бомба появляется в одном из 4 мест
            if rand_pos == 1:
                self.rect.x = 80
                self.rect.y = 130
            elif rand_pos == 2:
                self.rect.x = 80
                self.rect.y = 250
            elif rand_pos == 3:
                self.rect.x = 720
                self.rect.y = 130
            elif rand_pos == 4:
                self.rect.x = 720
                self.rect.y = 250
        else:
            pass

    def update(self):
        # if not pygame.sprite.collide_mask(self, grass):
        self.rect = self.rect.move(0, 2)


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)

        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


def draw(sc):
    global count
    font = pygame.font.Font(None, 50)
    text = font.render(f"Счёт: {count}", True, (255, 255, 255))
    text_x = 640
    text_y = 10
    sc.blit(text, (text_x, text_y))


if __name__ == '__main__':
    screen.fill((149, 200, 216))
    grass = Grass()
    clock = pygame.time.Clock()
    timer = pygame.USEREVENT + 1
    gamer_spr = pygame.sprite.Group()
    Catcher(gamer_spr)
    faller_spr = pygame.sprite.Group()
    pygame.time.set_timer(timer, 1000)
    # Border(0, 380, 800, 375)
    Border(0, 380, 0, 700)
    Border(0, 700, 800, 700)
    Border(800, 375, 800, 700)
    Border(80, 545, 130, 545)
    Faller(faller_spr)
    running = True
    while running:
        for event in pygame.event.get():
            if event == pygame.QUIT:
                running = False
            if event.type == timer:
                Faller(faller_spr)
                faller_spr.draw(screen)
                faller_spr.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
        event = None
        screen.fill((149, 200, 216))
        gamer_spr.update(event)
        all_sprites.draw(screen)
        all_sprites.update()
        gamer_spr.draw(screen)
        faller_spr.draw(screen)
        faller_spr.update()
        draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
