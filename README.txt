An environment (I am using that word to make it sound complex and interesting) for testing matchmaking algorithms.
Basically, it allows you to spawn a bunch of users with random elo scores and stuff.
I'm developing it so I can use it myself to implement a 1:1 MM algorithm but you could use it for N:N if you wanted.

Functions I'll probably add eventually:
- Simulated matches that eventually end. When they end, a turnover rate, so x% of members readd to queue and 100-x% despawn.
- Saturation rate (shows you what percent of users are in matches and what percent are waiting to play).
- A simple graphical display would be nice. Not just to visualize waiting members : playing members, but also to visualize your cost functions, etc.