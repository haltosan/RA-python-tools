from collections import deque


class Person:
    pid = None
    immediate = list()

    def __init__(self, pid=None, immediate=None):
        if immediate is None:
            immediate = list()
        self.pid = pid
        self.immediate = immediate


'''
gma/gpa -> dad, joe
dad/mom -> abby, logan, jonah, me, owen
joe/susan -> spencer, olivia, calvin, wesley

gma 0
gpa 1
joe 2
dad 3
mom 4
jonah 5
me 6
susan 7
olivia 8
'''

gma = Person(0, [1, 2, 3])
gpa = Person(1, [0, 2, 3])
joe = Person(2, [0, 1, 3, 7, 8])
dad = Person(3, [0, 1, 2, 4, 5, 6])
mom = Person(4, [0, 1, 3, 5, 6])
jonah = Person(5, [3, 4, 6])
me = Person(6, [3, 4, 5])
susan = Person(7, [2, 8])
olivia = Person(8, [2, 7])

people = {0: gma, 1: gpa, 2: joe, 3: dad, 4: mom, 5: jonah, 6: me, 7: susan, 8: olivia}  # key is pid, value is person

###algorithm start###
'''
get set of PIDs to work with (L1)
get pids for all immediate relatives (undirected, no repeats with L1 or L2)
get pids for all L2 immediate relatives (1 level only)
iter until no more pids OR L7
tag L1 pid to each person L2+
stop once L1 has tagged 150+
=group of connected pids, L1, size=
'''

L1 = me.pid  # arbitrary starting point

tree = set()

L2 = me.immediate
level = 1
while True:
    level += 1
    L3 = []
    if level >= 7:
        break
    if len(tree) >= 150:
        break
    for i in L2:
        if i in tree:
            pass
        else:
            L3.append(i)
        tree.add(i)
    L2 = L3.copy()
    del L3
'''
l1 = me
l2 = me.rels
-
 l3 = {l2 rels : rel not member of tree
 visited = L2
 l2 = l3
'''
