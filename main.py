import pygame
import sys
from MajorFunctions import *
from math import pi
from background import backgrounds




def main():
    rotated_image=""
    new_rect = ""
    player = Turret()
    enemys = []
    bullets = []
    items = []
    # score, bomb, emp

    lobby_buttons = [Button((0,0),0, "Start"), Button((0,-100),1, "Exit")]
    end_buttons = [Button((0,0),2, "Re-Start"), Button((0,-100),1, "Exit")]

    time = 0
    mob_stun_time = 0
    pygame.init()

    #global score, bomb_count, emp_count

    screen = pygame.display.set_mode([width,height])

    pygame.display.set_caption("Turreeeeeeet!")

    clock = pygame.time.Clock()
    game_start = False
    restart = False
    game_playing = True
    mob_count_speed = 1
    mob_count_creation = 1
    level = 0
    next_level_mob_count_speed = 20
    next_level_mob_count_creation = 20
    creation_time = 2000
    
    while game_playing:
        
        # 게임 시작 시 로비를 관리하는 코드
        while not game_start and not restart:
            clock.tick()
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    pygame.quit() # Flag that we are done so we exit this loop

            for b in lobby_buttons:
                flag = b.on_click()
                if flag == 0:
                    game_start = True
                elif flag == 1:
                    pygame.quit()
                

            screen.fill(WHITE)
            for b in lobby_buttons:
                b.draw_text(screen)
                draw_poly(screen, b, color=BLACK)

            #print(game_start)
            pygame.display.flip()
        # 여기까지 로비

        # 게임의 모든 상태를 초기화함. 게임을 다시 시작하는 경우에 필요한 기능
        player.cHP = player.HP
        score = 0
        creation_time = 2000
        mob_count_speed = 1
        mob_count_creation = 1
        next_level_mob_count_speed = 20
        next_level_mob_count_creation = 20
        enemys = []
        bullets = []
        time = 0
        mob_stun_time = 0
        update_time = 2

        init()

        # 본 게임의 흐름을 관리하는 코드
        while game_start:
            restart = False
            if(player.cHP <= 0):
                break

            
            clock.tick()

            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    pygame.quit() 
                if event.type == pygame.MOUSEBUTTONDOWN and player.can_attack_timer == 0: 
                    # 마우스 클릭 시 마우스 방향으로 탄환 생성 / 탄환은 생성 시 지정된 방향으로 자동 이동
                    bul = Bullet(player.AD, return_mouse_direction((0,0)))
                    bullets.append(bul)
                if event.type == pygame.KEYDOWN:
                    # E키 입력 시 맵 전체 Enemy가 파괴되며 파괴된 Enemy 수만큼 점수 획득, bomb_count가 1 줄어듦
                    
                    if event.key == pygame.K_e and get_bomb_count() > 0:
                        set_bomb_count(get_bomb_count() - 1)
                        while len(enemys) > 0:
                            enemys.remove(enemys[0])
                            set_score(get_score() + 10)
                            

                    # R키 입력 시 맵 전체 Enemy가 4초간 이동을 멈춤, emp_count가 1 줄어듦
                    if event.key == pygame.K_r and get_emp_count() > 0:
                        mob_stun_time = 4000
                        set_emp_count(get_emp_count() - 1)
                        for e in enemys:
                            e.isStun = True
                   

            # 게임의 상태를 갱신함. 모든 상호작용에 대한 변화는 아래 변수에 의해 결정됨.
            milliseconds = clock.get_time()
            time += milliseconds

            if player.can_attack_timer > 0:
                player.can_attack_timer -= milliseconds
            else:
                player.can_attack_timer = 0

            # 일정 시간마다 Enemy를 맵 끝 무작위 위치에서 생성.
            # enemy가 특정 횟수 생성될 때마다 enemy의 생성 딜레이와 enemy의 이동속도를 갱신하여 시간이 지날수록 난이도가 상승
            status_check(milliseconds)
            if time >= creation_time:
                new_pos = create_random_position()

                rand = randint(0,100)
                if rand > 20:
                    rand = 0
                else:
                    rand = 1

                e = Enemy(new_pos, rand, 2+level)
                enemys.append(e)
                time = 0
                mob_count_speed += 1
                mob_count_creation += 1
                if mob_count_speed % next_level_mob_count_speed == 0:
                    level += 1
                    next_level_mob_count_speed += next_level_mob_count_speed/6
                    mob_count_speed = 1

                if mob_count_creation % next_level_mob_count_creation == 0:
                    if creation_time > 400:
                        creation_time -= 200
                        next_level_mob_count_creation += 2
                        mob_count_creation = 1
                

            # 플레이어가 지속적으로 마우스를 쳐다본다
            player.look_mouse()
            
            update_time -= milliseconds
        

            if(update_time <= 0):
                rotated_image = pygame.transform.rotate(player.img, player.rotation_angle*180/pi+90)
                new_rect = rotated_image.get_rect(center=player.img.get_rect(center=(400, 400)).center)
                update_time = 10

            
            # 아래는 emp 발동 시 적의 이동 제한에 대한 코드임
            if(mob_stun_time > 0):
                mob_stun_time -= milliseconds

            if(mob_stun_time <= 0):
                mob_stun_time = 0
                for e in enemys:
                    e.isStun = False

            for e in enemys:
                if(e.isStun == False):
                    e.move(milliseconds)

            for b in bullets:
                b.move(milliseconds)

            
                
            

            # 총알과 Enemy가 맵 밖을 나가거나 플레이어와의 충돌을 다룸
            for b in bullets:
                is_over_map(screen, b, bullets)

            # Enemy는 플레이어와 충돌 시 즉시 파괴되면 플레이어의 체력을 깎음
            for e in enemys:
                is_over_map(screen, e, enemys)
                if abs(e.x) < 0.2 and abs(e.y) < 0.2:
                    enemys.remove(e)
                    player.cHP -= 1 

            # 모든 충돌을 다루는 함수 
            check_all_collisions(bullets, enemys, items, player)


            # 그래픽 업데이트 함수
            
            screen.blit(backgrounds, (0,0))

            update_interface(screen, player)
            draw_poly(screen, player, color=BLUE)
            screen.blit(rotated_image, new_rect)
            for b in bullets:
                draw_poly(screen, b, color=BLACK)
            for e in enemys:
                draw_poly(screen, e, color=RED)
                e.draw_rotated_image(screen)
            for i in items:
                item_color = BLACK
                if i.type == 0:
                    item_color = BLACK
                elif i.type == 1:
                    item_color = PURPLE
                elif i.type == 2:
                    item_color = RED
                elif i.type == 3:
                    item_color = GREEN
                draw_poly(screen, i, color=item_color)
                i.draw(screen)
            pygame.display.flip()

        # 여기까지 본 게임의 코드

        # 게임 오버 시 재시작 및 종료를 묻는 로비를 관리하는 코드
        while True:
            clock.tick()
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    pygame.quit()

            for b in end_buttons:
                flag = b.on_click()
                if flag == 2:
                    restart = True
                elif flag == 1:
                    pygame.quit()

            if restart:
                break   
             
            screen.fill(WHITE)
            for b in end_buttons:
                b.draw_text(screen)
                draw_poly(screen, b, color=BLACK)

            pygame.display.flip()
        # 여기까지 종료 로비
        
    pygame.quit()

if __name__ == "__main__":
    if '--screenshot' in sys.argv:
        screenshot_mode = True
    main()

print(__name__)