import pygame
 
from settings import *
 
from random import *
 
from timer import Timer
 
 
#基类精灵，其他的精灵都在这上面延申
 
class Generic(pygame.sprite.Sprite):
 
    def __init__(self,pos,surf,groups,z = LAYERS['main']):
 
       super().__init__(groups)
 
       self.image = surf
 
       self.rect = self.image.get_rect(topleft = pos)
 
       self.z = z
 
       self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
 
 
 
#水
 
class Water(Generic):
 
    def __init__(self, pos, frames, groups):
 
       #传入的参数，fream是一个列表，存放了水流不同动作的五张图片
 
       self.frames = frames
 
       #fream_index是正在播放第几张图片
 
       self.frame_index = 0
 
 
       super().__init__(
 
             pos = pos,
 
             surf = self.frames[self.frame_index],
 
             groups = groups,
 
             z = LAYERS['water'])
 
 
    #水的动画效果实现
 
    def animate(self,dt):
 
       self.frame_index += 5 * dt
 
       if self.frame_index >= len(self.frames):
 
          self.frame_index = 0
 
       self.image = self.frames[int(self.frame_index)]
 
 
    def update(self,dt,obj):
 
       self.animate(dt)
 
 
#可以产生交互的区域，比如床，交易区域
 
class Interaction(Generic):
 
    def __init__(self, pos, size, groups, name):
 
       surf = pygame.Surface(size)
 
       super().__init__(pos, surf, groups)
 
       self.name = name
 
 
#野花
 
class WildFlower(Generic):
 
    def __init__(self, pos, surf, groups):
 
       super().__init__(pos, surf, groups)
 
       self.hitbox = self.rect.copy().inflate(-20,-self.rect.height)
 
 
 
#粒子效果
 
class Particle(Generic):
 
    def __init__(self, pos, surf, groups, z, duration = 200):
 
       #其中duration是持续时间，默认为200ms
 
       super().__init__(pos, surf, groups, z)
 
       self.start_time = pygame.time.get_ticks()
 
       self.duration = duration
 
 
       #将图片透明的地方设为黑色(1),不透明的地方设为白色，来获取掩码
 
       mask_surf = pygame.mask.from_surface(self.image)
 
       #根据掩码生成图片，该图片只有黑白两种颜色
 
       new_surf = mask_surf.to_surface()
 
       #set_colorkey是在绘制图片的时候只绘制指定的颜色
 
       new_surf.set_colorkey((0,0,0))
 
       self.image = new_surf
 
 
    def update(self,dt,obj):
 
       #经过一定的时间之后，这个精灵会被删除
 
       current_time = pygame.time.get_ticks()
 
       if current_time - self.start_time > self.duration:
 
          self.kill()
 
 
 
#树木
 
class Tree(Generic):
 
    def __init__(self, pos, surf, groups, name,player_add,nums):
 
       super().__init__(pos, surf, groups)
 
 
       self.player_add = player_add
 
 
       #创建苹果用到的变量
 
       #导入苹果的图像素材
 
       self.apple_surf = pygame.image.load('../graphics/fruit/apple.png')
 
       #苹果的坐标，是一个常量
 
       self.apple_pos = APPLE_POS[name]
 
       #创建苹果精灵组，这个精灵组会在砍树的时候用到
 
       self.apple_sprites = pygame.sprite.Group()
 
       self.groups = groups
 
       self.create_fruit()
 
 
       #为砍树用到的变量
       self.health = int(nums)#树的生命值
 
       self.alive = True#树是否存活
 
       stump_path = f'../graphics/stumps/{"small" if name == "Small" else "large"}.png'#树状的图片路径
 
       self.stump_surf = pygame.image.load(stump_path).convert_alpha()#把树状图片导入进来
 
       self.invul_timer = Timer(200)#创建一个计时器
 
 
    def create_fruit(self):
 
       for pos in self.apple_pos:
 
          if randint(0,10) < 2:
 
             #x坐标 = 偏移坐标 + 树的左边缘坐标
 
             x = pos[0] + self.rect.left
 
             #y坐标 = 偏移坐标 + 树的顶部边缘坐标
 
             y = pos[1] + self.rect.top
 
             Generic(
 
                pos = (x,y),
 
                surf = self.apple_surf,
 
                #把它加入苹果精灵组和all_sprites精灵组
 
                #all_sprites是传入的参数的self.group的第一个元素，所以是【0】
 
                groups = [self.apple_sprites,self.groups[0]],
 
                z = LAYERS['fruit'])
 
 
    def damage(self):
      #生命值减一

      self.health -= 1

      #看看生命值是否小于0了,如果小于0就把该改的东西都改一下就行可

      if self.health <= 0:

         if self.alive:

            Particle(self.rect.topleft, self.image, self.groups[0], LAYERS['fruit'], 300)

         self.image = self.stump_surf

         self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

         self.hitbox = self.rect.copy().inflate(-10,-self.rect.height * 0.6)

         self.player_add('wood')

         self.alive = False


      #如果树上还有苹果，随机选一个去除

      if len(self.apple_sprites.sprites()) > 0:

         random_apple = choice(self.apple_sprites.sprites())

         Particle(

            pos=random_apple.rect.topleft,

            surf=random_apple.image,

            groups=self.groups[0],

            z=LAYERS['fruit'],

            )

         self.player_add('apple')

         random_apple.kill()#Sprite.kill()就是将该精灵删除