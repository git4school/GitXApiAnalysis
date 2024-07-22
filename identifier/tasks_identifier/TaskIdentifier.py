from tincan import Statement, Context, ActivityDefinition, Extensions
from gittoxapi.differential import Differential, DiffPart
from typing import Callable
from identifier.ActivityIdentifier import ActivityIdentifier
from copy import deepcopy


class TaskIdentifier(ActivityIdentifier):
    def __init__(self) -> None:
        pass

    def new_statement(origin: Statement, id: str = None) -> Statement:
        assert origin != None
        newstatement = deepcopy(origin)

        newstatement.object.id = id
        newstatement.object.definition = ActivityDefinition()
        newstatement.object.definition.extensions = Extensions()

        newstatement.context = Context()
        newstatement.context.extensions = Extensions()
        newstatement.context.extensions["origins"] = [origin.object.id]

        if "origins" in origin.context.extensions:
            newstatement.context.extensions["origins"] += origin.context.extensions[
                "origins"
            ]

        return newstatement

    def get_task(statement: Statement) -> tuple[str, dict]:
        if not "task" in statement.context.extensions:
            return None
        task = statement.context.extensions["task"]
        id = task["id"]
        meta = task["metadata"]
        return (id, meta)

    def set_task(statement: Statement, id: str, metadata: dict):
        statement.context.extensions["task"] = {"id": id, "metadata": metadata}

    def task_applier(id: str, metadata: dict):
        return lambda statement: TaskIdentifier.set_task(statement, id, metadata)

    def is_task_set(statement: Statement):
        return TaskIdentifier.get_task(statement) != None

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
        modifer: Callable[[Statement], None],
    ) -> Statement:
        newstatement: Statement = TaskIdentifier.new_statement(
            origin=statement,
            id=self.generator_prefix() + "~" + str(hash(diff.file)),
        )

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        newstatement.object.definition.extensions["git"] = [diff]
        differentials.remove(diff)

        modifer(newstatement)
        return newstatement

    def process_differential(
        self, st_getter: any, i: int, diff: Differential
    ) -> Callable[[Statement], None]:
        pass

    def process_statement(self, st_getter: any, i: int):

        statement: Statement = st_getter(i)
        if TaskIdentifier.is_task_set(statement):
            return [statement]

        if not "git" in statement.object.definition.extensions:
            return [statement]

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        new_statements = []

        for diff in differentials:
            returns = self.process_differential(st_getter, i, diff)

            if returns != None:
                new_statements += [self.identifier_generator(statement, diff, returns)]

        return new_statements + [statement]
