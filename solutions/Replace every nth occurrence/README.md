# Replace every n<sup>th</sup> character
Write a method that replaces every n<sup>th</sup> `char` `oldValue` with `char`
`newValue`.

> `replaceNth(std::string text, int n, char oldValue, char newValue)`

### Example:

> `n`: 2<br>
> `oldValue`: 'a'<br>
> `newValue`: 'o'<br>
> "Vader said: No, I am your father!" -> "Vader soid: No, I am your fother!"

Your method has to be case sensitive!

As you can see in the example, the first `'a'` changed is the second one, so the
start is always at the n<sup>th</sup> suitable character and not the first!

If `n` is `0` or negative, or if it is larger than the count of `oldValue` 
appearances, return the original text without any change. The text and the 
character parameters will never be `null`.
