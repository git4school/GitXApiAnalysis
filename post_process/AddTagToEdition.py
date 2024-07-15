from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb


class AddTagToEdition(PostProcessModifier):
    def level(self):
        return DiffPart

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        extensions = statement.object.definition.extensions

        if not "git" in extensions:
            return

        if not "editions" in statement.context.extensions:
            return

        for key in statement.context.extensions["editions"].keys():
            edition = statement.context.extensions["editions"][key]

            statement.context.extensions["atomic"] = True

            prefix = edition["prefix"]
            before = edition["before"]
            after = edition["after"]
            suffix = edition["suffix"]

            if len(before.strip()) == 0:
                edition["tags"].append("INSERT")

            if len(after.strip()) == 0:
                edition["tags"].append("DELETE")

            if PostProcessModifier.is_in_string(prefix + after + suffix, len(prefix)):
                edition["tags"].append("STRING")

            if (
                PostProcessModifier.is_in_comment(prefix + after + suffix, len(prefix))
                or before.strip() in ["/*", "*/"]
                or after.strip() in ["/*", "*/"]
                or before.strip() == "//"
                or after.strip() == "//"
            ):
                edition["tags"].append("COMMENT")

            if before.strip().count(" ") == 0 and after.strip().count(" ") == 0:
                edition["tags"].append("WORD_EDIT")
