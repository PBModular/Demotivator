# Module class template

from base.module import BaseModule, command
from pyrogram.types import Message

class ModuleTemplate(BaseModule):
    # Register handler
    @command("example")
    async def example_cmd(self, _, message: Message):
        await message.reply(self.S["some"]["strings"])
