using System.Text;

public class Kata
{
    public static string[] TowerBuilder(int numberOfFloors)
    {
        var result = new string[numberOfFloors];
        int baseLength = 2 * numberOfFloors - 1;
        for (int i = 0; i < numberOfFloors; i++)
        {
            result[i] = GenerateFloor(i, baseLength);
        }
        return result;
    }

    private static string GenerateFloor(int floorNumber, int length)
    {
        var result = new StringBuilder(length);
        int numberOfAsterisks = 2 * floorNumber + 1;
        int numberOfSpaces = (length - numberOfAsterisks) / 2;
        result.Append(' ', numberOfSpaces);
        result.Append('*', numberOfAsterisks);
        result.Append(' ', numberOfSpaces);
        return result.ToString();
    }
}
