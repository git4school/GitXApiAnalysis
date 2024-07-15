from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb


class TurnDiffToEdition(PostProcessModifier):
    def level(self):
        return DiffPart

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
                diffpart = PostProcessModifier.trim_diff(diffpart)
                content = diffpart.content
                if (
                    len(content) != 2
                    or len(content[0]) <= 1
                    or len(content[1]) <= 1
                    or content[0][0] == content[1][0]
                ):
                    return

                key = (
                    statement.object.id
                    + "_"
                    + diff.file
                    + "_"
                    + str(diffpart.a_start_line)
                )

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

                if statement.object.id == "#":
                    print("\n".join(content))
                    print(content[0][:insertion_begin_index])
                    print(content[1][:insertion_begin_index])

                    print(content[0][len(content[0]) - insertion_end_index :])
                    print(content[1][len(content[1]) - insertion_end_index :])

                    print(
                        content[0][
                            insertion_begin_index : len(content[0])
                            - insertion_end_index
                        ]
                    )
                    print(
                        content[1][
                            insertion_begin_index : len(content[1])
                            - insertion_end_index
                        ]
                    )

                if statement.context.extensions == None:
                    statement.context.extensions = {}
                if not "editions" in statement.context.extensions:
                    statement.context.extensions["editions"] = {}

                prefix = content[0][1:insertion_begin_index]
                before = content[0][
                    insertion_begin_index : len(content[0]) - insertion_end_index
                ]
                after = content[1][
                    insertion_begin_index : len(content[1]) - insertion_end_index
                ]
                suffix = content[1][len(content[1]) - insertion_end_index :]

                statement.context.extensions["editions"][key] = {
                    "prefix": prefix,
                    "before": before,
                    "after": after,
                    "suffix": suffix,
                    "tags": [],
                }
