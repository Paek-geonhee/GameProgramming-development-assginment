import pygame
import vectors
from math import pi, sqrt, cos, sin, atan2, atan
from random import randint, uniform
from linear_solver import do_segments_intersect
import sys
from draw2D import *
from Button import *
from ItemImage import image
from EnemyImage import Enemy_image


status_text_enable = False
status_text_timer = 0
text_str = ""


# DEFINE OBJECTS OF THE GAME

class Bullet():
    def __init__(self, ad, angle):
        self.points = [(0.2,0), (-0.2,0)]
        self.ad = ad
        self.angle = angle
        self.x=0
        self.y=0
        self.vx = 20*cos(angle)
        self.vy = 20*sin(angle)
        self.rotation_angle = angle

    def move(self, milliseconds):
        dx, dy = self.vx * milliseconds / 1000.0, self.vy * milliseconds / 1000.0
        self.x, self.y = vectors.add((self.x,self.y), (dx,dy))

    def transformed(self):
        rotated = [vectors.rotate2d(self.rotation_angle, v) for v in self.points]
        return [vectors.add((self.x,self.y),v) for v in rotated]

class ObjectModel():
    def __init__(self,points ,AD=10,HP=10):
        self.points = points
        self.rotation_angle = 0
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        
        self.HP = HP
        self.cHP = HP

        self.image = ""

    def transformed(self):
        rotated = [vectors.rotate2d(self.rotation_angle, v) for v in self.points]
        return [vectors.add((self.x,self.y),v) for v in rotated]

    def move(self, milliseconds):
        dx, dy = self.vx * milliseconds / 1000.0, self.vy * milliseconds / 1000.0
        self.x, self.y = vectors.add((self.x,self.y), (dx,dy))
        self.rotation_angle += self.angular_velocity * milliseconds / 1000.0
        

    def segments(self):
        point_count = len(self.points)
        points = self.transformed()
        return [(points[i], points[(i+1)%point_count])
                for i in range(0,point_count)]

    def does_collide(self, other_poly):
        for other_segment in other_poly.segments():
            if self.does_intersect(other_segment):
                return True
        return False

    def does_intersect(self, other_segment):
        for segment in self.segments():
            if do_segments_intersect(other_segment,segment):
                return True
        return False

class Turret(ObjectModel):
    def __init__(self):
        super().__init__([(0.4,0), (-0.2,0.2), (-0.2,-0.2)])
        self.img = pygame.image.load("Turret.png")
        self.img = pygame.transform.scale(self.img, (50, 50))

        self.can_attack_timer = 0

    def look_mouse(self):
        self.rotation_angle = return_mouse_direction((self.x,self.y))
        



class Enemy(ObjectModel):
    def __init__(self, points, type, speed = 2):


        super().__init__([ (0,0),(0.25,0.25), (-0.25,0.25), (-0.25,-0.25), (0.25,-0.25)])
        self.angular_velocity = 0
        self.x = points[0]/40
        self.y = points[1]/40
        self.type = type

        norm = sqrt(pow(points[0],2) + pow(points[1],2))
        self.vx = -speed*points[0]/norm
        self.vy = -speed*points[1]/norm

        angle = atan2(self.vy, self.vx)
        
        if angle < 0 :
            angle += 2*pi

        print(angle)

        self.rotation_angle = angle

        self.isStun = False
    
        self.img = Enemy_image[type]
        self.img = pygame.transform.scale(self.img, (50, 50))

        self.rotated_image = pygame.transform.rotate(self.img, self.rotation_angle*180/pi+90)
        
        
        #print(self.x, self.y, self.vx, self.vy)

    def draw_rotated_image(self, screen):
        new_rect = self.rotated_image.get_rect(center=self.img.get_rect(center=to_pixels(self.x, self.y)).center)
        screen.blit(self.rotated_image, new_rect)


        
class Item(ObjectModel):
    def __init__(self, pos, type):
        super().__init__([(0.2,0.2), (-0.2,0.2), (-0.2,-0.2), (0.2,-0.2)])
        self.angular_velocity = 10
        self.x = pos[0]
        self.y = pos[1]

        self.vx = 0
        self.vy = 0

        self.type = type
        self.img = image[type]
        self.img =pygame.transform.scale(self.img, (50, 50))

        self.new_rect = self.img.get_rect(center=self.img.get_rect(center=to_pixels(self.x, self.y)).center)


        # type 0 - bomb / type 1 - emp / type 2 - heal

        

    def draw(self,screen):
        screen.blit(self.img, self.new_rect)
# INITIALIZE GAME STATE



bomb_count = 0
emp_count = 0
score = 0

# 마우스 방향 각도를 반환하는 함수 - 
# 사용처 : 
# 1. 플레이어가 바라보는 방향
# 2. 마우스 클릭 시 총알이 나아가는 방향
def return_mouse_direction(pos):
    x=0
    y=1
        
    mouse_pos = (pygame.mouse.get_pos()[0]-width/2, pygame.mouse.get_pos()[1]-height/2)
    #mouse_pos = to_pixels(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]) # 마우스 위치
    dir_vec = (mouse_pos[x] - pos[x], mouse_pos[y] - pos[y])
        
    #print(dir_vec)
    angle = -atan2(dir_vec[y], dir_vec[x])
    if angle < 0 :
        angle += 2*pi
    
    return angle


    
def is_over_map(screen, b, bullets):
        if b.x < -width/40+0.5 or b.x > width/40-0.5:
            bullets.remove(b)
            return

        if b.y < -height/40+0.5 or b.y > height/40-0.5:
            bullets.remove(b)
    
def create_random_position():
    x=0
    y=0
    # 맵 바깥 랜덤 위치 반환
    axis = randint(0,3)
    if axis == 0:
        x = width/2
        y= uniform(-height/2,height/2)
    elif axis == 1:
        x = uniform(-width/2,width/2)
        y= height/2
    elif axis == 2:
        x = -width/2
        y= uniform(-height/2,height/2)
    elif axis == 3:
        x = uniform(-width/2,width/2)
        y= -height/2
        
    return (x,y)

def get_bomb_count():
    global bomb_count
    return bomb_count

def set_bomb_count(num):
    global bomb_count
    bomb_count = num

def get_emp_count():
    global emp_count
    return emp_count

def set_emp_count(num):
    global emp_count
    emp_count = num

def get_score():
    global score
    return score

def set_score(num):
    global score
    score = num

def init():
    global score
    global bomb_count
    global emp_count

    score = 0
    bomb_count = 0
    emp_count = 0

def check_all_collisions(bullets, enemys, items, player):
    global score
    global bomb_count
    global emp_count
    global text_str, status_text_timer
    for b in bullets:
        for e in enemys:
            if e.does_intersect((b.transformed()[0],b.transformed()[1])):
                if(e.type == 0):
                    posb = randint(0,100)
                    if posb > 70:
                        item_type = randint(0,3)
                        item = Item((e.x,e.y), item_type)
                        items.append(item)
                    enemys.remove(e)
                    bullets.remove(b)
                    
                    score += 10
                    break
                else:
                    enemys.remove(e)
                    bullets.remove(b)
                    score -= 20
                    player.can_attack_timer = 2000


    for b in bullets:
        for i in items:
            if i.does_intersect((b.transformed()[0],b.transformed()[1])):
                status_text_timer = 4000
                if i.type == 0 and bomb_count < 10:
                    bomb_count += 1
                    text_str = "BOMB +1"
                elif i.type == 1 and emp_count < 10:
                    emp_count += 1
                    text_str = "EMP +1"
                elif i.type == 2:
                    player.cHP = player.HP
                    text_str = "HEAL MAX"
                elif i.type == 3:
                    score += 50
                    text_str =  "SCORE +50"
                items.remove(i)

def update_interface(screen, player):
    global score, bomb_count, emp_count, status_text_enable, text_str
    font = pygame.font.SysFont("arial", 30, True, True)
    text_color = (100,100,100)

    hp_text = font.render("HP : "+str(player.cHP) + " / " + str(player.HP), True, text_color)
    bomb_text = font.render("BOMB(E) : "+str(bomb_count) + " / " + str(10), True, text_color)
    emp_text = font.render("EMP(R) : "+str(emp_count)+ " / " + str(10), True, text_color)
    score_text = font.render("SCORE : "+str(score), True, text_color)

    status_text = font.render(text_str, True, text_color)

    screen.blit(hp_text, (30, 10))
    screen.blit(score_text, (600, 10))
    screen.blit(bomb_text, (30, 710))
    screen.blit(emp_text, (30, 750))

    if status_text_enable:
        screen.blit(status_text, (350, 350))
   

def status_check(milliseconds):
    global status_text_enable, status_text_timer

    if status_text_timer > 0 :
        status_text_timer -= milliseconds
        status_text_enable = True
    else:
        status_text_timer = 0
        status_text_enable = False

