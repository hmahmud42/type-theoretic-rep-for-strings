There are three aspects:


1. The hypothesis/model space 
2. Inference algorithm / prediction for an individual hypothesis/model
3. Learning algorithm for picking a single model based on performance on the data.


# The Hypothesis Space 

Here we give a semi-formal description of the hypothesis space, sufficient for implementing the idea. A full formal description is given in the appendix. The overall idea is to, given a data point build up a hierarchical representation that captures invariances in data points that can be used to perform predictions. 

## Invariances and Hierarchies

An invariance is tuple $Inv := (P, A, f)$:

- $P = \times_{i=1}^n P_i$ a parameter space. 
- $A = \times_{i=1}^m A_i$ an argument space. Each $A_i = P_{Inv'}$ for some other invariance $Inv'$ defined previously. 
- a function with signature $f \rightarrow P_1 \rightarrow \cdots \rightarrow P_n \rightarrow \sigma(A) \rightarrow [0, 1]$. Here  $\sigma(A)$ is an inductive data structure containing elements of $A$. The set of invariancese are denoted by $\mathcal{I}$

We assume a hierarchy over the invariances so that if $P_{Inv'} = A_i$, then $A^{Inv'}_j \neq P_{Inv}$ for any argument space A^{Inv'}_j$ of $Inv'$ we denote this by $Inv > Inv'$.  Hence this defines a directed acyclic graph (DAG) $(V, E)$ over invariances so that $(Inv, Inv') \in E$ iff $Inv > Inv'$. Hence each $Inv$ has $\leq m$ incoming edges. The source nodes in this graph, or equivalently the base invariances, are elements extracted directly from the text (such as patches in images). For these elements, $P = \{v_1, v_2, v_3\}$, $A = \emptyset$, f(v_i) = 1$ where $v_i$ are some singletons. Denote these sets by $\mathcal{B}$

So the hierarchy of we have defined is
- layer 0 are specific data elements (one example are patches), 
- layer i are are invariances that exist across elements in layers j, j < i. 

> **Example:** In our case, each data point is a binary string of length $d$. Here, each base invariances are fixed length strings of some length (like $3$). One set of invariances are maximum edit distance between a sequence of elements. Here $P = N$, $A = P_{B_i}$ for some base invariance $B_i$, and $f: N \rightarrow List[P] \rightarrow [0, 1]$, such that $f(m, [v_{i_0}, v_{i_1}, v_{i_2}, v_{i_3}] = 1$ iff the maximum edit distance between $v_{i_0}$ and any other $v_{i}$ is $\leq m$ 

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

- A node is at layer-$0$ if all its incoming edges are from source nodes.
- A node is at layer-$i$ if all its incoming edges are from nodes at layer $j$ where $j < i$. 
- Given graphs $G_{1:k}$, for each node at each layer, we construct a set of beams. Each beam consists of one node from the same layer $i$ of each $G_i$, such that the Invariance function $f$ matches. 
- The cost of a beam $\beta = \{n_1, n_2, n_k\}$ is the sum of the pairwise scores $score(\beta) := \sum_i \sum_{j < i} score(n_i, n_j)$
- We now form a beam graph such that $(\beta, \beta') \in G_B$ iff for each $(n_i, n'_i) \in G_i$ for each $i$.
- Given the beam graph, we extract the maximum score sub-graphs. 
- We then extract the final graph by unifying each beam into a single element element by finding the highest scoring unifier across the parameters. 



## Graph Anti-Unification Algorithm

The graph anti-unification algorithm takes as input a set of  graphs $\{H^y_{1:k_y}| y \in Y\}, H^y_i \in Sub(\mathcal{G}_{CA})$ finds the common  across all the $H^y_i, H^w_j$ and removes the common elements:

- Take the graphs
- Find and score the beams 
- If the score is above a threshold, eleminate the nodes in that beam.

## Generation of Conditional Matching.

Given a representations of the classes $\{H^y_{1:k_y}| y \in Y\}$, $\phi_M$ creates a representation of $x$ using the representation generation algorithm, 


- It then matches the representation against the graph using two element beam-forming, keeping the highest matching graph. 
- It outputs probablility scores based on the scores computed.


# Reasoning 

The representations are typed and can be reasoned over - reasoning can be reveal what will happen if things change. If extrapolation is possible - how stable things are. 




