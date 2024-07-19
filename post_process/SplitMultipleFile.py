from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb
import copy


class SplitMultipleFile(PostProcessModifier):

    def level(self):
        return Verb

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        if not "git" in statement.object.definition.extensions:
            return

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        if len(differentials) <= 1:
            return

        statements = []

        for i in range(1, len(differentials)):

            newstatement: Statement = copy.deepcopy(statement)
            statements.append(newstatement)

            newstatement.object.id = (
                "generated~split~" + newstatement.object.id + "~" + str(i)
            )

            newstatement.object.definition.extensions["git"] = [differentials[i]]

        statement.object.definition.extensions["git"] = [differentials[0]]

        return [(st, False) for st in statements]
