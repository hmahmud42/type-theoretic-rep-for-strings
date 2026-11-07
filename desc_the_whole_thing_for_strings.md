There are three aspects:


1. The hypothesis/model space 
2. Inference algorithm / prediction for an individual hypothesis/model
3. Learning algorithm for picking a single model based on performance on the data.


# The Hypothesis Space 

Here we give a semi-formal description of the hypothesis space, sufficient for implementing the idea. A full formal description is given in the appendix. The overall idea is to, given a data point build up a hierarchical representation that captures invariances in data points that can be used to perform predictions. 

We assume that our formal system is dependently typed. 

## Invariances and Hierarchies

An invariance is tuple $Inv := (P, A, f)$:

- $P = \times_{i=1}^n P_i$ a parameter space, 
- $A = \times_{i=1}^m A_i$ an argument space. Each $A_i = \times_{Inv'} P_{Inv'}$ for some set of invariances $I$ defined previously, or proposition about $\times_{Inv'} P_{Inv'}$.  
- a function with signature $f \rightarrow P_1 \rightarrow \cdots \rightarrow P_n \rightarrow \sigma(A) \rightarrow [0, 1]$. Here  $\sigma(A)$ is an inductive data structure containing elements of $A$. The set of invariancese are denoted by $\mathcal{I}$

We assume a hierarchy over the invariances so that if $P_{Inv'} = A_i$, then $A^{Inv'}_j \neq P_{Inv}$ for any argument space A^{Inv'}_j$ of $Inv'$ we denote this by $Inv > Inv'$.  Hence this defines a directed acyclic graph (DAG) $(V, E)$ over invariances so that $(Inv, Inv') \in E$ iff $Inv > Inv'$. Hence each $Inv$ has $\leq m$ incoming edges. The source nodes in this graph, or equivalently the base invariances, are elements extracted directly from the text (such as patches in images). For these elements, $P = \{v_1, v_2, v_3\}$, $A = \emptyset$, f(v_i) = 1$ where $v_i$ are some singletons. Denote these sets by $\mathcal{B}$

So the hierarchy of we have defined is
- layer 0 are specific data elements (one example are patches), 
- layer i are are invariances that exist across elements in layers j, j < i. 

> **Example:** In our case, each data point is a binary string of length $d$. Here, each base invariances are fixed length strings of some length (like $3$). One set of invariances are maximum edit distance between a sequence of elements. Here $P = N$, $A = P_{B_i}$ for some base invariance $B_i$, and $f: N \rightarrow List[P] \rightarrow [0, 1]$, such that $f(m, [v_{i_0}, v_{i_1}, v_{i_2}, v_{i_3}] = 1$ iff the maximum edit distance between $v_{i_0}$ and any other $v_{i}$ is $\leq m$ 

Two special class of parameters are location parameters $Loc$ and location checker functions $LocChecks := \{f| f : List[Loc] \rightarrow [0, 1]\}$. The $Loc$ parameter gives the location of the where the invariance occurs in the data while $LocCheck$ can be used to require proofs that the arguments satisfy certain condition. For instance, $f$ could check if the input arguments have locations that are 

For a invariance $(P, A, f)$, the tuple $(P, A, f(p_{1:n}))$ with the curried function $f(p_{1:n})$ is called a concrete instance of the invariance with paramters $p = p_{1:n}$ while $(P, A, f(p_{1:n}, a_{1:m})$ is called the activated instance of concrete instance with activation level $f(p_{1:n}, a_{1:m})$. Let us denote these sets by $\mathcal{I}_C$ and $\mathcal{I}_{CA}$ respectively.

The graph structure over $\mathcal{I}$ induces a corresponding graph structure over both $\mathcal{I}_{C}$ and $\mathcal{I}_{CA}$. Let us denote these graphs by $\mathcal{G}, \mathcal{G}_C, and \mathcal{G}_{CA}$ respectively. 


Define the lift funciton as follows $lift((P, A, f(p_{1:n}, a_{1:m})) = (P, A, f(p_{1:n})$ and $lift((P, A, f(p_{1:n})) = (P, A, f)$. Hence  we have

>**Lemma 1.** $(a, b) \in \mathcal{G}_{CA}$ $\Leftrightarrow$  $(lift(a), lift(b)) \in \mathcal{G}_{C}$ iff $(lift(lift(a)), lift(lift(b))) \in \mathcal{G}$

With the above theorem, for any $G_{CA} \in Sub(\mathcal{G}_{CA})$ we let $lift(G_{CA}) \in Sub(\mathcal{G}_{C})$ be the graph obtained by lifting each node of $G_{CA}$ while retaining the edges, and similarly for $lift(lift(G_{CA})) \in Sub(\mathcal{G})$


## From Invariance Graphs To Models

We assume a (small) finite set of primitive polymorphic invarance computing functions $F_I$; the parameter space is set to be $P_i \subset R^k$ for some $k$ (this includes real matrices). Note that this means $A_i \subset R^{k \times m}$. So while the number of base invariance functions $|F|$ is small, the sets $\mathcal{I}, \mathcal{I}_A, \mathcal{I}_{CA}$ are all infinite. 

Given this each model $M$ is defined as tuple $(G^M, K^M, \phi^M) $, where
1. $G^M = \{G_i\}_{i=1}^k$ where each $G_i$ is a subgraph of $\mathcal{G}_C$
2. $K^M$ is sub-graph of $\mathcal{G}_C$ such that 
    - all the edges are labelled with weights
    - includes at least one element of $\mathcal{B}$.
    - the each element of $G^M$ is a sub-graph of $\mathcal{G}_C$
3.  $\phi^M: 2^{Sub(\mathcal{G}_C)} \rightarrow Pred(Y)$ is a prediction function that maps a subset of sub-graphs of $Sub(\mathcal{G}_C)$ to a prediction.

Let the set of subgraphs of $\mathcal{G}_C(M)$ satisfying conditions under $2$ above be $Sub^w(\mathcal{G}_C)$. For a $K \in Sub^w(\mathcal{G}_C)$, define $lift(K)$ to be $K$ wihtout the weights on edges - tht is $lift(K) \in Sub(\mathcal{G}_C)$ such that $(a, b) \in K$ iff $(a, b) \in lift(K)$.


## Inference Algorithm, Informally 

Informally, each model $(G^M, \mathcal{G}_C(M), \phi^M)$ predicts/inferences as follows: 
- Given an input $x$, a representation of it $G(x) \in Sub(\mathcal{G}_{CA})$ is created. 
- In creating $G(x)$, the weights in $\mathcal{G}_C(M)$ are used to prioritise which nodes to "activate" (the difference in the nodes of $\mathcal{G}_C$ and $\mathcal{G}_{CA}$ are the activation values).
- $\phi^M$ then checks which subgraphs in $G_i \in G^M$ are present in $lift(G(x))$ - it then assigns the predictions associated with each $G_i$ to output the final probablity. The predictions for each $G_i$ are are part of the definition of $\phi^M$.

Note that when we restrict $G(x)$ and $G^M$ to only contain the base-invariances $\mathcal{B}_i$, we recover classical machine learning algorithms with an appropriate definition of $\phi^M$.  


# Learning Algorithm

For this section we assume that problem is a discrete classification problem. Other types of prediction may be handled in a similar way, and we leave that for future work. The core of learning algorithm is an unification + anti-unification over graphs.

Given the above, let $D_N := (x_1, y_1), (x_2, y_2), \cdots, (x_N, y_N)$. The learning proceeds in steps $t$, with each step corresponding to a analysing a single batch and updating the model based on that. The initial model is $M_0 := (\{\}, K, \phi_0)$, where $K \in Sub^w(\mathcal{G}_C)$ is based on prior knowledge, and $\phi_0$ outputs the mean empircal distribution of the ouput values in $D_n$ as the prediction. 

The model update at step $t$ from $M_{t-1}$ to $M_t$ occurs as follows. 
1. Let $M_{t-1} := (G^M_{t-1}, K_{t-1}, \phi_{t-1})$, and let $B \in 2^{D_N}$ with $|B| = \text{batch-size}$ (where $\text{batch-size}$ is an algorithm parameter). 
2. Group samples in $B$ by their $y$ values, and let $B_y$ be the samples of the form $(x_i, y)$. 
3. For each $B_y$, for each $x \in B_y$, generate a representation using the procedure described below from $K_{t-1}$ - let these representations be $Rep(x) := \{R_x| x \in B_y, R_x \in Sub(lift(K_{t-1}))$.
4. For each $B_y$, find the most common subgraphs accross $\{Rep(x)|x \in B_y\}$ using an unification algorithm described below, and let these be $G'_{t}(y)$. 
5. Distinguish the elements $\{G'_{t}(y)$ using the anti-unification algorithm described below to make them more distinct, and let these final elements be $G^M_{t}$. 
6. Create $K^M_t$ by updating the weights of $K^M_{t-1}$ using $G^M_{t-1}, G^M_{t}$ using the weight update algorithm described below.
7. Set $\phi_t$ to be the distribution that matches the conditional probability on sub-graph matching of $G^M_{t}$.   

## Representation Generation

The input to the representation generation algorithm is an input data point $x$, a graph $K \in Sub^w(\mathcal{G}_C)$ and the output is $G$ such that $lift(G) \in Sub(K)$. The algorithm proceeds iteratively over layers in $K$. It maintains a set of *active invariances* $Actv_i$. The unoptimised version of the algorithm proceeds as follows

1. At step $0$, $Actv_0 := \{b | b \in K, b \in \mathcal{B}, b \in x$\}. 
2. The set of active invariances in step $i$ is defined as
$Actv_i := \{(P, A, f(p_{1:n}, (a_{1:m}))| (P, A, f(p_{1:n}) \in K, \forall j. a_j =  p_{1:n'}, (P', A', f'(p'_{1:n}, (a'_{1:m})) \in Actv_{i-1}   \} \cup Actv_{i-1} $ 

The generation stops when $Actv_i = Actv_{i-1}$. The graph $G$ is obtained by adding directed edges between elements of the final $Actv_i$ according to the rule described in Section "Invariances and Hierarchies".

As described, the set of active nodes can become very large due to the same node in $K$ getting activated for different arguments $a$. To help with this, we utilise the weights in $K$. Specifically, at each step we proceed as follows. We now maintain a weight $W(v)$ for each node of $K$, with $W(v) = 1$ initially. 

1. Sample 
1. At step $0$, set $Actv_0$ to be a fixed number $J$ of nodes from $Actv'_0 := \{b | b \in K, b \in \mathcal{B}, b \in x$\}, with sampling probability determined by $W_0(v)$ for $v \in Actv'_0$.  
2. The set of active invariances in $Actv_i$ step $i$ is a sampling of a fixed number $J$ of elements from  
$Actv'_i := \{(P, A, f(p_{1:n}, (a_{1:m}))| (P, A, f(p_{1:n}) \in K, \forall j. a_j =  p_{1:n'}, (P', A', f'(p'_{1:n}, (a'_{1:m})) \in Actv_{i-1}   \} \cup Actv_{i-1}$, with sampling probability determined by $W_0(v)$ for $v \in Actv'_0$.   
3. In a lookback step, we for each edge $(a, b)$ in the graph constructed so far, we set $W(a) = W(a) + \alpha W(b)$ for $\alpha \in [0, 1]$.

Step 3 is similar in spirit to how weights are updated in predictive coding. 


## Graph Unification Algorithm

The graph unification algorithm takes as input a set of  graphs $G_{1:k}, G_i \in Sub(\mathcal{G}_{CA})$ finds the most common  across all the $G_i$, which is a set $H_{1:l}$ such that $\forall i, j. H_j \preceq G_i$ 

~~1. We match nodes based on $(P, A, (f(p_{1:n}), a_{1:m}S))$ - matches are scored by matching based on how many of the $P_i \in P$ match; based on how many of the $A_i$ match and then how closely the $p_{1:n}, a_{1:m}$ match.
2. We match layer by layer in a greedy fashion - each node in layer $1$ in $G_1$ forms a multiple chains across the graph. We choose the highest scoring one. 
3. Same for each node in each graph.
4. Then we do the same for each node in layer $i$ taking into account the scores of the nodes that lead into it. So node $Score(A, B)$ is matching of $A, B$ $+$ matching of all the children of $A$ and $B$.
5. We extract the top $k$ graphs as our unification.~~


**Version 1:**  This is a brute-force algorithm.

- A node is at layer-$0$ if all its incoming edges are from source nodes.
- A node is at layer-$i$ if all its incoming edges are from nodes at layer $j$ where $j < i$. 
- Given graphs $G_{1:k}$, for each node at each layer, we construct a set of beams. Each beam consists of one node from the same layer $i$ of each $G_i$, such that the Invariance function $f$ matches. 
- The cost of a beam $\beta = \{n_1, n_2, n_k\}$ is the sum of the pairwise scores $score(\beta) := \sum_i \sum_{j < i} score(n_i, n_j)$
- We now form a beam graph such that $(\beta, \beta') \in G_B$ iff for each $(n_i, n'_i) \in G_i$ for each $i$.
- Given the beam graph, we extract the maximum score sub-graphs. 
- We then extract the final graph by unifying each beam into a single element element by finding the highest scoring unifier across the parameters. 

*Parallelisation opportunities:* We can compute and score the beams of Invariances with different $f$'s in parallel as they are never part of the same beam. 

**Version 2:** This is a greedy but low cost version of the algorithm
For each node at each layer, only keep the highest scroring beam. At the next layer, only score the edges connected to the nodes in the highest scoring beams in the previous layer, and continue in this fashion. 

*Parallelisation opportunities:* Same as version 1

**Version 2.5:** Same as version 2, but now we only do the beam formation $k$-wise (e.g. $k = 2$), and then unify the graphs from the different $k$-wise groups. 

*Parallelisation opportunities:* Same as version 2, but the pairwise computations can be parallelised as well.


**Version 3:** This is likely a convergent algorithm would be a minimum coste spanning tree type algorithm. In the following, the cost is the negative of the -score.
1. For each layer-0, form all the beams as in Version 1, and calculate the cost of each and them to the pool of candidates to expand. 
2. Choose the lowest cost beam from the pool, and activate all its parents and calculate its their costs. Remove the lowest cost beam, and add its parents to  the pool.
3. Repeat step 2 until the lowest cost node has no parent.
4. Return the lowest cost graph this constructed.

*Parallelisation opportunities:* Same as version 1

**Version 3.5:** Same as version 3, but now we only do the beam formation $k$-wise (e.g. $k = 2$), and then unify the graphs from the different $k$-wise groups. 

*Parallelisation opportunities:* Same as version 3, but the pairwise computations can be parallelised as well.



## Graph Anti-Unification Algorithm

The graph anti-unification algorithm takes as input a set of  graphs $\{H^y_{1:k_y}| y \in Y\}, H^y_i \in Sub(\mathcal{G}_{CA})$ finds the common  across all the $H^y_i, H^w_j$ and removes the common elements:

- Take the graphs
- Find and score the cross-$H^y$ beams 
- If the score is above a threshold, eleminate the nodes in that beam.


## Generation of Conditional Matching.

Given a representations of the classes $\{H^y_{1:k_y}| y \in Y\}$, $\phi_M$ creates a representation of $x$ using the representation generation algorithm, 

- It then matches the representation against the graph using two element beam-forming, keeping the highest matching graph. 

- It outputs probablility scores based on the scores computed.


## Weight Update Algorithm

The algorithm is given as input $K \in Sub^w(G_C), G, G' \in 2^{Sub(G_C)}$ such that each $G_i' \in G'$ satisfies $G_i' \in Sub(lift(K))$. The output is $K' \in  Sub^w(G_C)$. $K'$ is obtained from $K$ in two phases:

- Comparing $G_i$ to $G_i'$ and reducing the weight of edges which do not appear in $G_i'$ and increasing the weights of those that appear in both, with extra weight given to those that have persisted across $G_i$ and $G_i'$
- Sampling new edges according to a prior, and closeness to existing values. 


# Reasoning 

The representations are typed and can be reasoned over - reasoning can be reveal what will happen if things change. If extrapolation is possible - how stable things are. 


# Type Check Algorithm

The type checking requires a search algorithm - given an invariance, it will look through the space of invariances+locations and find ones that fit the type and location constraints - we present three versions - breadth first search, depth first search and cost based search. 




```python
function BFSTypeCheck(start_location, location_gen):
    queue = new Queue() # queue of type-checked elemnts
    found_tree = Tree() # tree of arguments that have type checked
    argument_list = []

    root = element at start_location
    if type-check root:
        found_tree.root = root
        queue.enqueue root
    else
        return found_tree
    
    while queue is not empty:
        current = queue.dequeue()
        locs = location_gen(current)
        if locs is empty:
            add path of current node to argument list
        for each loc in locs:
            candidate-child = element at loc 
            if type-check candidate-child:
                add candidate-child as a child of current in fround_tree
                queue.enque candidate-child
                
    return arguments_list, found_tree
```



```python
function DFSTypeCheck(graph, start, goal):
    stack = new Stack()
    found_tree = Tree() # tree of arguments that have type checked
    argument_list = []

    root = element at start_location
    if type-check root:
        found_tree.root = root
        stack.push root
    else
        return found_tree
   
    while stack is not empty:
        current = stack.pop()
        locs = location_gen(current)
        if locs is empty:
            add path of current node to argument list
        for each loc in locs:
            candidate-child = element at loc 
            if type-check candidate-child:
                add candidate-child as a child of current in fround_tree
                stack.push candidate-child
    return arguments_list
```



```python
function UniformCostTypeCheck(graph, start, goal):
    # Priority Queue stores tuples of (cost, node)
    pq = new PriorityQueue() 
    # Track the lowest known path cost to each node
    cost_so_far = Map()

    found_tree = Tree() # tree of arguments that have type checked
    argument_list = []

    root = element at start_location
    if type-check root:
        found_tree.root = root
        pq.enquue root (type-cost root)
    else
        return found_tree

    while pq is not empty:
        (current_cost, current) = pq.dequeue_min()

        locs = location_gen(current)
        if locs is empty:
            add current_cost and path of current node to argument list
        for each loc in locs:
            candidate-child = element at loc 
            if type-check candidate-child:
                add candidate-child as a child of current in fround_tree
                pq.enque candidate-child (current_cost + (type-cost candidate_child) )
        
                
    return argument_list, found_tree 
```

For fixed $R, C \in Nat$

$Loc :=  [R] \times [C]$

$Path := \Sigma l: Nat. List(l, Loc)$

$WPath = WeightedPath := Real^+ \times Path$

$WPathSet := \Sigma l:Nat. Set(l, WPath)$

$LocSet := \Sigma l:Nat. Set(l, Loc)$

$LocGroup := LocSet | WPathSet$ 

$Junction := LocGroup \times \Sigma a_{1:n}: ActInv \times a: ConcInv$ 


How to manage the following:

Given a set of locations - how to summarise this. 
----------

Given an invariance, find the path with the lowest cost direction

path = (x, y) 
dels = (0, 1), (0, 1), ... , (0, 1), 


1           1
 1         1
   1 1 1 1

(1, 1) (1, 1) (0, 1), (0, 1), (0, 1), (0, 1), (-1, 1), (-1, 1)


1 1 1 1 1 1 1

(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1),


      1
1 1 1   1 1 1

(0, 1), (0, 1), (0, 1), (-1, 1), (1, 1), (0, 1), (0, 1), (0, 1),


0 0 0
1 1 0
2 0 1

both convolve 


To search we need: 
- set of locations and their values.
- 



So I can show that a the protocol achieves equilibrium at some kind of optimal features

Ok so what we have so far is essentially half of the the inference half of the approach - the second half is matching the learned graph using to an existing set of templates.

the other part is the learning where we derve the templates themselves - which involves generaing representations using the above protocol and then emphasising the commonality between similar classes and de-emphasising the commonality between different classes.

I think we can use a game based approach as well. So...

Protocol 1: Generate representation by using a reference priortisation over which players whould be matched to which other players. We left the prioritisation as a bias in the above (or may be didn't do it at all). Equilibrium is achieved when no player can match with another player and improve their payoff.

Protocol 2: Match graph $G$ generated by protocal 1 to a reference template graph $T$. Here the players correspond to indiviudal nodes and are in a coalitions defined by their immediate neighbors. Players in $G$ only play with players in T. The payoff of $P_G$ as the sum of their match and the matches obtained by their immediate neighbors. The protocol proceeds a parallelised fashion with each player trying the find the best match for their self. An equilibrium is when no player can move their match on their won and improve their payoff.

Protocol 1 and 2 together give us inference: Generate representation and match to an existing template.



Protocol 3: Match graphs $G_{1:n}$ to construct a template graph. Here the players correspond to indiviudal nodes and are in a coalitions defined by their immediate neighbors. Players in $G_i$ only play with players in $G_{-i}$. The payoff of $P_{G_i}$ as the sum of their match and the matches obtained by their immediate neighbors. The protocol proceeds a parallelised fashion with each player trying the find the best match for their self. An equilibrium is when no player can move their match on their won and improve their payoff.

Positive Learning following protocol 3: All the graph  $G_i$ correspond to the same class. After equilibrium is reached, we the combined, mean value of the player attributes to give the template delta graph. This delta is applied to the existing templates to generate the new tempaltes/

Negative Learning following protocol 3: Each graph  $G_i$ correspond to the different classes. After equilibrium is reached, we the combined, mean value of the player attributes to give the template -delta graph. This delta is applied to the existing templates to generate the new tempaltes/


Protocol 3+Follow ons gives us the learning algorithm 


The above descriptions are high level, but details can be filled in with the relatively obvious completions.














