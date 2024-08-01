from copy import deepcopy
from typing import Callable
from tincan import Statement
from GitToXApi.differential import DiffPart, Differential
from modifier.StatementModifier import StatementModifier


class CodeModifier(StatementModifier):
    def __init__(self) -> None:
        super().__init__()

    def generate_sub_diffpart(
        parts: list[DiffPart],
        i: int,
        intervals: list[tuple[int, int]],
        modify_parent: bool,
    ) -> DiffPart:
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

        start = 0  # min(interval[0] for interval in intervals)
        end = len(part.content)  # max(interval[1] for interval in intervals)

        extracted = part.content[start:end]

        # Mark all lines that should be extracted
        for interval in intervals:
            for x in range(interval[0], interval[1]):
                if extracted[x - start][0] == "#":
                    continue
                else:
                    extracted[x - start] = "#" + extracted[x - start]

        newpart.content = [
            (" " if line[0] == "-" else "")
            + line[1 if line[0] in ["#", "-"] else None :]
            for line in extracted
            if not line[0] in ["+"]
        ]

        newpart.a_interval = len(
            [None for l in newpart.content if not l.startswith("+")]
        )
        newpart.b_interval = len(
            [None for l in newpart.content if not l.startswith("-")]
        )

        if not modify_parent:
            return newpart

        part.content = (
            part.content[:start]
            + [
                (
                    (" " if line[0] == "#" else "")
                    + line[2 if line[0] == "#" else None :]
                )
                for line in extracted
            ]
            + part.content[end:]
        )

        shift = newpart.b_interval - newpart.a_interval

        part.a_interval = len([None for l in part.content if l.startswith("+")])
        part.a_interval = len([None for l in part.content if l.startswith("+")])

        for j in range(i + 1, len(parts)):
            part = parts[j]
            part.a_start_line += shift
            part.b_start_line += shift
        return newpart

    def ignore_none_part(self) -> bool:
        return True

    def generator_prefix(self) -> str:
        pass

    def modifier_generator(
        self,
        statement: Statement,
        diff: Differential,
        i: int,
        intervals: list[tuple[int, int]],
        modifer: Callable[[Statement], None],
    ) -> Statement:
        newpart = CodeModifier.generate_sub_diffpart(diff.parts, i, intervals, True)
        newstatement: Statement = StatementModifier.new_statement(
            origin=statement,
            id=self.generator_prefix()
            + "~"
            + str(i)
            + "~"
            + str(intervals[0][0])
            + "~"
            + str(intervals[0][1])
            + "~"
            + statement.object.id,
        )
        newdiff = deepcopy(diff)
        newdiff.parts = [newpart]
        newstatement.object.definition.extensions["git"] = [newdiff]

        modifer(newstatement)
        return newstatement

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        pass

    def process_differential(
        self, st_getter: Callable[[int], Statement | None], i: int, diff: Differential
    ) -> list[Statement]:
        if diff.parts == None:
            return []
        newstatements = []
        part_index = 0
        while part_index < len(diff.parts):
            diffpart = diff.parts[part_index]
            if diffpart.content == None and self.ignore_none_part():
                continue
            length_snapshot = len(diff.parts)
            returns = self.process_part(st_getter, i, diff, diffpart)
            if len(diff.parts) == length_snapshot - 1:
                part_index -= 1

            if returns != None and len(returns) > 0:
                returns = [v for v in returns if len(v[0]) > 0]
                returns.sort(key=lambda v: -max([o[1] for o in v[0]]))
                for intervals, modifier in returns:
                    intervals.sort(key=lambda v: -v[1])
                    newstatements.append(
                        self.modifier_generator(
                            st_getter(i), diff, part_index, intervals, modifier
                        )
                    )
            part_index += 1
        return newstatements

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:

        statement: Statement = st_getter(i)

        if not "git" in statement.object.definition.extensions:
            return [statement]

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        new_statements = []

        for diff in differentials:
            new_statements += self.process_differential(st_getter, i, diff)
        return new_statements + [statement]
