# ---------------------------------------------------------------------------------
#  /\_/\  🌐 This module was loaded through https://t.me/hikkamods_bot
# ( o.o )  🔓 Not licensed.
#  > ^ <   ⚠️ Owner of heta.hikariatama.ru doesn't take any responsibilities or intellectual property rights regarding this script
# ---------------------------------------------------------------------------------
# Name: IrisfarmMod
# Author: Mister_HolY
# Commands:
# .farm | .farmiris
# ---------------------------------------------------------------------------------

# meta developer: @Mister_HolY

from .. import loader, utils
import asyncio
import time
import re

class IrisfarmMod(loader.Module):
    """Автоматизирует работу с Iris Chat Manager"""

    strings = {"name": "Irisfarm"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "iris_type",
                "Классический ирис🔵",
                "Выбор ириса",
                validator=loader.validators.Choice([
                    "Чёрный ирис⚫",
                    "Фиолетовый ирис🟣",
                    "Классический ирис🔵",
                    "Жёлтый ирис🟡",
                    "Белый ирис⚪"
                ])
            ),
        )
        self.iris_map = {
            "Чёрный ирис⚫": "iris_black_bot",
            "Фиолетовый ирис🟣": "iris_dp_bot",
            "Классический ирис🔵": "iris_cm_bot",
            "Жёлтый ирис🟡": "iris_bs_bot",
            "Белый ирис⚪": "iris_moon_bot"
        }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.farm_status = self.db.get("Irisfarm", "status", {})

        for mode in ["chat", "bot"]:
            if self.farm_status.get(mode) and (
                mode != "chat" or self.farm_status.get("chat_id")
            ):
                asyncio.create_task(self._farm_loop(mode, self.farm_status.get("chat_id")))

    def _get_iris_bot(self):
        iris_type = self.config["iris_type"]
        return f"@{self.iris_map.get(iris_type, 'iris_cm_bot')}"

    async def farmcmd(self, message):
        """- вкл/выкл фарму в текущем чате"""
        if self.farm_status.get("chat"):
            self.farm_status["chat"] = False
            self.farm_status["chat_id"] = None
            self.farm_status.pop("chat_next_time", None)
            self.db.set("Irisfarm", "status", self.farm_status)
            await utils.answer(message, "<emoji document_id=5420323339723881652>⚠️</emoji> <b>Фарма в чате остановлена.</b>")
        else:
            self.farm_status["chat"] = True
            self.farm_status["chat_id"] = message.chat.id
            self.farm_status["chat_next_time"] = time.time() + 5
            self.db.set("Irisfarm", "status", self.farm_status)
            await utils.answer(message, "<b>Фарма ☢️IC в чате запущена.</b>")
            asyncio.create_task(self._farm_loop("chat", message.chat.id))
        await asyncio.sleep(3)
        await message.delete()

    async def farmiriscmd(self, message):
        """- вкл/выкл фарму в лс бота"""
        if self.farm_status.get("bot"):
            self.farm_status["bot"] = False
            self.farm_status.pop("bot_next_time", None)
            self.db.set("Irisfarm", "status", self.farm_status)
            await utils.answer(message, "<emoji document_id=5420323339723881652>⚠️</emoji> <b>Фарма в лс бота остановлена.</b>")
        else:
            self.farm_status["bot"] = True
            self.farm_status["bot_next_time"] = time.time() + 5
            self.db.set("Irisfarm", "status", self.farm_status)
            await utils.answer(message, f"<b>Фарма ☢️IC в ЛС @{self.iris_map[self.config['iris_type']]} запущена.</b>")
            asyncio.create_task(self._farm_loop("bot"))
        await asyncio.sleep(3)
        await message.delete()

    async def _farm_loop(self, mode, chat_id=None):
        key = f"{mode}_next_time"
        while self.farm_status.get(mode):
            now = time.time()
            next_time = self.farm_status.get(key, now)
            wait_time = max(0, next_time - now)

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            try:
                target = chat_id if mode == "chat" and chat_id else self._get_iris_bot()
                msg = await self.client.send_message(target, "Фарма")

                async for response in self.client.iter_messages(target, reply_to=msg.id, limit=5):
                    text = response.raw_text.lower()

                    if re.search(r"✅\s*<b>зач[её]т!?</b>", text, re.IGNORECASE):
                        self.farm_status[key] = time.time() + 14700
                        break

                    if re.search(r"❌\s*незач[её]т!?", text, re.IGNORECASE) and re.search(r"следующ[а-я]*\s+добыча\s+через", text, re.IGNORECASE):
                        minutes = hours = seconds = 0
                        if res := re.search(r"(\d+)\s*час", text):
                            hours = int(res.group(1))
                        if res := re.search(r"(\d+)\s*мин", text):
                            minutes = int(res.group(1))
                        if res := re.search(r"(\d+)\s*сек", text):
                            seconds = int(res.group(1))

                        delay = hours * 3600 + minutes * 60 + seconds + 5
                        self.farm_status[key] = time.time() + max(delay, 120)
                        break

                self.db.set("Irisfarm", "status", self.farm_status)

            except Exception:
                await asyncio.sleep(10)
