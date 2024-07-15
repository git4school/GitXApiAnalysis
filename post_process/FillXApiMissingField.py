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
