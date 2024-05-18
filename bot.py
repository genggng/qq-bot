# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging

from botpy.message import DirectMessage, Message
from botpy.ext.cog_yaml import read
from QA_bot import QA_bot


test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()
# msg_loger = logging.get_logger("msg")

qa_bot = QA_bot(chat_host=test_config["chat_host"],model_name=test_config["model_name"],loger=_log)


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_direct_message_create(self, message: DirectMessage):
        reply = qa_bot.reply(message.author.id,message.content)
        # _log.info(f"「{message.author.username}」: {message.author.id}")
        _log.info(f"「{message.author.username}」: {message.content} --->「{self.robot.name}」: {reply}")
        await self.api.post_dms(
            guild_id=message.guild_id,
            content=reply,
            msg_id=message.id,
        )

if __name__ == "__main__":
    intents = botpy.Intents(direct_message=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
