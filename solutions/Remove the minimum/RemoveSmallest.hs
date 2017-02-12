module Codewars.Kata.RemoveSmallest where

import Data.List (delete)

removeSmallest :: [Int] -> [Int]
removeSmallest xs = delete (minimum xs) xs
