module Isogram where

import Data.Char (toUpper)
import Data.List (nub)

isIsogram :: String -> Bool
isIsogram str = list == nub list
  where
    list = map toUpper str