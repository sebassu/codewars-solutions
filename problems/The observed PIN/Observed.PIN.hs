module Observed.PIN where

import Data.Maybe (fromJust)

adjacentDigits :: [(Char, String)]
adjacentDigits =
  [ ('0', "8"),
    ('1', "24"),
    ('2', "135"),
    ('3', "26"),
    ('4', "157"),
    ('5', "2468"),
    ('6', "359"),
    ('7', "48"),
    ('8', "0579"),
    ('9', "68")
  ]

getPINs :: String -> [String]
getPINs [] = []
getPINs (x : xs) = case getPINs xs of
  [] -> [x] : map (: []) adjacentDigitsOfX
  (y : ys) -> [a : b | a <- x : adjacentDigitsOfX, b <- getPINs xs]
  where
    adjacentDigitsOfX = fromJust (lookup x adjacentDigits)