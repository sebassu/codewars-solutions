using System;

public class Tortoise
{
    public static int[] Race(int v1, int v2, int g)
    {
        if (v1 >= v2) return null;
        var time = TimeSpan.FromHours((double) g / (v2 - v1));
        return new int[] { time.Hours, time.Minutes, time.Seconds };
    }
}
