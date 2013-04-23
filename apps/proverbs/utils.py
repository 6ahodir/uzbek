from string import punctuation


def construct_question(text):
    """Transform text into a question, where each word's case is output.
    If the text reads "I went home, but no one was there.",
    the transformed text will look like so:
    ['u', 'l', 'l', ',', 'l', 'l', 'l', 'l', 'l', '.'],
    where 'u' stands for 'upper case', and 'l' stands for lowercase.
    Note that the punctuation mars are also in the list.
    """

    # add space before and after punctuataion marks so that we can split them
    spaced_punctuation = [' ' + x + ' ' for x in punctuation]
    text = text.translate(
        dict((ord(x), y) for (x, y) in zip(punctuation, spaced_punctuation))
    )

    result = []
    for word in text.split():
        if word in punctuation:
            result.append(word)
        elif word[0].isupper():
            result.append('u')
        else:
            result.append('l')

    return result
