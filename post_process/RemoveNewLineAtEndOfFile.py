from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb


class RemoveNewLineAtEndOfFile(PostProcessModifier):

    def level(self):
        return Verb

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        if not "git" in statement.object.definition.extensions:
            return

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        for diff in differentials:

            if diff.parts == None:
                continue

            for diffpart in diff.parts:

                if diffpart.content == None or len(diffpart.content) == 0:
                    continue

                diffpart.content = [
                    line
                    for line in diffpart.content
                    if line != "\\ No newline at end of file"
                ]
