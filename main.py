from base.module import BaseModule, command
from pyrogram.types import Message
import logging
from pyrogram import Client
from .utils import demot
import os

logger = logging.getLogger(__name__)

class DemotivatorModule(BaseModule):
    demotivator = demot.Demotivator()
    # Register handler
    @command("dmt")
    async def dmt_cmd(self, bot: Client, message: Message):
        # logger.info(message)

        if not message.reply_to_message:
            return await message.reply(self.S["error"]["reply"])
        if not (message.reply_to_message.photo or message.reply_to_message.animation or message.reply_to_message.video):
            return await message.reply(self.S["error"]["media"])

        media_path = await bot.download_media(message.reply_to_message)

        demot_path = os.path.abspath(__file__).replace("main.py", media_path.split("/")[-1])
        self.demotivator.generate_demotivator(media_path, demot_path, message.text[5:]) # Drop command
    
        # logger.info(media_path)
        # logger.info(demot_path)

        # TODO: Fix audio in video (No Audio)
        # Send
        if demot_path.endswith((".mp4", ".MP4")):  # If video/gif
            await message.reply_video(os.path.abspath(__file__).replace("main.py", media_path.split("/")[-1]))
        elif demot_path.endswith((".jpg", ".png")):  # If general photo
            await message.reply_photo(os.path.abspath(__file__).replace("main.py", media_path.split("/")[-1]))

        os.remove(os.path.abspath(__file__).replace("main.py", media_path.split("/")[-1]))
