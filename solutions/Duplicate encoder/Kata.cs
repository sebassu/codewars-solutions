using System;
using System.Linq;
using System.Text;

public class Kata
{
    public static string DuplicateEncode(string word)
    {
        StringBuilder result = new StringBuilder(word.Length);
        var isDuplicate = word.GroupBy(x => Char.ToUpper(x))
                .ToDictionary(x => x.Key, x => x.Count() > 1);
        foreach (var character in word.ToUpper())
            result.Append(isDuplicate[character] ? ')' : '(');
        return result.ToString();
    }
}
