from typing import Optional
from time import time
from html import escape

from mautrix.types import TextMessageEventContent, MessageType, Format, RelatesTo, RelationType, EventType
from maubot import Plugin, MessageEvent
from maubot.handlers import event, command

class EchoBot(Plugin):
    @staticmethod
    def plural(num: float, unit: str, decimals: Optional[int] = None) -> str:
        if decimals is not None:
            num = round(num, decimals)
        return f"{num} {unit}" if num == 1 else f"{num} {unit}s"

    @classmethod
    def prettify_diff(cls, diff: int) -> str:
        if abs(diff) < 10 * 1_000:
            return f"{diff} ms"
        elif abs(diff) < 60 * 1_000:
            return cls.plural(diff / 1_000, 'second', decimals=1)
        minutes, seconds = divmod(diff / 1_000, 60)
        return f"{cls.plural(minutes, 'minute')} and {cls.plural(seconds, 'second')}"

    async def get_server_info(self):
        """Gets IP and Country from ip-api"""
        try:
            async with self.http.get("http://ip-api.com/json/") as resp:
                data = await resp.json()
                return data.get("query", "N/A"), data.get("country", "Unknown")
        except Exception:
            return "N/A", "Unknown"

    async def run_test(self, evt: MessageEvent) -> None:
        # 1. Latency (Ping)
        diff = int(time() * 1000) - evt.timestamp
        pretty_diff = self.prettify_diff(diff)

        # 2. Server IP and Location
        server_ip, country = await self.get_server_info()
        
        # 3. Server Name (Domain)
        server_name = evt.sender.split(':')[-1]

        # Final HTML message in English
        html_body = (
            f"<b>✅ Test successful</b><br/>"
            f"<i>Message received by server</i><br/>"
            f"<ul>"
            f"<li><b>Latency:</b> {pretty_diff}</li>"
            f"<li><b>Server Name:</b> {server_name}</li>"
            f"<li><b>Server IP:</b> {server_ip}</li>"
            f"<li><b>Location:</b> {country}</li>"
            f"</ul>"
        )
        await evt.respond(html_body, allow_html=True)

    @event.on(EventType.ROOM_MESSAGE)
    async def handle_message(self, evt: MessageEvent) -> None:
        # Ignore if not text or if sent by the bot itself
        if evt.content.msgtype != MessageType.TEXT or evt.sender == self.client.mxid:
            return

        # Trigger on "test" or "Test" (case insensitive)
        content = evt.content.body.strip()
        if content.lower() == "test":
            await self.run_test(evt)

    @command.new("ping")
    async def ping_handler(self, evt: MessageEvent) -> None:
        await self.run_test(evt)
