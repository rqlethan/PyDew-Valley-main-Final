import copy
import pygame, sys
import json
import requests
from settings import *
from level import Level
import tkinter as tk
from ChatInterface import ChatInterface


input_show = False
display_text = True
function_name = ""
loop_completed = False
loop_completed_list = False
function_name_list = []
class Game:
 
    def __init__(self):
 
        #初始化
 
        pygame.init()
 
        #设置屏幕
 
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
 
        #设置标题
 
        pygame.display.set_caption('星露谷风(按TAB唤起AI助手)')
 
        #创建时钟，为以后得到dt使用
 
        self.clock = pygame.time.Clock()
 
        #创建关卡对象Level,该类在level.py文件中
 
        self.level = Level()
        
    def run(self):
        obj = {
            "name":"",
            'arguments':{},
            'status':False,
            "undo":False
        }
        global input_show
        global display_text
        global loop_completed
        global function_name 
        global commnd_list
        global undo_commnd
        global loop_completed_list
        global function_name_list
        save_obj = []
         # 读取JSON文件
        with open('Archive.json', 'r') as f:
            object_list = json.load(f)
            # json.dump([], f, indent=4)
            if len(object_list) >0:
                save_obj = copy.deepcopy(object_list)
        self.screen.fill((0, 0, 0))  # 使用黑色填充窗口背景
        while True:
            #按键检测
 
            for event in pygame.event.get():
 
                """如果按下的是右上角的红叉，就退出程序"""
                if event.type == pygame.QUIT:
 
                    #退出pygame
                    self.tk.destroy()
                    pygame.quit()
                    #退出python程序，不捕获异常,不加上这一句也能退出，但是会在中断报错
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        # self.tk = init_tk()
                        root = tk.Tk()
                        self.chat_interface = ChatInterface(root)
                        self.tk = self.chat_interface.root
                        print(function_name)
                        input_show = True
                        # display_text = True

            if input_show:
                function_name = self.chat_interface.function_name
                commnd_list = self.chat_interface.commnd_list
                undo_commnd = self.chat_interface.undo_commnd
                function_name_list = self.chat_interface.function_name_list
                loop_completed_list = self.chat_interface.loop_completed_list
                if undo_commnd:
                    self.level = None
                    self.player = None
                    loop_completed = False
                    loop_completed_list = False
                    save_obj = []
                    with open('Archive.json', 'r') as f:
                        object_list = json.load(f)
                        # json.dump([], f, indent=4)
                        if len(object_list) >0:
                            save_obj = copy.deepcopy(object_list)
                    self.level = Level()
                    self.level.__init__()
                    self.chat_interface.undo_commnd = False


           
            # elif function_name :
            #     if commnd_list[function_name]['status']:
                    
            #         if function_name == 'set_window':
            #             width_now=int(json.loads((commnd_list[function_name]['arguments']))['width'])
            #             height_now=int(json.loads((commnd_list[function_name]['arguments']))['height'])
            #             self.screen = pygame.display.set_mode((width_now, height_now))
            #             commnd_list[function_name]['status'] = False
            #         else:
            #             commnd_list[function_name]['arguments'] = json.loads(commnd_list[function_name]['arguments'])
            #             obj = commnd_list[function_name]

            dt = self.clock.tick() / 1000
            if not loop_completed and len(save_obj) >0:
                for item in save_obj:
                    temp= json.loads(item['arguments'])
                    item['arguments'] = temp
                    item['status'] = True
                    item['undo'] = False
                    self.level.run(dt,item)
                    pygame.display.update()
                else:
                    obj = item
                    loop_completed = True

            #代表的是一帧(一次循环)所花费的事件，单位为秒
            # if not display_text:
            if not loop_completed_list and len(function_name_list) > 0:
                for item in function_name_list:
                    if commnd_list[item]['status']:
                        if item == 'set_window':
                            width_now=int(json.loads((commnd_list[item]['arguments']))['width'])
                            height_now=int(json.loads((commnd_list[item]['arguments']))['height'])
                            self.screen = pygame.display.set_mode((width_now, height_now))
                            commnd_list[item]['status'] = False
                        else:
                            commnd_list[item]['arguments'] = json.loads(commnd_list[item]['arguments'])
                            obj = commnd_list[item]
                        self.level.run(dt,obj)
                    else:
                        self.chat_interface.function_name_list = []
                        loop_completed_list = True  

            self.level.run(dt,obj)

            #更新画面，一定要写在while循环的最后
            if input_show:
                self.tk.update()
            pygame.display.update()
 
 
 
if __name__ == '__main__':
    
    game = Game()
 
    game.run()
    
