from tincan import Statement, Context, ActivityDefinition, Extensions
from gittoxapi.differential import Differential, DiffPart
from typing import Callable
from modifier.Modifier import Modifier
from copy import deepcopy


class StatementModifier(Modifier):
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

    def generator_prefix(self) -> str:
        pass

    def modifier_generator(
        self,
        statement: Statement,
        diff: Differential,
        modifer: Callable[[Statement], None],
    ) -> Statement:
        newstatement: Statement = StatementModifier.new_statement(
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
            returns = self.process_differential(st_getter, i, diff)

            if returns != None:
                new_statements += [self.modifier_generator(statement, diff, returns)]

        return new_statements + [statement]
