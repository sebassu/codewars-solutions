# Directions Reduction
**Once upon a time, on a way through the old wild _mountainous_ west…**<br>
… a man was given directions to go from one point to another. The directions
were `"NORTH"`, `"SOUTH"`, `"WEST"` and `"EAST"`. Clearly `"NORTH"` and
`"SOUTH"` are opposite, `"WEST"` and `"EAST"` too.

Going to one direction and coming back the opposite direction right away is a
needless effort. Since this is the wild west, with dreadful weather and not much
water, it's important to save yourself some energy, otherwise you might die of
thirst!

### How I crossed a _mountainous_ desert the smart way.
The directions given to the man are, for example, the following:

> `["NORTH", "SOUTH", "SOUTH", "EAST", "WEST", "NORTH", "WEST"]`.

You can immediately see that going `"NORTH"` and immediately `"SOUTH"` is not
reasonable, better stay to the same place! So the task is to give to the man a
simplified version of the plan. A better plan in this case is simply:

> `["WEST"]`

### Other examples:
In `["NORTH", "SOUTH", "EAST", "WEST"]`, the direction `"NORTH" + "SOUTH"` is
going north and coming back right away.

The path becomes `["EAST", "WEST"]`, now `"EAST"` and `"WEST"` annihilate each
other, therefore, the final result is `[]`.

In `["NORTH", "EAST", "WEST", "SOUTH", "WEST", "WEST"]`, `"NORTH"` and `"SOUTH"`
are not directly opposite but they become directly opposite after the reduction
of `"EAST"` and `"WEST"` so the whole path is reducible to `["WEST", "WEST"]`.

## Task
Write a function `dirReduc` which will take an `array` of `strings` and returns
an array of strings with the needless directions removed (`West ↔ East` or
`South ↔ North` side by side).

#### Note
* Not all paths can be made simpler. The path
`["NORTH", "WEST", "SOUTH","EAST"]` is not reducible. `"NORTH"` and `"WEST"`,
`"WEST"` and `"SOUTH"`, `"SOUTH"` and `"EAST"` are not directly opposite of each
other and can't become such. Hence the result path is itself: 
`["NORTH", "WEST", "SOUTH", "EAST"]`.
