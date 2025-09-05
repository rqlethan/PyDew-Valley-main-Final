# ChatInterface.py
import json
import os
import threading
import traceback
import tkinter as tk
import queue
from tkinter.font import Font
from pathlib import Path
from PIL import Image, ImageTk

# OpenAI client
from openai import OpenAI

# ---------- Tools (unchanged) ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "set_window",
            "description": "初始化一个用户指定分辨率的游戏窗口，确保它按比例正确显示并验证图像渲染无误",
            "parameters": {
                "type": "object",
                "properties": {
                    "width": {"type": "string", "description": "游戏窗口的宽度"},
                    "height": {"type": "string", "description": "游戏窗口的长度"},
                },
                "required": ["width","height"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_player",
            "description": "创建一个角色",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_player_action",
            "description": "赋予主角移动功能，可通过键盘自定义按键来输入控制主角的移动",
            "parameters": {
                "type": "object",
                "properties": {
                    "up":    {"type": "string", "description": "自定义移动按键的上,以pygame中键盘常量来表示,例如pygame.K_UP这样的格式"},
                    "down":  {"type": "string", "description": "自定义移动按键的下,以pygame中键盘常量来表示,例如pygame.K_DOWN这样的格式"},
                    "left":  {"type": "string", "description": "自定义移动按键的左,以pygame中键盘常量来表示,例如pygame.K_LEFT这样的格式"},
                    "right": {"type": "string", "description": "自定义移动按键的右,以pygame中键盘常量来表示,例如pygame.K_RIGHT这样的格式"},
                },
                "required": ["up","down","left","right"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_bg",
            "description": "给游戏绘制一个地图背景",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_house",
            "description": "给角色搭建一个房屋、栅栏或者生成一个住宿场所",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_scene",
            "description": "在地图中绘制水流、树木、花草等其他事物,并给地图上的东西设置碰撞盒，让主角无法从一些障碍物上走过",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_tools",
            "description": "为主角创建浇水、挖地、砍树的工具和动作，通过按下空格键进行工具的使用;同时可以创建工具和种子的切换功能。按键盘左边shift键，切换工具。按下键盘右边shift键，切换种子,如果用户的提问没有涉及到具体的自定义按键，则提醒他",
            "parameters": {
                "type": "object",
                "properties": {
                    "active":       {"type": "string", "description": "通过按下此按键来进行工具的使用,以pygame中键盘常量来表示,例如pygame.K_SPACE这样的格式"},
                    "tools_change": {"type": "string", "description": "通过按下此按键来进行工具的切换,以pygame中键盘常量来表示,例如pygame.K_LSHIFT这样的格式"},
                    "seeds_change": {"type": "string", "description": "通过按下此按键来进行种子的切换,以pygame中键盘常量来表示,例如pygame.K_RSHIFT这样的格式"},
                },
                "required": ["active","tools_change","seeds_change"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_plow",
            "description": "添加耕地功能。主角对着耕地的区域使用锄头，可以进行耕地操作",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_water",
            "description": "添加浇水功能。主角拿着水壶对着开垦过的土地使用，会获得水渍效果，并且睡一觉后，到了第二天，水渍会消失",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_axe",
            "description": "添加砍树功能,在树上随机生成苹果，在手持斧头并且面对树木的时候操作可以砍树，砍树可以砍掉苹果。砍5次后树会死亡，变成树桩",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_sleep",
            "description": "为游戏添加睡觉功能。玩家走到床边，按下回车键睡觉。此时屏幕渐渐变成纯黑色，再渐渐变亮。睡觉之后的一些东西会重置。如：树上的苹果会重新长出来，作物会成熟，天色变量",
            "parameters": {
                "type": "object",
                "properties": {
                    "sleep": {"type": "string", "description": "通过按下此按键来进行睡觉,以pygame中键盘常量来表示,例如pygame.K_RETURN这样的格式"},
                },
                "required": ["sleep"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_seeds",
            "description": "添加种植的功能。按下右边ctrl键实现作物种植。并且如果当天浇水了，作物会在第二天长大，直到成熟为止,加收获作物功能。当作物成熟后，主角与作物发生碰撞，会触发收获作物的效果，此时作物会消失，并且会有白色的例子效果，此时主角背包里会多出一份相应的作物",
            "parameters": {
                "type": "object",
                "properties": {
                    "seed": {"type": "string", "description": "通过按下此按键来实现作物种植,以pygame中键盘常量来表示,例如pygame.K_RCTRL这样的格式"},
                },
                "required": ["seed"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_shop",
            "description": "添加游戏交易商店功能。主角可以在NPC处按下回车键，出售农作物或者树木苹果来换取金币，金币可以用来购买种子",
            "parameters": {
                "type": "object",
                "properties": {
                    "shop": {"type": "string", "description": "通过按下此按键来实现出售农作物或者树木苹果来换取金币,以pygame中键盘常量来表示"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_times",
            "description": "添加时间流动效果。随着时间的推移，游戏中的天色会逐渐变暗。如果天黑了主角睡觉来到新的一天明天色会重新变亮",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

# ---------- Command-state dict (unchanged) ----------
commnd_list = {
    "set_window":      {"name":"set_window",      "status":False,"arguments":"","undo":False},
    "set_player":      {"name":"set_player",      "status":False,"arguments":"","undo":False},
    "set_player_action":{"name":"set_player_action","status":False,"arguments":"","undo":False},
    "set_bg":          {"name":"set_bg",          "status":False,"arguments":"","undo":False},
    "set_scene":       {"name":"set_scene",       "status":False,"arguments":"","undo":False},
    "set_house":       {"name":"set_house",       "status":False,"arguments":"","undo":False},
    "set_tools":       {"name":"set_tools",       "status":False,"arguments":"","undo":False},
    "set_plow":        {"name":"set_plow",        "status":False,"arguments":"","undo":False},
    "set_water":       {"name":"set_water",       "status":False,"arguments":"","undo":False},
    "set_axe":         {"name":"set_axe",         "status":False,"arguments":"","undo":False},
    "set_sleep":       {"name":"set_sleep",       "status":False,"arguments":"","undo":False},
    "set_seeds":       {"name":"set_seeds",       "status":False,"arguments":"","undo":False},
    "set_shop":        {"name":"set_shop",        "status":False,"arguments":"","undo":False},
    "set_times":       {"name":"set_times",       "status":False,"arguments":"","undo":False},
}

# ---------- OpenAI client wrapper ----------
class OpenAIClient:
    """Minimal OpenAI Chat Completions client (function calling)."""
    def __init__(self, model="gpt-4o-mini"):
        # Requires OPENAI_API_KEY in environment
        self.client = OpenAI()
        self.model = model

    def send(self, user_text, tools):
        sys_prompt = (
            "You are an in-game assistant for a Stardew-like game. "
            "When the user asks for an action, respond using a function tool call with valid JSON arguments "
            "matching the tool schema. If no function applies, reply in plain text."
        )
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": user_text},
            ],
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
        ).to_dict()

def parse_openai_response(resp_dict):
    """
    Returns (text, tool_calls) for OpenAI Chat Completions.
    tool_calls: list of {"function": {"name": str, "arguments": str}}
    """
    text, tool_calls = None, []
    try:
        choices = resp_dict.get("choices") or []
        if not choices:
            return None, []
        msg = choices[0].get("message") or {}
        c = msg.get("content")
        if isinstance(c, str) and c.strip():
            text = c
        tc = msg.get("tool_calls") or []
        for t in tc:
            fn = t.get("function") or {}
            name = fn.get("name")
            args = fn.get("arguments", "{}")  # JSON string
            if name:
                tool_calls.append({"function": {"name": name, "arguments": args}})
    except Exception:
        pass
    return text, tool_calls

# ---------- Chat UI ----------
class ChatInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("AI助手")

        # Thread-safe UI queue + poller (must schedule AFTER root is set)
        self.ui_queue = queue.Queue()
        self.root.after(50, self._drain_ui_queue)

        # Base path for assets (project root = parent of /code)
        BASE = Path(__file__).resolve().parent.parent

        # Load avatars with absolute paths (robust to working dir changes)
        self.user_avatar = ImageTk.PhotoImage(Image.open(BASE / "graphics" / "user.png").resize((30, 30)))
        self.bot_avatar  = ImageTk.PhotoImage(Image.open(BASE / "graphics" / "ai.png").resize((30, 30)))

        # Chat history
        self.chat_history = tk.Text(root, state='disabled', width=60, height=44, wrap=tk.WORD)
        self.chat_history.pack(padx=10, pady=10)

        # Text tags
        self.chat_history.tag_configure('left', justify='left', background='#FFFFFF')
        self.chat_history.tag_configure('right', justify='right', background='#89D961')
        self.chat_history.tag_configure('separator', background='white', relief='raised', foreground='#808080')

        # Input box
        self.entry_message = tk.Text(root, height=5, width=60)
        self.entry_message.pack(padx=10, pady=8)
        self.entry_message.bind("<Return>", self.on_enter_pressed)

        # State
        self.function_name = ""
        self.undo_commnd = False
        self.commnd_list = ""
        self.function_name_list = []
        self.loop_completed_list = False

        # Buttons
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.RIGHT, padx=5, pady=1)
        tk.Button(self.top_frame, text="clear All", command=self.on_button_click).pack(side=tk.RIGHT, padx=5, pady=4)
        tk.Button(self.top_frame, text="undo",      command=self.undo).pack(side=tk.RIGHT, padx=5, pady=4)
        tk.Button(self.top_frame, text="send",      command=self.on_send_button_clicked).pack(side=tk.RIGHT, padx=5, pady=4)

        # OpenAI client (model can be overridden via env)
        self.ai = OpenAIClient(model=os.environ.get("GAME_AI_MODEL", "gpt-4o-mini"))

        # Optional: warn if API key is missing
        if not os.environ.get("OPENAI_API_KEY"):
            self.display_message("未检测到 OPENAI_API_KEY，请先设置环境变量。", "", "")

    # Poll results produced by worker threads (runs on main Tk thread)
    def _drain_ui_queue(self):
        try:
            while True:
                fn, args = self.ui_queue.get_nowait()
                try:
                    fn(*args)
                except Exception:
                    pass
        except queue.Empty:
            pass
        try:
            self.root.after(50, self._drain_ui_queue)
        except tk.TclError:
            return  # window closed

    def undo(self):
        self.undo_commnd = True
        try:
            with open('Archive.json', 'r', encoding='utf-8') as f:
                object_list = json.load(f)
        except Exception:
            object_list = []

        try:
            for i, obj in enumerate(object_list):
                if obj.get('name') == self.function_name:
                    del object_list[i]
                    break
            with open('Archive.json', 'w', encoding='utf-8') as f:
                json.dump(object_list, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.display_message(f"撤销失败：{e}", "", "")

    def on_button_click(self):
        try:
            with open('Archive.json', 'w', encoding='utf-8') as file:
                file.write('[]')
            self.display_message("已清空所有记录。", "", "")
        except Exception as e:
            self.display_message(f"清空失败：{e}", "", "")

    def on_enter_pressed(self, event=None):
        message = self.entry_message.get(1.0, tk.END).strip()
        if not message:
            return "break"

        # Show user's text immediately
        self.display_message(message, "我", "")
        self.entry_message.delete(1.0, tk.END)

        def worker():
            try:
                resp = self.ai.send(message, tools)
                text, tool_calls = parse_openai_response(resp)

                function_name_list = []
                if tool_calls:
                    for call in tool_calls:
                        fn = call.get("function", {})
                        name = fn.get("name")
                        arguments = fn.get("arguments", "{}")  # JSON string
                        if not name:
                            continue

                        # Update Archive.json
                        try:
                            with open('Archive.json', 'r', encoding='utf-8') as f:
                                object_list = json.load(f)
                        except Exception:
                            object_list = []
                        object_list.append({"name": name, "arguments": arguments, "undo": False})
                        with open('Archive.json', 'w', encoding='utf-8') as f:
                            json.dump(object_list, f, indent=4, ensure_ascii=False)

                        # Flag command for the game loop
                        commnd_list[name]["status"] = True
                        commnd_list[name]["arguments"] = arguments
                        function_name_list.append(name)

                def finish_ui():
                    self.function_name = function_name_list[-1] if function_name_list else ""
                    self.function_name_list = function_name_list
                    self.loop_completed_list = False
                    self.commnd_list = commnd_list

                    if function_name_list:
                        desc = ""
                        for item in function_name_list:
                            for el in tools:
                                if el["function"]["name"] == item:
                                    desc += el["function"]["description"] + ";"
                        self.display_message("", "", desc)
                    elif text is not None:
                        self.display_message(text, "", "")
                    else:
                        self.display_message("（无文本或工具调用）", "", "")

                # enqueue UI update (no Tk calls from worker)
                self.ui_queue.put((finish_ui, ()))

            except Exception as e:
                # Friendly error in UI via queue
                err_msg = ""
                try:
                    from openai import RateLimitError
                    if isinstance(e, RateLimitError):
                        err_msg = "OpenAI 配额不足 (429)。请检查账单/额度或换用更便宜的模型/密钥。"
                except Exception:
                    pass
                if not err_msg:
                    err_msg = "OpenAI 调用失败：\n" + traceback.format_exc()
                self.ui_queue.put((self.display_message, (err_msg, "", "")))

        threading.Thread(target=worker, daemon=True).start()
        return "break"

    def on_send_button_clicked(self):
        self.on_enter_pressed()

    def display_message(self, message, sender, desc):
        bold_font = Font(self.chat_history, self.chat_history.cget("font"), weight="bold")
        self.chat_history.tag_configure('bold', font=bold_font)
        self.chat_history.config(state='normal')
        self.chat_history.tag_configure('user_name', justify='left')
        self.chat_history.tag_configure('bot_name', justify='left')

        if self.chat_history.index("end-1c") != "1.0":
            self.chat_history.insert(tk.END, '\n')

        if sender == "我":
            self.chat_history.tag_configure('user_msg', lmargin1=60, lmargin2=60)
            self.chat_history.window_create(tk.END, window=tk.Label(self.chat_history, image=self.user_avatar), align='center', padx=10)
            self.chat_history.insert(tk.END, "：", 'bold')
            self.chat_history.insert(tk.END, f"\n{message}\n", 'user_msg')
        else:
            self.chat_history.tag_configure('bot_msg', lmargin1=60, lmargin2=60)
            self.chat_history.tag_configure('desc', lmargin1=60, lmargin2=60, foreground='red')
            self.chat_history.window_create(tk.END, window=tk.Label(self.root, image=self.bot_avatar), align='bottom', padx=10)
            self.chat_history.insert(tk.END, "：", 'bold')
            if len(desc) > 0:
                self.chat_history.insert(tk.END, "\n执行成功！", 'bot_msg')
                self.chat_history.insert(tk.END, f"{desc}\n", 'desc')
            else:
                self.chat_history.insert(tk.END, f"\n{message}\n", 'bot_msg')

        separator = '---' * 20
        self.chat_history.insert(tk.END, f'{separator}', 'separator')
        self.chat_history.yview(tk.END)
        self.chat_history.config(state='disabled')
