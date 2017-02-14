module Codewars.Kata.XO where

import Data.Char (toLower)

xo :: String -> Bool
xo str = length (filter (auxCompare 'x') str) == length (filter (auxCompare 'o') str)

auxCompare :: Char -> Char -> Bool
auxCompare c1 c2 = c1 == toLower c2
