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
        """Gets IP, Country and ISP info."""
        url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
        try:
            async with self.http.get(url) as resp:
                data = await resp.json()
                # Extraemos IP, País e ISP
                return (
                    data.get("query", "N/A"), 
                    data.get("country", "Unknown"), 
                    data.get("isp", "Unknown Provider")
                )
        except Exception:
            return "N/A", "Unknown", "Unknown Provider"

    def resolve_ip(self, domain: str) -> str:
        """Resolves domain to IP address"""
        try:
            return socket.gethostbyname(domain)
        except Exception:
            return "N/A"

    def identify_type(self, isp_name: str) -> str:
        """Heuristic to guess if the IP is Hosting/VPS or Domestic."""
        isp_lower = isp_name.lower()
        hosting_keywords = [
            "hetzner", "digitalocean", "amazon", "aws", "google", "cloud", 
            "microsoft", "azure", "ovh", "contabo", "linode", "vultr", 
            "oracle", "leaseweb", "fastly", "cloudflare", "akamai"
        ]
        if any(kw in isp_lower for kw in hosting_keywords):
            return "Data Center / VPS"
        return "Residential / Business"

    async def run_test(self, evt: MessageEvent) -> None:
        now_ms = int(time() * 1000)
        diff = now_ms - evt.timestamp
        latency = f"{diff} ms"
        received_at = datetime.fromtimestamp(now_ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S')


        sender_mxid = evt.sender
        sender_server = sender_mxid.split(':', 1)[1]
        sender_ip = self.resolve_ip(sender_server)
        _, sender_loc, sender_isp = await self.get_location_data(sender_ip)
        sender_type = self.identify_type(sender_isp)
        
        sent_at = datetime.fromtimestamp(evt.timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

        bot_server = self.client.mxid.split(':', 1)[1]
        bot_ip, bot_loc, bot_isp = await self.get_location_data()
        bot_type = self.identify_type(bot_isp)


        html_body = (
            f"✅ <b>Test successful</b><br/>"
            f"Message received by server<br/>"
            f"<br/>"
            f"<b>SENDER SERVER INFO</b><br/>"
            f"• <b>Server:</b> {sender_server}<br/>"
            f"• <b>Sent at:</b> {sent_at}<br/>"
            f"• <b>Sender IP:</b> {sender_ip}<br/>"
            f"• <b>Provider:</b> {sender_isp} ({sender_type})<br/>"
            f"• <b>Location:</b> {sender_loc}<br/>"
            f"• <b>User:</b> <code>{sender_mxid}</code><br/>"
            f"<br/>"
            f"<b>RECEIVER SERVER INFO</b><br/>"
            f"• <b>Server:</b> {bot_server}<br/>"
            f"• <b>Received at:</b> {received_at}<br/>"
            f"• <b>Server IP:</b> {bot_ip}<br/>"
            f"• <b>Provider:</b> {bot_isp} ({bot_type})<br/>"
            f"• <b>Location:</b> {bot_loc}<br/>"
            f"• <b>Latency:</b> {latency}"
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
