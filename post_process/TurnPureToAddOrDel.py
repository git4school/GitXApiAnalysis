from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb


class TurnPureToAddOrDel(PostProcessModifier):
    def level(self):
        return DiffPart

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        extensions = statement.object.definition.extensions

        if not "git" in extensions:
            return

        if not "editions" in extensions:
            return

        differentials: list[Differential] = extensions["git"]

        for diff in differentials:
            if diff.parts == None:
                continue
            for diffpart in diff.parts:
                key = (
                    statement.object.id
                    + "_"
                    + diff.file
                    + "_"
                    + str(diffpart.a_start_line)
                )

                if not key in statement.context.extensions["editions"]:
                    return

                edition = statement.context.extensions["editions"][key]

                before = edition["before"]
                after = edition["after"]

                if len(before) == 0 or len(after) == 0:
                    statement.context.extensions["editions"].pop(key)

                if len(before) == 0:
                    if not "insertions" in statement.context.extensions:
                        statement.context.extensions["insertions"] = {}
                    statement.context.extensions["insertions"][key] = {
                        "prefix": edition["prefix"],
                        "content": after,
                        "suffix": edition["suffix"],
                    }

                if len(after) == 0:
                    if not "deletions" in statement.context.extensions:
                        statement.context.extensions["deletions"] = {}
                    statement.context.extensions["deletions"][key] = {
                        "prefix": edition["prefix"],
                        "content": before,
                        "suffix": edition["suffix"],
                    }

                if len(statement.context.extensions["editions"]) == 0:
                    statement.context.extensions.pop("editions")
