import pygame
import sys
import os
pygame.init()
size = width, height = 600, 600
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
                      "поймать падающие м неба вирусы",
                      "в свою маску."
                      "Игра продолжается, в зависимости от",
                      "выбранного уровня,",
                      "либо до касания вируса земли",
                      "или игрока,",
                      "либо до истечения времени,",
                      "отведенного на раунд."]

        fon = pygame.transform.scale(load_image(fon_image), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in self.intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 15
            intro_rect.top = text_coord
            intro_rect.x = 40
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return  # начинаем игру
            pygame.display.flip()
            clock.tick(FPS)


StartScreen('fon_for_pg1.jpeg')