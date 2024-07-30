from typing import Callable
from tincan import Statement, Verb
from modifier.StatementModifier import StatementModifier
from GitToXApi.differential import Differential, DiffPart
from utils import find_name_path


class NamePathModifier(StatementModifier):

    def process_statement(self, st_getter: Callable[[int], Statement | None], i: int):
        statement = st_getter(i)

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]
        if len(differentials) != 1:
            return [statement]

        diff = differentials[0]

        if len(diff.parts) != 1:
            return [statement]
        part = diff.parts[0]
        content = part.content
        file = diff.file

        paths = []

        for i in [i for i in range(len(content)) if content[i][0] != " "]:
            paths.append(
                ".".join([o[0] for o in find_name_path(content, i) if o[1] != "BLOCK"])
            )
        paths = list(set(paths))
        if len(paths) == 1:
            statement.context.extensions["name_path"] = file + ":" + paths[0]

        return [statement]
