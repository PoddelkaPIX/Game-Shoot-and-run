import pygame,time, sys
from pygame.locals import*
pygame.init()
screen_size = (400,400)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("timer")
time_left = 90 #duration of the timer in seconds
crashed  = False
font = pygame.font.SysFont("Somic Sans MS", 30)
color = (255, 255, 255)

while not crashed:
    for event in pygame.event.get():
        if event.type == QUIT:
            crashed = True
    total_mins = time_left//60 # minutes left
    total_sec = time_left-(60*(total_mins)) #seconds left
    time_left -= 1
    if time_left > -1:
        text = font.render(("Time left: "+str(total_mins)+":"+str(total_sec)), True, color)
        screen.blit(text, (200, 200))
        pygame.display.flip()
        screen.fill((20,20,20))
        time.sleep(1)#making the time interval of the loop 1sec
    else:
        text = font.render("Time Over!!", True, color)
        screen.blit(text, (200, 200))
        pygame.display.flip()
        screen.fill((20,20,20))




pygame.quit()
sys.exit()
