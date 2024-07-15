from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb
import copy


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

        if len(differentials) != 1 or differentials[0].parts == None:
            return

        splitting_parts: list[object] = []

        diff = differentials[0]

        for i in range(len(diff.parts)):
            real_part = diff.parts[i]
            diffpart = PostProcessModifier.trim_diff(real_part)
            content = diffpart.content
            if (
                len(content) != 2
                or len(content[0]) <= 1
                or len(content[1]) <= 1
                or content[0][0] == content[1][0]
            ):
                continue

            key = (
                statement.object.id + "_" + diff.file + "_" + str(diffpart.a_start_line)
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

            splitting_parts.append(
                (
                    i,
                    key,
                    {
                        "prefix": prefix,
                        "before": before,
                        "after": after,
                        "suffix": suffix,
                        "tags": [],
                    },
                )
            )

        if len(splitting_parts) == 1:

            i, key, v = splitting_parts.pop()
            statement.context.extensions["editions"][key] = v
            return [(statement, False)]
        else:

            statements = []
            used = []

            for element in splitting_parts:
                i, key, v = element
                used.append(i)
                newstatement: Statement = copy.deepcopy(statement)
                statements.append(newstatement)

                newstatement.object.id = (
                    "generated~edition~" + newstatement.object.id + "~" + str(key)
                )

                newdifferential: Differential = Differential(diff.__dict__)
                newstatement.object.definition.extensions["git"] = [newdifferential]
                newstatement.context.extensions["atomic"] = True
                newstatement.context.extensions["refactoring"] = None

                newdifferential.parts = []
                newdifferential.parts.append(diff.parts[i])
                newstatement.context.extensions["editions"] = {key: v}

            if len(splitting_parts) != len(diff.parts):
                diff.parts = [
                    diff.parts[i] for i in range(len(diff.parts)) if not i in used
                ]
                statements.append(statement)

            return [(st, False) for st in statements]
