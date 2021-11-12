from random import randint

splitTime = [5, 10]
survivalRate = 8
normalValue = 1
mutateRate = 32
mutateValue = 4
splitQueue = [0] * (splitTime[-1] + 1)

maturityTime = 5
age = [0] * (maturityTime + 1)

increaseFactor = 2
simulations = 100

p_0 = 50

def printState():
    print('splitQueue:', splitQueue, end ='\t')
    print('age:', age)

def shiftList(lst, increase = True):
    if increase:
        lst.reverse()
    for i in range(len(lst) - 1):
        if i == 0:
            lst[0] += lst[1]
        else:
            lst[i] = lst[i+1]
    lst[-1] = 0
    if increase:
        lst.reverse()
    return lst

def create(num):
    global age
    age[0] += num

def putInQueue(num):
    global splitQueue
    for i in range(num):
        splitQueue[randint(splitTime[0], splitTime[1])] += 1

def split():
    global splitQueue
    splitNum = splitQueue[0]
    splitQueue[0] = 0  # these are now going to split
    splitQueue = shiftList(splitQueue, increase=False)
    # each particle that is ready to split is given a chance to
    for chance in range(splitNum):
        if randint(1, survivalRate) == 1:
            if randint(1, mutateRate) == 1:
                create(mutateValue)
            else:
                create(normalValue)
    putInQueue(splitNum)  # ea particle that split resets its timer to split again

def increaseAge():
    global age
    newParticles = age[-2]
    shiftList(age)
    putInQueue(newParticles)  # these new particles are now mature enough to reproduce

def minute():
    increaseAge()
    split()

def simulation():
    global age, splitQueue
    age = [0] * (maturityTime + 1)
    splitQueue = [0] * (splitTime[-1] + 1)
    age[-1] = p_0
    putInQueue(p_0)
    i = 0
    p = p_0
    while p < p_0 * increaseFactor:
        minute()
        p = age[-1]
        i += 1

    return i

def simulationRun():
    total = 0
    for i in range(simulations):
        total += simulation()

    #print(total / simulations, 'average iterations needed to double with p_0', p_0)
    return total / simulations

def listSummary(lst):
    print('min:', min(lst))
    print('max:', max(lst))
    print('average:', sum(lst) / len(lst))

def p_0Modify(minp_0, maxp_0):
    global p_0
    times = []
    for i in range(minp_0, maxp_0 + 1):
        p_0 = i
        times.append(simulationRun())
    return times

def increaseFactorModify():
    global increaseFactor, p_0
    buf = ''
    for i in range(2,16 + 1):
        increaseFactor = i
        times = p_0Modify(50, 60)
        buf += str(i) + '\n'
        buf += 'time per cell:' + str((sum(times)/len(times)) / i * 2) + '\n\n'
    print(
'''
= = = = = = = = = = RESULTS = = = = = = = = = =
-p_0 from 50 to 100-
min: 56.13
max: 59.02
average: 57.40745098039218

-increaseFactor-
2
time per cell:57.23454545454546

3
time per cell:57.334545454545456

4
time per cell:52.92000000000001

5
time per cell:48.73818181818182

6
time per cell:44.79121212121212

7
time per cell:41.37688311688312

8
time per cell:38.68159090909091

9
time per cell:36.094545454545454

10
time per cell:34.025999999999996

11
time per cell:32.17586776859504

12
time per cell:30.405909090909088

13
time per cell:28.961398601398596

14
time per cell:27.65077922077922

15
time per cell:26.402424242424242

16
time per cell:25.393636363636368


'''
