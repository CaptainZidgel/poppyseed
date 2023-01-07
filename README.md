# Poppyseed
A script for testing online matching algorithms. It was originally going to be a library but it came out to be simple enough such that you can just edit the script.  
An online algorithm is one which operates on incomplete datasets in realtime.  
A min-cost matching with delays algorithm seeks to match together points in a dataset with the lowest cost by delaying some matches (as opposed to matching-or-discarding at point arrival).  
I became interested in this to match players together from an elo score.  
The script is incredibly simple and does not simulate things like players leaving due to waiting too long.

The script generates some set of requests randomly (seed with time.time()), then shares that dataset to multiple algorithms incrementally in a for loop (simulating revealing points in time). It prints out the costs, the set of unmatched points, and draws:
- A box-and-whisker plot of skill differences and time-differences (distance from latest node to the matching time) for each matching
- A scatter plot of each matching.
	* Pink points are unmatched
	* Blue points are matched and have lines connecting them.
	* The lines are colored from blue to red. Red = time it took to create the matching was > 300, otherwise scaled from blue to red in a normalized sense of t/300 (bluer is better/faster).
	* The x-axis is time of an unspecified duration. It could be seconds or milliseconds or minutes. Depends on how you want to implement it I guess. (The math papers I read for this didn't specify it either. One called it a "infinitesimally small timestep" but I don't know how you would actually implement that in code.)
	* The y-axis is skill differences.
	* Thus, a vertical line is a matching of two nodes from the same time location with different skills. This doesn't mean the matching was made quickly though, as the algorithm could have greatly delayed it (therefore the connection line would be red).

#### Example images
```python
reqs = create_requests_dist_skill(1072023, 10000, 0.009, 1600)
	#	create_requests_dist_skill(seed, length, spawn_chance, mean)
	#	this function creates skill levels in a normal distribution based around mean.
    #	on each timestep there is a (spawn_chance * 100)% chance of a new player joining.
    #	length = how many timesteps to consider spawning in. the simulation will run further past 
    #	this when considering making matches
    #
btspace = BTrialSpace()
gspace = GreedySpace()
bkspace = BienkowskiSpace(0.5, 2)
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
```
![A box-and-whiskers plot](/img/boxplot.PNG)  
![A scatter plot of the matchings](/img/scatterplot.PNG)  
```
Greedy Algorithm Avg Cost: 293.2134040715357
Bienkowski Space Avg Cost: 776.5689765241297
Bernoulli Trial Avg Cost: 378.05132913571316
Unmatched in Greedy Algorithm: []
Unmatched in Bienkowski Space: []
Unmatched in Bernoulli Trial: []
```


# Algorithms
I am not a mathematician. I am not even a computer scientist. Hence I have found these algorithms difficult to read and implement. My implementations are more like approximations of the general ideas, and some algorithms I could not implement because I could not understand what was happening within them. As such, in my findings the best algorithm is actually the greedy algorithm, even though in the literature this should be beaten by others.
Note: Some of these papers also contribute to or are mainly focused on the bipartite matching problem, which matches asymmetrical request types (driver-passenger instead of player-player). This could easily be implemented in the script if you wished.

*"Online Matching: Haste makes Waste!"* Emek et al. arXiv:1603.03024  
(Not implemented)  
This paper is cited by others as responsible for renewing interest in this type of problem. The algorithmic solution involves embedding the metric space into tree space (something I could not figure out how to do, skimming the cited articles, but you may be able to do) then running a bernoulli trial based on the timestep. It also has a deterministic algorithm.

**class BTrialSpace()** (Me)  
I wrote this algorithm inspired by the bernoulli trial of Emek et al.  
`if 1/dist(p, q) >= random number on interval [0, 1]: match`  
*Note that distance is simply abs(p.loc - q.loc)*  
The principle is that as the distance gets lower and lower, the left-side number is more and more likely to be larger than the right side number and gets closer and closer to a match.

*"Min-cost bipartite perfect matching with delays"* Ashlagi et al. https://web.stanford.edu/~iashlagi/papers/mbpmd.pdf  
(Not implemented)  
This paper also uses a tree-embedding and presents detailed randomistic and deterministic algorithms.

*"Online matching with delays and stochastic arrival times"* Mari et al.  	arXiv:2210.07018  
This paper was far too large and impressive for me to understand, but its approach involves incorporating distribution data of when players of different skill levels are likely to arrive. As one of the preliminaries, it presents an extremely simple algorithm.  
**class GreedySpace()**  
*"once the total
waiting time of any two pending requests exceeds the distance between them, Greedy immediately
matches them together"*  
`if (t - p.t) + (t - q.t) >= dist(p, q): match`  
*Note that distance is simply abs(p.loc - q.loc)*  
So far this is the algorithm that consistently shows the lowest costs.

*"Deterministic Min-Cost Matching with Delays"* Azar and Jacob-Fanani. arXiv:1806.03708  
(Approximately implemented)  
This paper presents a deterministic algorithm for the metric space that does not require embedding. The metric space's distance formula includes time as a parameter. `D(p, q) = |p.loc - q.loc| + |t1 − t2|`  
The algorithm takes a parameter from the positive reals, and when this is "small enough" the algorithm is competitive. I do not know how to pick the parameter (I'm calling it E since the symbol they use is not on the keyboard).  
**class AzarFananiSpace(E)**  
`if p.t >= q.t and t = p.t + D(p, q)/E: match`  
You can read more about this in the paper and what it is supposed to geometrically represent of course.  
In my testings I use Es of 2, 1 and 0.1 arbitrarily.  
This algorithm seems to perform very poorly (ie no matches at all) on the distributed skill requests. However, if I generate requests totally randomly we are more likely to get requests. E = 1 performs well enough on reducing the differences between skills but it takes way too long. 2 is a little better on time but worse on skill. 0.1 is a no-go.

*"A Match in Time Saves Nine: Deterministic Online Matching With Delays"* Bienkowski et al. arXiv:1704.06980  
(Approximately implemented)  
**class BienkowskiSpace(alpha, beta)**  
This algorithm defines a kind of "budget" that is based on the time a node has been waiting multiplied by a parameter alpha, and matches when:  
* summed budgets of p and q >= dist(p, q)
* for each p and q as a and b, budget(a) <= beta * budget(b)  

The paper defines beta = 2 and alpha = 1/2 as the optimal parameters.  
Performance isn't great in poppyseed. But again, in case I haven't made it clear, *I have no idea what I'm doing here*

## "Open problems" for Poppyseed
There were a few issues for me in reading these papers, besides the tree-embedding problem that kept cropping up.

Simpler issue: What should the timestep be? I can compute time at any interval (1 ms = 1 ms, 1 sec = 1000 ms), but *what should* I be computing time differences in? milliseconds or seconds or minutes? If I represent time in milliseconds, t is going to be larger and thus match faster than if time were represented in seconds. But which setting presents the fastest, lowest-cost matches?

Difficult issue: How should distances be normalized? This goes for both time and skill differences. None of the papers come with examples for their metric spaces. Now that I'm writing this I'm wondering why I didn't already try normalizing my distances in each space to distance/3000 (approximating 3000 as a max distance) so it comes out to an interval of [0, 1]. If the papers were written around this, then it could solve the issue of them not specifying what distances could be considered "large" (intolerable) or "small" (tolerable). The distance will heavily vary based on the metric space being used for a chess match or rideshare program. With that said, what about time? I can't easily normalize that, as there is no hypothetical max time distance, just what users are willing to wait. If we take t as seconds, then a time wait of t = 500 is great for a rideshare program or perhaps a larger team game, but probably intolerable for a shorter 1:1 video game match.

## Addendum
Documentation! Finally!  
A custom space (algorithm) should come with a `should_match` method that takes parameters (p, q, t) and returns either self.match(p, q, t) or False for each p, q at time t. If your space uses a custom node type for whatever reason you want, you need to override the add method:
```python
class YourSpace(Space): #all spaces inherit from List
	def __init__(self, parameters):
    	super().__init__()
        self.title = "My Space"
        self.my_paremeter = parameters

	def add(self, loc, t):
		self.append(YourNode(loc, t))

	def should_match(self, p, q, t):
        if t > p.t + 10000000000 or q.t == 1234567: #You think I could submit this to a journal?
            return self.match(p, q, t)
        return False
```
You don't really *need* a custom node if you want to have a custom metric space, you can just implement distance functions and all that in your space's methods, but I liked the idea of overloading the subtraction `-` operation for nodes. The default node subtraction method is abs(p.loc - q.loc), so you can do p - q easily. Here's how I made a custom node for the Azar and Jacob-Fanani algorithm's time-augmented metric space.
```python
class AzarFananiNode(Node):
    def __init__(self, loc, time):
        super().__init__(loc, time)

    def __sub__(self, other):
        return abs(self.loc - other.loc) + abs(self.t - other.t)
```
