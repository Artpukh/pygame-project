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


class InputBox:
    def __init__(self, x, y, w, h, lev=False, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color_inactive
        self.text = text
        self.txt_surface = shrift.render(text, True, self.color)
        self.active = False
        self.lev = lev

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
                    self.text = ''
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

    def recorder(self):
        return (self.best_nck, self.record)



def main(screen):
    buttom = pygame.Rect(300, 450, 150, 75)
    bt_surf = pygame.Surface((150, 75))
    labels_cord_sp = [(290, 170), (40, 295), (325, 450), (35, 28)]
    labels_ttl_sp = ['Введите ваш никнейм', 'Введите уровень сложности: до касания земли или до истечения времени',
                     'Играть!']
    labels(labels_ttl_sp, labels_cord_sp, bt_surf)
    clock = pygame.time.Clock()
    input_box1 = InputBox(300, 200, 140, 35)
    input_box2 = InputBox(300, 340, 140, 35, True)
    input_boxes = [input_box1, input_box2]
    best_player, record = input_box2.recorder()
    labels_cord_sp.append((650, 30))
    labels_ttl_sp.append('Лучший игрок:')
    labels_cord_sp.append((650, 60))
    labels_ttl_sp.append(best_player)
    labels_cord_sp.append((650, 90))
    labels_ttl_sp.append('Рекорд:')
    labels_cord_sp.append((650, 120))
    labels_ttl_sp.append(record)
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            for box in input_boxes:
                box.handle_event(event)
        for i in input_boxes:
            i.update()


        pygame.draw.rect(screen, (20, 220, 120), buttom)
        labels(labels_ttl_sp, labels_cord_sp, bt_surf)
        for i in input_boxes:
            i.draw(screen)

        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main(screen)
    pygame.quit()