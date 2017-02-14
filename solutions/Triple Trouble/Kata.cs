using System;
using System.Linq;
using System.Collections.Generic;

public class Kata
{
    public static int TripleDouble(long num1, long num2)
    {
        int[] digitsNum1 = ExtractDigitsFromNumber(num1);
        int[] digitsNum2 = ExtractDigitsFromNumber(num2);
        IList<int> validElementsInNum1 = ValidateStraights(digitsNum1, 3);
        IList<int> validElementsInNum2 = ValidateStraights(digitsNum2, 2);
        return ListsHaveCommonElements<int>(validElementsInNum1, validElementsInNum2) ? 1 : 0;
    }

    private static bool ListsHaveCommonElements<T>(IList<T> list1, IList<T> list2)
    {
        return list1.Intersect(list2).Any();
    }

    private static IList<int> ValidateStraights(int[] digits, int repeatsNeeded)
    {
        IList<int> result = new List<int>();
        int previousDigit = Int32.MinValue;
        int repeatsDetected = 1;
        foreach (var digit in digits)
        {
            if (digit == previousDigit) repeatsDetected += 1;
            else repeatsDetected = 1;

            if (repeatsDetected == repeatsNeeded) result.Add(digit);
            previousDigit = digit;
        }
        return result;
    }

    private static int[] ExtractDigitsFromNumber(long number)
    {
        return number.ToString().Select(d => Convert.ToInt32(d)).ToArray();
    }
}
