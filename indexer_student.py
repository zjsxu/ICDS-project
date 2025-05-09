import pickle


class Index:
    def __init__(self, name):
        self.name = str(name)
        self.msgs = []
        """
        ["1st_line", "2nd_line", "3rd_line", ...]
        Example:
        "How are you?\nI am fine.\n" will be stored as
        ["How are you?", "I am fine." ]
        """

        self.index = {}
        """
        {word1: [line_number_of_1st_occurrence,
                 line_number_of_2nd_occurrence,
                 ...]
         word2: [line_number_of_1st_occurrence,
                  line_number_of_2nd_occurrence,
                  ...]
         ...
        }
        """

        self.total_msgs = 0
        self.total_words = 0

    def get_total_words(self):
        return self.total_words

    def get_msg_size(self):
        return self.total_msgs

    def get_msg(self, n):
        return self.msgs[n]

    def add_msg(self, m):
        """
        m: the message to add

        updates self.msgs and self.total_msgs
        """
        # IMPLEMENTATION
        # ---- start your code ---- #
        lines = m.split('\n')
        washed_lines = [line.strip() for line in lines if line.strip()]
        self.msgs.extend(washed_lines)
        self.total_msgs += len(washed_lines)
        # ---- end of your code --- #
        return self.msgs

    def add_msg_and_index(self, m):
        self.add_msg(m)
        line_at = self.total_msgs - 1
        self.indexing(m, line_at)

    def indexing(self, m, l):
        """
        updates self.total_words and self.index
        m: message, l: current line number
        """

        # IMPLEMENTATION
        # ---- start your code ---- #

        words = m.split()
        for word in words:
            clean_word = word.lower().strip(',.?!')
            if clean_word:
                self.index.setdefault(clean_word, []).append(l)
                self.total_words += 1
        # ---- end of your code --- #
        return self.index

    # implement: query interface

    def search(self, term):
        """
        return a list of tupple.
        Example:
        if index the first sonnet (p1.txt),
        then search('thy') will return the following:
        [(7, " Feed'st thy light's flame with self-substantial fuel,"),
         (9, ' Thy self thy foe, to thy sweet self too cruel:'),
         (9, ' Thy self thy foe, to thy sweet self too cruel:'),
         (12, ' Within thine own bud buriest thy content,')]
        """
        msgs = []
        # IMPLEMENTATION
        # ---- start your code ---- #
        if term not in self.index:
            return []
        line_numbers = self.index[term]
        for line_num in line_numbers:
            line_content = self.msgs[line_num]
            msgs.append((line_num, line_content))
        # ---- end of your code --- #
        return msgs


class PIndex(Index):
    def __init__(self, name):
        super().__init__(name)
        roman_int_f = open('roman.txt.pk', 'rb')
        self.int2roman = pickle.load(roman_int_f)
        # print(self.int2roman)
        roman_int_f.close()
        self.load_poems()

    def load_poems(self):
        """
        open the file for read, then call
        the base class's add_msg_and_index()
        """
        # IMPLEMENTATION
        # ---- start your code ---- #
        with open(self.name, 'r') as f:
            self.add_msg_and_index(f.read())

        # ---- end of your code --- #
        return self

    def get_poem(self, p):
        """
        p is an integer, get_poem(1) returns a list,
        each item is one line of the 1st sonnet

        Example:
        get_poem(1) should return:
        ['I.', '', 'From fairest creatures we desire increase,',
         " That thereby beauty's rose might never die,",
         ' But as the riper should by time decease,',
         ' His tender heir might bear his memory:',
         ' But thou contracted to thine own bright eyes,',
         " Feed'st thy light's flame with self-substantial fuel,",
         ' Making a famine where abundance lies,',
         ' Thy self thy foe, to thy sweet self too cruel:',
         " Thou that art now the world's fresh ornament,",
         ' And only herald to the gaudy spring,',
         ' Within thine own bud buriest thy content,',
         " And, tender churl, mak'st waste in niggarding:",
         ' Pity the world, or else this glutton be,',
         " To eat the world's due, by the grave and thee.",
         '', '', '']
        """
        poem = []

        current_num = self.int2roman[p] + '.'
        next_num = self.int2roman[p + 1] + '.' if p + 1 in self.int2roman else None

        start_lines = [line_num for line_num, line in enumerate(self.msgs)
                       if line.startswith(current_num)]
        if not start_lines:
            return poem

        start_line = start_lines[0]

        end_line = len(self.msgs)
        if next_num:
            end_lines = [line_num for line_num, line in enumerate(self.msgs)
                         if line.startswith(next_num)]
            if end_lines:
                end_line = end_lines[0]

        poem = self.msgs[start_line:end_line]
        return poem


if __name__ == "__main__":
    sonnets = PIndex("AllSonnets.txt")
    # the next two lines are just for testing
    p3 = sonnets.get_poem(22)
    print(p3)
    # s_love = sonnets.search("love")
    # print(s_love)
