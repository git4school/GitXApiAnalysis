from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *


class MethodInvocationTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "method_invocation"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[tuple[int, str, dict]] = []
        for i in range(len(part.content)):
            line = part.content[i]
            if line[0] in ["+", "-"]:

                content: str = line[1:].strip().replace("\t", " ")

                if not "(" in content:
                    continue

                par_i = content.index("(")

                if par_i == 0:
                    continue

                if " " in content[:par_i].strip():
                    continue

                name = content[:par_i].strip()
                if name in ["for", "if", "while", "do", "switch"]:
                    continue

                extractions.append((i, line[0], {"method": name}))

        return [
            (
                [(v[0], v[0] + 1)],
                (
                    TaskIdentifier.task_applier(
                        "InvocationStatement" + ("Add" if v[1][0] == "+" else "Remove"),
                        v[2],
                    )
                ),
            )
            for v in extractions
        ]

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        statement = st_getter(i)
        if "editions" in statement.context.extensions:
            return [statement]
        return super().process_statement(st_getter, i)
