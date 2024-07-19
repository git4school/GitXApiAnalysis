from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb
import copy


class TrimContentPrefixAndSuffix(PostProcessModifier):

    def level(self):
        return Verb

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        if not "git" in statement.object.definition.extensions:
            return

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]
        statements = [statement]

        for diff in differentials:
            if diff == None or diff.parts == None:
                continue
            for diffpart in diff.parts[-1:]:
                content = diffpart.content

                i = 0
                while i < len(content):
                    line = content[i]

                    if len(line) == 0 or line[0] == " ":
                        i += 1
                        continue
                    first_sign = line[0]
                    last_of_first = [
                        j
                        for j in range(i, len(content))
                        if not content[j].startswith(first_sign)
                    ]
                    if len(last_of_first) == 0:
                        i += 1
                        continue
                    last_of_first = last_of_first[0] - 1

                    first_of_second = last_of_first + 1

                    if first_of_second >= len(content) or content[first_of_second][
                        0
                    ] in [" ", first_sign]:
                        i = last_of_first + 2
                        continue

                    second_sign = content[first_of_second][0]

                    last_of_second = [
                        j
                        for j in range(first_of_second, len(content))
                        if not content[j].startswith(second_sign)
                    ] + [len(content)]
                    last_of_second = last_of_second[0] - 1
                    min_len = min(
                        last_of_first + 1 - i, last_of_second + 1 - first_of_second
                    )

                    for k in range(min_len):
                        if content[i + k][1:] == content[first_of_second + k][1:]:
                            content[i + k] = None
                            content[first_of_second + k] = (
                                " " + content[first_of_second + k][1:]
                            )
                    diffpart.content = [l for l in content if l != None]
                    i = last_of_second + 1

            diffpart.a_interval = len(
                [None for l in diffpart.content if not l.startswith("-")]
            )
            diffpart.b_interval = len(
                [None for l in diffpart.content if not l.startswith("+")]
            )

        return [(st, False) for st in statements]
