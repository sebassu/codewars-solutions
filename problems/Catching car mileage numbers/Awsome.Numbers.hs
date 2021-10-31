module Awesome.Numbers where

import Data.Char (digitToInt)

data Answer = No | Almost | Yes deriving (Show, Read, Eq, Ord)

toDigits :: Integer -> [Integer]
toDigits = map (fromIntegral . digitToInt) . show

isInteresting :: Integer -> [Integer] -> Answer
isInteresting x xs
  | checkInteresting x xs = Yes
  | checkInteresting (x + 1) xs || checkInteresting (x + 2) xs = Almost
  | otherwise = No

checkInteresting :: Integer -> [Integer] -> Bool
checkInteresting x xs =
  x > 99
    && ( elem x xs || followedByZeros digits || sameNumber digits
           || secuentialIncrementing digits
           || secuentialDecrementing digits
           || palindrome digits
       )
  where
    digits = toDigits x

followedByZeros :: [Integer] -> Bool
followedByZeros xs = all (== 0) (tail xs)

sameNumber :: [Integer] -> Bool
sameNumber xs = all (== head xs) (tail xs)

secuentialIncrementing :: [Integer] -> Bool
secuentialIncrementing (x : y : xs) = comparingWith0As10 x y && secuentialIncrementing (y : xs)
  where
    comparingWith0As10 x y = mod y 10 == mod (x + 1) 10
secuentialIncrementing _ = True

secuentialDecrementing :: [Integer] -> Bool
secuentialDecrementing (x : y : xs) = x - 1 == y && secuentialDecrementing (y : xs)
secuentialDecrementing _ = True

palindrome :: [Integer] -> Bool
palindrome xs = xs == reverse xs