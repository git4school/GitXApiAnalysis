from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb


class TrimAtomic(PostProcessModifier):
    def level(self):
        return DiffPart

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        extensions = statement.object.definition.extensions

        if not "git" in extensions:
            return

        differentials: list[Differential] = extensions["git"]

        if not statement.context.extensions["atomic"] and not all(
            [
                all(
                    [
                        all(
                            True for l in d2.content if len(l) == 0 or l.startswith(" ")
                        )
                        for d2 in d.parts
                        if d2 != None
                    ]
                )
                for d in differentials
                if d != None and d.parts != None
            ]
        ):
            return

        for i in range(len(differentials)):
            if differentials[i].parts == None:
                continue
            for j in range(len(differentials[i].parts)):
                differentials[i].parts[j] = PostProcessModifier.trim_diff(
                    differentials[i].parts[j]
                )
