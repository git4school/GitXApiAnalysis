from typing import Callable
from tincan import Statement
from GitToXApi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *


class TrimEditionContentModifier(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "trim_edition_content"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        content = part.content

        splitting_parts: list[tuple[tuple[int, int], tuple[int, int]]] = []

        i = 0
        while i < len(content):
            line = content[i]

            if len(line) == 0 or not line[0] in ["+", "-"]:
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

            if first_of_second >= len(content) or content[first_of_second][0] in [
                " ",
                first_sign,
            ]:
                i = last_of_first + 2
                continue

            second_sign = content[first_of_second][0]

            last_of_second = [
                j
                for j in range(first_of_second, len(content))
                if not content[j].startswith(second_sign)
            ] + [len(content)]
            last_of_second = last_of_second[0] - 1
            min_len = min(last_of_first + 1 - i, last_of_second + 1 - first_of_second)

            for k in range(min_len):
                if content[i + k][1:] == content[first_of_second + k][1:]:
                    splitting_parts.append((i + k, first_of_second + k))

            i = last_of_second + 1

        return [
            (
                [(p1, p1 + 1), (p2, p2 + 1)],
                TaskIdentifier.task_applier("TrimEditionContent", {}),
            )
            for (p1, p2) in splitting_parts
        ]

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        statement = st_getter(i)
        if "editions" in statement.context.extensions:
            return [statement]
        return super().process_statement(st_getter, i)
