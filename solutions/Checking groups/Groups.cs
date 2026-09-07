using System;
using System.Collections.Generic;

public static class Groups
{
    private static readonly Dictionary<char, char>
        ValidParenthesisPairs =
            new Dictionary<char, char>()
            { { '{', '}' }, { '[', ']' }, { '(', ')' } };

    public static bool Check(string input)
    {
        var parenthesis = new Stack<char>();
        foreach (var character in input)
        {
            if (IsOpeningParenthesis(character))
                parenthesis.Push(character);
            else if (ParenthesisMatch(character, parenthesis.Peek()))
                parenthesis.Pop();
            else
                return false;
        }
        return parenthesis.Count == 0;
    }

    private static bool ParenthesisMatch(char character)
    {
        return ValidParenthesisPairs.ContainsKey(character);
    }

    private static bool CharacterMatchesTop(char character, char top)
    {
        return character == ValidParenthesisPairs[top];
    }
}
