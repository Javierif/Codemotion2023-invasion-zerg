from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units


class Supermente(BotAI):
    botScore = 0
    gameTime = 500

    AttactAt = 0
    ConTodo = False

    chromosome = []
    stateStats = []
    geneNumber = 0

    async def on_step(self, iteration: int):
        if self.time > self.gameTime:
            print("Game Over!")
            try:
                await self.client.leave()
            except:
                print("Error al salir del juego")
                pass
        if self.time > self.AttactAt:
            await self.AtacarConTodo()
            cantidadTropas = self.units(UnitTypeId.ZERGLING).amount + self.units(UnitTypeId.DRONE).amount
            if cantidadTropas == 0:
                await self.client.leave()
        else:
            # await self.recogerRecursos(True)
            # await self.atacar()

            # print("Orden a ejecutar es " + self.chromosome[self.geneNumber] + " GEN Nº: " + str(self.geneNumber))
            if self.geneNumber < len(self.chromosome):
                if self.chromosome[self.geneNumber] == "Trabajador":
                    await self.creaTrabajador()                        
                elif self.chromosome[self.geneNumber] == "Overlord":
                    await self.creaOverlord()
                elif self.chromosome[self.geneNumber] == "Zerling":
                    await self.crearZerling()

    async def creaTrabajador(self):
        larvas = self.units(UnitTypeId.LARVA).amount
        if larvas > 0  and self.can_afford(UnitTypeId.DRONE) and self.supply_left > 0:
            self.train(UnitTypeId.DRONE)
            self.geneNumber += 1
            # print("Gene Trabajador: " + str(self.geneNumber)+ " GEN Nº: " + str(self.geneNumber))
            return True
        # elif self.supply_left == 0 and larvas > 0 and self.can_afford(UnitTypeId.OVERLORD):
        #     self.train(UnitTypeId.OVERLORD)
        return False

    async def creaOverlord(self):
        larvas = self.units(UnitTypeId.LARVA).amount
        if larvas > 0 and self.can_afford(UnitTypeId.OVERLORD):
            self.geneNumber += 1            
            self.train(UnitTypeId.OVERLORD)
            # print("Gene Overlord: " + str(self.geneNumber)+ " GEN Nº: " + str(self.geneNumber))
            return True
        return False

    async def crearZerling(self):
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).amount
            + self.already_pending(UnitTypeId.SPAWNINGPOOL)
            == 0
        ):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                base = self.structures(UnitTypeId.HATCHERY)[0]
                # Buscamos un lugar libre para construir el spawning pool
                for d in range(4, 15):
                    pos: Point2 = base.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.SPAWNINGPOOL, pos):
                        drone: Unit = self.workers.closest_to(pos)
                        drone.build(UnitTypeId.SPAWNINGPOOL, pos)
            return False

        larvas = self.units(UnitTypeId.LARVA).amount
        if larvas > 0 and self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0 and self.can_afford(UnitTypeId.ZERGLING) and self.supply_left > 0:
            self.train(UnitTypeId.ZERGLING, 1)
            self.geneNumber += 1            
            # print("Gene Zerling: " + str(self.geneNumber)+ " GEN Nº: " + str(self.geneNumber))
            return True
        return False

    async def buildHydralisk(self):
        if (
            self.structures(UnitTypeId.HYDRALISKDEN).amount
            + self.already_pending(UnitTypeId.HYDRALISKDEN)
            == 0
        ):
            if self.can_afford(UnitTypeId.HYDRALISKDEN):
                base = self.structures(UnitTypeId.HATCHERY)[0]
                # Buscamos un lugar libre para construir el spawning pool
                for d in range(4, 15):
                    pos: Point2 = base.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.HYDRALISKDEN, pos):
                        drone: Unit = self.workers.closest_to(pos)
                        drone.build(UnitTypeId.HYDRALISKDEN, pos)
            return False

        if self.can_afford(UnitTypeId.HYDRALISK) and self.supply_left > 0:
            self.train(UnitTypeId.HYDRALISK, 1)
            self.geneNumber += 1
            return True

    async def atacar(self):
        groundCritters = []
        allCritters = []

        if not self.AtacarConTodo:
            groundCrittersPointer = 0
            allCrittersPointer = 0

            if len(self.enemy_units) > 0:
                for nexus in self.structures(UnitTypeId.HATCHERY):
                    for enemy in self.enemy_units.not_flying.closer_than(15.0, nexus):
                        groundCritters.append(enemy)
                    for enemy in self.enemy_units.closer_than(15.0, nexus):
                        allCritters.append(enemy)
            if len(self.enemy_units) > 0:
                for zerling in self.units(UnitTypeId.ZERGLING):
                    if len(groundCritters) > 0:
                        zerling.attack(groundCritters[groundCrittersPointer])
                        groundCrittersPointer += 1
                        if groundCrittersPointer >= len(groundCritters):
                            groundCrittersPointer = 0

            if len(allCritters) > 0:
                for Hydralisk in self.units(UnitTypeId.HYDRALISK):
                    Hydralisk.attack(allCritters[allCrittersPointer])
                    allCrittersPointer += 1
                    if allCrittersPointer >= len(allCritters):
                        allCrittersPointer = 0
        else:
            for z in self.units(UnitTypeId.ZERGLING).idle:
                if len(self.enemy_units.not_flying) > 0:
                    z.attack(self.enemy_units.not_flying.closest_to(z))
            for z in self.units(UnitTypeId.HYDRALISK).idle:
                if len(self.enemy_units) > 0:
                    z.attack(self.enemy_units.closest_to(z))

    async def AtacarConTodo(self):
        if not self.ConTodo:
            # print("Atacar con todo")
            base_enemiga = self.enemy_start_locations[0]
            for unidad in self.units.not_structure:
                unidad.attack(base_enemiga)
            self.ConTodo = True
        await self.atacar()

    async def expandirse(self):
        if self.can_afford(UnitTypeId.HATCHERY):
            await self.expand_now()
            return True
        return False

    async def recogerRecursos(self, priorizarGas):
        owned_bases = self.townhalls
        pool_trabajadores = []
        actions = []

        if priorizarGas:
            pool_trabajadores.extend(self.workers.idle)

            for idle_worker in pool_trabajadores:
                if len(self.gas_buildings) > 0:
                    print("GetGass")
                    gb = self.gas_buildings.closest_to(idle_worker)
                    idle_worker.gather(gb)
        else:
            for idle_worker in self.workers.idle:
                mf = self.state.mineral_field.closest_to(idle_worker)
                idle_worker.gather(mf)
