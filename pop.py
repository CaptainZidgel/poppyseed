import time
import datetime
import random

class Member:
    #Score, latency, and timeWaiting derive defaults from population.
    def __init__(self, population, score=None, latency=None, timeWaiting=None):
        self.id = None
        self.population = population
        self.score = score or population.defaultScore #Equivalent to Elo or something like that
        self.latency = latency or population.defaultLatency
        self.timeWaiting = timeWaiting or population.defaultTimeWaiting #I don't know why you wouldn't want this to start at 0.

        self.inMatch = False

    def GetMatch(self):
        return self.match if self.inMatch else False

class Population:
    def __init__(self, timescale=1.0, spawnChance=None, despawnChance=None,
                     defaultScore=1000, defaultLatency=60, defaultTimeWaiting=0):
        self.members = []
        self.matches = set()
        self.stream = False
        self.unitsElapsed = 0
        self.timescale = timescale #TODO: Clip to 0-1.0
        #time in fractional seconds, that is, if ts=0.500 then one second will pass in 500 milliseconds.
        self.spawnChance = spawnChance or self.timescale / 5 #TODO: Clip to 0-1.0
        self.despawnChance = despawnChance or self.timescale / 50 #TODO: Clip
        #if population.timescale is 0.900 and spawnChance is 0.5, then every
        #900 milliseconds, there will be a 50% chance of spawning.
        self.defaultScore = defaultScore
        self.defaultLatency = defaultLatency
        self.defaultTimeWaiting = defaultTimeWaiting

        self.PostLoopFunction = lambda x: None
        self.PreLoopFunction = lambda x: None

    def AddMember(self, score=None, latency=None, timeWaiting=None):
        m = Member(self, score=score, latency=latency, timeWaiting=timeWaiting)
        self.members.append(m)
        return m

    def GetMembers(self, maxi=None, predicate=None):
        #get members that meet predicate, up to maxi amount.
        if (not maxi) and (not predicate):
            return self.members

    def GetUnmatchedMembers(self):
        l = []
        for m in self.members:
            if not m.GetMatch():
                l.append(m)
        return l

    def EnableStream(self):
        self.stream = True

    def DisableStream(self):
        self.stream = False

    def Update(self):
        self.unitsElapsed = self.unitsElapsed + 1
        self.PreLoopFunction(self)
        if self.stream and random.random() < self.spawnChance:
            m = self.AddMember(score=random.randint(1000, 2000), latency=random.randint(10, 120), timeWaiting=0)
            print("Spawning 1 Member, score {} lat {}".format(m.score, m.latency))
        for m in self.GetUnmatchedMembers():
            if random.random() < self.despawnChance:
                self.members.remove(m)
                print("Despawning 1 Member, total pop:", len(self.members))
                #m.Destroy <- Any need for a function like this?
        self.PostLoopFunction(self)

    def Loop(self):
        currentTime = time.time()
        t = 0
        dt = 1/60
        while True:
            newTime = time.time()
            frameTime = newTime - currentTime
            currentTime = newTime

            while frameTime > 0.0:
                deltaTime = min(frameTime, dt)
                frameTime -= deltaTime
                t += deltaTime
            if t > self.timescale:
                t = 0
                self.Update()

#End user example:
#Create a population. Timescale: 1.0 causes an Update every 1 second, 0.500 causes an update every 500 milliseconds.
##I don't know a better way of scaling time like this. My intention is that if timescale is x milliseconds,
##then one real second occurs in x milliseconds, but I don't know if that is actually a good description for what I coded.
#spawnChance/despawnChance: decimal coded percentage chance of a spawn or despawn. Despawn chance is evaluated for each member
##not in a match.
p = Population(timescale=0.9, spawnChance=0.25, despawnChance=0.05)
#The stream turns on "the sink" of constantly incoming players. You may want to code your own function but I've included this
##to start. This is where spawnChance comes in.
p.EnableStream()
#You can use p.PreLoopFunction or p.PostLoopFunction to do stuff. The population is passed as the arg.
p.PostLoopFunction = lambda pop: print("P: {}, T: {}".format(len(pop.members), pop.unitsElapsed))
#One day I will learn async. But today is not that day.
p.Loop()
