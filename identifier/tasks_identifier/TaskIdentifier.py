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
        self, st_getter: Callable[[int], Statement | None], i: int, diff: Differential
    ) -> Callable[[Statement], None]:
        pass

    def process_statement(self, st_getter: Callable[[int], Statement | None], i: int):

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
