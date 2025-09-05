import pygame
 
from settings import *
 
 
class Overlay:
 
    def __init__(self,player):
 
 
        #获得屏幕
 
        self.display_surface = pygame.display.get_surface()
 
        #由于需要知道玩家正在手持什么工具或者种子，所以需要调用player里面的变量，所以把player当成参数传进来
 
        self.player = player
 
        #用于存放所有的工具的图片的字典，其key值是工具名，value值是图片
 
        self.tools_surf = {}
 
        #用于存放所有种子的图片的字典，其key值是种子名，value值是图片
 
        self.seeds_surf = {}
 
 
        #存放种子和工具的文件夹路径
 
        overlay_path = '../graphics/overlay/'
 
 
        #利用for循环分别把每一个工具和种子，利用image.load函数导入进来，然后再加入到字典中
 
        for tool in player.tools:
 
            #把图片加载进来
 
            img = pygame.image.load(overlay_path+'/'+tool+'.png').convert_alpha()
 
            self.tools_surf[tool] = img
 
 
        for seed in player.seeds:
 
            #把图片加载进来
 
            img = pygame.image.load(overlay_path+'/'+seed+'.png').convert_alpha()
 
            self.seeds_surf[seed] = img
 
 
    def display(self):
 
        #获取玩家正在使用的工具的图像
        tool_surf = self.tools_surf[self.player.selected_tool]
 
        #设置图像要显示的位置，其中midbottom 是图片下边的中间，OVERLAY_POSITIONS[]是在settings.py内设置的常量
 
        tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
 
        #绘制工具图像
 
        #.blit(要绘制的图像，要绘制的坐标)
 
        self.display_surface.blit(tool_surf,tool_rect)
 
 
        seed_surf = self.seeds_surf[self.player.selected_seed]
 
        seed_rect = seed_surf.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
 
        self.display_surface.blit(seed_surf, seed_rect)