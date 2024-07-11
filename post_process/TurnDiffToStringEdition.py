from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb


def count_quote(str):

    tilde_count = 0

    for c in str:
        if c == '"':
            tilde_count += 1

    return tilde_count


class TurnDiffToStringEdition(PostProcessModifier):
    def level(self):
        return DiffPart

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        extensions = statement.object.definition.extensions

        if not "git" in extensions:
            return

        differentials: list[Differential] = extensions["git"]

        for diff in differentials:
            if diff.parts == None:
                continue
            for diffpart in diff.parts:
                content = diffpart.content
                if (
                    len(content) != 2
                    or len(content[0]) <= 1
                    or len(content[1]) <= 1
                    or content[0][0] == content[1][0]
                ):
                    return

                insertion_begin_index = 1
                insertion_end_index = 0

                min_len = min(len(content[0]), len(content[1]))

                while (
                    insertion_begin_index < min_len
                    and content[0][insertion_begin_index]
                    == content[1][insertion_begin_index]
                ):
                    insertion_begin_index += 1

                while (
                    insertion_end_index < min_len
                    and content[0][len(content[0]) - insertion_end_index - 1]
                    == content[1][len(content[1]) - insertion_end_index - 1]
                ):
                    insertion_end_index += 1

                if not '"' in content[0] or not '"' in content[1]:
                    return

                prefix = [
                    content[0][:insertion_begin_index],
                    content[1][:insertion_begin_index],
                ]

                interval = [
                    content[0][
                        insertion_begin_index : len(content[0]) - insertion_end_index
                    ],
                    content[1][
                        insertion_begin_index : len(content[1]) - insertion_end_index
                    ],
                ]

                suffix = [
                    content[0][len(content[0]) - insertion_end_index :],
                    content[1][len(content[1]) - insertion_end_index :],
                ]
                if (
                    count_quote(interval[0]) % 2 != 0
                    or count_quote(interval[1]) % 2 != 0
                ):
                    return

                if (
                    count_quote(suffix[0]) * count_quote(prefix[0]) % 2 != 1
                    or count_quote(suffix[1]) * count_quote(prefix[1]) % 2 != 1
                ):
                    return

                if statement.context.extensions == None:
                    statement.context.extensions = {}
                if not "string_edition" in statement.context.extensions:
                    statement.context.extensions["string_edition"] = []

                editions = statement.context.extensions["string_edition"]
                if editions == None:
                    editions = []

                editions.append({"before": interval[0], "after": interval[1]})

                statement.context.extensions["string_edition"] = editions
