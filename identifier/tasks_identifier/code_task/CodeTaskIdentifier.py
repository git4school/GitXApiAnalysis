from copy import deepcopy
from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from tasks_identifier.TaskIdentifier import TaskIdentifier


class CodeTaskIdentifier(TaskIdentifier):
    def __init__(self) -> None:
        super().__init__()

    def generate_sub_diffpart(
        parts: list[DiffPart],
        i: int,
        intervals: list[tuple[int, int]],
        modify_parent: bool,
    ):
        part = parts[i]

        assert all(
            interval[0] >= 0 and interval[1] <= len(part.content)
            for interval in intervals
        )

        newpart = DiffPart()
        newpart.a_start_line = part.a_start_line + min(
            interval[0] for interval in intervals
        )
        newpart.b_start_line = part.a_start_line + min(
            interval[0] for interval in intervals
        )

        start = min(interval[0] for interval in intervals)
        end = max(interval[1] for interval in intervals)

        extracted = part.content[start:end]

        for interval in intervals:
            for x in range(interval[0], interval[1]):
                if extracted[x - start][0] == "#":
                    continue
                else:
                    extracted[x - start] = "#" + extracted[x - start]

        extracted = [line for line in extracted if not line.startswith("+")]

        i = 0
        while i < len(extracted):
            line = extracted[i]

            if line.startswith("#"):
                i += 1
                continue

            if line.startswith("+"):
                extracted = extracted[:i] + extracted[i + 1 :]
            elif line.startswith("-"):
                extracted[i] = " " + line[1:]
            else:
                i += 1

        extracted = [l[1:] for l in extracted]

        before_content = [l for l in extracted if len(l) == 0 or not l.startswith("+")]
        after_content = [l for l in extracted if len(l) == 0 or not l.startswith("-")]

        newpart.a_interval = len(before_content)

        newpart.b_interval = len(after_content)

        newpart.content = extracted

        if not modify_parent:
            return newpart

        part.content = (
            part.content[:start]
            + [
                " " + l[1:] if len(l) > 0 else ""
                for l in extracted
                if len(l) == 0 or l[0] != "-"
            ]
            + part.content[end:]
        )

        shift = newpart.b_interval - newpart.a_interval

        part.a_interval += newpart.b_interval
        part.a_interval -= len(extracted) - len(after_content)

        for j in range(i + 1, len(parts)):
            part = parts[j]
            part.a_start_line += shift
            part.b_start_line += shift
        return newpart

    def ignore_none_part(self) -> bool:
        return True

    def generator_prefix(self) -> str:
        pass

    def identifier_generator(
        self,
        statement: Statement,
        diff: Differential,
        i: int,
        intervals: list[tuple[int, int]],
        modifer: Callable[[Statement], None],
    ) -> Statement:
        newpart = CodeTaskIdentifier.generate_sub_diffpart(
            diff.parts, i, intervals, True
        )
        newstatement: Statement = TaskIdentifier.new_statement(
            origin=statement,
            id=self.generator_prefix() + "~" + str(i) + "~" + hash(intervals),
        )
        newdiff = deepcopy(diff)
        newdiff.parts = [newpart]
        newstatement.object.definition.extensions["git"] = newdiff

        modifer(newstatement)

    def process_part(
        self, st_getter: any, i: int, part: DiffPart
    ) -> dict[str, tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        pass

    def process_differential(self, st_getter: any, i: int, diff: Differential):
        if diff.parts == None:
            return []
        newstatements = []
        for diffpart in diff.parts:
            if diffpart.content == None and self.ignore_none_part():
                continue
            returns = self.process_part(st_getter, i, diffpart)

            if returns != None:
                newstatements += [
                    self.identifier_generator(
                        st_getter(i), diff, i, intervals, modifier
                    )
                    for (intervals, modifier) in returns.values()
                ]
        return newstatements

    def process_statement(self, st_getter: any, i: int):

        statement: Statement = st_getter(i)
        if TaskIdentifier.is_task_set(statement):
            return

        if not "git" in statement.object.definition.extensions:
            return

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        new_statements = []

        for diff in differentials:
            new_statements += self.process_differential(st_getter, i, diff)
        return [statement] + new_statements
