from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from modifier.code_modifier import *


class EditionDetectionModifier(CodeModifier):

    def generator_prefix(self) -> str:
        return "edition"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        statement = st_getter(i)
        content = part.content

        splitting_parts = []

        for i1, i2 in zip(range(len(content) - 1), range(1, len(content))):
            key = (
                statement.object.id
                + "_"
                + diff.file
                + "_"
                + str(part.a_start_line)
                + "_"
                + str(i1)
            )

            insertion_begin_index = 1
            insertion_end_index = 0

            min_len = min(len(content[i1]), len(content[i2]))
            min_len_stripped = min(len(content[i1].strip()), len(content[i2].strip()))

            if min_len == 0 or not (
                (content[i1][0] == "+" and content[i2][0] == "-")
                or (content[i1][0] == "-" and content[i2][0] == "+")
            ):
                continue

            while (
                insertion_begin_index < min_len
                and content[i1][insertion_begin_index]
                == content[i2][insertion_begin_index]
            ):
                insertion_begin_index += 1

            while (
                insertion_end_index < min_len
                and content[i1][len(content[i1]) - insertion_end_index - 1]
                == content[i2][len(content[i2]) - insertion_end_index - 1]
                and min_len - insertion_end_index - 1 >= insertion_begin_index
            ):
                insertion_end_index += 1

            prefix = content[i1][1:insertion_begin_index]
            before = content[i1][
                insertion_begin_index : len(content[i1]) - insertion_end_index
            ]
            after = content[i2][
                insertion_begin_index : len(content[i2]) - insertion_end_index
            ]
            suffix = content[i2][len(content[i2]) - insertion_end_index :]

            if len(prefix + suffix) <= 0.2 * min_len and min_len_stripped >= 4:
                continue

            splitting_parts.append(
                (
                    i1,
                    i2 + 1,
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

        def edition_applier(statement: Statement, key: str, v: dict):
            if not "editions" in statement.context.extensions:
                statement.context.extensions["editions"] = dict()
            statement.context.extensions["editions"][key] = v

        return [
            ([(i1, i2)], lambda statement: edition_applier(statement, key, v))
            for (i1, i2, key, v) in splitting_parts
        ]

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        statement = st_getter(i)
        if "editions" in statement.context.extensions:
            return [statement]
        return super().process_statement(st_getter, i)
