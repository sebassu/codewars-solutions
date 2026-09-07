#include <iostream>

class Kata
{
public:
    std::string replaceNth(std::string text, int n, char oldValue, char newValue)
    {
        if (n <= 0)
            return text;
        unsigned int count = 0;
        for (int i = 0; i < text.length(); i += 1)
        {
            if (text[i] == oldValue)
                count += 1;
            if (count == n)
            {
                text[i] = newValue;
                count = 0;
            }
        }
    }
};
