import pygame
import vectors
from draw2D import to_pixels 


class Button():
    def __init__(self, pos, action, text):
        self.points = [(2,1),(-2,1),(-2,-1),(2,-1)]
        self.x = pos[0]/40
        self.y = pos[1]/40
        self.text = text

        self.action = action

    def transformed(self):
        return [vectors.add((self.x,self.y),v) for v in self.points]
    
    def on_click(self):
        global game_start, restart
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        new_points = self.transformed()

        if click[0]==1:
            v1_pixel = to_pixels(new_points[1][0],new_points[0][1])
            v2_pixel = to_pixels(new_points[0][0],new_points[3][1])
            if v1_pixel[0] <  mouse_pos[0] < v2_pixel[0] and v1_pixel[1] < mouse_pos[1] < v2_pixel[1]:
                return self.action
        else:
            return -1

    def draw_text(self, screen):
        font = pygame.font.SysFont("arial", 80, True, True)
        text_color = (100,100,100)

        text = font.render(self.text, True, text_color)

        create_pos = to_pixels(self.points[1][0]+self.x, self.points[1][1]+self.y)
        screen.blit(text, create_pos)