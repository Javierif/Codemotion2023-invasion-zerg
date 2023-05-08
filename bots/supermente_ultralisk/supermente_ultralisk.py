from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units

import random
from contextlib import suppress
from typing import Set


class Supermente(BotAI):
    botScore = 0
    gameTime = 500

    AttactAt = 0
    ConTodo = False

    chromosome = []
    stateStats = []
    geneNumber = 0

    minTropas = 0

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
            # Dificil remontada si nos han eliminado todo
            cantidadTropas = self.units(UnitTypeId.ZERGLING).amount + self.units(UnitTypeId.DRONE).amount + self.units(UnitTypeId.HYDRALISK).amount
            if cantidadTropas == 0:
                await self.client.leave()

        if self.structures(UnitTypeId.HATCHERY).amount + self.structures(UnitTypeId.LAIR).amount == 0:
            await self.client.leave()
        try:
            # await self.recogerRecursos(True)
            await self.atacar()
            await self.distribute_workers()

            # print("Orden a ejecutar es " + self.chromosome[self.geneNumber] + " GEN Nº: " + str(self.geneNumber))
            if self.geneNumber < len(self.chromosome):
                if self.chromosome[self.geneNumber] == "Trabajador":
                    await self.creaTrabajador()                        
                elif self.chromosome[self.geneNumber] == "Overlord":
                    await self.creaOverlord()
                elif self.chromosome[self.geneNumber] == "Zerling":
                    await self.crearZerling()
                elif self.chromosome[self.geneNumber] == "Hydralisk":
                    await self.crearHydralisk()
                elif self.chromosome[self.geneNumber] == "Expandirse":
                    await self.expandirse()
        except:
            print("Error en el on_step")
            pass

    async def creaTrabajador(self):
        larvas = self.units(UnitTypeId.LARVA).amount
        if larvas > 0  and self.can_afford(UnitTypeId.DRONE) and self.supply_left > 0:
            self.train(UnitTypeId.DRONE)
            self.geneNumber += 1
            # print("Gene Trabajador: " + str(self.geneNumber)+ " GEN Nº: " + str(self.geneNumber))
            return True
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
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
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
        # elif self.supply_left == 0 and larvas > 0 and self.can_afford(UnitTypeId.OVERLORD):
        #     self.train(UnitTypeId.OVERLORD)
        return False

    async def crearHydralisk(self):
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).amount
            + self.already_pending(UnitTypeId.SPAWNINGPOOL)
            == 0
        ):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                # Buscamos un lugar libre para construir el spawning pool
                for d in range(4, 15):
                    pos: Point2 = base.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.SPAWNINGPOOL, pos):
                        drone: Unit = self.workers.closest_to(pos)
                        drone.build(UnitTypeId.SPAWNINGPOOL, pos)
            return False
        

        if (
            self.structures(UnitTypeId.SPAWNINGPOOL)
            and self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) < 1
        ):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                # May crash if we dont have any drones
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                for vg in self.vespene_geyser.closer_than(10, base):
                    drone: Unit = self.workers.random
                    drone.build_gas(vg)
                    break
        elif self.gas_buildings.amount == 1:
            for a in self.gas_buildings:
                if a.assigned_harvesters < a.ideal_harvesters:
                    w: Units = self.workers.closer_than(10, a)
                    if w:
                        w.random.gather(a)
        
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if self.structures(UnitTypeId.LAIR).amount == 0:
                base = self.structures(UnitTypeId.HATCHERY)[0]
            else:
                base = self.structures(UnitTypeId.LAIR)[0]
            if base.is_idle and self.structures(UnitTypeId.LAIR).amount + self.already_pending(UnitTypeId.LAIR) == 0:
                if self.can_afford(UnitTypeId.LAIR):
                    base.build(UnitTypeId.LAIR)

        if (
            self.structures(UnitTypeId.HYDRALISKDEN).amount
            + self.already_pending(UnitTypeId.HYDRALISKDEN)
            == 0
        ):
            if self.can_afford(UnitTypeId.HYDRALISKDEN):
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                # Buscamos un lugar libre para construir el spawning pool
                for d in range(4, 15):
                    pos: Point2 = base.position.towards(self.game_info.map_center, d)
                    if await self.can_place_single(UnitTypeId.HYDRALISKDEN, pos):
                        drone: Unit = self.workers.closest_to(pos)
                        drone.build(UnitTypeId.HYDRALISKDEN, pos)
            return False

        larvas = self.units(UnitTypeId.LARVA).amount
        if larvas > 0 and self.already_pending(UnitTypeId.HYDRALISKDEN) == 0 and self.can_afford(UnitTypeId.HYDRALISK) and self.supply_left > 0:
            self.train(UnitTypeId.HYDRALISK, 1)
            self.geneNumber += 1            
            # print("Gene Hydralisk: " + str(self.geneNumber)+ " GEN Nº: " + str(self.geneNumber))
            return True
        return False


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
            cantidadTropas = self.units(UnitTypeId.ZERGLING).amount + self.units(UnitTypeId.HYDRALISK).amount

            if cantidadTropas > self.minTropas:
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
                if(unidad.type_id != UnitTypeId.OVERLORD and unidad.type_id != UnitTypeId.DRONE and unidad.type_id != UnitTypeId.QUEEN):
                    unidad.attack(base_enemiga)
            self.ConTodo = True
        await self.atacar()

    async def expandirse(self):
        with suppress(AssertionError):
            if self.can_afford(UnitTypeId.HATCHERY):
                planned_hatch_locations: Set[Point2] = {placeholder.position for placeholder in self.placeholders}
                my_structure_locations: Set[Point2] = {structure.position for structure in self.structures}
                enemy_structure_locations: Set[Point2] = {structure.position for structure in self.enemy_structures}
                blocked_locations: Set[Point2] = (
                    my_structure_locations | planned_hatch_locations | enemy_structure_locations
                )
                shuffled_expansions = self.expansion_locations_list.copy()
                if self.structures(UnitTypeId.LAIR).amount == 0:
                    base = self.structures(UnitTypeId.HATCHERY)[0]
                else:
                    base = self.structures(UnitTypeId.LAIR)[0]
                closeBase: Point2 = base.position.towards(self.game_info.map_center, 5)
                #order shuffled_expansions by distance to base
                shuffled_expansions.sort(key=lambda x: x.distance_to(closeBase))

                
                for exp_pos in shuffled_expansions:
                    if exp_pos in blocked_locations:
                        continue
                    for drone in self.workers.collecting:
                        drone: Unit
                        drone.build(UnitTypeId.HATCHERY, exp_pos)
                        self.geneNumber += 1  
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
