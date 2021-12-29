import pygame
import sys
import os
import sqlite3
data = sqlite3.connect('game_data.db')
cur = data.cursor()

pygame.init()
size = width, height = 800, 700
screen = pygame.display.set_mode(size)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
shrift = pygame.font.Font(None, 32)


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


def labels(titles, coords, surf):
    fonn = pygame.transform.scale(load_image('black_fon.jpg'), (width, height))
    screen.blit(fonn, (0, 0))
    label_font = pygame.font.Font(None, 28)
    label_text1 = label_font.render(titles[0], True, (255, 255, 255))
    label_text2 = label_font.render(titles[1], True, (255, 255, 255))
    label_text3 = label_font.render(titles[2], True, (10, 10, 10))
    screen.blit(label_text1, coords[0])
    screen.blit(label_text2, coords[1])
    screen.blit(surf, coords[2])
    surf.fill((20, 220, 20))
    surf.blit(label_text3, coords[3])


def bestlb_tch(spis):
    font = pygame.font.Font(None, 20)
    text_1 = font.render('Лучший игрок в "до касания":', True, (255, 255, 255))
    text_2 = font.render(spis[0], True, (255, 255, 255))
    text_3 = font.render('Баллы:', True, (255, 255, 255))
    text_4 = font.render(f'{spis[1]}', True, (255, 255, 255))
    screen.blit(text_1, (50, 35))
    screen.blit(text_2, (50, 60))
    screen.blit(text_3, (50, 85))
    screen.blit(text_4, (50, 110))


def bestlb_time(spis):
    font = pygame.font.Font(None, 20)
    text_5 = font.render('Лучший игрок в "до истечения времени":', True, (255, 255, 255))
    text_6 = font.render(f'{spis[0]}', True, (255, 255, 255))
    text_7 = font.render('Баллы:', True, (255, 255, 255))
    text_8 = font.render(f'{spis[1]}', True, (255, 255, 255))
    screen.blit(text_5, (500, 35))
    screen.blit(text_6, (500, 60))
    screen.blit(text_7, (500, 85))
    screen.blit(text_8, (500, 110))


def thebest_tch():
    players_tch = cur.execute('''SELECT nickname, points from Touch_Level''').fetchall()
    if players_tch:
        players_tch = sorted(players_tch, key=lambda x: -x[1])
        pl_tch, record_tch = players_tch[0]
        bestlb_tch([pl_tch, record_tch])
        return [pl_tch, record_tch]
    else:
        bestlb_tch(['Пока что никого нет :(', 0])
        return ['Пока что никого нет :(', 0]


def thebest_time():
    players_time = cur.execute('''SELECT nickname, points from Time_Level''').fetchall()
    if players_time:
        players_time = sorted(players_time, key=lambda x: -x[1])
        pl_time, record_time = players_time[0]
        bestlb_time([pl_time, record_time])
        return [pl_time, record_time]
    else:
        bestlb_time(['Пока что никого нет :(', 0])
        return ['Пока что никого нет :(', 0]


class InputBox:
    def __init__(self, x, y, w, h, text='', lev=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color_inactive
        self.text = text
        self.txt_surface = shrift.render(text, True, self.color)
        self.active = False
        self.lev = lev
        self.nick = ''
        self.level = ''

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = color_active if self.active else color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN and not self.lev:
                    self.nick = self.text
                elif event.key == pygame.K_RETURN and self.lev:
                    self.level = self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = shrift.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def nick_and_lvl(self):
        return [self.nick, self.level]


def main_prog(rect, boxes, *args):
    if args and args[0].type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(args[0].pos):
        sp = []
        for i in range(len(boxes)):
            sp.append(boxes[i].nick_and_lvl()[i])
        print(sp)
        return sp


def main(screen):
    bt_surf = pygame.Surface((150, 75))
    labels_cord_sp = [(290, 170), (40, 295), (325, 450), (35, 28)]
    labels_ttl_sp = ['Введите ваш никнейм', 'Введите уровень сложности: до касания земли или до истечения времени',
                     'Играть!']
    labels(labels_ttl_sp, labels_cord_sp, bt_surf)
    touching = thebest_tch()
    timing = thebest_time()
    clock = pygame.time.Clock()
    input_box1 = InputBox(300, 200, 140, 35)
    input_box2 = InputBox(300, 340, 140, 35, lev=True)
    input_boxes = [input_box1, input_box2]
    bottom = pygame.Rect(325, 450, 150, 75)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main_prog(pygame.Rect(325, 450, 150, 75), input_boxes, event)
                if main_prog(pygame.Rect(325, 450, 150, 75), input_boxes, event):
                    run = False
            for box in input_boxes:
                box.handle_event(event)

        for i in input_boxes:
            i.update()

        labels(labels_ttl_sp, labels_cord_sp, bt_surf)
        bestlb_tch(touching)
        bestlb_time(timing)
        for i in input_boxes:
            i.draw(screen)

        pygame.display.flip()
        clock.tick(30)
 # pygame.Rect(325, 450, 150, 75)
