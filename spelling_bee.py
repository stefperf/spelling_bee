# Riddler Classic "Spelling Bee" @ https://fivethirtyeight.com/features/can-you-solve-the-vexing-vexillology/

from itertools import chain, combinations

ADMISSIBLE_LETTERS = 'abcdefghijklmnopqrtuvwxyz' # all English alphabet except for 's'


def powerset(iterable):
    """
    standard-recipe implementation of powerset

    >>> list(powerset([1,2,3]))
    [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))


def set2str(charset):
    """
    converts a set of letters into a sorted string
    """
    return ''.join(sorted(list(charset)))


class Word:
    """
    Stores a word with its properties, computed at initialization; a word is valuable if worth more than zero points
    """
    def __init__(self, word):
        self.word = word
        self.val, self.letters, self.n_letters = self.word_val(word)

    def __str__(self):
        return "<%s,%d,%s,%d>" % (self.word, self.val, set2str(self.letters), self.n_letters)

    def is_valuable(self):
        return self.val > 0

    @staticmethod
    def word_val(word):
        """
        computes the value of a word according to the rules of the game
        """
        word_len = len(word)
        letters = frozenset(word)
        n_letters = len(letters)
        if word_len > 4:
            word_val = word_len
            if n_letters >= 7:
                word_val += 7
        elif word_len == 4:
            word_val = 1
        else:
            word_val = 0
        return word_val, letters, n_letters


class LetterSet:
    """
    stores a letter set, including the list of valuable words (as Word objects) that share that exact letter set
    """
    def __init__(self, letters):
        self.letters = letters
        self.n_letters = len(letters)
        self.words = []
        self.val = 0

    def __str__(self):
        return "<%s,%d,[%s]>" % (set2str(self.letters), self.val, ','.join([str(w) for w in self.words]))

    def add_word(self, word):
        self.words.append(word)
        self.val += word.val


class SpellingBee:
    """
    stores a spelling bee puzzle which is valid according to the rules of the game
    """
    def __init__(self, letters, center_letter):
        self.letters = letters
        self.center_letter = center_letter
        self.key = self.get_key()
        self.letter_sets = {}
        self.val = 0

    def __str__(self):
        return '<%s,%d>' % (self.key, self.val)

    def get_key(self):
        """
        represents the puzzle as a sorted string where only the central letter is capitalized
        """
        key = list(set2str(self.letters))
        for i, letter in enumerate(key):
            if letter == self.center_letter:
                key[i] = str(chr(ord(key[i]) + ord('A') - ord('a')))
        return ''.join(key)

    @classmethod
    def from_letters(cls, seven_letters):
        """
        returns all 7 spelling bees possible with the given 7 letters, by varying the central letter
        """
        spelling_bees = {}
        for letter in seven_letters:
            spelling_bee = cls(seven_letters, center_letter=letter)
            spelling_bees[spelling_bee.key] = spelling_bee
        return spelling_bees

    def letter_subsets(self):
        """
        returns all possible letter subsets of this puzzle including at least the central letter, as per the game rules
        """
        other_letters = self.letters.difference(set(self.center_letter))
        return [frozenset([self.center_letter] + list(ls)) for ls in powerset(other_letters)]

    def evaluate(self, all_letter_sets, debug=False):
        """
        finds all letter subsets that bring points for this puzzle and sum up the points
        """
        for key in self.letter_subsets():
            if key in all_letter_sets:
                ls = all_letter_sets[key]
                self.letter_sets[key] = ls
                self.val += ls.val
                if debug: print(ls)
            else:
                if debug: print('key %s not found' % key)

    def get_words(self):
        """
        yields all valuable words that can be found in this puzzle
        """
        for ls in self.letter_sets.values():
            for w in ls.words:
                yield w


# parse word list, collecting all valuable words and organizing them by their letter sets
valuable_words = []
all_letter_sets = {}
with open('enable1.txt') as file:
    for line in file:
        word = Word(line.strip())
        if word.is_valuable() and word.n_letters <= 7 and 's' not in word.letters:
            if word.n_letters == 1:
                print('Word %s has only one letter!' % word.word)
            # elif word.n_letters == 2:
            #     print('Word %s has only two letters!' % word.word)
            valuable_words.append(word)
            if word.letters not in all_letter_sets:
                new_ls = LetterSet(word.letters)
                all_letter_sets[word.letters] = new_ls
                # for letter in word.letters:
                #     letter_sets_by_letter[letter][word.letters] = new_ls
            all_letter_sets[word.letters].add_word(word)

# # debug
# print(len(valuable_words))
# print([str(w) for w in valuable_words[:10]])
# print(len(all_letter_sets))
# for ls in list(all_letter_sets.values())[:5]:
#     print('%s' % ls)

# collect the sets of 7 letters, corresponding to pangrams
seven_letter_sets = {}
for letters, ls in all_letter_sets.items():
    if ls.n_letters == 7:
        seven_letter_sets[letters] = ls

# # debug
# print(len(seven_letter_sets))
# for ls in list(seven_letter_sets.values())[:5]:
#     print('%s' % ls)

# create and collect the 7 spelling bees that are possible from each pangram
spelling_bees = {}
for ls in seven_letter_sets.values():
    spelling_bees.update(SpellingBee.from_letters(ls.letters))

# # debug
# print(len(spelling_bees))
# for sb in list(spelling_bees.values())[:5]:
#     print('%s' % sb)

# # debug
# print(spelling_bees['adfloRw'].letter_subsets())
# spelling_bees['adfloRw'].evaluate(all_letter_sets, debug=True)
# print(spelling_bees['adfloRw'])
# for ls in spelling_bees['adfloRw'].letter_sets:
#     print(ls)

# evaluate all spelling bees, then rank them
for sb in spelling_bees.values():
    sb.evaluate(all_letter_sets)
ranked_spelling_bees = list(spelling_bees.values())
ranked_spelling_bees.sort(key=lambda el: (-el.val, el.key))

# show top 10 spelling bees
print('Top 10 spelling bees, with central letter capitalized:')
for i, sb in enumerate(ranked_spelling_bees[:10], 1):
    print('#%d: spelling bee %s => %s points' % (i, sb.key, sb.val))
top_sb = ranked_spelling_bees[0]
top_words = list(top_sb.get_words())
print()

# show the words of the nr. 1 spelling bee
print('The #1 spelling bee %s contains these %d words, from best to worst word:' % (top_sb.key, len(top_words)))
for i, w in enumerate(sorted(top_words, key=lambda w: (-w.val, w.word)), 1):
    print('#%d: word %s => %d points' %(i, w.word, w.val))
