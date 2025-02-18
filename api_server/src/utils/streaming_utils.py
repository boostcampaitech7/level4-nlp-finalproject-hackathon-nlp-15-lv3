from __future__ import annotations

import json
import re
import typing
from functools import partial
from typing import List, Any

import anyio
import anyio.to_thread
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

Content = typing.Union[str, bytes, memoryview]
SyncContentStream = typing.Iterable[Content]
AsyncContentStream = typing.AsyncIterable[Content]
ContentStream = typing.Union[AsyncContentStream, SyncContentStream]


def parse_stream(x: Content, model_type: typing.Literal['PyTriton'] = "Others") -> Content:
    if model_type == "PyTriton":
        return json.loads(re.sub("^data: ?", "", x.decode("utf-8")))["text"]
    return x


class StreamingResponse(Response):
    body_iterator: AsyncContentStream

    def __init__(
            self,
            content: ContentStream,
            status_code: int = 200,
            model_type: typing.Literal['PyTriton', 'Others'] = "Others",
            headers: typing.Mapping[str, str] | None = None,
            media_type: str | None = None,
            background: BackgroundTask | None = None,
            db_manager: Any | None = None,
            metadata: List[str] | None = None,
    ) -> None:
        if isinstance(content, typing.AsyncIterable):
            self.body_iterator = content
        else:
            self.body_iterator = iterate_in_threadpool(content)
        self.status_code = status_code
        self.media_type = self.media_type if media_type is None else media_type
        self.background = background
        self.init_headers(headers)
        self.db_manager = db_manager
        self.metadata = metadata
        self.model_type = model_type

    async def listen_for_disconnect(self, receive: Receive) -> None:
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                break

    async def stream_response(self, send: Send) -> None:
        _response_text = ""
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        async for chunk in self.body_iterator:
            chunk = parse_stream(chunk, self.model_type)
            _response_text += chunk
            if not isinstance(chunk, (bytes, memoryview)):
                chunk = chunk.encode(self.charset)
            await send({"type": "http.response.body", "body": chunk, "more_body": True})

        await send({"type": "http.response.body", "body": b"", "more_body": False})

        if self.metadata is not None:
            self.metadata.append(_response_text)

        if self.db_manager is not None:
            self.db_manager.insert(*self.metadata)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async with anyio.create_task_group() as task_group:
            async def wrap(func: typing.Callable[[], typing.Awaitable[None]]) -> None:
                await func()
                task_group.cancel_scope.cancel()

            task_group.start_soon(wrap, partial(self.stream_response, send))
            await wrap(partial(self.listen_for_disconnect, receive))

        if self.background is not None:
            await self.background()
