from base.module import BaseModule, command
from pyrogram.types import Message
import logging
from pyrogram import Client
from .utils import demot
import os

logger = logging.getLogger(__name__)

class DemotivatorModule(BaseModule):
    
    # Register handler
    @command("dmt")
    async def dmt_cmd(self, bot: Client, message: Message):
        # logger.info(message)

        if not message.reply_to_message:
            return await message.reply(self.S["error"]["reply"])
        if not message.reply_to_message.photo:
            return await message.reply(self.S["error"]["photo"])

        media_path = await bot.download_media(message.reply_to_message, "demot.png")

        demot.generate_demotivator(media_path, os.path.abspath(__file__).replace("main.py", "demot.png"), message.text[5:]) # Drop command
        await message.reply_photo(os.path.abspath(__file__).replace("main.py", "demot.png"))
