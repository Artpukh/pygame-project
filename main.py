import pygame
import sys
import os
import random
from open_2 import main
import sqlite3


pygame.init()
size = width, height = 800, 700
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
bomb_borders = pygame.sprite.Group()
count = 0
seconds = 60
wall_list = []
step = 8
choosen_level = None
screen_rect = pygame.Rect(0, 0, width, height)


def check_level(level):
    global choosen_level
    if level == 'до касания земли':
        choosen_level = True
    else:
        choosen_level = False


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
    while True:
        EndScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if EndScreen().check(event):
                    pygame.quit()
                    os.system('python main.py')
                    sys.exit()
        EndScreen()
        pygame.display.flip()
        clock.tick(30)


def end(spis):
    data = sqlite3.connect('game_data.db')
    cur = data.cursor()
    if spis[1] == "до касания земли":
        players = cur.execute('''SELECT nickname, points from Touch_Level''').fetchall()
        our_pl = list(filter(lambda x: x[0] == spis[0], players))
        if our_pl:
            if our_pl[0][1] < count:
                players = cur.execute("""UPDATE Touch_Level
                    SET points=?
                    WHERE nickname=?""", (count, spis[0]))
        else:
            add = '''INSERT into Touch_Level(nickname,points)
                                                        VALUES(?, ?)'''
            tuplee = (spis[0], count)
            cur.execute(add, tuplee)
    elif spis[1] == "до истечения времени":
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
    else:
        pygame.quit()
        sys.exit()
    data.commit()
    data.close()
    spis = for_open_2()
    return spis


class Grass(pygame.sprite.Sprite):
    image = load_image("grass2.png", color_key=None) # grass1.png

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
        self.spr = self.rect
        self.gamer_left = pygame.transform.flip(self.image, True, False)
        self.main_gamer = self.image

    def move(self, x_step, y_step):
        self.spr.x += x_step
        for wall in wall_list:
            if self.spr.colliderect(wall):
                if x_step < 0:
                    self.spr.left = wall.right
                elif x_step > 0:
                    self.spr.right = wall.left
                break

        self.spr.y += y_step
        for wall in wall_list:
            if self.spr.colliderect(wall):
                if y_step < 0:
                    self.spr.top = wall.bottom
                elif y_step > 0:
                    self.spr.bottom = wall.top
                break

    def update(self, *args):
        if pygame.sprite.spritecollide(self, faller_spr, True):
            global count
            count += 1
        if args and (pygame.key.get_pressed()[pygame.K_RIGHT]):
            self.move(step, 0)
            self.image = self.main_gamer

        if args and (pygame.key.get_pressed()[pygame.K_LEFT]):
            self.move(-step, 0)

            self.image = self.gamer_left
        if args and (pygame.key.get_pressed()[pygame.K_UP]):
            self.move(0, -step)

        if args and (pygame.key.get_pressed()[pygame.K_DOWN]):
            self.move(0, step)


class Faller(pygame.sprite.Sprite, ):
    image = load_image('bomb.png')

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Faller.image
        self.rect = self.image.get_rect()
        rand_pos = random.randint(1, 4)

        # Бомба появляется в одном из 4 мест
        if rand_pos == 1:
            self.rect.x = 80
            self.rect.y = 130
        elif rand_pos == 2:
            self.rect.x = 120
            self.rect.y = 250
        elif rand_pos == 3:
            self.rect.x = 720
            self.rect.y = 130
        elif rand_pos == 4:
            self.rect.x = 675
            self.rect.y = 250

    def update(self):
        self.rect = self.rect.move(0, 2)
        if choosen_level:
            if pygame.sprite.spritecollide(self, bomb_borders, False):
                global spis
                end(spis)


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.image.fill((119, 168, 58))
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
            wall_list.append(self.rect)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.image.fill((119, 168, 58))
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
            wall_list.append(self.rect)


class VirusBorder(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2):
        super().__init__(all_sprites)
        # горизонтальная стенка
        self.add(bomb_borders)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)

    def update(self):
        if not choosen_level:
            if pygame.sprite.spritecollide(self, faller_spr, True):
                pass


def draw(sc):
    global count
    font = pygame.font.Font(None, 50)
    text = font.render(f"Счёт: {count}", True, (255, 255, 255))
    text_x = 640
    text_y = 10
    sc.blit(text, (text_x, text_y))
    if not choosen_level:
        text_timer = font.render(f'Осталось секунд: {seconds}', True, (255, 255, 255))
        text_timer_x = 5
        text_timer_y = 10
        sc.blit(text_timer, (text_timer_x, text_timer_y))


class StartScreen:
    def __init__(self, fon_image):
        self.intro_text = ["Игра 'Ну, вирус, погоди!' "" ",
                      "Правила игры:",
                      "Главный герой - доктор, который должен",
                      "поймать падающие с неба вирусы",
                      "в свою маску."
                      "Игра продолжается, в зависимости от",
                      "выбранного уровня,",
                      "либо до касания вирусом земли,",
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
        font = pygame.font.Font(None, 35)
        label_text1 = font.render(f'Ваш результат: {count}', True, (255, 255, 255))
        label_text2 = font.render('Вернуться в стартовое меню', True, (0, 0, 0))
        bt_surf = pygame.Surface((350, 75))
        screen.blit(label_text1, (300, 250))
        bt_surf.fill((0, 255, 0))
        bt_surf.blit(label_text2, (3, 28))
        screen.blit(bt_surf, (240, 350))
        self.bt_rect = pygame.Rect(250, 350, 350, 75)

    def check(self, *args):
        if args and self.bt_rect.collidepoint(args[0].pos):
            return True
        return False


def for_win_screen():
    while True:
        WinnerScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if WinnerScreen().check(event):
                    pygame.quit()
                    os.system('python main.py')
                    sys.exit()
        particle_count = 1
        numbers = range(-3, 10)
        for i in range(particle_count):
             Particle(random.choice(numbers), random.choice(numbers))
        stars.update()
        WinnerScreen()
        stars.draw(screen)
        pygame.display.flip()
        clock.tick(50)


class WinnerScreen:
    def __init__(self):
        fon = pygame.transform.scale(load_image('black_fon.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 35)
        label_text = font.render('Поздравляем! Вы набрали 50 баллов', True, (255, 255, 255))
        but_text = font.render('Вернуться в стартовое меню', True, (0, 0, 0))
        bt_surf = pygame.Surface((350, 75))
        screen.blit(label_text, (220, 280))
        bt_surf.fill((0, 255, 0))
        bt_surf.blit(but_text, (3, 28))
        screen.blit(bt_surf, (240, 350))
        self.bt_rect = pygame.Rect(250, 350, 350, 75)

    def check(self, *args):
        if args and self.bt_rect.collidepoint(args[0].pos):
            return True
        return False


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, dx, dy):
        super().__init__(stars)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = random.randint(75, 600), random.randint(150, 550)
        self.gravity = 0.25

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


spis = for_open_1()
if spis is None:
    pygame.quit()
    sys.exit()
check_level(spis[1])
if __name__ == '__main__':
    screen.fill((149, 200, 216))
    grass = Grass()
    timer = pygame.USEREVENT + 1
    pygame.time.set_timer(timer, 1000)
    timer2 = pygame.USEREVENT + 2
    pygame.time.set_timer(timer2, 60000)
    VirusBorder(85, 545, 115)
    VirusBorder(125, 615, 155)
    VirusBorder(725, 545, 755)
    VirusBorder(680, 615, 710)
    gamer_spr = pygame.sprite.Group()
    Catcher(gamer_spr)
    faller_spr = pygame.sprite.Group()
    Border(0, 380, 0, 700)
    Border(0, 700, 800, 700)
    Border(800, 375, 800, 700)
    Border(0, 380, 800, 380)
    Faller(faller_spr)
    stars = pygame.sprite.Group()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end(spis)
            if event.type == timer:
                Faller(faller_spr)
                faller_spr.draw(screen)
                faller_spr.update()
                seconds -= 1
            if event.type == timer2:
                if choosen_level is False:
                    end(spis)
        event = None
        screen.fill((149, 200, 216))
        gamer_spr.update(event)
        all_sprites.draw(screen)
        all_sprites.update()
        gamer_spr.draw(screen)
        faller_spr.draw(screen)
        faller_spr.update()
        bomb_borders.update()
        draw(screen)
        if choosen_level and count == 50:
            for_win_screen()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()