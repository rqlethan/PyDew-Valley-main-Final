import pygame
 
from settings import *
 
from sprites import Generic
 
from random import *
 
from support import import_folder
 
 
 
#天空类，管理天色的
 
class Sky:
 
    def __init__(self):
 
        self.display_surface = pygame.display.get_surface()
 
        #创建一个与游戏窗口相同大小的图片，来当作蒙版
 
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
 
        #开始的颜色，也就是天亮的颜色
 
        self.start_color = [255, 255, 255]
 
        #最终的颜色，也即是深夜的颜色
 
        self.end_color = (38, 101, 189)
 
 
    def display(self, dt):
 
        for index, value in enumerate(self.end_color):
 
            if self.start_color[index] > value:
 
                #R,G,B值分别每秒 减小 2
 
                self.start_color[index] -= 2 * dt
 
        #给图片填充颜色
 
        self.full_surf.fill(self.start_color)
 
        #以蒙版的形式绘制到窗口上
 
        self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
 
#雨滴精灵
 
class Drop(Generic):
 
    def __init__(self, surf, pos, moving, groups, z):
 
        #参数中moving表示是否是移动的雨滴，雨滴分为两种，已经落到地上的我们就不让他移动，在空中的我们给他一个向着左下的速度
 
        super().__init__(pos, surf, groups, z)
 
        #雨滴这个精灵的存活时间
 
        self.lifetime = randint(400, 500)
 
        #计时器的开始时间
 
        self.start_time = pygame.time.get_ticks()
 
 
        #如果moving为true，表示这个雨滴是需要移动的
 
        self.moving = moving
 
        #精灵移动所需要的三个参数
 
        if self.moving:
 
            self.pos = pygame.math.Vector2(self.rect.topleft)
 
            self.direction = pygame.math.Vector2(-2, 4)
 
            self.speed = randint(200, 250)
 
 
    def update(self, dt,obj):
 
        #让雨滴动起来
 
        if self.moving:
 
            self.pos += self.direction * self.speed * dt
 
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
 
        #过了存活时间，把这个精灵kill掉
 
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
 
            self.kill()
 
 
#掌管下雨的类
 
class Rain:
 
    def __init__(self,all_sprites):
 
        self.all_sprites = all_sprites
 
        #导入雨滴正在落下的图片，一共三张，以列表的形式返回
 
        self.rain_drops = import_folder('../graphics/rain/drops/')
 
        # 导入雨滴落到地板的图片，一共三张，以列表的形式返回
 
        self.rain_floor = import_folder('../graphics/rain/floor/')
 
        #整张地图的宽度和高度，我们需要这两个数据取随机数，在随机的位置生成雨滴
 
        self.floor_w, self.floor_h = pygame.image.load('../graphics/world/ground.png').get_size()
 
 
    #生成落到地板上的雨滴
 
    def create_floor(self):
 
        Drop(
 
            surf=choice(self.rain_floor),
 
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
 
            moving=False,
 
            groups=self.all_sprites,
 
            z=LAYERS['rain floor'])
 
 
    #生成在空中的雨滴
 
    def create_drops(self):
 
        Drop(
 
            surf=choice(self.rain_drops),
 
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
 
            moving=True,
 
            groups=self.all_sprites,
 
            z=LAYERS['rain drops'])
 
 
    def update(self):
 
        self.create_floor()
 
        self.create_drops()