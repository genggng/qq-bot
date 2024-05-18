from utils.api_sets import wyy_words, emotion_words, social_words, one_word, heart_hen_soup, anwei_words, famous_words
from utils.system_tools import get_system_info,kill_vscode_server
from collections import deque
from ollama import Client
import ollama
from func_timeout import func_timeout, FunctionTimedOut
from botpy.ext.cog_yaml import read
import os

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))


key_api = {
   "网易云":wyy_words,
   "谈感情":emotion_words,
   "社会人":social_words,
   "来一句":one_word,
   "喝鸡汤":heart_hen_soup,
   "安慰一下":anwei_words,
   "名人名言":famous_words,
}

cmd_list = [
    "#清空记忆",
    "#系统信息",
    "#猫的记忆",
    "#杀掉vscode",
    # "#切换模型",
]


class QA_bot(object):
    def __init__(self,
                 chat_host,
                 model_name,
                 loger,
                 max_memory:int=4096,
                 ) -> None:
        self.client = Client(host=chat_host)
        self.model_name = model_name
        self.loger = loger
        self.memory_dict = {}
        self.memory_len_dict = {}
        self.max_memory = max_memory

    def init_memory(self,user_id:str):
        self.memory_dict[user_id] = deque()
        self.memory_len_dict[user_id] = 0

    def clear_memory(self,user_id:str):
        if user_id in self.memory_dict:
            self.init_memory(user_id)

    def sliding_window(self,user_id:str):
        if user_id in self.memory_dict:
            while self.memory_len_dict[user_id] > self.max_memory:
                pop_msg = self.memory_dict[user_id].popleft()
                msg_len = len(pop_msg["content"])
                self.memory_len_dict[user_id] -= msg_len

    def update_msg_memory(self,user_id:str, message:dict):
        self.memory_dict[user_id].append(message)
        self.memory_len_dict[user_id] += len(message["content"])

    def reply(self,user_id:str, message: str) -> str:
        # assert isinstance(user_id, str)
        if user_id not in self.memory_dict:
            self.init_memory(user_id)
        if not isinstance(message, str):
            return  "小猫目前只能听懂文字哦。"
        for key in key_api.keys():
            if key in message:
                try:
                    ret = key_api[key]()
                except Exception as e:
                    self.loger.error(f"key:{key} error:{e}")
                    return "小猫有点累了，稍后再试试吧。"
                
                if ret["status_code"] == 200:
                    reply = ret["text"]
                else:
                    reply = "小猫有点累了，稍后再试试吧。"
                return reply
        if "技能" in message:
            skills = ",".join(key_api.keys())
            return f"小猫目前有这些技能：{skills}"
        elif "指令" in message:
            cmds = ",".join(cmd_list)
            return f"小猫目前有这些指令：{cmds}"
        elif "帮助" in message:
            return "输入「技能」查看小猫的技能，输入「指令」查看小猫的指令。"
        elif "#清空记忆" in message:
            self.clear_memory(user_id)
            return "小猫已经忘记了和你的对话。"
        elif "#系统信息" in message:
            info = get_system_info()
            return f"CPU使用率：{info['cpu_usage']}%，内存使用率：{info['memory_usage']}%"
        elif "#猫的记忆" in message:
            reply = " "
            for msg in self.memory_dict[user_id]:
                reply +=  f"{msg['role']}:{msg['content']}\n"
            reply += f"上下文总长度：{str(self.memory_len_dict[user_id])}"
            return reply
        elif "#杀掉vscode" in message:
            ret_code = kill_vscode_server()
            if ret_code != 0:
                return "杀掉vscode-server进程失败。"
            else:
                return "杀掉vscode-server进程成功。"
        # elif "#切换模型" in message:
        #     _,model_name = message.split(":")
        #     self.model_name = "gpt2"
        #     return "切换模型成功。"
        else:
            q_msg = {
                'role': 'user',
                'content': message,
            }
            self.update_msg_memory(user_id, q_msg)
            self.sliding_window(user_id)
            try:

                kwArgs={'model': self.model_name, 'messages': list(self.memory_dict[user_id])}
                reply = func_timeout(test_config["wait_time"], self.client.chat, kwargs=kwArgs)
                # reply = self.client.chat(model=self.model_name, messages=list(self.memory_dict[user_id]))
            except ollama.ResponseError as e:
                self.loger.error(f"ollama error:{e}")
                return "小猫有点累了，稍后再试试吧。"
            except FunctionTimedOut:
                self.loger.error(f"ollama timeout")
                return "小猫有点累了，稍后再试试吧。"
            self.update_msg_memory(user_id, reply["message"])

            return reply["message"]["content"].strip()+"."
