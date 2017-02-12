module Codewars.Kata.DigPow where

digpow :: Integer -> Integer -> Integer
digpow n p = case mod powerSum n of
  0 -> div powerSum n
  _ -> -1
  where
    powerSum = sum (zipWith (^) (map toInteger (digits n)) [p .. (p + toInteger (length (digits n)))])

digits :: Integer -> [Int]
digits = map (read . return) . show
