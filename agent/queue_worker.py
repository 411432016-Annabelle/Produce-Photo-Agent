"""One queue, one worker: each photo is fully handled before the next starts (architecture sections 4 and 7)."""

import asyncio
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import discord

from . import replies
from .analyzer import AnalyzerError, analyze_photo
from .contract import READY_VALUES, ContractError, NotProduce, Produce, parse_claude_output
from .excel_log import ERROR, NOT_PRODUCE, ExcelLog
from .log import log
from .photos import PhotoError, save_photo, to_jpeg

PROCESSING_EMOJI = "⏳"
NO_PINGS = discord.AllowedMentions.none()


@dataclass
class MessageTracker:
    """Counts a message's photos still to be answered, so ⏳ comes off after the last one."""
    remaining: int


@dataclass
class Job:
    message: Any       # discord.Message
    attachment: Any    # discord.Attachment
    index: int
    total: int
    uploader_text: str
    display_name: str
    user_id: str
    message_link: str
    tracker: MessageTracker
    replied: bool = field(default=False)


class Worker:
    def __init__(self, data_dir: Path, photos_dir: Path, model: str, bot_user: Any = None,
                 claude_bin: str = "claude"):
        self.data_dir = data_dir
        self.photos_dir = photos_dir
        self.model = model
        self.bot_user = bot_user
        self.claude_bin = claude_bin
        self.queue: asyncio.Queue[Job] = asyncio.Queue()
        self.excel = ExcelLog(data_dir)
        self.counts = self.excel.count_today(datetime.now().date())

    async def run_forever(self) -> None:
        while True:
            job = await self.queue.get()
            try:
                await self.process(job)
            except Exception:
                log("❌ Unexpected problem while handling a photo:\n" + traceback.format_exc())
                if not job.replied:
                    await self._reply(job, replies.error_reply(self.counts, self._label(job)))
            finally:
                await self._finish_message(job)
                self.queue.task_done()

    async def process(self, job: Job) -> None:
        now = datetime.now()
        self.counts.roll_to(now.date())
        log(f"Checking photo {job.index}/{job.total} from {job.display_name} ({self.queue.qsize()} waiting)")

        jpeg = None
        result: Produce | NotProduce | None = None
        error_reason = ""
        try:
            jpeg = await asyncio.to_thread(to_jpeg, await job.attachment.read())
            stdout = await analyze_photo(jpeg, job.uploader_text, self.data_dir, self.model, self.claude_bin)
            result = parse_claude_output(stdout)
        except (AnalyzerError, ContractError, PhotoError) as error:
            error_reason = str(error)
        except discord.HTTPException as error:
            error_reason = f"photo download failed ({error.status})"
        except Exception as error:
            log("❌ Unexpected problem while checking a photo:\n" + traceback.format_exc())
            error_reason = f"unexpected error ({type(error).__name__})"
        if error_reason:
            log(f"⚠️  Recognition failed: {error_reason}")

        if isinstance(result, Produce):
            self.counts.add(result.produce_type)
            item_name = result.name
        elif isinstance(result, NotProduce):
            item_name = NOT_PRODUCE
        else:
            item_name = ERROR

        photo_file = ""
        if jpeg is not None:
            try:
                photo_file = str(await asyncio.to_thread(save_photo, self.photos_dir, now, item_name, jpeg))
            except Exception as error:
                log(f"⚠️  Could not save the photo ({error}). Continuing without it.")

        await self.excel.append(self._row(job, now, result, error_reason, photo_file))

        label = self._label(job)
        if isinstance(result, Produce):
            text = replies.produce_reply(result, self.counts, label)
        elif isinstance(result, NotProduce):
            text = replies.not_produce_reply(result, self.counts, label)
        else:
            text = replies.error_reply(self.counts, label)
        await self._reply(job, text)
        log(f"Replied: {item_name}")

    def _row(self, job: Job, now: datetime, result, error_reason: str, photo_file: str) -> list:
        if isinstance(result, Produce):
            details = [
                result.produce_type, result.name, result.freshness_score,
                READY_VALUES[result.ready_to_eat], result.days_left,
                result.storage_tip, result.description, result.confidence,
            ]
        elif isinstance(result, NotProduce):
            details = ["", NOT_PRODUCE, None, "", None, "", result.description, result.confidence]
        else:
            details = ["", ERROR, None, "", None, "", error_reason, None]
        return [
            f"{now:%Y-%m-%d %H:%M:%S}", job.display_name, job.user_id, *details,
            job.uploader_text, photo_file, job.message_link,
            self.counts.total, self.counts.fruits, self.counts.vegetables,
        ]

    @staticmethod
    def _label(job: Job) -> str:
        return replies.photo_label(job.index, job.total)

    async def _reply(self, job: Job, text: str) -> None:
        try:
            await job.message.reply(text, mention_author=False, allowed_mentions=NO_PINGS)
            job.replied = True
        except Exception as error:
            log(f"⚠️  Could not send the reply ({error}). Was the message deleted?")

    async def _finish_message(self, job: Job) -> None:
        job.tracker.remaining -= 1
        if job.tracker.remaining > 0:
            return
        try:
            await job.message.remove_reaction(PROCESSING_EMOJI, self.bot_user)
        except Exception as error:
            log(f"⚠️  Could not remove ⏳ ({error}).")
