module Kata where

dontGiveMeFive :: Int -> Int -> Int
dontGiveMeFive start end = countNonFives [start..end]
  where countNonFives = length . filter (notElem '5' . show)
