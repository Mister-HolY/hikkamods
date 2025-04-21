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

_bot = "@iris_cm_bot"

class IrisfarmMod(loader.Module):
    """Автоматизирует работу с Iris Chat Manager"""

    strings = {"name": "Irisfarm"}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.farm_status = self.db.get("Irisfarm", "status", {})  

        if self.farm_status.get("chat") and self.farm_status.get("chat_id"):
            asyncio.create_task(self._farm_loop("chat", self.farm_status["chat_id"]))
        if self.farm_status.get("bot"):
            asyncio.create_task(self._farm_loop("bot"))

    async def farmcmd(self, message):
        """- вкл/выкл фарму в текущем чате"""      
        if self.farm_status.get("chat"):
            self.farm_status["chat"] = False
            self.farm_status["chat_id"] = None
            self.db.set("Irisfarm", "status", self.farm_status)
            await utils.answer(message, "<emoji document_id=5420323339723881652>⚠️</emoji> <b>Фарма в чате остановлена.</b>")
        else:
            self.farm_status["chat"] = True
            self.farm_status["chat_id"] = message.chat.id
            self.db.set("Irisfarm", "status", self.farm_status)
            await utils.answer(message, "<b>Фарма ☢️IC в чате запущена.</b>")
            asyncio.create_task(self._farm_loop("chat", message.chat.id))
            await asyncio.sleep(3)
            await message.delete()

    async def farmiriscmd(self, message):
        """- вкл/выкл фарму в лс бота"""
        if self.farm_status.get("bot"):
            self.farm_status["bot"] = False
            self.db.set("Irisfarm", "status", self.farm_status)
            await utils.answer(message, "<emoji document_id=5420323339723881652>⚠️</emoji> <b>Фарма в лс бота остановлена.</b>")
        else:
            self.farm_status["bot"] = True
            self.db.set("Irisfarm", "status", self.farm_status)
            await utils.answer(message, "<b>Фарма ☢️IC в лс бота запущена.</b>")
            asyncio.create_task(self._farm_loop("bot"))

    async def _farm_loop(self, mode, chat_id=None):
        while self.farm_status.get(mode):
            try:
                if mode == "chat" and chat_id:
                    await self.client.send_message(chat_id, "Фарма")
                elif mode == "bot":
                    await self.client.send_message(_bot, "Фарма")
                await asyncio.sleep(14700)  
            except Exception:
                await asyncio.sleep(10)
