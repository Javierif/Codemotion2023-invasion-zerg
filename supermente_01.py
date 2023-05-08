from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from bots.supermente_drone import Supermente
from bots.supermente_zerling import Supermente
from bots.supermente_hydralisk.supermente_hydralisk import Supermente
from bots.supermente_hydralisk.geneticAlgorithm import GeneticAlgorithm
from bots.supermente_hydralisk.chromosome import Chromosome
import pandas as pd
import random


MaxGenerations = 4
CantidadCromosomas = 5
TimeAtacarMin = 200
TiempoMaximoPartida = 800


ga = GeneticAlgorithm()
ga.Init(CantidadCromosomas)

# introducción de Genes a mano
# ga.Population[0].Chromosome = ['Overlord','Trabajador','Overlord']
# ga.Population[0].TiempoAtaque = 268

for generation in range(MaxGenerations):
    print("Generación: " + str(generation))
    for member in range(CantidadCromosomas):
        print("Member: " + str(member))
        bot = Supermente()
        # Checkeamos que el cromosoma sea válido
        ga.Population[member].CheckChromosome(ga.Genes)
        # Asignamos el cromosoma al bot
        bot.chromosome = ga.Population[member].Chromosome
        bot.gameTime = TiempoMaximoPartida
        # Asignamos el tiempo de ataque al bot solo si es la primera vez
        if(ga.Population[member].TiempoAtaque == 0):
            #Le quitamos 120 para que en el último segundo no ataque, si no que tenga tiempo de atacar
            ga.Population[member].TiempoAtaque = random.randint(TimeAtacarMin, TiempoMaximoPartida-120)
        bot.AttactAt = ga.Population[member].TiempoAtaque
        # print("Cromosoma implantado: " + str(bot.chromosome)) - Para debug

        #Ejecutamos el juego
        try:
             game = run_game(maps.get("AcropolisLE"), [
                Bot(Race.Zerg, bot),
                Computer(Race.Terran, Difficulty.Easy)
            ], realtime=False)
        except:
            print("Error")
        #Fin Partida

        #Sacamos las estadísticas
        for stat in bot.state.score.summary:
            # print("Stat = " ,stat[0],"----",stat[1])
            if(stat[0] == "score"):
                print("Stat = " ,stat[0],"----",stat[1])
                ga.Population[member].Score = stat[1]
            if(stat[0] == "killed_value_structures"):
                print("Stat = " ,stat[0],"----",stat[1])
                ga.Population[member].Score = ga.Population[member].Score +stat[1]*10
            if(stat[0] == "killed_value_units"):
                print("Stat = " ,stat[0],"----",stat[1])
                ga.Population[member].Score = ga.Population[member].Score +stat[1]*2

        #Asignamos los cronosomas que hemos usado
        ga.Population[member].Chromosome = ga.Population[member].Chromosome[:bot.geneNumber]
        #Guardamos cuando atacamos
        ga.Population[member].TiempoAtaque = bot.AttactAt
        #Guardamos si hemos ganado o perdido
        ga.Population[member].Game = str(game)
        #Si hemos ganado le sumamos 100000 puntos a Gryffindor
        if(str(ga.Population[member].Game) != "Result.Defeat"):
            ga.Population[member].Score = ga.Population[member].Score+100000

        print("Score: " + str(ga.Population[member].Score))
        print("Chromosome: " + str(ga.Population[member].Chromosome))
        print("Tiempo Ataque: " + str(ga.Population[member].TiempoAtaque))
        print("Game: " + str(ga.Population[member].Game))



    print("----------------------- Sección de scores x Generación -----------------------")
    print("Generation: " + str(ga.Generation))
    chromos = []
    scores = []
    tiemposAtaque = []
    victorias = []

    for member in range(CantidadCromosomas):
        print("Member: " + str(member))
        print("Score: " + str(ga.Population[member].Score))
        chromos.append(ga.Population[member].Chromosome)
        scores.append(ga.Population[member].Score)
        tiemposAtaque.append(ga.Population[member].TiempoAtaque)
        victorias.append(ga.Population[member].Game)

    #Procesamos los resultados
    ga.ProcessResults()
    #Evolucionamos nuestro modelo
    ga.Evolve()

    #Guardamos los datos en un csv

    df_chromos = pd.DataFrame(chromos)
    df_chromos.to_csv(f"./dataset/supermente_01/chromos/chromos_{ga.Generation}.csv")

    df_scores = pd.DataFrame(scores)
    df_scores.to_csv(f"./dataset/supermente_01/scores/scores_{ga.Generation}.csv")

    df_tiemposAtaque = pd.DataFrame(tiemposAtaque)
    df_tiemposAtaque.to_csv(f"./dataset/supermente_01/tiemposAtaque/tiemposAtaque_{ga.Generation}.csv")

    df_victorias = pd.DataFrame(victorias)
    df_victorias.to_csv(f"./dataset/supermente_01/victorias/victorias_{ga.Generation}.csv")



    

    dataFrame = pd.DataFrame(ga.Results)
    dataFrame.to_csv(f"./dataset/supermente_01/Evolution.csv")
    ChFrame = pd.DataFrame(ga.TopChromosomes)
    ChFrame.to_csv(f"./dataset/supermente_01/TopChromosomes.csv")