from base.module import BaseModule, command
from pyrogram.types import Message
import logging
from pyrogram import Client
from .utils import demot
import os
import inspect

logger = logging.getLogger(__name__)

class DemotivatorModule(BaseModule):
    @property
    def help_page(self) -> str:
        """
        Help string to be displayed in Core module help command. Highly recommended to set this!
        Defaults to auto-generated command listing, which uses callback func __doc__ for description
        """
        auto_help = f'{self.S["help"]["available"]}:\n'
        commands = [s for s in dir(self) if s.endswith("_cmd")]
        for cmd in commands:
            if cmd in ['start_cmd']:
                continue
            
            auto_help += (
                f"/{cmd.replace('_cmd', '')}"
                + (f" - {getattr(self, cmd).__doc__}" if getattr(self, cmd).__doc__ else "")
                + "\n"
            )
        return auto_help

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
