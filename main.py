import pygame
import sys
import os
import random
from open_2 import main
pygame.init()
size = width, height = 800, 700
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


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


def for_open_1():
    StartScreen('black_fon.jpg')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                main(screen)
                return
        pygame.display.flip()
        clock.tick(30)


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


class StartScreen:
    def __init__(self, fon_image):
        self.intro_text = ["Игра 'Ну, вирус, погоди!' "" ",
                      "Правила игры:",
                      "Главный герой - доктор, который должен",
                      "поймать падающие с неба вирусы",
                      "в свою маску."
                      "Игра продолжается, в зависимости от",
                      "выбранного уровня,",
                      "либо до касания вирусом земли",
                      "или игрока,",
                      "либо до истечения времени,",
                      "отведённого на раунд."]

        fon = pygame.transform.scale(load_image(fon_image), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 35)
        text_coord = 50
        for line in self.intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 20
            intro_rect.top = text_coord
            intro_rect.x = 40
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)


for_open_1()
if __name__ == '__main__':
    screen.fill((20, 20, 240))
    screen.fill((0, 255, 0), pygame.Rect(0, 500, width, 200))
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