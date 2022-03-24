import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)


import random
try:
    from fuzzywuzzy import fuzz
except:
    fuzz = lambda a,b: None
import re

import cfgBoi as cfg

POPULATION_SIZE = 1000
MUTATION_RATE = .1

GENES = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'_, -.()<>?{[]}*'''

RAW_TEXT = '''Jeremiah O'Connor... 22.2... oe eee eee eee eee ee cneeee reas May 1, 1856.
Peter Smith.................-.. ee nena April 27, 1857.
Cseorge SION gis x suse ceo am wae wo wo was ER Rice wn as oem me as cen ene aoe gi ce me April 16, 1873.
John Winklemaan. ...............2.--006 ee ee ee November 2, 18
Pred. SHEClOW os cne oie 0 as os ow ow sais we ew A we RE led hee May ts, 1878.
Michael KOSS. «os 0 cs200 sen mee niece os see Gees we ees woe wR oe Sow BOR Sw June 11, 1878.
Sebastian: Wiester, «ass one 220 om ce nom meee oom 6 ame ws Oe Bae ow November 13, |
John O’Brien. ................ |e oe ee mse we mae ra A eS a Hw April 20, 1880.
Charles Bock. 2.222.020. cece eee ee eee cece ee cette nee eens May 7, 1880.
Fred. Bender. ...... 0.2.02 ccc ccc eee cee cent cence eet cneceeeees May 7, 1880.
Leonard Beyer ......... 0. ccc cece ere cece cece nee tant eeeenes May 7, 1880.
Charles Hake. .... 2.22... 2 0. cece e cece eee ee cece emer ee eeneeene May 7, 1880.'''

TARGET = '''Jerimiah O'Connor
Peter Smith
Cseorge SION
John Winklemann
Pred. SHEClOW
Michael KOSS
Sebastian: Wiester
John O’Brien
Charles Bock
Fred. Bender
Leonard Beyer
Charles Hake'''

class Individual(object):
    chromosome = None
    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.fitness, self.precise = self.calcFitness()

    @classmethod
    def mutatedGenes(self):
        global GENES
        return random.choice(GENES)

    @classmethod
    def createGnome(self):
        global TARGET
        return cfg.regexCFG.gen_random_convergent('S')

    def mate(self, other):
        child = ''
        for gp1, gp2 in zip(self.chromosome, other.chromosome):
            prob = random.random()
            p1 = (1 - MUTATION_RATE) / 2
            p2 = 1 - MUTATION_RATE

            if prob < p1:
                child = child + gp1
            elif prob < p2:
                child = child + gp2
            else:
                child = child + self.mutatedGenes()

        return Individual(child)

    def calcFitness(self):
        global TARGE, RAW_TEXT
        outputString = ''
        for line in RAW_TEXT.split('\n'):
            try:
                match = re.match(self.chromosome, line)
            except:
                match = None

            if match is not None:
                try:
                    outputString = outputString + match[0] + '\n'
                except:
                    pass
        fuzzScore = fuzz.ratio(outputString, TARGET)
        preciseScore = len(outputString)
        for i in range(len(outputString)):
            if outputString[i] != TARGET[i]:
                preciseScore -= 1
        preciseScore *= 100 / len(TARGET)
        return (preciseScore + fuzzScore) / 2, preciseScore

generation = 1
goodRegex = r'^(?P<first>[A-C][a-z]+)[ .]{1,2}?(?P<last>[A-Za-z]+)'
population = []
for i in range(POPULATION_SIZE - len(population)):  # can start with people in population already
    population.append(Individual(Individual.createGnome()))

while True:
    population = sorted(population, key = lambda x: x.fitness, reverse = True)

    if population[0].fitness >= 100 or population[0].precise >= 100:
        break
    if generation >= 300:
        break

    newPopulation = list()
    eliteCutoff = int(.1 * POPULATION_SIZE)
    newPopulation.extend(population[:eliteCutoff])
    remainderOfPop = POPULATION_SIZE - eliteCutoff

    mateable = int(.5 * POPULATION_SIZE)
    for i in range(remainderOfPop):
        parent1 = random.choice(population[:mateable])
        parent2 = random.choice(population[:mateable])
        newPopulation.append(parent1.mate(parent2))
    population = newPopulation

    if generation % 20 == 0:
        print("Generation: {}\tString: {}\tFitness: {}\tPreciseScore: {}".
              format(generation,"".join(population[0].chromosome),
                     population[0].fitness, population[0].precise))

    generation += 1

print('END:', generation, '\tString:', population[0].chromosome,
      '\tFitness:', population[0].fitness, '\tPreciseScore:', population[0].precise)

        


        







    
