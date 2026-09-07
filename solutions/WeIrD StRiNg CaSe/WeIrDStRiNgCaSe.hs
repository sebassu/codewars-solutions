module WeIrDStRiNgCaSe where

import Data.Char (toLower, toUpper)

toWeirdCase :: String -> String
toWeirdCase str = unwords (map (toWeirdCaseAux True) (words str))

toWeirdCaseAux :: Bool -> String -> String
toWeirdCaseAux _ [] = []
toWeirdCaseAux b (x : xs)
  | b = toUpper x : rest
  | otherwise = toLower x : rest
  where
    rest = toWeirdCaseAux (not b) xs
