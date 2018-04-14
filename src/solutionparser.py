class SladerBook:
    """ Represents a book in slader
    """
    def __init__(self, isbn="", name=""):
        self.book = (isbn, name)
        self.exercise_type = None
        self.page = None
        self.q_num = None

    def set_name(self, name):
        self.book = (self.book[0], name)
        return self

    def set_isbn(self, isbn):
        self.book = (isbn, self.book[1])
        return self


class SladerAnswer:
    """ Represents the answer, both the book and the text rows
    """
    URL_FMT = "https://slader.com/textbook/{isbn}/{pg}/{extype}/{qno}/"

    def __init__(self, book):
        self.book = book
        self.rows = []
        self.page, self.q_num = 0, 0
        self.exercise_type = ""

    def add_solution_row(self, text):
        if text:
            self.rows.append(text)
        else:
            raise ValueError("Null text not allowed")

    def clear_rows(self):
        self.rows = []

    def set_page_number(self, pg_no):
        self.page = pg_no
        return self

    def set_exercise_type(self, typ):
        self.exercise_type = typ
        return self

    def set_question_num(self, qno):
        self.q_num = qno
        return self

    def get_url(self):
        if self.exercise_type and self.page and self.q_num:
            return SladerAnswer.URL_FMT \
                        .format(isbn=self.book.book[0],
                                name=self.book.book[1],
                                pg=self.page, extype=self.exercise_type,
                                qno=self.q_num)
        else:
            raise ValueError("Invalid page_number")

    def __str__(self):
        string = "{book}: Exercise {ex}, Page {pg}, Question {qno}"\
                        .format(book=self.book.book[0],
                                ex=self.exercise_type,
                                pg=self.page, qno=self.q_num)
        string += "\n" + "\n\n".join(self.rows)
        return string


class SolutionParameters:
    # Book attributes
    TAG_BOOK = r"book"
    ATTR_ISBN = r"isbn"
    ATTR_NAME = r'name'
    book_arg_setter = {
        ATTR_ISBN: SladerBook.set_isbn,
        ATTR_NAME: SladerBook.set_name
    }

    # Answer Attributes
    ATTR_EX_NAME = r'exname'
    ATTR_PAGE_NUM = r'page'
    ATTR_QUES_NUM = r'quesnum'
    ATTR_CLEAR = r'clear'
    ATTR_REF = r'ref'
    ATTR_LINES = r'lines'
    ans_arg_setter = {
        ATTR_EX_NAME: SladerAnswer.set_exercise_type,
        ATTR_PAGE_NUM: SladerAnswer.set_page_number,
        ATTR_QUES_NUM: SladerAnswer.set_question_num
    }
    TAG_SOLN = r'solution'
    TAG_ROW = r'row'
    SOLN_BEGIN = r'sol_start'
    SOLN_END = r'end'

    @classmethod
    def make_command(cls, tag):
        return "\\" + tag


class SolutionParser:
    def __init__(self, file_name):
        self.file_name = file_name
        self.book = None

    def __enter__(self):
        pass

    @staticmethod
    def _filter_comments(lines):
        return filter(lambda x: x.strip() and x.strip()[0] != ";", lines)

    def solutions(self):
        """ Generator to generate all solutions from the
            file or directory
        """
        pass

    def get_book(self):
        return self.book

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class TextSolutionParser(SolutionParser):
    """ Parse solutions from a given text file. The top of the file
        should contain book details
    """

    def __init__(self, file_name):
        super().__init__(file_name)
        self.book = SladerBook()

    def __enter__(self):
        self.file = open(self.file_name, "r")
        self.init_book()
        return self

    def process_line(self, line):
        if len(line.split(maxsplit=2)) < 2:
            return False
        cmd, arg = line.split(maxsplit=2)
        if cmd not in SolutionParameters.book_arg_setter:
            return False
        SolutionParameters.book_arg_setter[cmd](self.book, arg)
        return True

    def init_book(self):
        for line in self.file:
            line = line.strip()
            if line == SolutionParameters.SOLN_BEGIN:
                break
            self.process_line(line)

    def _parse_solution_row(self):
        soln_row = ""
        empty_flag = False
        for line in self.file:
            line = line[:-1] if line[-1] == '\n' else line
            if (line == "" and empty_flag) or \
                    line == SolutionParameters.SOLN_END:
                break
            empty_flag = (line == "")
            soln_row += line + "\n"
        return soln_row.strip(), line

    def solutions(self):
        """ Genertor to return solutions"""
        ans = SladerAnswer(self.book)
        # Iterate through answers
        for line in self.file:
            line = line.strip()
            if not line: continue
            split = line.split()
            if split[0] == SolutionParameters.TAG_SOLN:
                ans.book.set_page_number(split[1]).set_question_num(split[2])
            # Read a row of solution
            if line == SolutionParameters.TAG_ROW:
                soln_row, line = self._parse_solution_row()
                if soln_row:
                    ans.add_solution_row(soln_row)
            if line == SolutionParameters.SOLN_END:
                yield ans
                ans = SladerAnswer(self.book)
    # yield ans

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()


class SolutionDirParser(SolutionParser):
    pass


if __name__ == "__main__":
    with TextSolutionParser("solns") as prsr:
        for soln in prsr.solutions():
            print("Pg, Q:", soln.book.page, soln.book.q_num, soln.book.exercise_type)
            for row in soln.rows:
                print(row + "\n\n")
            print("########################")
