import pygame
import sys
import os
from open_2 import main
pygame.init()
size = width, height = 800, 700
FPS = 50
clock = pygame.time.Clock()
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


def terminate():
    pygame.quit()
    sys.exit()


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
      #  run = True

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
            pygame.display.flip()
            clock.tick(FPS)