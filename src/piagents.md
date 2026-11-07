Consider the following protocol for a game, with the goal of creating hierachaol representation of some data.

Players are units of computation

The goal of each player is to combine with as many other players as possible. 

An player $A$ can only combine with other players by adopting an invariance function $f : V \times V -> R$ and a value $v \in V$. Note that $V$ can be complex and structured.

The game begins with a set of invariances $f$, which are the game parameters, and a set of values $v_{1:n}$ - which are the basis data values, and a fixed number of players $N$. Each value pair $(f, v)$ can be taken by at most one player.

Two players $A(f, v)$ and $B(g,v') can only combine when they $f=g$ and $f(v, v') \in Comb$ where $Comb \subset R$ and defined by the game designer. 

When two players combine, they form a collective player $P_{AB}(f, agg(v, v'))$ where $agg$ is an aggregation function $V$ . 

After the round ends, we have a set of values $v^{new}_{1:m}$ corresponding to each collective player. 

These values are used as a feedstock for the round, which leads to higher order represenations.


------

The system initiates by 









