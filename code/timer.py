import pygame
 
 
class Timer:
 
    def __init__(self,duration,func = None):
 
        self.duration = duration#计时器的持续时间
 
        self.func = func#计时结束后要执行的函数
 
        self.start_time = 0#开始时间，初始化为0
 
        self.active = False#bool，表示是否正在计时
 
 
    def activate(self):
 
        self.active = True
 
        # pygame.time.get_ticks()与pygame.time.Clock().get_ticks()不同
 
        # 这里返回的是 从程序开始 到现在的时间，单位是ms
 
        self.start_time = pygame.time.get_ticks()
 
 
    def deactivate(self):
 
        self.active = False
 
        self.start_time = 0
 
 
    def update(self):
 
        current_time = pygame.time.get_ticks()
 
        if current_time - self.start_time >=self.duration:
 
            if self.func and self.start_time !=0:
 
                self.func()
 
            self.deactivate()