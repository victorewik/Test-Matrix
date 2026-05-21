from typing import Optional
from time import time
import platform
import sys
from html import escape

from mautrix.types import TextMessageEventContent, MessageType, Format, RelatesTo, RelationType
from maubot import Plugin, MessageEvent
from maubot.handlers import command, event

class EchoBot(Plugin):
    @staticmethod
    def plural(num: float, unit: str, decimals: Optional[int] = None) -> str:
        if decimals is not None:
            num = round(num, decimals)
        if num == 1:
            return f"{num} {unit}"
        else:
            return f"{num} {unit}s"

    @classmethod
    def prettify_diff(cls, diff: int) -> str:
        if abs(diff) < 10 * 1_000:
            return f"{diff} ms"
        elif abs(diff) < 60 * 1_000:
            return cls.plural(diff / 1_000, 'second', decimals=1)
        minutes, seconds = divmod(diff / 1_000, 60)
        if abs(minutes) < 60:
            return f"{cls.plural(minutes, 'minute')} and {cls.plural(seconds, 'second')}"
        hours, minutes = divmod(minutes, 60)
        if abs(hours) < 24:
            return (f"{cls.plural(hours, 'hour')}, {cls.plural(minutes, 'minute')}"
                    f" and {cls.plural(seconds, 'second')}")
        days, hours = divmod(hours, 24)
        return (f"{cls.plural(days, 'day')}, {cls.plural(hours, 'hour')}, "
                f"{cls.plural(minutes, 'minute')} and {cls.plural(seconds, 'second')}")

    async def get_public_ip(self) -> str:
        try:
            # Usamos el cliente HTTP interno de maubot para obtener la IP pública del bot
            async with self.http.get("https://api.ipify.org") as resp:
                return await resp.text()
        except Exception:
            return "No disponible"

    @command.new("test", help="Datos de prueba y diagnóstico")
    async def test_handler(self, evt: MessageEvent) -> None:
        # 1. Calcular Latencia (Ping)
        diff = int(time() * 1000) - evt.timestamp
        pretty_diff = self.prettify_diff(diff)

        # 2. Obtener IP del bot
        bot_ip = await self.get_public_ip()

        # 3. Otros datos de test
        py_version = platform.python_version()
        os_info = f"{platform.system()} {platform.release()}"
        
        # Construir mensaje
        html_body = (
            f"<b>Test de Diagnóstico</b><br/>"
            f"<ul>"
            f"<li><b>Latencia:</b> {pretty_diff}</li>"
            f"<li><b>IP del Bot:</b> {bot_ip}</li>"
            f"<li><b>Servidor del Bot:</b> {evt.sender.split(':')[-1]}</li>"
            f"<li><b>Versión Python:</b> {py_version}</li>"
            f"<li><b>Sistema Operativo:</b> {os_info}</li>"
            f"<li><b>ID del Evento:</b> <code>{evt.event_id}</code></li>"
            f"</ul>"
        )
        
        await evt.respond(html_body, allow_html=True)

    # Este decorador permite que el bot responda a "test" sin necesidad del prefijo de comando (ej: !)
    @event.on(MessageType.TEXT)
    async def handle_message(self, evt: MessageEvent) -> None:
        if evt.content.body.strip().lower() == "test":
            # Si el usuario escribe solo "test" o "Test", ejecutamos el test_handler
            await self.test_handler(evt)

    @command.new("ping", help="Ping")
    @command.argument("message", pass_raw=True, required=False)
    async def ping_handler(self, evt: MessageEvent, message: str = "") -> None:
        diff = int(time() * 1000) - evt.timestamp
        pretty_diff = self.prettify_diff(diff)
        text_message = f'"{message[:20]}" took' if message else "took"
        html_message = f'"{escape(message[:20])}" took' if message else "took"
        content = TextMessageEventContent(
            msgtype=MessageType.NOTICE, format=Format.HTML,
            body=f"{evt.sender}: Pong! (ping {text_message} {pretty_diff} to arrive)",
            formatted_body=f"<a href='https://matrix.to/#/{evt.sender}'>{evt.sender}</a>: Pong! "
            f"(<a href='https://matrix.to/#/{evt.room_id}/{evt.event_id}'>ping</a> {html_message} "
            f"{pretty_diff} to arrive)",
            relates_to=RelatesTo(
                rel_type=RelationType("xyz.maubot.pong"),
                event_id=evt.event_id,
            ))
        pong_from = evt.sender.split(":", 1)[1]
        content.relates_to["from"] = pong_from
        content.relates_to["ms"] = diff
        content["pong"] = {
            "ms": diff,
            "from": pong_from,
            "ping": evt.event_id,
        }
        await evt.respond(content)

    @command.new("echo", help="Repeat a message")
    @command.argument("message", pass_raw=True)
    async def echo_handler(self, evt: MessageEvent, message: str) -> None:
        await evt.respond(message)
