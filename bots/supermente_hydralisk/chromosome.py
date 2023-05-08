from random import randint
from random import random


class Chromosome(object):
    def __init__(self):
        self.Chromosome = []
        self.Score = 0
        self.ChromosomeLength = 0
        self.TiempoAtaque = 0


    def InitRandom(self, genes, chromosomeLength):
        self.Chromosome = []
        self.Score = 0
        self.ChromosomeLength = 0
        self.TiempoAtaque = 0
        self.ChromosomeLength = chromosomeLength
        for i in range(chromosomeLength):
            self.Chromosome.append(genes[randint(0, len(genes) - 1)])
    
    def Mutate(self, mutationRate, genes):
        for i in range(len(self.Chromosome)):
            if random() < mutationRate:
                randnum = randint(0, len(genes) - 1)
                #Evita que se mute al mismo gen
                while self.Chromosome[i] == genes[randnum]:
                    randnum = randint(0, len(genes) - 1)
                print("¡Mutación random detectada! Se va a cambiar el Gen:", self.Chromosome[i], " por el Gen:", genes[randnum], '. El número de la cadena que se va a cambiar es:', i)
                self.Chromosome[i] = genes[randnum]
        while len(self.Chromosome) < self.ChromosomeLength:
            randnum = randint(0, len(genes) - 1)
            self.Chromosome.append(genes[randnum])

    def CheckChromosome(self, genes):
        self.Score = 0 
        while len(self.Chromosome) < self.ChromosomeLength:
            randnum = randint(0, len(genes) - 1)
            # print("Random Mutate es ",  randnum)
            self.Chromosome.append(genes[randnum])