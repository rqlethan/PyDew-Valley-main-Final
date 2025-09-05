import pygame
 
from settings import *
 
from support import *
 
from timer import Timer

import copy
 
player_up = ""
player_down = ""
player_left = ""
player_right = ""
player_tool_change = ""
player_seed_change = ""
player_use_tool = ""
player_sleep = ""
player_seed = ""
player_shop = ""
status_done = False
plow_status_done =False
axe_status_done = False
water_status_done = False
sleep_status_done = False
seed_status_done = False
shop_status_done = False
player_action = False
class Player(pygame.sprite.Sprite):
    

    def __init__(self,pos,group,collision_sprites,tree_sprites,interaction,soil_layer,toggle_shop):
        # global player_up 
        # global player_down 
        # global player_left 
        # global player_right
        # global player_tool_change
        # global player_seed_change 
        # global player_use_tool
        # global status_done
        # global plow_status_done
        # global axe_status_done
        # global water_status_done
        # global player_sleep
        # global player_seed
        # global sleep_status_done
        # global seed_status_done
        # global shop_status_done
        # global player_shop
        # global player_action

        # player_up = ""
        # player_down = ""
        # player_left = ""
        # player_right = ""
        # player_tool_change = ""
        # player_seed_change = ""
        # player_use_tool = ""
        # player_sleep = ""
        # player_seed = ""
        # player_shop = ""
        # status_done = False
        # plow_status_done =False
        # axe_status_done = False
        # water_status_done = False
        # sleep_status_done = False
        # seed_status_done = False
        # shop_status_done = False
        # player_action = False
        #这个参数可以传一个精灵组，这样就会自动把该精灵加入到该精灵组中
 
        #也可以为空，这样需要在外面手动调用精灵组的add函数来将这个精灵加入到精灵组中
 
        super().__init__(group)
 
 
        self.import_assets()
 
        self.status = 'down_idle'
 
        self.frame_index = 0
 
 
        #这里的变量名一定要叫image，因为这是它父类Sprite规定的
 
        self.image = self.animations[self.status][self.frame_index]
 
 
 
        #这个get_rect()也是父类中设置的方法
 
        #返回值是有很多，大概有x,y,centerx,centery,center,width,height这几类
 
        #大概就是image的x坐标，y坐标，中心的x坐标，中心的y坐标，中心点的坐标，宽度，高度等
 
        #参数可以不填，那么位置就默认是(0,0)，也可以填一个列表，比如(100,100)，那么初始的位置就是(100,100)
 
        #也可以是center = 一个坐标，这表示设置该图像的中心在这个坐标上
 
        #同样的这里的变量名也一定要叫rect，这是父类规定的
 
        self.rect = self.image.get_rect(center = pos)
 
 
        #z轴
 
        self.z = LAYERS['main']
 
 
        #创建一个二维的向量，参数不填默认是(0,0)
 
        self.direction = pygame.math.Vector2()#速度的方向
 
        self.pos = pygame.math.Vector2(self.rect.center)#位置
 
        self.speed = 200#速度
 
 
        #碰撞箱
 
        self.hitbox = self.rect.copy().inflate((-126,-70))
 
        self.collision_sprites = collision_sprites
 
 
        self.timers = {
            
            'tool use':Timer(350,self.use_tool),

            'tool use plow':Timer(350,self.use_tool_plow),

            'tool use axe':Timer(350,self.use_tool_axe),

            'tool use water':Timer(350,self.use_tool_water),
 
            'tool switch': Timer(200),
 
            'seed use': Timer(350, self.use_seed),
 
            'seed switch': Timer(200),
 
        }
 
 
        self.tools = ['hoe', 'axe', 'water']
 
        self.tool_index = 0
 
        self.selected_tool = self.tools[self.tool_index]
 
 
        self.seeds = ['corn', 'tomato']
 
        self.seed_index = 0
 
        self.selected_seed = self.seeds[self.seed_index]
 
 
        #玩家的农作物背包
 
        self.item_inventory = {
 
            'wood': 20,
 
            'apple': 20,
 
            'corn': 20,
 
            'tomato': 20
 
        }
 
        #玩家的种子背包
 
        self.seed_inventory = {
 
            'corn': 5,
 
            'tomato': 5
 
        }
 
        # 玩家的金币
 
        self.money = 200
 
        #接收树木精灵组
 
        self.tree_sprites = tree_sprites
 
        #接收特殊区域精灵组
 
        self.interaction = interaction
 
        #是否在睡觉
 
        self.sleep = False
 
 
        #泥土管理
 
        self.soil_layer = soil_layer
 
 
        #打开商店
 
        self.toggle_shop = toggle_shop
 
 
    def use_tool_plow(self):
        if self.selected_tool == 'hoe' :
           
            self.soil_layer.get_hit(self.target_pos)

    def use_tool_axe(self):
        if self.selected_tool == 'axe':
 
            for tree in self.tree_sprites.sprites():
 
                if tree.rect.collidepoint(self.target_pos):
 
                    tree.damage()

    def use_tool_water(self):
        if self.selected_tool == 'water':
 
            self.soil_layer.water(self.target_pos)

    def use_tool(self):
        return None
 
    def get_target_pos(self):
 
        # 获取工具的作用区域坐标
 
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
 
 
    def use_seed(self):
 
        #如果背包里还有种子才能种
 
        if self.seed_inventory[self.selected_seed] > 0:
 
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
 
            #种子数量减一
 
            self.seed_inventory[self.selected_seed] -= 1
 
    def import_assets(self):
 
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
 
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
 
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
 
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
 
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}
 
 
        for animation in self.animations.keys():
 
            full_path = '../graphics/character/' + animation
 
            self.animations[animation] = import_folder(full_path)
 
 
    def animate(self, dt):
 
 
        # 4 是比较合适的数字
 
        # 数字 决定做动作的快慢
 
        # 做一个动作需要 1/4秒
 
        # fream_index += dt 的话，要经过1s，才能变成下一个整数，做下一个动作
 
        # fream_index += 4*dt，那么增加的速度就快了四倍，经过1/4秒就能做下一个动作了
 
        self.frame_index += 4 * dt
 
        # print(self.frame_index)
 
        if self.frame_index >= len(self.animations[self.status]):
 
            self.frame_index = 0
 
 
        self.image = self.animations[self.status][int(self.frame_index)]
 
 
    def input(self,obj):
        
        global player_up 
        global player_down 
        global player_left 
        global player_right
        global player_tool_change
        global player_seed_change 
        global player_use_tool
        global status_done
        global plow_status_done
        global axe_status_done
        global water_status_done
        global player_sleep
        global player_seed
        global sleep_status_done
        global seed_status_done
        global shop_status_done
        global player_shop
        global player_action

        if 'up' in obj['arguments'] :
            player_up = copy.deepcopy(key_mapping.get(obj['arguments']['up']) )
            player_down = copy.deepcopy(key_mapping.get(obj['arguments']['down']))
            player_left = copy.deepcopy(key_mapping.get(obj['arguments']['left']))
            player_right = copy.deepcopy(key_mapping.get(obj['arguments']['right']))

        if 'active' in obj['arguments'] :
            player_tool_change = copy.deepcopy(key_mapping.get(obj['arguments']['tools_change']))
            player_seed_change = copy.deepcopy(key_mapping.get(obj['arguments']['seeds_change']))
            player_use_tool = copy.deepcopy(key_mapping.get(obj['arguments']['active']))

        if 'sleep' in obj['arguments'] :
            player_sleep = copy.deepcopy(key_mapping.get(obj['arguments']['sleep']))
            
        if 'seed' in obj['arguments'] :
            player_seed = copy.deepcopy(key_mapping.get(obj['arguments']['seed']))
        if 'shop' in obj['arguments'] :
            player_shop = copy.deepcopy(key_mapping.get(obj['arguments']['shop']))
            
        
        keys = pygame.key.get_pressed()
 
        #已经在使用工具的时候，或者正在睡觉的时候，停止对按键的检测
        if obj['name'] == 'set_player_action':
            player_action = True
        
        if not self.timers['tool use'].active and not self.timers['tool use plow'].active and not self.timers['tool use axe'].active and not self.timers['tool use water'].active and not self.sleep and player_action:
            
            if keys[player_up]:
                
                self.direction.y = -1
 
                self.status = 'up'
 
            elif keys[player_down]:
 
                self.direction.y = 1
 
                self.status = 'down'
 
            else:
 
                self.direction.y = 0#不要忘记加上这一句，不然按下键盘后再松开也不会停
 
 
            if keys[player_right]:
 
                self.direction.x = 1
 
                self.status = 'right'
 
            elif keys[player_left]:
 
                self.direction.x = -1
 
                self.status = 'left'
 
            else:
 
                self.direction.x = 0

            if obj['name'] == 'set_plow':
                plow_status_done = True
            if obj['name'] == 'set_axe':
                axe_status_done = True
            if obj['name'] == 'set_water':
                water_status_done = True
            if obj['name'] == 'set_seeds':
                seed_status_done = True
            if obj['name'] == 'set_sleep':
                sleep_status_done = True
            if obj['name'] == 'set_shop':
                shop_status_done = True
           
            if obj['name'] == "set_tools" or status_done:
                status_done = True
                
                if keys[player_use_tool]:

                    if obj['name'] == 'set_plow' or plow_status_done:
                        self.timers['tool use plow'].activate()
                        plow_status_done = True
                        
                    if obj['name'] == 'set_axe' or axe_status_done:
                        self.timers['tool use axe'].activate()
                        axe_status_done = True
                    if obj['name'] == 'set_water' or water_status_done:
                        self.timers['tool use water'].activate()
                        water_status_done = True

                    if not plow_status_done:
                       self.timers['tool use'].activate()

                    #实用工具的时候是不能移动的
    
                    self.direction = pygame.math.Vector2()
    
                    #要从第一张图片开始绘制
    
                    self.frame_index = 0
                    
    
                #按下左边的shift键更换工具
    
                if keys[player_tool_change] and not self.timers['tool switch'].active:
    
                    self.timers['tool switch'].activate()
    
                    self.tool_index += 1
    
                    self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
    
                    self.selected_tool = self.tools[self.tool_index]
    
    
                #按下右边的ctrl键，使用种子
                if obj['name'] == 'set_seeds' or seed_status_done:
                    if keys[player_seed]:
                        seed_status_done = True
                        self.timers['seed use'].activate()
        
                        self.direction = pygame.math.Vector2()
        
                        self.frame_index = 0
    
    
                #按下右边的shift键，切换种子
    
                if keys[player_seed_change] and not self.timers['seed switch'].active:
    
                    self.timers['seed switch'].activate()
    
                    self.seed_index += 1
    
                    self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
    
                    self.selected_seed = self.seeds[self.seed_index]
    
                #交易商店
                if obj['name'] == 'set_shop' or shop_status_done:
                    if keys[player_shop]:
                        shop_status_done = True
                        #返回值是与第一个参数的精灵发生碰撞的精灵
        
                        collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
        
                        #参数False表示，如果发生了重叠，不会kill掉第二个参数的精灵，如果是True，就Kill掉第二个参数的精灵
        
                        if collided_interaction_sprite:
        
                            #交易的部分以后再说
        
                            if collided_interaction_sprite[0].name == 'Trader' :
        
                                self.toggle_shop()
        

                #进行睡觉
                if obj['name'] == 'set_sleep' or sleep_status_done:
                    if keys[player_sleep]:
                        sleep_status_done = True
                        #返回值是与第一个参数的精灵发生碰撞的精灵
        
                        collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
        
                        #参数False表示，如果发生了重叠，不会kill掉第二个参数的精灵，如果是True，就Kill掉第二个参数的精灵
        
                        if collided_interaction_sprite:
        
                            #为了视觉效果设置成面朝床边
    
                            self.status = 'left_idle'
    
                            self.sleep = True

 
    def get_status(self):
 
 
        # idle
 
        if self.direction.magnitude() == 0:
 
            # self.status += '_idle'
 
            # 上面这种方法不可取因为每一帧都会在字符串后面加上一个_idel
 
            # 所以status会变成 xxx_idle_idle_idle
 
            # 实际上当出现两个_idle的时候就已经报错了
 
            # 下面这种方法
 
            # split('_')是把一个字符串 以 '_' 为分节符分开
 
            # 他返回的是一个列表
 
            # 比如 a_b_c_d
 
            # 返回的就是[a,b,c,d]
 
            # 所以下面的【0】获取的就是_之前的内容
 
            self.status = self.status.split('_')[0] + '_idle'
 
 
        if self.timers['tool use'].active or self.timers['tool use water'].active or self.timers['tool use plow'].active or self.timers['tool use axe'].active:
 
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
 
 
    def update_timers(self):
        
        for timer in self.timers.values():
 
            timer.update()
 
 
 
    def collision(self,direction):
 
        # 遍历碰撞箱精灵组的所有精灵
 
        for sprite in self.collision_sprites.sprites():
 
            # 如果该精灵有一个叫hitbox的属性
 
            #实际上collision_sprites精灵组内的所有精灵都应该有hitbox这个属性，这句话属实多余
 
            if hasattr(sprite,'hitbox'):
 
                #如果该精灵的hitbox与玩家的hitbox有重叠
 
                if sprite.hitbox.colliderect(self.hitbox):
 
                    #如果此时正在水平方向移动
 
                    if direction == 'horizontal':
 
                        if self.direction.x > 0:  #玩家正在向右移动
 
                            self.hitbox.right = sprite.hitbox.left
 
                        if self.direction.x < 0:  # 玩家正在向左移动
 
                            self.hitbox.left = sprite.hitbox.right
 
                        self.rect.centerx = self.hitbox.centerx
 
                        self.pos.x = self.hitbox.centerx
 
                    #如果此时正在竖直方向移动
 
                    if direction == 'vertical':
 
                        if self.direction.y > 0:  # 玩家正在向下移动
 
                            self.hitbox.bottom = sprite.hitbox.top
 
                        if self.direction.y < 0:  # 玩家正在向上移动
 
                            self.hitbox.top = sprite.hitbox.bottom
 
                        self.rect.centery = self.hitbox.centery
 
                        self.pos.y = self.hitbox.centery
 
 
 
    def move(self,dt):
 
        #向量归一化，比如一个n维向量为(x1,x2,x3...,xn)
 
        #那么向量归一化的操作就是等比例缩放x1到xn的大小让 根号下(x1的平方+x2的平方+...+xn的平方) 等于1
 
        #归一化的目的是如果同时按右键和上，那么direction就会变成(1,1)，他的速度向量就是一个大小为根2，方向右上的向量了
 
        #magnitude()返回的是一个float类型的数据，他的大小为根号下(x1的平方+x2的平方+...+xn的平方)
 
        if self.direction.magnitude() > 0:#这表示如果有按键按下，如果向量里面全是0，会使归一化中的数学计算出现错误
 
            self.direction = self.direction.normalize()
 
 
        #位移 = 方向 * 速度 * 变化的时间()
 
        #水平方向
 
        self.pos.x += self.direction.x * self.speed * dt
 
        self.hitbox.centerx = round(self.pos.x)
 
        self.rect.centerx = self.hitbox.centerx
 
        self.collision('horizontal')
 
 
        #竖直方向
 
        self.pos.y += self.direction.y * self.speed * dt
 
        self.hitbox.centery = round(self.pos.y)
 
        self.rect.centery = self.hitbox.centery
 
        self.collision('vertical')
 
 
    def update(self,dt,obj):
        
        self.input(obj)
 
        self.get_status()
 
        self.update_timers()
 
        self.get_target_pos()
 
 
        self.move(dt)
 
        self.animate(dt)

key_mapping = {
    # 数字 0-9
    'pygame.K_0': pygame.K_0,
    'pygame.K_1': pygame.K_1,
    'pygame.K_2': pygame.K_2,
    'pygame.K_3': pygame.K_3,
    'pygame.K_4': pygame.K_4,
    'pygame.K_5': pygame.K_5,
    'pygame.K_6': pygame.K_6,
    'pygame.K_7': pygame.K_7,
    'pygame.K_8': pygame.K_8,
    'pygame.K_9': pygame.K_9,
    # 字母 A-Z
    'pygame.K_a': pygame.K_a,
    'pygame.K_b': pygame.K_b,
    'pygame.K_c': pygame.K_c,
    'pygame.K_d': pygame.K_d,
    'pygame.K_e': pygame.K_e,
    'pygame.K_f': pygame.K_f,
    'pygame.K_g': pygame.K_g,
    'pygame.K_h': pygame.K_h,
    'pygame.K_i': pygame.K_i,
    'pygame.K_j': pygame.K_j,
    'pygame.K_k': pygame.K_k,
    'pygame.K_l': pygame.K_l,
    'pygame.K_m': pygame.K_m,
    'pygame.K_n': pygame.K_n,
    'pygame.K_o': pygame.K_o,
    'pygame.K_p': pygame.K_p,
    'pygame.K_q': pygame.K_q,
    'pygame.K_r': pygame.K_r,
    'pygame.K_s': pygame.K_s,
    'pygame.K_t': pygame.K_t,
    'pygame.K_u': pygame.K_u,
    'pygame.K_v': pygame.K_v,
    'pygame.K_w': pygame.K_w,
    'pygame.K_x': pygame.K_x,
    'pygame.K_y': pygame.K_y,
    'pygame.K_z': pygame.K_z,

    'pygame.K_UP': pygame.K_UP,
    'pygame.K_DOWN': pygame.K_DOWN,
    'pygame.K_LEFT': pygame.K_LEFT,
    'pygame.K_RIGHT': pygame.K_RIGHT,

    # 数字小键盘
    'pygame.K_KP0': pygame.K_KP0,
    'pygame.K_KP1': pygame.K_KP1,
    'pygame.K_KP2': pygame.K_KP2,
    'pygame.K_KP3': pygame.K_KP3,
    'pygame.K_KP4': pygame.K_KP4,
    'pygame.K_KP5': pygame.K_KP5,
    'pygame.K_KP6': pygame.K_KP6,
    'pygame.K_KP7': pygame.K_KP7,
    'pygame.K_KP8': pygame.K_KP8,
    'pygame.K_KP9': pygame.K_KP9,
    'pygame.K_KP_PERIOD': pygame.K_KP_PERIOD,
    'pygame.K_KP_DIVIDE': pygame.K_KP_DIVIDE,
    'pygame.K_KP_MULTIPLY': pygame.K_KP_MULTIPLY,
    'pygame.K_KP_MINUS': pygame.K_KP_MINUS,
    'pygame.K_KP_PLUS': pygame.K_KP_PLUS,
    'pygame.K_KP_ENTER': pygame.K_KP_ENTER,
    'pygame.K_KP_EQUALS': pygame.K_KP_EQUALS,
    # 修改键
    'pygame.K_LSHIFT': pygame.K_LSHIFT,
    'pygame.K_RSHIFT': pygame.K_RSHIFT,
    'pygame.K_LCTRL': pygame.K_LCTRL,
    'pygame.K_RCTRL': pygame.K_RCTRL,
    'pygame.K_LALT': pygame.K_LALT,
    'pygame.K_RALT': pygame.K_RALT,
    'pygame.K_LMETA': pygame.K_LMETA,
    'pygame.K_RMETA': pygame.K_RMETA,
    'pygame.K_LSUPER': pygame.K_LSUPER,
    'pygame.K_RSUPER': pygame.K_RSUPER,
    'pygame.K_MODE': pygame.K_MODE,
    'pygame.K_SPACE': pygame.K_SPACE,
    "pygame.K_RETURN":pygame.K_RETURN
}