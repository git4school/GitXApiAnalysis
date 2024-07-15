from tincan import *
from gittoxapi.differential import Differential, DiffPart
import regex

import classification.ClassificationProcess


# Ensure unique class
class EditionClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:
        if not "editions" in statement.context.extensions:
            return

        if len(statement.context.extensions["editions"].keys()) != 1:
            return

        edition: dict = list(statement.context.extensions["editions"].values())[0]

        prefix: str = edition["prefix"]
        before: str = edition["before"]
        after: str = edition["after"]
        suffix: str = edition["suffix"]

        strip_prefix: str = prefix.strip()
        strip_before: str = before.strip()
        strip_after: str = after.strip()
        strip_suffix: str = suffix.strip()

        tags: list[str] = edition["tags"]

        def is_removed(raw: str):
            return not raw in after and raw in before

        def is_added(raw: str):
            return raw in after and not raw in before

        if "COMMENT" in tags:
            if is_added("//"):
                return "COMMENT_ADDITION"
            if is_removed("//"):
                return "COMMENT_DELETION"
            if is_removed("/*") or is_added("/*") and not "*/" in after:
                return "COMMENT_MOVED"
            if ("/*" in after and "/*" in before) or ("*/" in after and "*/" in before):
                return "COMMENT_BLOCK_MOVE"
            else:
                return "COMMENT_EDITION"

        if "STRING" in tags:
            return "STRING_EDITION"

        if "INSERT" in tags:
            if strip_prefix.endswith("return"):
                return "ADD_RETURN_VALUE"

            if strip_prefix.endswith("=") and not strip_prefix.endswith("=="):
                return "ADD_VARIABLE_VALUE"

            if len(strip_after) == 1:
                return "TYPO"

        if "WORD_EDIT" in tags:
            if before.strip() == "fals" and after.strip() == "tru":
                return "FALSE_TO_TRUE"
            if before.strip() == "tru" and after.strip() == "fals":
                return "TRUE_TO_FALSE"

            if strip_prefix.endswith(".") and strip_suffix.startswith("("):
                return "BUGFIX_WRONG_FUNCTION"

        if strip_after == strip_before:
            return "WHITESPACE"

        if strip_after.endswith(strip_before) and not "INSERT" in tags:
            return "ACCUMULATE"

        if strip_after.startswith("=") and not strip_after.startswith("=="):
            return "ASSIGN_VARIABLE"
        if strip_before.startswith("=") and not strip_before.startswith("=="):
            return "UNASSIGN_VARIABLE"

        if (strip_prefix.count("[") - strip_prefix.count("]")) * (
            strip_prefix.count("]") - strip_prefix.count("[")
        ) % 2 == 1:
            return "BUGFIX_ARRAY_INDEX"

        if (strip_after + "  ")[:2] in ("&&", "||", "=="):
            return "CHANGE_CONDITION"

        if strip_suffix.startswith("."):
            return "CHANGE_FUNCTION_SOURCE"

        # 439 strip_suffix.startswith("=") and not strip_suffix.startswith("==")
        if regex.match("[a-zA-Z_$0-9]*( )*=[^=]", suffix):
            if " " in strip_after and not " " in strip_before:
                return "SAVE_VALUE_IN_NEW_VARIABLE"

            if " " in strip_before and not " " in strip_after:
                return "REMOVE_VARIABLE_AND_SAVE_VALUE_IN_OLD_VARIABLE"

            if not " " in strip_before and not " " in strip_after:
                return "RENAME"

        if not (" " + prefix)[-1] in [",", ")", ".", "]", " "]:
            return "REWORD"
