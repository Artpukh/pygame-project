import pygame
from pygame_functions import *
import sys
import os
import random

pygame.init()
size = width, height = 800, 700
screen = pygame.display.set_mode(size)
screen_rect = (0, 0, width, height)
GRAVITY = 0.25
end_pos = None


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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, *group):
        super().__init__(*group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect()
        print(self.image.get_rect())
        self.rect = self.rect.move(x, y)
        self.spr = self.rect

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

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


    def update(self):
        if pygame.sprite.spritecollide(self, faller_spr, True):
            global count
            count += 1
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def update_left(self):
        if pygame.sprite.spritecollide(self, faller_spr, True):
            global count
            count += 1
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)


class Grass(pygame.sprite.Sprite):
    image = load_image("grass2.png", color_key=None)

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Grass.image
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        # располагаем горы внизу
        self.rect.bottom = height


"""class Catcher(pygame.sprite.Sprite):
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
        print(self.spr)

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
            self.move(0, step)"""


class Faller(pygame.sprite.Sprite):
    image = load_image('korona1.png')

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

        if pygame.sprite.spritecollide(self, bomb_borders, True):
            print(self.rect.x, self.rect.y)
            create_particles((self.rect.x, self.rect.y))
            global running
            running = True


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


class BombBorder(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2):
        super().__init__(all_sprites)
        # горизонтальная стенка
        self.add(bomb_borders)
        self.image = pygame.Surface([x2 - x1, 1])
        self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("korona1.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
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


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def draw(sc):
    global count
    font = pygame.font.Font(None, 50)
    text = font.render(f"Счёт: {count}", True, (255, 255, 255))
    text_x = 640
    text_y = 10
    sc.blit(text, (text_x, text_y))


def restart():
    os.system("python main.py")


if __name__ == '__main__':
    all_sprites = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    animation = pygame.sprite.Group()
    bomb_borders = pygame.sprite.Group()
    dragon = AnimatedSprite(load_image("spritesheet_x6.png"), 36, 1, 300, 550, animation)
    gamer_left = pygame.transform.flip(dragon.image, True, False)
    main_gamer = dragon.image
    count = 0
    wall_list = []
    step = 6
    screen.fill((149, 200, 216))
    grass = Grass()
    clock = pygame.time.Clock()
    timer = pygame.USEREVENT + 1
    BombBorder(85, 545, 115)
    BombBorder(125, 615, 155)
    BombBorder(725, 545, 755)
    BombBorder(680, 615, 710)
    gamer_spr = pygame.sprite.Group()
    faller_spr = pygame.sprite.Group()
    pygame.time.set_timer(timer, 1000)
    timer3 = pygame.USEREVENT + 3
    pygame.time.set_timer(timer3, 20000)
    # Border(0, 380, 800, 375)
    Border(0, 380, 0, 700)
    Border(0, 700, 800, 700)
    Border(800, 375, 800, 700)
    Border(0, 380, 800, 380)
    Faller(faller_spr)
    #Catcher(gamer_spr)

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == timer:
                Faller(faller_spr)
                faller_spr.draw(screen)
                faller_spr.update()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
                restart()

         # Эта часть кода отвечает за передвижение анимации, надо как-то перенсти сюда метод move, чтоб он со стенками не сталкивался
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            #dragon.move(step, 0)
            dragon.rect.x += step
            dragon.rect.y += 0
            dragon.update()
            dragon.image = pygame.transform.scale(dragon.image, (150, 150))

        if pygame.key.get_pressed()[pygame.K_LEFT]:
            #dragon.move(-step, 0)
            dragon.rect.x += -step
            dragon.rect.y += 0
            dragon.update_left()
            dragon.image = pygame.transform.scale(dragon.image, (150, 150))

        if pygame.key.get_pressed()[pygame.K_UP]:
            #dragon.move(0, -step)
            dragon.rect.x += 0
            dragon.rect.y += -step
            dragon.image = pygame.transform.scale(dragon.image, (150, 150))

        if pygame.key.get_pressed()[pygame.K_DOWN]:
            #dragon.move(0, step)
            dragon.rect.x += 0
            dragon.rect.y += step
            dragon.image = pygame.transform.scale(dragon.image, (150, 150))

        event = None
        screen.fill((149, 200, 216))
        gamer_spr.update(event)
        all_sprites.draw(screen)
        all_sprites.update()
        gamer_spr.draw(screen)
        faller_spr.draw(screen)
        faller_spr.update()
        draw(screen)
        animation.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
