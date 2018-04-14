from solutionparser import SolutionParser, SladerBook, SladerAnswer, SolutionParameters
import xml.etree.ElementTree as ET

# Alias for SolutionParameters
Params = SolutionParameters


class XmlSolutionParser(SolutionParser):
    """ Parse solutions from a given XML file. See example file
        for the format
    """
    def __init__(self, file_name):
        super().__init__(file_name)
        self.tree = ET.parse(self.file_name)
        self.root, self.sol_iter = None, None
        self._init_book()

    def _init_book(self):
        self.root = self.tree.getroot()
        book_tag = self.root.find(Params.TAG_BOOK)
        self.book = SladerBook(book_tag.get(Params.ATTR_ISBN),
                               book_tag.get(Params.ATTR_NAME))
        self.soln = SladerAnswer(self.book)
        self.sol_iter = iter(book_tag.findall(Params.TAG_SOLN))

    def _incr_soln(self, soln_tag):
        """ Clear the solution rows and increment the question
            number
        """
        self.soln.clear_rows()
        try:
            self.soln.q_num = str(int(self.soln.q_num) + 1)
        except ValueError as e:
            pass
        if soln_tag.get(Params.ATTR_CLEAR, "false") == "true":
            self.soln = SladerAnswer(self.book)
        return self.soln

    @staticmethod
    def _resolve_ext_ref(row_tag):
        """ Resolve external references for solution row """
        if not row_tag.get(Params.ATTR_REF)\
                or not row_tag.get(Params.ATTR_LINES):
            return ""
        s, e = [int(i.strip()) for i in row_tag.get(Params.ATTR_LINES)
                .split(",")]
        with open(row_tag.get(Params.ATTR_REF)) as f:
            return "".join(SolutionParser
                           ._filter_comments(f.readlines()[(s-1):e]))

    def _make_soln(self, soln_tag):
        """ Extract solution tag data into a SladerAnswer object
        """
        soln = self._incr_soln(soln_tag)
        # set the answer arguments
        for arg, setter in Params.ans_arg_setter.items():
            val = soln_tag.get(arg, None)
            if val:
                setter(soln, val)
        for row_tag in soln_tag.findall(Params.TAG_ROW):
            ext_ref = row_tag.get("ref")
            if ext_ref:
                row_text = XmlSolutionParser._resolve_ext_ref(row_tag)
            else:
                row_text = row_tag.text.strip()
            soln.add_solution_row(row_text)
        return soln

    def solutions(self):
        """ Generator for solutions """
        while True:
            soln_tag = next(self.sol_iter)
            yield self._make_soln(soln_tag)


if __name__ == "__main__":
    parser = XmlSolutionParser("test_sol.xml")
    for soln in parser.solutions():
        print("URL", soln.get_url())
        print(str(soln), "\n----------------------------------------")
