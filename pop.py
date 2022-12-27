import random
import time
import matplotlib.pyplot as plt
import numpy as np
import time
import math

class Node():
    def __init__(self, loc, time):
        self.loc = loc
        self.t = time

    def __str__(self):
        return f"Node:l({self.loc}), t({self.t})"

    def __repr__(self):
        return self.__str__()

class AzarFananiNode(Node):
    def __init__(self, loc, time):
        super().__init__(loc, time)

    def __sub__(self, other):
        return abs(self.loc - other.loc) + abs(self.t - other.t)

class Space(list):
    def __init__(self):
        super().__init__()
        self.matchings = []
        self.title = "Default Space"

    def add(self, loc, t):
        self.append(Node(loc, t))

    def match(self, p, q):
        self.remove(p)
        self.remove(q)
        match = (p, q, t)
        self.matchings.append(match)
        return match

    def get_loc_diffs(self):
        diffs = []
        for m in self.matchings:
            diffs.append(abs(m[0].loc - m[1].loc))
        return diffs

    def get_t_diffs(self):
        diffs = []
        for m in self.matchings:
            later = max(m[0], m[1], key=lambda m: m.t)
            diffs.append(m[2] - later.t)
        return diffs

#https://link.springer.com/article/10.1007/s00224-019-09963-7
class AzarFananiSpace(Space):
    def __init__(self, E=1):
        super().__init__()
        self.title = f"Azar&Fanani ALG({E})"
        self.E = E
        
    def add(self, loc, t):
        self.append(AzarFananiNode(loc, t))
    
    def should_match(self, p, q, t):
        #print(t, "<>", p.t + ((p-q)/0.01), p.t + ((p-q)/0.1), p.t + ((p-q)/1))
        if p.t >= q.t and t == p.t + ((p-q)/self.E):
            return self.match(p, q)
        return False

class BTrialSpace(Space):
    def __init__(self, seed=time.time()):
        super().__init__()
        self.title = "Bernoulli Trial"
        random.seed(seed)

    #Since 1/x tends to 1 x approaches 1 from the right,
    #Then as the distance from p-q decreases, the fraction approaches 1
    #And thus should have a greater chance to match
    def should_match(self, p, q, t):
        chance = random.random()
        if 1/abs(p.loc-q.loc) >= chance: #I think mathematically I'm supposed to use <= to represent a bernoulli trial but I'm getting better results this way.
            return self.match(p, q)
        else:
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

def draw_data(spaces):
    fig = plt.figure()
    for n, space in enumerate(spaces):
        ax = fig.add_subplot(1, len(spaces), n+1)
        ax.set_xlabel("Time")
        ax.set_ylabel("Player Score")
        ax.set_title(space.title)
        xc = [(m[0].t, m[1].t) for m in space.matchings]
        yc = [(m[0].loc, m[1].loc) for m in space.matchings]
        ax.scatter(xc, yc, color='c')
        for n in space.matchings:
            later_node = max(n[0], n[1], key=lambda n: n.t)
            time_gap = n[2] - later_node.t #gap from later node
            redness = 1 if time_gap > 300 else time_gap/300
            ax.plot([n[0].t, n[1].t], [n[0].loc, n[1].loc], color=(redness, 0, 1-redness))
        ax.scatter([n.t for n in space], [n.loc for n in space], color='salmon') #Draw unmatched nodes
        print(f"Unmatched in {space.title}: {space}")
    plt.show()

def draw_stats(spaces):
    fig, (ax1, ax2) = plt.subplots(2)
    ax1.boxplot([space.get_t_diffs() for space in spaces], vert=False, labels=[space.title for space in spaces])
    ax1.set_title("time diffs from latest node to matching time")

    ax2.boxplot([space.get_loc_diffs() for space in spaces], vert=False, labels=[space.title for space in spaces])
    ax2.set_title("Location differences between nodes in matchings")

    plt.show()

reqs = create_requests(time.time(), 6000, 0.009, 100, 2400)
afspace = AzarFananiSpace(1)
afspace2 = AzarFananiSpace(0.1)
btspace = BTrialSpace()
spaces = [afspace, afspace2, btspace]
for t, r in enumerate(reqs):
    for space in spaces:
        if r:
            space.add(r[0], r[1])
        for node in space:
            for other in space:
                if node == other:
                    continue
                m = space.should_match(node, other, t)

draw_stats(spaces)
draw_data(spaces)
