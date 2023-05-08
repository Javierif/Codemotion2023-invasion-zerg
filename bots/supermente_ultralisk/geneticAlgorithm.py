from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from bots.supermente_hydralisk.chromosome import Chromosome
from random import random

# Version 0.0.1
class GeneticAlgorithm():
    
    ChromosomeLength = 2000
    Genes = ['Trabajador', 'Overlord', 'Zerling', 'Hydralisk', 'Expandirse']

    Population = []
    Results = []
    TopChromosomes = []
    Generation = 0



    def Init(self,cantidadCromosomas):
        for i in range(cantidadCromosomas):
            chromo = Chromosome()
            chromo.InitRandom(self.Genes, self.ChromosomeLength)
            self.Population.append(chromo)

    def Evolve(self):
        print("Comenzando la evolución")

        self.Selection()

        #obtengo el mejor cromosoma
        championChromo = self.Population[0]

        #obtengo el peor cromosoma
        worstChromo = self.Population[-1]
        #lo elimino y genero uno nuevo
        worstChromo.InitRandom(self.Genes, self.ChromosomeLength)
        self.Population[-1] = worstChromo

        #obtengo el segundo peor cromosoma y le asigno el mejor antes de mutarlo
        secondWorstChromo = self.Population[-2]
        secondWorstChromo =  championChromo
        self.Population[-2] = secondWorstChromo

        #Muto el mejor cromosoma
        championChromo.Mutate(0.1,self.Genes)
        self.Population[0] = championChromo

        


        self.Generation += 1

    def Selection(self):
        print("Selection")
        self.Population = sorted(self.Population,key=lambda x: x.Score)
        self.Population.reverse()

        print("Mejor Genética:")
        print(self.Population[0].Chromosome)
        print(self.Population[0].Score)
        self.TopChromosomes.append({'Ch':self.Population[0].Chromosome})

        print("Peor Genética:")
        print(self.Population[-1].Chromosome)
        print(self.Population[-1].Score)
    
    def ProcessResults(self):
        print("ProcessResults")
        total = 0.0
        max = 0.0
        for i in range(len(self.Population)):
            total += self.Population[i].Score
            if self.Population[i].Score > max:
                max = self.Population[i].Score
        average = total / len(self.Population)
        print("Average: " + str(average))
        print("Max: " + str(max))
        self.Results.append({'Generation':self.Generation,'ScoreAvg':average, 'ScoreMax':max})

        print(self.Results)