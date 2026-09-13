import asyncio
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class MediaGroupMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.5):
        self.latency = latency
        self.album_data: dict[str, list[Message]] = {}

    async def __call__(self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)
            data["album"] = self.album_data.pop(event.media_group_id)
            return await handler(event, data)

        self.album_data[event.media_group_id].append(event)
