module Graph.Solution where

import Data.List (delete)

type Node = Char

type Arc = (Node, Node)

solveGraph :: Node -> Node -> [Arc] -> Bool
solveGraph _ _ [] = False
solveGraph s e (x : xs) =
  s == e || fst x == s && snd x == e
    || any (\y -> solveGraph (snd y) e (delete y (x : xs))) (filter ((== s) . fst) (x : xs))