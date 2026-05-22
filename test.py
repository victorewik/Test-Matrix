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
                return (
                    data.get("query", "N/A"), 
                    data.get("country", "Unknown"), 
                    data.get("isp", "Unknown Provider")
                )
        except Exception:
            return "N/A", "Unknown", "Unknown Provider"

    def resolve_public_endpoint(self, domain: str) -> str:
        """Resolves the domain IP."""
        try:
            return socket.gethostbyname(domain)
        except Exception:
            return "N/A"

    def identify_type(self, isp_name: str) -> str:
        isp_lower = isp_name.lower()
        hosting_keywords = ["hetzner", "digitalocean", "amazon", "aws", "google", "cloud", 
                            "ovh", "contabo", "linode", "vultr", "cloudflare"]
        if any(kw in isp_lower for kw in hosting_keywords):
            return "Data Center / VPS"
        return "Residential / Business"

    async def run_test(self, evt: MessageEvent) -> None:
        # 1. Capture timing
        now_ms = int(time() * 1000)
        latency = f"{now_ms - evt.timestamp} ms"
        received_at = datetime.fromtimestamp(now_ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

        # 2. Sender Data
        sender_mxid = evt.sender
        sender_domain = sender_mxid.split(':', 1)[1]
        sender_ip = self.resolve_public_endpoint(sender_domain)
        _, sender_loc, sender_isp = await self.get_location_data(sender_ip)
        sender_type = self.identify_type(sender_isp)
        sent_at = datetime.fromtimestamp(evt.timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

        # 3. Receiver / Bot Data
        bot_hs_domain = self.client.mxid.split(':', 1)[1]
        bot_hs_ip = self.resolve_public_endpoint(bot_hs_domain)
        
        # Get actual hosting data
        hosting_ip, hosting_loc, hosting_isp = await self.get_location_data()
        hosting_type = self.identify_type(hosting_isp)

        # 4. Logic: Is it remote?
        # Compare Homeserver IP with Actual Hosting IP
        is_remote = (bot_hs_ip != hosting_ip and bot_hs_ip != "N/A")

        # 5. HTML Construction
        html_body = (
            f"✅ <b>Test successful</b><br/>"
            f"Message received by server<br/>"
            f"<br/>"
            f"<b>SENDER SERVER INFO</b><br/>"
            f"• <b>Server:</b> {sender_domain}<br/>"
            f"• <b>Public Endpoint IP:</b> {sender_ip}<br/>"            
            f"• <b>Sent at:</b> {sent_at}<br/>"
            f"• <b>Provider:</b> {sender_isp} ({sender_type})<br/>"
            f"• <b>Location:</b> {sender_loc}<br/>"
            f"• <b>User:</b> <code>{sender_mxid}</code><br/>"
            f"<br/>"
        )

        if is_remote:
            html_body += f"⚠️ <b>Note: This bot is hosted on a remote server.</b><br/>"

        html_body += f"<b>RECEIVER SERVER INFO</b><br/>"
        
        if is_remote:

            html_body += (
                f"• <b>Server:</b> {bot_hs_domain}<br/>"
                f"• <b>Server IP:</b> {bot_hs_ip}<br/>"
                f"• <b>Hosting IP:</b> {hosting_ip}<br/>"
            )
        else:

            html_body += (
                f"• <b>Server:</b> {bot_hs_domain}<br/>"
                f"• <b>Server IP:</b> {hosting_ip}<br/>"
            )

        html_body += (
            f"• <b>Received at:</b> {received_at}<br/>"
            f"• <b>Provider:</b> {hosting_isp} ({hosting_type})<br/>"
            f"• <b>Location:</b> {hosting_loc}<br/>"
            f"• <b>Latency:</b> {latency}"
        )

        await evt.respond(html_body, allow_html=True)

    @event.on(EventType.ROOM_MESSAGE)
    async def handle_message(self, evt: MessageEvent) -> None:
        if evt.content.msgtype != MessageType.TEXT or evt.sender == self.client.mxid:
            return
        content = evt.content.body.strip().lower()
        if content == "test":
            await self.run_test(evt)

    @command.new("test")
    async def test_handler(self, evt: MessageEvent) -> None:
        await self.run_test(evt)
