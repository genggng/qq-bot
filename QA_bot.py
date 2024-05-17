from utils.api_sets import wyy_words, emotion_words, social_words, one_word, heart_hen_soup, anwei_words, famous_words

from ollama import Client
import ollama

key_api = {
   "网易云":wyy_words,
   "谈感情":emotion_words,
   "社会人":social_words,
   "来一句":one_word,
   "喝鸡汤":heart_hen_soup,
   "安慰一下":anwei_words,
   "名人名言":famous_words,
}
class QA_bot(object):
    def __init__(self,
                 chat_host,
                 model_name,
                 loger,
                 ) -> None:
        self.client = Client(host=chat_host)
        self.model_name = model_name
        self.loger = loger

    def reply(self, message: str) -> str:
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

        else:
            try:
                reply = self.client.chat(model=self.model_name, messages=[
                    {
                        'role': 'user',
                        'content': message,
                    },
                    ])
            except ollama.ResponseError as e:
                self.loger.error(f"ollama error:{e}")
                return "小猫有点累了，稍后再试试吧。"
            
            return reply["message"]["content"]