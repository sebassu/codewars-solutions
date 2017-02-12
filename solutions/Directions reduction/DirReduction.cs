using System;
using System.Linq;
using System.Collections.Generic;

public class DirReduction
{

    public static string[] dirReduc(string[] directions)
    {
        var result = new LinkedList<string>();
        foreach (var direction in directions)
        {
            var shouldBeReduced = result.Last?.Value.Equals(OppositeDirectionOf(direction));
            if (shouldBeReduced is true) result.RemoveLast();
            else result.AddLast(direction);
        }
        return result.ToArray();
    }

    private static string OppositeDirectionOf(string direction)
    {
        switch (direction)
        {
            case "NORTH": return "SOUTH";
            case "SOUTH": return "NORTH";
            case "WEST": return "EAST";
            case "EAST": return "WEST";
        }
        throw new ArgumentException("Invalid direction");
    }
}