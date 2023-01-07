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

    def __sub__(self, other):
        return abs(self.loc - other.loc)

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

    def match(self, p, q, t):
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

    def get_all_costs(self):
        l = []
        for matching in self.matchings:
            n = matching[0]
            m = matching[1]
            t = matching[2]
            l.append(abs(n.loc - m.loc) + (t - n.t) + (t - m.t))
        return l

    def skill_range(self):
        _min = min(self, key=lambda x: x.loc)
        _max = max(self, key=lambda x: x.loc)
        return _max.loc - _min.loc

#10.1007/978-3-319-89441-6_11
class BienkowskiSpace(Space):
    def __init__(self, alpha, beta):
        super().__init__()
        self.title = "Bienkowski Space"
        self.alpha = alpha #must be greater than 0
        self.beta = beta #must be greater than 1

    def budget(self, n, t):
        return self.alpha * (t - n.t)

    def budget_suff(self, p, q, t):
        return self.budget(p, t) + self.budget(q, t) >= p - q

    def budget_bal(self, p, q, t):
        return self.budget(p, t) <= self.beta * self.budget(q, t) and self.budget(q, t) <= self.beta * self.budget(p, t)

    def should_match(self, p, q, t):
        if self.budget_suff(p, q, t) and self.budget_bal(p, q, t):
            return self.match(p, q, t)
        return False

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
            return self.match(p, q, t)
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
            return self.match(p, q, t)
        return False

#This greedy algorithm is presented as a preliminary in https://arxiv.org/pdf/2210.07018.pdf
class GreedySpace(Space):
    def __init__(self):
        super().__init__()
        self.title = "Greedy Algorithm"

    def should_match(self, p, q, t):
        if (t - p.t) + (t - q.t) >= abs(p.loc - q.loc):
            return self.match(p, q, t)
        return False

class CustomSpace(Space):
    def __init__(self):
        super().__init__()
        self.title = "Custom Space"

    def should_match(self, p, q, t):
        normal = 1 - abs(p.loc - q.loc)/self.skill_range()
        #The closer normal is to 0, the closer the values are.
        if abs(q.t - p.t) * normal > 500:
            return self.match(p, q, t)
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

def create_requests_dist_skill(seed, length, spawn_chance, mean_loc):
    random.seed(seed)
    l = []
    dist = np.random.normal(loc=mean_loc, scale=150.0, size=length)
    for i in range(0, length):
        if random.random() <= spawn_chance:
            l.append((dist[0], i))
            dist = dist[1:]
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

#reqs = create_requests(time.time(), 3000, 0.009, 1000, 2400)
reqs = create_requests_dist_skill(time.time(), 30000, 0.009, 1600)
#afspace = AzarFananiSpace(1)
#afspace2 = AzarFananiSpace(0.001)
btspace = BTrialSpace()
gspace = GreedySpace()
bkspace = BienkowskiSpace(0.5, 2)
#cust = CustomSpace()
spaces = [gspace, bkspace, btspace]
for t, r in enumerate(reqs):
    if t % 1000 == 0:
        print(f"T: {t}")
    for space in spaces:
        if r:
            space.add(r[0], r[1])
        for node in space:
            for other in space:
                if node == other:
                    continue
                m = space.should_match(node, other, t)
for space in spaces:
    print(f"{space.title} Avg Cost: {np.average(space.get_all_costs())}")
draw_stats(spaces)
draw_data(spaces)
