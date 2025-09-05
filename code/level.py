import pygame
 
from settings import *
 
from player import Player
 
from overlay import Overlay
 
from sprites import *
 
from pytmx.util_pygame import load_pygame
 
from support import *
 
from transition import Transition
 
from soil import SoilLayer
 
from sky import Rain,Sky
 
from menu import Menu
 

overlay_show = False
times_show = False
shop_show = False
tree_nums = 5

class Level():
 
    def __init__(self):
 
        #得到屏幕的画面，得到的这个画面与main.py中的screen相同
        
        self.display_surface = pygame.display.get_surface()
        #创建精灵组
        self.all_sprites = None
        self.all_sprites = CameraGroup()
 
        #具有碰撞箱的精灵组
        self.collision_sprites = None
        self.collision_sprites = pygame.sprite.Group()
 
        #树木精灵组
        self.tree_sprites = None
        self.tree_sprites = pygame.sprite.Group()
 
        #特殊区域精灵组
        self.interaction_sprites = None
        self.interaction_sprites = pygame.sprite.Group()
        self.player_exist = False
        self.player = None
        #调用setup方法
        #土地管理类
        self.soil_layer = None
        self.soil_layer = SoilLayer(self.all_sprites,self.collision_sprites)
        self.setup(obj={})
    
 
    def setup(self,obj):
        player_show = False
        bg_show = False
        scene_show = False
        house_show = False
        global tree_nums
        if obj:
            if obj['name'] == 'set_player':
                if obj['undo'] == True:
                    player_show = False
                    obj['undo'] = False
                else:
                    player_show = True
            if obj["name"] == "set_bg":
                
                if obj['undo'] == True:
                    bg_show = False
                    obj['undo'] = False
                else:
                    bg_show = True
            if obj["name"] == "set_scene":
                if obj['undo'] == True:
                    scene_show = False
                    obj['undo'] = False
                else:
                    scene_show = True

            # if obj['name'] == 'set_axe':
            #     tree_nums = obj['arguments']['times']

            if obj["name"] == "set_house":
                if obj['undo'] == True:
                    house_show = False
                    obj['undo'] = False
                else:
                    house_show = True

        # 载入.tmx文件
 
        tmx_data = load_pygame('../data/map.tmx')
 
        # # #绘制房子与栅栏，他们都属于Generic类
        if house_show:
            for layer in ['HouseFloor', 'HouseFurnitureBottom']:
    
                for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
    
                    Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
    
            for layer in ['HouseWalls', 'HouseFurnitureTop','Fence']:
    
                for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
    
                    Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])
            house_show = False
 
        
            
        # #水流
        if scene_show :

            water_frames = import_folder('../graphics/water')
    
            for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
    
                Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
    

            #树木
    
            for obj in tmx_data.get_layer_by_name('Trees'):
                
                Tree(
    
                    pos=(obj.x, obj.y),
    
                    surf=obj.image,
    
                    groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
    
                    name=obj.name,
    
                    player_add=self.player_add,

                    nums=tree_nums
                    
                    )
    
            #野花
    
            for obj in tmx_data.get_layer_by_name('Decoration'):
    
                WildFlower((obj.x, obj.y), obj.image,[self.all_sprites, self.collision_sprites])
    
    
            #空气墙
    
            for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
    
                Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)
            scene_show = False

        
        
        for obj in tmx_data.get_layer_by_name('Player'):

            if obj.name == 'Start':
                if not self.player_exist :
                    self.player = Player(

                    pos=(obj.x, obj.y),

                        group=self.all_sprites if player_show else "",

                        collision_sprites=self.collision_sprites ,

                        tree_sprites=self.tree_sprites ,

                        interaction = self.interaction_sprites ,

                        soil_layer = self.soil_layer ,

                        toggle_shop = self.toggle_shop )
                
                if  player_show  :
                    self.player_exist = True
                    player_show = False
            if obj.name == 'Bed':

                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)


            if obj.name == 'Trader':

                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
    
        if bg_show:
            Generic(
    
                pos = (0,0),
                
                surf = pygame.image.load("../graphics/world/ground.png").convert_alpha(),
    
                groups = self.all_sprites,
    
                z = LAYERS['ground']
    
            )
        #创建工具和种子显示图层
 
        self.overlay = Overlay(self.player)
 
        #创建transition对象
 
        self.transition = Transition(self.reset,self.player)
 
 
        # #实例化Rain对象
 
        self.rain = Rain(self.all_sprites)
 
        # 一个bool值，表示是否正在下雨，有1/10的概率为true

        self.raining = randint(0,10) > 20

        self.soil_layer.raining = self.raining
 
        #实例化天空对象
 
        self.sky = Sky()
 
 
        #交易
 
        self.shop_active = False
 
        self.menu = Menu(self.player,self.toggle_shop)
 
    def run(self,dt,obj):
        global overlay_show 
        global times_show
        global shop_show
        if obj :
            if obj['name'] == 'set_tools':
                if obj['undo'] == True:
                    overlay_show = False
                    obj['undo'] = False
                else:
                    overlay_show = True
            if obj['name'] == 'set_times':
                if obj['undo'] == True:
                    times_show = False
                    obj['undo'] = False
                else:
                    times_show = True
            if obj['name'] == 'set_shop':
                if obj['undo'] == True:
                    shop_show = False
                    obj['undo'] = False
                else:
                    shop_show = True
            
            if obj['status'] == True or obj['undo']:
                self.setup(obj)
                obj['status'] = False

        #窗口的背景设为黑色

        self.display_surface.fill('black')
 
        #调用精灵组的draw方法
 
        self.all_sprites.custom_draw(self.player)
 
        #如果正在打开商店，就执行相应的函数
        
        if self.shop_active:
            
            self.menu.update()

        else: #并且我们希望打开商店的时候，精灵组的其他精灵停止一切动作，也就是update

            #调用精灵组的update方法

            self.all_sprites.update(dt,obj)

            #收获植物

            self.plant_collision()
    
        if overlay_show:

            self.overlay.display()
 
 
        #如果在睡觉，执行相应的函数
 
        if self.player.sleep:
 
            self.transition.play()
 
 
        #如果在下雨，就生成雨滴，但是正在打开商店，就不要生成雨滴了，因为雨滴会覆盖到商店菜单上
 
        if self.raining and not self.shop_active:
 
            self.rain.update()
 
 
        # #天色变暗
        if times_show:
            self.sky.display(dt)
 
 
        #print(self.shop_active)
 
 
 
    def player_add(self, item):
 
        #item是一个str类型的数据，代表要对哪一种物品加一
 
        self.player.item_inventory[item] += 1
 
 
    def toggle_shop(self):
 
 
        self.shop_active = not self.shop_active
 
 
    def reset(self):
 
        #更新植物状态
 
        self.soil_layer.update_plants()
 
 
        # 清除农田里的水渍
 
        self.soil_layer.remove_water()
 
 
        #每天重新随机一下是否要下雨
 
        self.raining = randint(0, 10) > 20
 
        self.soil_layer.raining = self.raining
 
        #如果新的一天下雨了，就自动灌溉所有被开垦过的土地
 
        if self.raining:
 
            self.soil_layer.water_all()
 
 
        #苹果重新长在树上
 
        for tree in self.tree_sprites.sprites():
 
            for apple in tree.apple_sprites.sprites():
 
                apple.kill()
 
            tree.create_fruit()
 
 
        #天色重新变量
 
        self.sky.start_color = [255, 255, 255]
 
 
    def plant_collision(self):
 
        #如果plant_sprite这个精灵组不为空
 
        if self.soil_layer.plant_sprites:
 
            #遍历精灵组中的所有精灵
 
            for plant in self.soil_layer.plant_sprites.sprites():
 
                #如果作物成熟了并且与玩家发生了碰撞
 
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
 
                    #背包增加相应的作物
 
                    self.player_add(plant.plant_type)
 
                    #消除植物
 
                    plant.kill()
 
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')
 
                    #绘制粒子效果
 
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, z=LAYERS['main'])
 
class CameraGroup(pygame.sprite.Group):
 
    def __init__(self):
 
        super().__init__()
 
        #获取窗口
 
        self.display_surface = pygame.display.get_surface()
 
        #这是一个偏移量，代表的是玩家的实际位置与屏幕中间的矢量
 
        self.offset = pygame.math.Vector2()
 
    def custom_draw(self,player):
        
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
 
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
 
 
        for layer in LAYERS.values():#按照z轴从小到达绘制
 
            for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
 
                if sprite.z == layer:#如果该精灵的z值等于当前要绘制的z值，才绘制
 
                    offset_rect = sprite.rect.copy()
 
                    offset_rect.center -= self.offset
 
                    #if sprite == player:
 
                        #print("player.rect.center为：（" +
 
                             # str(player.rect.centerx)+"，" + str(player.rect.centery)+"）")
 
                        #print("offset_rect为：（" + str(offset_rect.x)
 
                             # +"，" +str(offset_rect.y)+"）")
 
                    self.display_surface.blit(sprite.image,offset_rect)