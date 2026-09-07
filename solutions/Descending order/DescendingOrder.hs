module DescendingOrder where

import Data.List (sort)

descendingOrder :: Integer -> Integer
descendingOrder = read . reverse . sort . show
