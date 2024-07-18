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
                if differentials[i].parts[j] == None:
                    continue
                differentials[i].parts[j] = PostProcessModifier.trim_diff(
                    differentials[i].parts[j]
                )

    def process(self, statements: list[Statement]):

        i = 0

        elements = [(s, True) for s in statements]

        while i < len(statements):

            to_process = elements[i][1]

            if not to_process:
                i += 1
                continue

            l = self._process(
                lambda x: elements[x][0] if 0 <= x < len(elements) else None, i
            )

            if l == None:
                l = [(elements[i][0], False)]
            elements = elements[:i] + l + elements[i + 1 :]
        elements = [e[0] for e in elements]

        return [
            e
            for e in elements
            if not "git" in e.object.definition.extensions
            or any(
                [
                    any([p != None for p in diff.parts])
                    for diff in e.object.definition.extensions["git"]
                    if diff != None and diff.parts != None
                ]
            )
        ]
