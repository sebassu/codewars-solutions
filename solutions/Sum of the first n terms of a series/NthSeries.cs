using System;

public class NthSeries
{

    public static string seriesSum(int number)
    {
        double result = 0;
        for (double i = 0; i < number; i++) result += 1 / (3 * i + 1);
        return result.ToString("0.00");
    }
}