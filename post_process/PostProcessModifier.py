from tincan import *
from gittoxapi.differential import Differential, DiffPart


class PostProcessModifier:
    def __init__(self) -> None:
        pass

    def level(self):
        pass

    """
    Returns a list where each statement is linked to a boolean which describe whether this statement*
    should be reprocessed by this modifier
    """

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:
        pass

    def process(self, statements: list[Statement]):

        i = 0

        elements = [(s, True) for s in statements]

        while i < len(statements):

            to_process = elements[i][1]

            if not to_process:
                i += 1
                continue

            l = self._process(lambda x: elements[x][0], i)

            if l == None:
                l = [(elements[i][0], False)]
            elements = elements[:i] + l + elements[i + 1 :]

        return [e[0] for e in elements]
