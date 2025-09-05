import pygame
 
from settings import *
 
from pytmx.util_pygame import load_pygame
 
from support import *
 
from random import choice
 
 
#开垦过的土地
 
class SoilTile(pygame.sprite.Sprite):
 
    def __init__(self, pos, surf, groups):
 
       super().__init__(groups)
 
       self.image = surf
 
       self.rect = self.image.get_rect(topleft = pos)
 
       self.z = LAYERS['soil']
 
 
#浇过水的土地
 
class WaterTile(pygame.sprite.Sprite):
 
    def __init__(self, pos, surf, groups):
 
       super().__init__(groups)
 
       self.image = surf
 
       self.rect = self.image.get_rect(topleft = pos)
 
       self.z = LAYERS['soil water']
 
 
#植物
 
class Plant(pygame.sprite.Sprite):
 
    def __init__(self, plant_type, groups, soil, check_watered):
 
        super().__init__(groups)
 
 
        #种子的类型
 
        self.plant_type = plant_type
 
        #载入植物图片，里面存放的是植物不同年龄下的图片
 
        self.frames = import_folder(f'../graphics/fruit/{plant_type}')
 
        #种植该植物的那块土壤
 
        self.soil = soil
 
        #检查该土地是否浇水的函数
 
        self.check_watered = check_watered
 
 
        #植物的年龄，一开始是0，表示种子状态
 
        self.age = 0
 
        #植物的最大年龄
 
        #植物的最大年龄取决于我们准备了多少张不同年龄植物的图片，由于我们的年龄是从0开始计数的，所以还得减一
 
        self.max_age = len(self.frames) - 1
 
        #植物的生长速度
 
        self.grow_speed = GROW_SPEED[plant_type]
 
        #植物是否可以被收获了
 
        self.harvestable = False
 
 
        #设置植物的图片
 
        self.image = self.frames[self.age]
 
        #植物的坐标相对于土地的偏移量
 
        self.y_offset = -16 if plant_type == 'corn' else -8
 
        #植物的坐标
 
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
 
        #植物的图层
 
        self.z = LAYERS['ground plant']
 
 
    def grow(self):
        if self.check_watered(self.rect.center):
 
            self.age += self.grow_speed
 
            if int(self.age) > 0:
 
                self.z = LAYERS['main']
 
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)
 
            if self.age >= self.max_age:
 
                self.age = self.max_age
 
                self.harvestable = True
 
            self.image = self.frames[int(self.age)]
 
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
 
 
#管理所有土地的类
 
class SoilLayer:
 
    def __init__(self,all_sprites,collision_sprites):
 
        #all_sprites精灵组
 
        self.all_sprites = all_sprites
 
        #碰撞精灵组
 
        self.collision_sprites = collision_sprites
 
        #创建开垦过的土地精灵组
 
        self.soil_sprites = pygame.sprite.Group()
 
        #浇过水的土地精灵组
 
        self.water_sprites = pygame.sprite.Group()
 
        #植物精灵组
 
        self.plant_sprites = pygame.sprite.Group()
 
 
        # #导入开垦过的土地的图片
 
        self.soil_surf = pygame.image.load('../graphics/soil/o.png')
 
        #获取浇水图片，一共有三张
 
        self.water_surfs = import_folder('../graphics/soil_water')
 
 
        self.create_soil_grid()
 
        self.create_hit_rects()
 
 
    def create_soil_grid(self):
 
        #导入地图的图片
 
        ground = pygame.image.load('../graphics/world/ground.png')
 
        #地图的宽度，高度除以64，就是一共有多少块(64*64)的土地
 
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
 
        #创建一个三维列表，最一开始，所有土地的属性都是空的
 
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
 
        #如果是可以被耕种的土地块，就给他的列表添加一个标记'F'
 
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
 
            self.grid[y][x].append('F')
 
 
    def create_hit_rects(self):
 
        #列表里存放的是所有能被耕种的土地,数据类型是pygame里提供的Rect数据类型，包含了坐标和宽高
 
        self.hit_rects = []
 
        for index_row, row in enumerate(self.grid):
 
            for index_col, cell in enumerate(row):
 
                #如果是能被耕种的
 
                if 'F' in cell:
 
                    x = index_col * TILE_SIZE
 
                    y = index_row * TILE_SIZE
 
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
 
                    self.hit_rects.append(rect)
 
 
    def get_hit(self, point):
 
        #point是传入的参数，代表的是玩家挥舞的锄头的落点的坐标
 
        for rect in self.hit_rects:
 
            #如果该可耕种的土地块与玩家的锄头坐标发生了重叠，说明玩家锄的就是这块地，就给他的属性再加上一个标记'X'
 
            if rect.collidepoint(point):
 
                #相反，这里得把pygame的坐标系转换成tmx文件中的坐标系
 
                x = rect.x // TILE_SIZE
 
                y = rect.y // TILE_SIZE
 
 
                if 'F' in self.grid[y][x]:
 
                    self.grid[y][x].append('X')
 
                    SoilTile(
 
                        pos=(rect.x,rect.y),
 
                        surf=self.soil_surf,
 
                        groups=[self.all_sprites, self.soil_sprites])
 
                    if self.raining:
 
                        self.water(point)
 
                    #self.create_soil_tiles()
 
 
    def water(self, target_pos):
 
        for soil_sprite in self.soil_sprites.sprites():
 
            if soil_sprite.rect.collidepoint(target_pos):
 
                x = soil_sprite.rect.x // TILE_SIZE
 
                y = soil_sprite.rect.y // TILE_SIZE
 
                #给grid添加”W“标记
 
                self.grid[y][x].append('W')
 
 
                pos = soil_sprite.rect.topleft
 
                #随机选择三张之中的一张图片，来作为这个精灵的image
 
                surf = choice(self.water_surfs)
 
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])
 
 
    def remove_water(self):
 
        #删除所有的精灵
 
        for sprite in self.water_sprites.sprites():
 
            sprite.kill()
 
        #同时别忘了清理grid中的标记
 
        for row in self.grid:
 
            for cell in row:
 
                if 'W' in cell:
 
                    cell.remove('W')
 
 
    #给所有被开垦过的农田浇水
 
    def water_all(self):
 
        for index_row, row in enumerate(self.grid):
 
            for index_col, cell in enumerate(row):
 
                if 'X' in cell and 'W' not in cell:
 
                    cell.append('W')
 
                    x = index_col * TILE_SIZE
 
                    y = index_row * TILE_SIZE
 
                    WaterTile((x, y), choice(self.water_surfs), [self.all_sprites, self.water_sprites])
 
 
    #检擦某块土地是否浇水
 
    def check_watered(self, pos):
 
        x = pos[0] // TILE_SIZE
 
        y = pos[1] // TILE_SIZE
 
        cell = self.grid[y][x]
 
        is_watered = 'W' in cell
        
        return is_watered
 
 
    #种植植物
 
    def plant_seed(self, target_pos, seed):

        for soil_sprite in self.soil_sprites.sprites():
            
            if soil_sprite.rect.collidepoint(target_pos):
 
 
                x = soil_sprite.rect.x // TILE_SIZE
 
                y = soil_sprite.rect.y // TILE_SIZE
 
                #该土地并没有被种植植物
                
                if 'P' not in self.grid[y][x]:
 
                    self.grid[y][x].append('P')
                    
                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite,
 
                          self.check_watered)
 
 
    #更新植物的状态
 
    def update_plants(self):
        
        for plant in self.plant_sprites.sprites():
 
            plant.grow()
 
 
    """
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    SoilTile(
                        pos=(index_col * TILE_SIZE, index_row * TILE_SIZE),
                        surf=self.soil_surf,
                        groups=[self.all_sprites, self.soil_sprites])"""