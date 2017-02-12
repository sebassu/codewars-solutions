# Count the digit
1. Take an integer `n` `(n >= 0)` and a digit `d` `(0 <= d <= 9)` as an integer.
2. Square all numbers `k` `(0 <= k <= n)` between `0` and `n`.
3. Count the numbers of digits `d` used in the writing of all the `k^2`.

Call `NbDig`, a function taking `n` and `d` as parameters and returning this
count.

### Examples:

> `n = 10`, `d = 1`<br>
> The resulting `k*k` are `0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100`.<br>
> We are using the digit `1` in: `1, 16, 81, 100`. The total count is then `4`.

> `NbDig(25, 1)` returns `11` since the `k*k` that contain the digit 1 are:
`1, 16, 81, 100, 121, 144, 169, 196, 361, 441`.<br>
> Therefore, there are `11` 1 digits for the squares of numbers between `0` and
> `25`.

Note that 121 has the digit 1 twice.
