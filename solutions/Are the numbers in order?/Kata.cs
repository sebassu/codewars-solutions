using System;

public class Kata
{
    public static bool IsAscOrder(int[] numbers)
    {
        int previousNumber = 0;
        foreach (int currentNumber in numbers)
        {
            if (currentNumber < previousNumber) return false;
            previousNumber = currentNumber;
        }
        return true;
    }
}
