"""Discord Gateway listener (architecture section 3.3)."""

import asyncio

import discord

from .config import Config
from .log import log
from .photos import is_supported_attachment
from .queue_worker import PROCESSING_EMOJI, Job, MessageTracker, Worker


class ProduceBot(discord.Client):
    def __init__(self, config: Config):
        intents = discord.Intents.none()
        intents.guilds = True
        intents.guild_messages = True
        intents.message_content = True
        super().__init__(intents=intents, allowed_mentions=discord.AllowedMentions.none())
        self.config = config
        self.worker = Worker(config.data_dir, config.photos_dir, config.claude_model)
        self.worker_task: asyncio.Task | None = None

    async def setup_hook(self) -> None:
        self.worker_task = asyncio.create_task(self.worker.run_forever())

    async def on_ready(self) -> None:
        self.worker.bot_user = self.user
        channel = self.get_channel(self.config.channel_id)
        where = f"#{channel.name}" if channel else f"channel {self.config.channel_id} (not visible to the bot yet!)"
        log(f"✅ Logged in as {self.user}. Watching {where}. Data folder: {self.config.data_dir}")
        counts = self.worker.counts
        log(f"Today so far: {counts.total} checked ({counts.fruits} fruits, {counts.vegetables} vegetables)")

    async def on_message(self, message: discord.Message) -> None:
        try:
            await self._handle_message(message)
        except Exception as error:
            log(f"⚠️  Could not queue a message ({error}).")

    async def _handle_message(self, message: discord.Message) -> None:
        if message.channel.id != self.config.channel_id or message.author.bot:
            return
        photos = [
            attachment for attachment in message.attachments
            if is_supported_attachment(attachment.filename, attachment.content_type, attachment.size)
        ]
        if not photos:
            return

        try:
            await message.add_reaction(PROCESSING_EMOJI)
        except discord.HTTPException as error:
            log(f"⚠️  Could not add ⏳ ({error}). Continuing anyway.")

        tracker = MessageTracker(remaining=len(photos))
        for index, attachment in enumerate(photos, start=1):
            await self.worker.queue.put(Job(
                message=message,
                attachment=attachment,
                index=index,
                total=len(photos),
                uploader_text=message.content,
                display_name=message.author.display_name,
                user_id=str(message.author.id),
                message_link=message.jump_url,
                tracker=tracker,
            ))
        log(f"Queued {len(photos)} photo(s) from {message.author.display_name}")
