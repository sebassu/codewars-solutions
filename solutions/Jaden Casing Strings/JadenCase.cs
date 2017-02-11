using System;

public static class JadenCase
{
    public static string ToJadenCase(this string phrase)
    {
        string[] words = phrase.Split(' ');
        for (int i = 0; i < words.Length; i++)
            UppercaseFirstLetterOfWord(ref words[i]);
        return string.Join(" ", words);
    }

    public static void UppercaseFirstLetterOfWord(ref string word)
    {
        char[] wordLetters = word.ToCharArray();
        wordLetters[0] = char.ToUpper(wordLetters[0]);
        word = new string(wordLetters);
    }
}
