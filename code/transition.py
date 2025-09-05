import pygame
 
from settings import *
 
 
 
class Transition:
 
    def __init__(self, reset, player):
 
 
        #获取屏幕
 
        self.display_surface = pygame.display.get_surface()
 
        #获取reset这个方法
 
        self.reset = reset
 
        #由于要对玩家的sleep变量做改动，所以把player当参数传递接受进来
 
        self.player = player
 
 
        #获取一个与窗口等宽等高的image
 
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
 
        #颜色的深度
 
        self.color = 255
 
        #颜色的变化速率
 
        self.speed = -0.5
 
 
    def play(self):
 
        self.color += self.speed
 
        #当窗口变成纯黑的时候，开始反过来让数字变大，并且调用reset函数
 
        if self.color <= 0:
 
            self.speed *= -1
 
            self.color = 0
 
            self.reset()
 
        #当color大于255的时候，说明已经变成纯白的了，此时睡觉结束了，把一些变量恢复成原来的大小即可
 
        if self.color > 255:
 
            self.color = 255
 
            self.player.sleep = False
 
            self.speed = -0.5
 
 
        self.image.fill((self.color, self.color, self.color))
 
        #special_flags=pygame.BLEND_RGBA_MULT是一种绘制方式
 
        #使用了这种绘制方式后，当image是纯白色的，反而会变得透明，而它变得越来越黑的时候，会逐渐变得不透明
 
        #这样，就不会出现刚开始color很大的时候屏幕变白的效果了
 
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)