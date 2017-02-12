using System.Linq;

public class CountDig
{

    public static int NbDig(int n, int d)
    {
        var squares = Enumerable.Range(0, n + 1).Select(number => number * number);
        return squares.Sum(number => CountOcurrencesOfDigitIn((char)('0' | d), number));
    }

    private static int CountOcurrencesOfDigitIn(char digit, int number)
    {
        return number.ToString().Count(character => character == digit);
    }
}
