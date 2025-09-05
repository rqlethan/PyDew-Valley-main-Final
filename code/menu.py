import pygame
 
from settings import *
 
from timer import Timer
 
 
class Menu:
 
    def __init__(self, player, toggle_menu):
 
        #设置player
 
        self.player = player
 
        #设置关闭菜单的函数，实际上传进来的是level.py里面的toggle_shop函数
 
        self.toggle_menu = toggle_menu
 
        #获取游戏窗口
 
        self.display_surface = pygame.display.get_surface()
 
        #设置字体
 
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
 
 
        #菜单设置
 
        self.width = 400#菜单宽度
 
        self.space = 10#菜单的space
 
        self.padding = 8#菜单的padding
 
 
        #文字列表，就是商店都卖什么，把卖得东西的名称放到一个列表里
 
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
 
        #这些东西前四个是出售的，后两个是收购的，所以sell_border是一个分界的下标，如果下标小于等于sell_border就是出售，反之是收购
 
        self.sell_border = len(self.player.item_inventory) - 1
 
        #执行setup函数，把文字都渲染出来，并且计算一下总共需要多高的菜单
 
        self.setup()
 
 
        #当前正在选择第几号商品
 
        self.index = 0
 
        #200ms计时器
 
        self.timer = Timer(200)
 
 
 
    #将文字渲染，计算整体菜单的位置
 
    def setup(self):
 
 
        #文字列表，options是存放str的列表，而text_surfs是让这些str经过Font的渲染之后，生成的可以显示在屏幕上的文字的列表
 
        self.text_surfs = []
 
        #菜单的高度
 
        self.total_height = 0
 
 
        for item in self.options:
 
            #render的参数分别为：需要渲染的文字，是否抗锯齿，文字的颜色
 
            text_surf = self.font.render(item, False, 'Black')
 
            #把渲染好的文字加到列表中
 
            self.text_surfs.append(text_surf)
 
            #增加文本框的padding，一个文本框在竖直方向上有上下两个padding，所以padding要乘二
 
            self.total_height += text_surf.get_height() + (self.padding * 2)
 
 
        #最后别忘了加上space，每两个文本框之间有一个space，所以space的数目是文本框数目减一
 
        self.total_height += (len(self.text_surfs) - 1) * self.space
 
        #设置菜单的放置位置
 
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
 
        #把菜单的放置位置封装成一个rect数据类型
 
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)
 
 
        #渲染"buy"
 
        self.buy_text = self.font.render('buy', False, 'Black')
 
        #渲染"sell"
 
        self.sell_text = self.font.render('sell', False, 'Black')
 
 
    #显示玩家的金币余额
 
    def display_money(self):
 
        text_surf = self.font.render(f'${self.player.money}', False, 'Black')
 
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
 
        #在文字的外面扩张10像素，来当背景，第四个参数为边框的宽度，这里我们不给背景设置边框
 
        #第五个参数为半径，如果为0，绘制出来的就是纯正方形，半径越大越圆
 
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 4)
 
        self.display_surface.blit(text_surf, text_rect)
 
 
    #接收键盘事件
 
    def input(self):
 
        keys = pygame.key.get_pressed()
 
 
        #因为input在update函数中被调用了，所以timer也可以在这里更新，当然也可以把下面这一行写到update函数中
 
        self.timer.update()
 
        #按下ESC，退出商店
 
        if keys[pygame.K_ESCAPE]:
 
            self.toggle_menu()
 
        if not self.timer.active:
 
            #按上选择上一个商品
 
            if keys[pygame.K_UP]:
 
                self.index -= 1
 
                self.timer.activate()
 
            #按下选择下一个商品
 
            if keys[pygame.K_DOWN]:
 
                self.index += 1
 
                self.timer.activate()
 
 
            #按下空格，出售或者购买
 
            if keys[pygame.K_SPACE]:
 
                self.timer.activate()
 
                #根据下标index获取当前选择的商品的名称
 
                current_item = self.options[self.index]
 
                #如果下标小于等于sell_border，就是出售商品
 
                if self.index <= self.sell_border:
 
                    #先看看背包里有没有剩余
 
                    if self.player.item_inventory[current_item] > 0:
 
                        #背包中相应的物品减一
 
                        self.player.item_inventory[current_item] -= 1
 
                        #钱数相应的增加，其中SALE_PRICES是settings.py里面的常量
 
                        self.player.money += SALE_PRICES[current_item]
 
                #否则就是购买
 
                else:
 
                    #获取单价
 
                    seed_price = PURCHASE_PRICES[current_item]
 
                    #先判断能否买得起
 
                    if self.player.money >= seed_price:
 
                        #玩家背包内相应物品数量加一
 
                        self.player.seed_inventory[current_item] += 1
 
                        #玩家扣钱
 
                        self.player.money -= seed_price
 
 
 
 
        #让index值保持在0到5之间
 
        if self.index < 0:
 
            self.index = len(self.options) - 1
 
        if self.index > len(self.options) - 1:
 
            self.index = 0
 
 
    def show_entry(self, text_surf, amount, top,selected):
 
        #参数：text_surf为文本，amount为玩家背包中的库存，top为单个的文本放置的位置，为顶端的坐标
 
        # 绘制白色的文本框背景
 
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
 
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)
 
 
        # 把文本绘制出来
 
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
 
        self.display_surface.blit(text_surf, text_rect)
 
 
        # 把玩家背包中的库存绘制出来
 
        amount_surf = self.font.render(str(amount), False, 'Black')
 
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
 
        self.display_surface.blit(amount_surf, amount_rect)
 
 
        if selected:
 
            #如果是被选中的一行，就给他绘制黑色的边框表示选中
 
            pygame.draw.rect(self.display_surface,'black',bg_rect,4,4)
 
            #显示是收购还是出售
 
            if self.index <= self.sell_border:
 
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
 
                self.display_surface.blit(self.sell_text, pos_rect)
 
            else:
 
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
 
                self.display_surface.blit(self.buy_text, pos_rect)
 
 
 
    def update(self):
 
        self.input()
 
        self.display_money()
 
        for text_index, text_surf in enumerate(self.text_surfs):
 
            #分别计算需要放置的坐标
 
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
 
            #玩家背包中的库存
 
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
 
            amount = amount_list[text_index]
 
            #调用show_entry函数把它们都绘制出来
 
            self.show_entry(text_surf, amount, top,self.index == text_index)