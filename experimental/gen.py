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
import file_analysis as analysis
import predicates as p

POPULATION_SIZE = 1000
MAX_GENERATIONS = 300
FITNESS_THRESHOLD = 70
PRECISION_THRESHOLD = 100
MUTATION_RATE = .1
PRECISION_WEIGHT = 1.2
FUZZY_WEIGHT = 2 - PRECISION_WEIGHT  # weights add up to 2 before the average

UPDATE_INTERVAL = 100

GENES = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'_, -.()<>?{[]}*'''
TERMINALS = '(?P<p> )[]A-Zaz+.*{}1234567890'

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
    def __init__(self, chromosome, derivation):
        self.chromosome = chromosome
        self.derivation = derivation
        self.fitness, self.precise = self.calcFitness()

    @classmethod
    def mutatedGenes(self):
        global GENES
        return random.choice(TERMINALS)

    @classmethod
    def createIndividual(self):
        global TARGET
        production = cfg.regexCFG.gen_random('S')
        return Individual(production[0], production[1])

    def mate(self, other):
        combinedCFG = cfg.derivedCFG(self.derivation)
        for production in other.derivation:
            combinedCFG.add_prod_tuple(production)
        childString, childDerivation = combinedCFG.gen_random('S')

        newChildString = ''
        for i in childString:
            p = random.random()
            if p < MUTATION_RATE:
                i = self.mutatedGenes()
            newChildString += i

        return Individual(childString, childDerivation)

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
        usableLen = min(len(outputString),len(TARGET))
        preciseScore = usableLen
        for i in range(usableLen):
            if outputString[i] != TARGET[i]:
                preciseScore -= 1
        preciseScore *= 100 / len(TARGET)
        return ((preciseScore*PRECISION_WEIGHT) + (fuzzScore*FUZZY_WEIGHT)) / 2, preciseScore

def main():
    global RAW_TEXT
    RAW_TEXT = analysis.cleanChars(RAW_TEXT, lambda x: p.alphaSpaceChar(x) or x=='\n')
    print(RAW_TEXT)
    generation = 1
    goodRegex = r'^(?P<first>[A-C][a-z]+)[ .]{1,2}?(?P<last>[A-Za-z]+)'
    population = []

    ELITE_CUTOFF = .1
    MATEABLE_CUTOFF = .5

    for i in range(POPULATION_SIZE - len(population)):  # can start with people in population already
        population.append(Individual.createIndividual())

    while True:
        population = sorted(population, key = lambda x: [x.fitness,x.precise], reverse = True)

        if population[0].fitness >= FITNESS_THRESHOLD or population[0].precise >= PRECISION_THRESHOLD:
            break
        if generation >= MAX_GENERATIONS:
            break

        newPopulation = list()
        eliteCutoff = int(ELITE_CUTOFF * POPULATION_SIZE)
        newPopulation.extend(population[:eliteCutoff])
        remainderOfPop = POPULATION_SIZE - eliteCutoff

        mateable = int(MATEABLE_CUTOFF * POPULATION_SIZE)
        for i in range(remainderOfPop):
            parent1 = random.choice(population[:mateable])
            parent2 = random.choice(population[:mateable])
            newPopulation.append(parent1.mate(parent2))
        population = newPopulation

        if generation % UPDATE_INTERVAL == 0:
            avgFitness = 0
            avgPrecise = 0
            for i in population:
                avgFitness += i.fitness
                avgPrecise += i.precise
            avgFitness /= POPULATION_SIZE
            avgPrecise /= POPULATION_SIZE
            print('Generation:', generation, '\tString:', population[0].chromosome,
                  '\tFitness:', population[0].fitness, '\tPreciseScore:',population[0].precise,
                  '\tAvgFitness:',avgFitness, '\tAvgPrecise:',avgPrecise)

        generation += 1

    print('END:', generation)
    for individual in population[:10]:
        print('\tString:', individual.chromosome,
          '\tFitness:', individual.fitness, '\tPreciseScore:', individual.precise)
    return population

if __name__ == '__main__':
    main()


        







    
