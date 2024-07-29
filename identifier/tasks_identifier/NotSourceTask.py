from typing import Callable
from tincan import Statement
from GitToXApi.differential import Differential
from identifier.tasks_identifier.TaskIdentifier import TaskIdentifier
from modifier.StatementModifier import StatementModifier
import copy


class NotSourceTask(TaskIdentifier):

    def generator_prefix(self) -> str:
        return "notsource"

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:

        statement: Statement = st_getter(i)

        if TaskIdentifier.is_task_set(statement):
            return [statement]

        if not "git" in statement.object.definition.extensions:
            return [statement]

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        new_statements = []

        diff_i = 0
        while diff_i < len(differentials):
            diff = differentials[diff_i]
            if diff.file.endswith(".java"):
                diff_i += 1
                continue
            differentials.pop(diff_i)

            newstatement: Statement = StatementModifier.new_statement(
                origin=statement,
                id=self.generator_prefix() + "~" + str(len(differentials)),
            )
            newdiff = copy.deepcopy(diff)
            newstatement.object.definition.extensions["git"] = [newdiff]
            new_statements.append(newstatement)
            TaskIdentifier.set_task(newstatement, "NotSource", {})

        statement.object.definition.extensions["git"] = differentials

        return new_statements + [statement]
