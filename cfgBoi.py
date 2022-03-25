import random

def weighted_choice(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

class CFG(object):
    def __init__(self):
        self.prod = dict()

    def add_prod(self, lhs, rhs):
        """ Add production to the grammar. 'rhs' can
            be several productions separated by '|'.
            Each production is a sequence of symbols
            separated by whitespace.

            Usage:
                grammar.add_prod('NT', 'VP PP')
                grammar.add_prod('Digit', '1|2|3|4')
        """
        prods = rhs.split('|')
        for prod in prods:
            if lhs not in self.prod:
                self.prod[lhs] = list()
            self.prod[lhs].append(tuple(prod.split()))
            
    def add_prod_tuple(self, prod):
        rhs = prod[1]
        lhs = prod[0]
        self.add_prod(lhs, ' '.join(rhs))

    def remove_prod(self, lhs, rhs):
        prods = rhs.split('|')
        for prod in prods:
            if lhs in self.prod:
                del self.prod[lhs]

    def gen_random(self, symbol, cfactor=0.25, pcount=dict(), productions = list()):
        """ Generate a random sentence from the
          grammar, starting with the given symbol.

          Uses a convergent algorithm - productions
          that have already appeared in the
          derivation on each branch have a smaller
          chance to be selected.

          cfactor - controls how tight the
          convergence is. 0 < cfactor < 1.0

          pcount is used internally by the
          recursive calls to pass on the
          productions that have been used in the
          branch.
        """
        sentence = ''

        # The possible productions of this symbol are weighted
        # by their appearance in the branch that has led to this
        # symbol in the derivation
        #
        weights = []
        for prod in self.prod[symbol]:
            if prod in pcount:
                weights.append(cfactor ** (pcount[prod]))
            else:
                weights.append(1.0)

        rand_prod = self.prod[symbol][weighted_choice(weights)]
        if symbol == 'S':
            productions = list()
        productions.append((symbol, rand_prod))

        # pcount is a single object (created in the first call to
        # this method) that's being passed around into recursive
        # calls to count how many times productions have been
        # used.
        # Before recursive calls the count is updated, and after
        # the sentence for this call is ready, it is rolled-back
        # to avoid modifying the parent's pcount.
        #
        if rand_prod not in pcount:
            pcount[rand_prod] = 0
        pcount[rand_prod] += 1

        for sym in rand_prod:
            # for non-terminals, recurse
            if sym in self.prod:
                both = self.gen_random(
                                  sym,
                                  cfactor=cfactor,
                                  pcount=pcount, productions=productions)
                sentence += both[0]
                productions = productions
            else:
                sentence += sym

        # backtracking: clear the modification to pcount
        pcount[rand_prod] -= 1
        return sentence.replace('_', ' '), productions

    def fromProduction(self, productions):
        sent = productions[0][0]
        for production in productions:
            sent = sent.replace(production[0], ' '.join(production[1]), 1)
        return sent.replace(' ','').replace('_', ' ')


def derivedCFG(productions):
    newCFG = CFG()
    for production in productions:
        newCFG.add_prod_tuple(production)
    return newCFG

regexCFG = CFG()
regexCFG.add_prod('S', '^ NGROUP INFO NGROUP2 INFO')
regexCFG.add_prod('NGROUP', '(?P<p> INFO )')
regexCFG.add_prod('NGROUP2', '(?P<p2> INFO )')
regexCFG.add_prod('INFO', 'INFO INFO | CHARS MODIFY')
regexCFG.add_prod('CHARS', '[ CHARS ] | CHARS CHARS | A-Z | a-z | _')
regexCFG.add_prod('MODIFY', '+ | . | * | ? | { N }')
regexCFG.add_prod('N', '1, n1 | 2, n2 | 3, n3 | 4, n4 | 5, n5 | 6, n6 | 7, n7 | 8, n8 | 0, n0')
regexCFG.add_prod('n0', '1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9')
regexCFG.add_prod('n1', '2 | 3 | 4 | 5 | 6 | 7 | 8 | 9')
regexCFG.add_prod('n2', '3 | 4 | 5 | 6 | 7 | 8 | 9')
regexCFG.add_prod('n3', '4 | 5 | 6 | 7 | 8 | 9')
regexCFG.add_prod('n4', '5 | 6 | 7 | 8 | 9')
regexCFG.add_prod('n5', '6 | 7 | 8 | 9')
regexCFG.add_prod('n6', '7 | 8 | 9')
regexCFG.add_prod('n7', '8 | 9')
regexCFG.add_prod('n8', '9')
