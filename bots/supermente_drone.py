from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI

#Version 0.0.1
class Supermente(BotAI):
    async def on_step(self, iteration: int):
        if iteration == 0:
            #Guardamos en una variable la localización de la base enemiga
            base_enemiga = self.enemy_start_locations[0]
            #Enviamos un mensaje para atemorizar al enemigo
            await self.client.chat_send("Soy la supermente, doblegaros ante mi",False) 
            #Enviamos todas nuestras unidades a atacar la base enemiga
            for worker in self.workers:
                worker.attack(base_enemiga)