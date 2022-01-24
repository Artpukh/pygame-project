import pygame
import sys
import os
import sqlite3
data = sqlite3.connect('game_data.db')
cur = data.cursor()

pygame.init()
size = width, height = 800, 700
screen = pygame.display.set_mode(size)
color_inactive = pygame.Color(175, 238, 238)
color_active = pygame.Color(0, 191, 255)
font_txt = pygame.font.Font(None, 32)


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


def labels(titles, coords, surf):  # надписи на кнопках, над полем ввода, об уровнях сложности
    fonn = pygame.transform.scale(load_image('black_fon.jpg'), (width, height))
    screen.blit(fonn, (0, 0))
    label_font = pygame.font.Font(None, 28)
    label_text1 = label_font.render(titles[0], True, (255, 255, 255))
    label_text2 = label_font.render(titles[1], True, (255, 255, 255))
    label_text3 = label_font.render(titles[2], True, (10, 10, 10))
    label_text4 = label_font.render(titles[3], True, (10, 10, 10))
    screen.blit(label_text1, coords[0])
    screen.blit(label_text2, coords[1])
    screen.blit(surf[0], coords[2])
    screen.blit(surf[1], coords[3])
    surf[0].fill((20, 220, 20))
    surf[1].fill((20, 220, 20))
    surf[0].blit(label_text3, coords[4])
    surf[1].blit(label_text4, coords[4])


def bestlb_tch(spis):  # надписи с лучшим игроком в режиме "до касания"
    font = pygame.font.Font(None, 20)
    text_1 = font.render('Лучший игрок в "до касания":', True, (255, 255, 255))
    text_2 = font.render(f'{spis[0]}', True, (255, 255, 255))
    text_3 = font.render('Баллы:', True, (255, 255, 255))
    text_4 = font.render(f'{spis[1]}', True, (255, 255, 255))
    screen.blit(text_1, (50, 35))
    screen.blit(text_2, (50, 60))
    screen.blit(text_3, (50, 85))
    screen.blit(text_4, (50, 110))


def bestlb_time(spis):  # надписи с лучшим игроком в режиме "до истечения времени"
    font = pygame.font.Font(None, 20)
    text_5 = font.render('Лучший игрок в "до истечения времени":', True, (255, 255, 255))
    text_6 = font.render(f'{spis[0]}', True, (255, 255, 255))
    text_7 = font.render('Баллы:', True, (255, 255, 255))
    text_8 = font.render(f'{spis[1]}', True, (255, 255, 255))
    screen.blit(text_5, (500, 35))
    screen.blit(text_6, (500, 60))
    screen.blit(text_7, (500, 85))
    screen.blit(text_8, (500, 110))


def thebest_tch():  # достаём из таблицы лучшего игрока в "до касания"
    players_tch = cur.execute('''SELECT nickname, points from Touch_Level''').fetchall()
    if players_tch:
        players_tch = sorted(players_tch, key=lambda x: -x[1])
        pl_tch, record_tch = players_tch[0]
        bestlb_tch([pl_tch, record_tch])
        return [pl_tch, record_tch]
    else:
        bestlb_tch(['Пока что никого нет :(', 0])
        return ['Пока что никого нет :(', 0]


def thebest_time():  # достаём из таблицы лучшего игрока в "до истечения времени"
    players_time = cur.execute('''SELECT nickname, points from Time_Level''').fetchall()
    if players_time:
        players_time = sorted(players_time, key=lambda x: -x[1])
        pl_time, record_time = players_time[0]
        bestlb_time([pl_time, record_time])
        return [pl_time, record_time]
    else:
        bestlb_time(['Пока что никого нет :(', 0])
        return ['Пока что никого нет :(', 0]


class InputBox:  # строка для ввода
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color_inactive
        self.text = text
        self.txt_surf = font_txt.render(text, True, self.color)
        self.active = False
        self.nick = ''

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = color_active if self.active else color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.nick = self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surf = font_txt.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surf.get_width() + 10)
        self.rect.w = width  # ширина поля ввода

    def draw(self, screen):  # отображаем на экране поле ввода и текст
        screen.blit(self.txt_surf, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def nick_and_lvl(self):
        return self.nick


def main_prog(rect, box, *args):  # при нажатии на кнопку возврщаем введённый никнейм и выбранный режим
    if args and args[0].type == pygame.MOUSEBUTTONDOWN:
        if rect[0].collidepoint(args[0].pos):
            sp = []
            sp.append(box.nick_and_lvl())
            sp.append('до касания земли')
            return sp
        if rect[1].collidepoint(args[0].pos):
            sp = []
            sp.append(box.nick_and_lvl())
            sp.append('до истечения времени')
            return sp


def main(screen):  # основной цикл
    bt1_surf = pygame.Surface((220, 75))  # кнопка "до касания"
    bt2_surf = pygame.Surface((330, 75))  # кнопка "до истечения времени"
    surfaces = [bt1_surf, bt2_surf]
    labels_cord_sp = [(210, 170), (40, 295), (100, 400), (380, 400), (2, 28)]  # координаты надписей
    labels_ttl_sp = ['Введите ваш никнейм (не забудьте enter!)', 'Введите уровень сложности: до касания земли или до истечения времени',
                     'Играть в "до касания"', 'Играть в "до истечения времени"']  # надписи
    labels(labels_ttl_sp, labels_cord_sp, surfaces)
    touching = thebest_tch()
    timing = thebest_time()
    clock = pygame.time.Clock()
    input_box = InputBox(300, 200, 140, 35)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:  # проверяем нажатие кнопки возвращаем информацию в основную программу
                main_prog([pygame.Rect(100, 400, 220, 75), pygame.Rect(380, 400, 330, 75)], input_box, event)
                if main_prog([pygame.Rect(100, 400, 220, 75), pygame.Rect(380, 400, 330, 75)], input_box, event):
                    return main_prog([pygame.Rect(100, 400, 220, 75), pygame.Rect(380, 400, 330, 75)], input_box, event)

            input_box.handle_event(event)

        input_box.update()

        labels(labels_ttl_sp, labels_cord_sp, surfaces)
        bestlb_tch(touching)
        bestlb_time(timing)
        input_box.draw(screen)

        pygame.display.flip()
        clock.tick(30)
