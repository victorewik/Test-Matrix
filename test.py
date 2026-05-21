from typing import Optional
from time import time
import socket
from datetime import datetime
from html import escape

from mautrix.types import TextMessageEventContent, MessageType, Format, RelatesTo, RelationType, EventType
from maubot import Plugin, MessageEvent
from maubot.handlers import event, command

class EchoBot(Plugin):
    async def get_location_data(self, ip: Optional[str] = None):
        """Gets IP and Country. If IP is provided, gets that IP's info."""
        url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
        try:
            async with self.http.get(url) as resp:
                data = await resp.json()
                return data.get("query", "N/A"), data.get("country", "Unknown")
        except Exception:
            return "N/A", "Unknown"

    def resolve_ip(self, domain: str) -> str:
        """Resolves domain to IP address"""
        try:
            return socket.gethostbyname(domain)
        except Exception:
            return "N/A"

    async def run_test(self, evt: MessageEvent) -> None:
        # --- SENDER INFO ---
        sender_mxid = evt.sender
        sender_server = sender_mxid.split(':', 1)[1]
        sender_ip = self.resolve_ip(sender_server)
        # Get location of the sender's IP
        _, sender_loc = await self.get_location_data(sender_ip)
        sent_at = datetime.fromtimestamp(evt.timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

        # --- RECEIVER INFO ---
        bot_server = self.client.mxid.split(':', 1)[1]
        bot_ip, bot_loc = await self.get_location_data()
        received_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Latency
        diff = int(time() * 1000) - evt.timestamp
        latency = f"{diff} ms"

        # Final HTML message (Clean, English, no lines, no parentheses)
        html_body = (
            f"✅ <b>Test successful</b><br/>"
            f"Message received by server<br/>"
            f"<br/>"
            f"<b>SENDER USER INFO</b><br/>"
            f"<ul>"
            f"<li><b>User:</b> <code>{sender_mxid}</code></li>"
            f"<li><b>Sender Server:</b> {sender_server}</li>"
            f"<li><b>Sent at:</b> {sent_at}</li>"
            f"<li><b>Sender IP:</b> {sender_ip}</li>"
            f"<li><b>Location:</b> {sender_loc}</li>"
            f"</ul>"
            f"<b>RECEIVER SERVER INFO</b><br/>"
            f"<ul>"
            f"<li><b>Latency:</b> {latency}</li>"
            f"<li><b>Server:</b> {bot_server}</li>"
            f"<li><b>Received at:</b> {received_at}</li>"
            f"<li><b>Server IP:</b> {bot_ip}</li>"
            f"<li><b>Location:</b> {bot_loc}</li>"
            f"</ul>"
        )
        await evt.respond(html_body, allow_html=True)

    @event.on(EventType.ROOM_MESSAGE)
    async def handle_message(self, evt: MessageEvent) -> None:
        if evt.content.msgtype != MessageType.TEXT or evt.sender == self.client.mxid:
            return

        content = evt.content.body.strip()
        if content.lower() == "test":
            await self.run_test(evt)

    @command.new("ping")
    async def ping_handler(self, evt: MessageEvent) -> None:
        await self.run_test(evt)
