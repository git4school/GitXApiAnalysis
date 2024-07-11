from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb


class TurnPureToAddOrDel(PostProcessModifier):
    def level(self):
        return DiffPart

    def _process(
        self,
        statement: Statement,
        differential: Differential,
        diffpart: DiffPart,
        **kargs
    ):
        if statement.context.extensions == None:
            return

        if not "editions" in statement.context.extensions:
            return

        key = (
            statement.object.id
            + "_"
            + differential.file
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
