import pygame.display
from pygame_functions import *
import random
from open_2 import main
import sqlite3

os.system("pip install -r requirements.txt")
pygame.init()
pygame.display.set_caption('Ну, вирус, погоди!')
size = width, height = 800, 700
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
bomb_borders = pygame.sprite.Group()
count = 0  # очки
seconds = 70  # время таймера
milliseconds = 800  # время, через которое появляются новые вирусы
main_time = 0
wall_list = []  # список стен
left = False  # повернут ли персонаж влево
STEP = 7  # шаг персонажа
GRAVITY = 0.25  # "притяжение" звёздочек к нижней границе
choose_level = None  # выбранный уровень
p50 = False  # проверка, не набрал ли игрок 50 баллов
screen_rect = pygame.Rect(0, 0, width, height)


def check_level(level):  # проверака уровня
    global choose_level
    if level == 'до касания земли':
        choose_level = True
    else:
        choose_level = False


def load_image(name, color_key=None):  # загрузка фотографий
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


def for_open_1():  # открытие первого стартового окна
    StartScreen('black_fon.jpg')
    while True:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif events.type == pygame.KEYDOWN or \
                    events.type == pygame.MOUSEBUTTONDOWN:
                lst = main(screen)  # список, содержащий никнейм игрока и выбранный им уровень
                return lst
        pygame.display.flip()
        clock.tick(30)


def for_final():  # открытие финального окна
    while True:
        EndScreen()
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if events.type == pygame.MOUSEBUTTONDOWN:
                if EndScreen().check(events):
                    pygame.quit()
                    os.system('python main.py')  # перезапуск игры
                    sys.exit()
        EndScreen()
        pygame.display.flip()
        clock.tick(30)


def end(lst, pts50):  # добавление результатов в базу данных
    data = sqlite3.connect('game_data.db')
    cur = data.cursor()
    if lst[1] == "до касания земли":
        players = cur.execute('''SELECT nickname, points from Touch_Level''').fetchall()
        our_pl = []
        # находим элемент, у которого никнейм совпадает с никнеймом современного игрока
        for i in players:
            if str(i[0]) == str(lst[0]):
                our_pl.append(i)
        if our_pl:
            if our_pl[0][1] < count:  # проверка на величнину набранных очков
                cur.execute("""UPDATE Touch_Level
                    SET points=?
                    WHERE nickname=?""", (count, lst[0]))
        else:
            add = '''INSERT into Touch_Level(nickname,points)
                                                        VALUES(?, ?)'''
            tpl = (lst[0], count)
            cur.execute(add, tpl)
    elif lst[1] == "до истечения времени":
        players = cur.execute('''SELECT nickname, points from Time_Level''').fetchall()
        our_pl = []
        # находим элемент, у которого никнейм совпадает с никнеймом современного игрока
        for i in players:
            if str(i[0]) == str(lst[0]):
                our_pl.append(i)
        if our_pl:
            if our_pl[0][1] < count:
                cur.execute("""UPDATE Time_Level
                            SET points=?
                            WHERE nickname=?""", (count, lst[0]))
        else:
            add = '''INSERT into Time_Level(nickname,points)
                                            VALUES(?, ?)'''
            tpl = (lst[0], count)
            cur.execute(add, tpl)
    else:
        pygame.quit()
        sys.exit()
    data.commit()
    data.close()
    if not pts50:  # если игрок набирает 50 очков в "до касания", то финальное окно не открывается
        for_final()


def move(x_step, y_step, player_rect):  # проверка на столкновение со стенами
    player_rect.x += x_step
    for block in wall_list:
        if player_rect.colliderect(block):
            if x_step < 0:
                player_rect.left = block.right  # выравниваем по левой стене
            elif x_step > 0:
                player_rect.right = block.left  # выравниваем по правой стене
            break

    player_rect.y += y_step
    for block in wall_list:
        if player_rect.colliderect(block):
            if y_step < 0:
                player_rect.top = block.bottom  # выравние по верхней стене
            elif y_step > 0:
                player_rect.bottom = block.top  # выравнивание по нижней стене
            break


class Grass(pygame.sprite.Sprite):  # фон травы
    image = load_image("grass2.png", color_key=None)

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Grass.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height


class Faller(pygame.sprite.Sprite, ):  # вирусы
    image = load_image("korona1.png")

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
        if choose_level:
            if pygame.sprite.spritecollide(self, bomb_borders, False):
                global spis
                stopMusic()
                loose_music = makeSound("data/sound_for_lose1.mp3")
                playSound(loose_music)
                end(spis, p50)


class Border(pygame.sprite.Sprite):  # границы
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


class VirusBorder(pygame.sprite.Sprite):  # границы для вируса
    def __init__(self, x1, y1, x2):
        super().__init__(all_sprites)
        # горизонтальная стенка
        self.add(bomb_borders)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)

    def update(self):
        if not choose_level:
            if pygame.sprite.spritecollide(self, faller_spr, True):
                pass  # если "до истечения времени", то ничего не происходит


def draw(sc):  # количество очков и таймер
    global count
    font = pygame.font.Font(None, 50)
    text = font.render(f"Счёт: {count}", True, (255, 255, 255))
    text_x = 640
    text_y = 10
    sc.blit(text, (text_x, text_y))
    if not choose_level:
        text_timer = font.render(f'Осталось секунд: {seconds}', True, (255, 255, 255))
        text_timer_x = 5
        text_timer_y = 10
        sc.blit(text_timer, (text_timer_x, text_timer_y))


class StartScreen:   # первое стартовое окно
    def __init__(self, fon_image):
        self.intro_text = ["                            Игра 'Ну, вирус, погоди!' "" ",
                      "                                     Правила игры:",
                      "                  Главный герой - доктор, который должен",
                      "                          ловить падающие с неба вирусы.",
                      "                    Игра продолжается, в зависимости от",
                      "                                выбранного уровня,",
                      "                         либо до касания вирусом земли,",
                      "                         либо до истечения времени,",
                      "                             отведённого на раунд."]

        fon = pygame.transform.scale(load_image(fon_image), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 35)
        text_coord = 75  # отступ по оси y
        for line in self.intro_text:
            string_rendered = font.render(line, True, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 20
            intro_rect.top = text_coord
            intro_rect.x = 40
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)


class EndScreen:  # финальный экран
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

    def check(self, *args):  # проверка на нажатие кнопки
        if args and self.bt_rect.collidepoint(args[0].pos):
            return True
        return False


def for_win_screen():  # для открытия окна при наборе 50 баллов в "до касания земли"
    while True:
        WinnerScreen()
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if events.type == pygame.MOUSEBUTTONDOWN:
                if WinnerScreen().check(events):
                    global p50
                    p50 = True  # набрано 50 баллов
                    end(spis, p50)
                    pygame.quit()
                    os.system('python main.py')  # перезагрузка программы
                    sys.exit()
        particle_count = 1  # количество появившихся звёздочек за одну иттерацию
        numbers = range(-3, 10)  # скорости звёздочек
        for i in range(particle_count):
            Particle(random.choice(numbers), random.choice(numbers))  # "рождаем" звёздочки
        stars.update()
        WinnerScreen()
        stars.draw(screen)
        pygame.display.flip()
        clock.tick(50)


class WinnerScreen:  # победное окно
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

    def check(self, *args):  # проверка на нажатие кнопки
        if args and self.bt_rect.collidepoint(args[0].pos):
            return True
        return False


class Particle(pygame.sprite.Sprite):  # звёздочки
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))   # добавляем звёздочки разных размеров

    def __init__(self, dx, dy):
        super().__init__(stars)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = random.randint(75, 600), random.randint(150, 550)
        self.gravity = GRAVITY

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


class AnimatedSprite(pygame.sprite.Sprite):  # анимация
    def __init__(self, sheet, columns, rows, x, y, *group):
        super().__init__(*group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (150, 150))  # уменьшаем доктора
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)
        self.spr = self.rect

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):  # ставим новую картинку, смотрящую вправо
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def update_left(self):  # ставим новую картинку, смотрящую влево
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)

    def touch(self):  # добавляем баллы за каждый пойманный вирус
        if pygame.sprite.spritecollide(self, faller_spr, True):
            global count
            count += 1


pygame.display.set_icon(load_image('icon.png'))
spis = for_open_1()  # принимаем никнейм и уровень
if spis is None:
    pygame.quit()
    sys.exit()
check_level(spis[1])
if __name__ == '__main__':
    all_sprites = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    animation = pygame.sprite.Group()
    bomb_borders = pygame.sprite.Group()
    doctor = AnimatedSprite(load_image("spritesheet_x6.png"), 36, 1, 300, 550, animation)
    gamer_left = pygame.transform.flip(doctor.image, True, False)
    main_gamer = doctor.image
    count = 0
    wall_list = []
    sound = makeMusic("data/sound1.mp3")
    playMusic()
    screen.fill((149, 200, 216))
    grass = Grass()
    clock = pygame.time.Clock()
    spawn_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_timer, 1000)  # частота, с которой падают вирусы в самом начале
    VirusBorder(85, 545, 115)
    VirusBorder(125, 615, 155)
    VirusBorder(725, 545, 755)
    VirusBorder(680, 615, 710)
    gamer_spr = pygame.sprite.Group()
    faller_spr = pygame.sprite.Group()
    timer_70sec = pygame.USEREVENT + 2
    pygame.time.set_timer(timer_70sec, 70000)  # таймер
    timer_for_acceleration = pygame.USEREVENT + 3
    pygame.time.set_timer(timer_for_acceleration, 1000)  # ускорение частиц
    timer_for_music = pygame.USEREVENT + 4
    pygame.time.set_timer(timer_for_music, 85000)  # для перезапуска музыки
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
                stopMusic()
                lose_music = makeSound("data/sound_for_lose1.mp3")
                playSound(lose_music)
                end(spis, p50)
                
            if event.type == spawn_timer:
                Faller(faller_spr)
                faller_spr.draw(screen)
                faller_spr.update()

            if event.type == timer_for_acceleration:
                seconds -= 1
                main_time += 1
                if main_time == 15 or main_time == 30 or main_time == 45 or main_time == 60 or main_time == 75\
                        or main_time == 100 or main_time == 115 or main_time == 130:
                    if milliseconds == 0:
                        milliseconds += 100
                    pygame.time.set_timer(spawn_timer, milliseconds)
                    milliseconds -= 100

            if event.type == timer_70sec:
                if choose_level is False:
                    stopMusic()
                    lose_music = makeSound("data/sound_for_lose1.mp3")
                    playSound(lose_music)
                    end(spis, p50)

            if event.type == timer_for_music:
                rewindMusic()

        if pygame.key.get_pressed()[pygame.K_RIGHT]:  # движение вправо
            move(STEP, 0, doctor.rect)
            doctor.update()
            doctor.image = pygame.transform.scale(doctor.image, (150, 150))
            left = False

        if pygame.key.get_pressed()[pygame.K_LEFT]:  # движение влево
            move(-STEP, 0, doctor.rect)
            doctor.update_left()
            doctor.image = pygame.transform.scale(doctor.image, (150, 150))
            left = True

        if pygame.key.get_pressed()[pygame.K_UP]:  # движение вверх
            move(0, -STEP, doctor.rect)
            if left:  # если герой смотрел влево, то, поднимаясь, он тоже будет смотреть влево
                doctor.update_left()
                doctor.image = pygame.transform.scale(doctor.image, (150, 150))
            else:
                doctor.update()
                doctor.image = pygame.transform.scale(doctor.image, (150, 150))

        if pygame.key.get_pressed()[pygame.K_DOWN]:  # движение вниз
            move(0, STEP, doctor.rect)
            if left:  # если герой смотрел влево, то, опускаясь, он тоже будет смотреть влево
                doctor.update_left()
                doctor.image = pygame.transform.scale(doctor.image, (150, 150))
            else:
                doctor.update()
                doctor.image = pygame.transform.scale(doctor.image, (150, 150))

        event = None
        screen.fill((149, 200, 216))
        gamer_spr.update(event)
        all_sprites.draw(screen)
        all_sprites.update()
        faller_spr.draw(screen)
        faller_spr.update()
        doctor.touch()
        draw(screen)
        animation.draw(screen)
        if choose_level and count == 50:
            stopMusic()
            win_music = makeSound("data/sound_for_win1.mp3")
            playSound(win_music)  # перезапуск музыки
            for_win_screen()  # если игрок набирает 50 баллов в "до касания", то открывается специальное окно
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
