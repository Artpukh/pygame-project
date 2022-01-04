import pygame
import sys
import os
import random
from open_2 import main
import sqlite3

all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
pygame.init()
size = width, height = 800, 700
screen = pygame.display.set_mode(size)
count = 0
clock = pygame.time.Clock()
data = sqlite3.connect('game_data.db')
cur = data.cursor()


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
            colorkey = image.get_at((0, 0))
        image.set_colorkey(color_key)
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
                spis = main(screen)
                return spis
        pygame.display.flip()
        clock.tick(30)


def for_open_2():
    EndScreen()
    while True:
        EndScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                if EndScreen().check(event):
                    spis = main(screen)
                    return spis
   #     EndScreen()
        pygame.display.flip()
        clock.tick(30)


def end(spis):
    if spis[1] == 'до касания земли':
        players = cur.execute('''SELECT nickname from Touch_Level''').fetchall()
        if spis[0] in players:
            players = cur.execute("""UPDATE Touch_Level
                SET points=?
                WHERE nickname=?""", (count, spis[0]))
        else:
            add = '''INSERT into Time_Level(nickname,points)
                                                        VALUES(?, ?)'''
            tuplee = (spis[0], count)
            cur.execute(add, tuplee)
    else:
        players = cur.execute('''SELECT nickname from Time_Level''').fetchall()
        if spis[0] in players:
            players = cur.execute("""UPDATE Time_Level
                        SET points=?
                        WHERE nickname=?""", (count, spis[0]))
        else:
            add = '''INSERT into Time_Level(nickname,points)
                                            VALUES(?, ?)'''
            tuplee = (spis[0], count)
            cur.execute(add, tuplee)
    data.commit()
    data.close()
    spis = for_open_2()
    return


class Grass(pygame.sprite.Sprite):
    image = load_image("fon_for_pg1.jpeg", color_key=None) # grass1.png

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Grass.image
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        # располагаем горы внизу
        self.rect.bottom = height


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
            string_rendered = font.render(line, True, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 20
            intro_rect.top = text_coord
            intro_rect.x = 40
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)


class EndScreen:
    def __init__(self):
        fon = pygame.transform.scale(load_image('black_fon.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 40)
        label_text1 = font.render(f'Ваш результат: {count}', True, (255, 255, 255))
        label_text2 = font.render('Вернуться в стартовое меню', True, (255, 255, 255))
        bt_surf = pygame.Surface((250, 75))
        screen.blit(label_text1, (300, 250))
        screen.blit(bt_surf, (300, 350))
        bt_surf.fill((0, 255, 0))
        bt_surf.blit(label_text2, (35, 28))
        self.bt_rect = pygame.Rect(300, 350, 250, 75)

    def check(self, *args):
        if args and self.bt_rect.collidepoint(args[0].pos):
            return True
        return False


spis = for_open_1()
print(spis)
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
            if event.type == pygame.QUIT:
                running = False
                end(spis)
            '''
            if event.type == timer:
                Faller(faller_spr)
                faller_spr.draw(screen)
                faller_spr.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
            '''
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


'''
def check_level(level):
    if level == 'до касания земли':



if spis and spis[1] == 'до касания земли:'
    check_level('до касания земли')
'''