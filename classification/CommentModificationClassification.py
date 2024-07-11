from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique class
class CommentModificationClassification(
    classification.ClassificationProcess.Classification
):

    def process(self, statement: Statement) -> str:
        diffs: list[Differential] = statement.object.definition.extensions["git"]
        for diff in diffs:

            for diffpart in diff.parts:
                content = diffpart.content
                if not (
                    len(content) != 2
                    or len(content[0]) <= 1
                    or len(content[1]) <= 1
                    or content[0][0] == content[1][0]
                ):
                    insertion_begin_index = 1

                    min_len = min(len(content[0]), len(content[1]))

                    while (
                        insertion_begin_index < min_len
                        and content[0][insertion_begin_index]
                        == content[1][insertion_begin_index]
                    ):
                        insertion_begin_index += 1

                    if (
                        "//" in content[0][:insertion_begin_index]
                        and "//" in content[1][:insertion_begin_index]
                    ):
                        return "COMMENT_EDITION"

                key = (
                    statement.object.id
                    + "_"
                    + diff.file
                    + "_"
                    + str(diffpart.a_start_line)
                )

                if (
                    "insertions" in statement.context.extensions
                    and key in statement.context.extensions["insertions"]
                ):
                    insert = statement.context.extensions["insertions"][key]["content"]
                    if insert != None:
                        insert = insert.strip()

                    if insert.startswith("//"):
                        return "COMMENT_ADDITION"

                    if insert.startswith("/*"):
                        return "COMMENT_BLOCK_START_APPEND"

                    if insert.startswith("*/"):
                        return "COMMENT_BLOCK_END_APPEND"

                if (
                    "deletions" in statement.context.extensions
                    and key in statement.context.extensions["deletions"]
                ):
                    delete = statement.context.extensions["deletions"][key]["content"]
                    if delete != None:
                        delete = delete.strip()

                    if delete.startswith("//"):
                        return "COMMENT_DELETION"

                    if delete.startswith("/*"):
                        return "COMMENT_BLOCK_START_DELETE"

                    if delete.startswith("*/"):
                        return "COMMENT_BLOCK_END_DELETE"
