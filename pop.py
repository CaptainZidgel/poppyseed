import random
import time

def btrial(x1, x2):
    chance = random.random()
    if 1/abs(x1-x2) <= chance:
        print(f"Match {x1} and {x2}")
    else:
        print(f"No match {x1} and {x2}")

E = 1
class Node():
    def __init__(self, loc, time):
        self.score = loc
        self.t = time

    def __sub__(self, other):
        return abs(self.score - other.score) + abs(self.t - other.t)

    def __str__(self):
        return f"Node:l({self.score}), t({self.t})"

    def __repr__(self):
        return self.__str__()

    def should_match(self, other, ct):
        if self.t >= other.t and ct == self.t + self.__sub__(other)/E:
            return True
        else:
            return False

class Space(list):
    def __init__(self):
        super().__init__(self)
        self.matchings = []
    
    def should_match(self, p, q, t):
        #print(t, "<>", p.t + ((p-q)/0.01), p.t + ((p-q)/0.1), p.t + ((p-q)/1))
        if p.t >= q.t and t == p.t + ((p-q)/E):
            self.remove(p)
            self.remove(q)
            match = (p, q, t)
            self.matchings.append(match)
            return match
        return False

def create_requests(seed, length, spawn_chance, min_loc, max_loc):
    random.seed(seed)
    l = []
    for i in range(0, length):
        if random.random() <= spawn_chance:
            l.append((random.randint(min_loc, max_loc), i))
        else:
            l.append(None)
    l = l + [None]*99999
    return l

reqs = create_requests(123, 1000, 0.02, 100, 2400)
space = Space()
t = 1
while len(reqs) > 0:
    r = reqs.pop(0)
    if r:
        space.append(Node(r[0], r[1]))
        print("Inserting", len(space))
    if len(space) == 0:
        print("no nodes")
    for node in space:
        for other in space:
            if node == other:
                continue
            m = space.should_match(node, other, t)
            if m:
                print("Matching", m[0], m[1], m[2])
    t = t + 1
print(f"Finished at timestep {t}")
print(space.matchings)
