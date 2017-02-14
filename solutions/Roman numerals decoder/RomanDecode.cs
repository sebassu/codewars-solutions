using System.Linq;
using System.Collections.Generic;

public class RomanDecode
{
    private static readonly Dictionary<char, int> Value =
            new Dictionary<char, int>() {
                { 'M', 1000 }, { 'D', 500 }, { 'C', 100 },
                { 'L', 50 }, { 'X', 10 }, { 'V', 5 }, { 'I', 1 }
            };

    public static int Solution(string roman)
    {
        var result = 0;
        var previousValue = int.MinValue;
        foreach (var value in roman.ToCharArray().Select(c => Value[c]).Reverse())
        {
            result += value < previousValue ? -value : value;
            previousValue = value;
        }
        return result;
    }
}
