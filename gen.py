# Python3 program to create target string, starting from
# random string using Genetic Algorithm

import random
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

import cfgBoi

# Number of individuals in each generation
POPULATION_SIZE = 100
MUTATION_RATE = .2
MAX_RETRY = 5

# Valid genes
GENES = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890, -.()<>?{[]}*'''

# Target string to be generated
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
	'''
	Class representing individual in population
	'''
	def __init__(self, chromosome):
		self.chromosome = chromosome
		self.fitness, self.precise = self.cal_fitness()

	@classmethod
	def mutated_genes(self):
		'''
		create random genes for mutation
		'''
		global GENES
		gene = random.choice(GENES)
		return gene

	@classmethod
	def create_gnome(self):
		'''
		create chromosome or string of genes
		'''
		global TARGET
		gnome_len = len(TARGET)
		return [self.mutated_genes() for _ in range(gnome_len)]

	def mate(self, par2):
		'''
		Perform mating and produce new offspring
		'''

		# chromosome for offspring
		child_chromosome = []
		for gp1, gp2 in zip(self.chromosome, par2.chromosome):

			# random probability
			prob = random.random()
			p1 = (1 - MUTATION_RATE) / 2
			p2 = 1 - MUTATION_RATE


			if prob < p1:
				child_chromosome.append(gp1)


			elif prob < p2:
				child_chromosome.append(gp2)

			# otherwise insert random gene(mutate),
			# for maintaining diversity
			else:
				child_chromosome.append(self.mutated_genes())

		# create new Individual(offspring) using
		# generated chromosome for offspring
		return Individual(child_chromosome)

	def cal_fitness(self):
		'''
		Calculate fitness score, it is the number of
		characters in string which differ from target
		string.
		'''
		global TARGET, RAW_TEXT
		outputString = ''
		for line in RAW_TEXT.split('\n'):
			for i in range(MAX_RETRY):
				try:
					match = re.match(self.chromosome, line)
					break
				except:
					match = None
			if match is None:
				pass
			else:
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
		preciseScore = fuzzScore
		return (preciseScore + fuzzScore) / 2, preciseScore

# Driver code
def main():
	global POPULATION_SIZE

	#current generation
	generation = 1

	found = False
	population = [Individual(r'^(?P<first>[A-C][a-z]+)[ .]{1,2}?(?P<last>[A-Za-z]+)'),
                      Individual(r'^(?P<first>[P-Z][a-z]+)[ .]{1,2}?(?P<last>[A-Za-z]+)')]

	# create initial population
	for _ in range(POPULATION_SIZE - len(population)):
				gnome = Individual.create_gnome()
				population.append(Individual(gnome))

	while not found:

		# sort the population in increasing order of fitness score
		population = sorted(population, key = lambda x:x.fitness, reverse = True)
		# if the individual having lowest fitness score ie.
		# 0 then we know that we have reached to the target
		# and break the loop
		if population[0].fitness >= 100 or population[0].precise >= 100:
			found = True
			break
		if generation >= 300:
			break

		# Otherwise generate new offsprings for new generation
		new_generation = []

		# Perform Elitism, that mean 10% of fittest population
		# goes to the next generation
		s = int(.10*POPULATION_SIZE)
		new_generation.extend(population[:s])

		# From 50% of fittest population, Individuals
		# will mate to produce offspring
		s = int(.90*POPULATION_SIZE)
		matable = int(.5 * POPULATION_SIZE)
		for _ in range(s):
			parent1 = random.choice(population[:matable])
			parent2 = random.choice(population[:matable])
			child = parent1.mate(parent2)
			new_generation.append(child)

		population = new_generation
		if generation % 20 == 0:
			print("Generation: {}\tString: {}\tFitness: {}\tPreciseScore: {}".format(generation,"".join(population[0].chromosome),population[0].fitness, population[0].precise))

		generation += 1

	
	print("Generation: {}\tString: {}\tFitness: {}".\
		format(generation,
		"".join(population[0].chromosome),
		population[0].fitness))

if __name__ == '__main__':
	main()
