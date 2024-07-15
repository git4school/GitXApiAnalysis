from post_process.PostProcessModifier import PostProcessModifier
from tincan import Statement, Verb
from tincan import *


class FillXApiMissingField(PostProcessModifier):

    def level(self):
        return Statement

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        if statement.context == None:
            statement.context = Context()

        if statement.context.extensions == None:
            statement.context.extensions = dict()

        if not "classified" in statement.context.extensions:
            statement.context.extensions["classified"] = []

        if not "atomic" in statement.context.extensions:
            statement.context.extensions["atomic"] = False

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
