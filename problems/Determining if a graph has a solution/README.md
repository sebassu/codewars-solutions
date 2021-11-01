# Determining if a graph has a solution
Implement a function `solve_graph`/`solveGraph` (or equivalent depending
on your language) accepting 3 arguments in the given order:
1. `start` - The initial node of the directed graph
2. `end` - The destination node of the directed graph
3. `arcs` - A directed graph represented by a list/array of directed
   edges

It must return a boolean value depending on whether the destination node
can be reached from the initial node by traversing zero or more directed
edges. That means that if the start and end nodes are identical then the
end node is trivially considered to be reachable - return `true`/`True`
in this case. Also, if the start and end nodes are distinct and either
node does not appear in arcs then you should return `false`/`False`
since there is no sequence of directed edges that you may traverse to
reach the end node from the start node.

You may not assume any properties of the given directed graph (other
than the fact that it is a directed graph) - for example, the given
directed graph may contain multiple edges (in either direction) between
two nodes or contain loops (directed edges starting and finishing on the
same node).

You may also wish to take a look at adjacency lists.

### Example:
    -- The given directed graph has (at least) two nodes
    -- 'a', 'b' (and maybe other nodes as well) and two
    -- directed edges: 'a' -> 'b' and 'a' -> 'a' (a loop)
    let arcs = [('a', 'b'), ('a', 'a')]

    -- We can reach node 'b' from node 'a' by traversing 1
    -- directed edge 'a' -> 'b'
    solveGraph 'a' 'b' arcs `shouldBe` True

    -- There exists no sequence of directed edges that could
    -- bring us from 'a' to 'c'
    solveGraph 'a' 'c' arcs `shouldBe` False
