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

        prefix: str = edition["prefix"].replace("\t", "    ")
        before: str = edition["before"].replace("\t", "    ")
        after: str = edition["after"].replace("\t", "    ")
        suffix: str = edition["suffix"].replace("\t", "    ")

        strip_prefix: str = prefix.strip()
        strip_before: str = before.strip()
        strip_after: str = after.strip()
        strip_suffix: str = suffix.strip()

        tags: list[str] = edition["tags"]

        def is_removed(raw: str):
            return not raw in after and raw in before

        def is_added(raw: str):
            return raw in after and not raw in before

        if "STRING" in tags:
            return "STRING_EDITION"

        if "COMMENT" in tags:
            if is_added("//"):
                return "COMMENT_ADDITION"
            if is_removed("//"):
                return "COMMENT_DELETION"
            if (is_removed("/*") or is_added("/*") and not "*/" in after) or (
                is_removed("*/") or is_added("*/") and not "/*" in after
            ):
                return "COMMENT_MOVED"
            else:
                return "COMMENT_EDITION"

        if "INSERT" in tags:
            if strip_prefix.endswith("return") and (
                strip_suffix.startswith(";") or len(strip_suffix) == 0
            ):
                return "ADD_RETURN_VALUE"

            if strip_prefix.endswith("=") and not strip_prefix.endswith("=="):
                if len(strip_before) == 0 and (
                    strip_suffix == ";" or strip_suffix == ""
                ):
                    return "ADD_VARIABLE_VALUE"
                else:
                    return "MODIFY_VARIABLE_VALUE"

            if len(strip_after) == 1:
                return "TYPO"

        if "WORD_EDIT" in tags:
            if before.strip() == "fals" and after.strip() == "tru":
                return "FALSE_TO_TRUE"
            if before.strip() == "tru" and after.strip() == "fals":
                return "TRUE_TO_FALSE"

            if strip_prefix.endswith(".") and strip_suffix.startswith("("):
                return "REPLACE_METHOD"
            if (
                prefix.endswith(" ")
                and not regex.match("[a-zA-Z$0-9]", (" " + strip_prefix)[-1])
                and strip_suffix.startswith("(")
            ):
                return "REPLACE_FUNCTION"

            if (
                regex.match(
                    " *((public|private|protected) +|)[a-zA-Z0-9_]+ +[a-zA-Z0-9_]+( )*\\(",
                    prefix + after + suffix,
                )
                != None
                and regex.match(
                    " *((public|private|protected) +|)[a-zA-Z0-9_]+ +[a-zA-Z0-9_]+( )*",
                    prefix + after,
                )
                != None
                and regex.match("[a-zA-Z0-9_]+( )*", after) != None
                and regex.match(
                    " *((public|private|protected) +|)([a-zA-Z0-9_]+) +([a-zA-Z0-9_]*) *\(",
                    prefix,
                )
                == None
            ):
                return "RENAME_FUNCTION"

        # if strip_after.endswith(strip_before) and not "INSERT" in tags:
        #     return "ACCUMULATE"

        if strip_after.startswith("=") and not strip_after.startswith("=="):
            return "ASSIGN_VARIABLE"
        if (
            strip_before.startswith("=") and not strip_before.startswith("==")
        ) and prefix.endswith(" "):
            return "UNASSIGN_VARIABLE"

        c1 = strip_prefix.count("[") - strip_prefix.count("]")
        c2 = strip_suffix.count("[") - strip_suffix.count("]")
        if c1 != 0 and c1 == c2:
            return "CHANGE_ARRAY_INDEX"

        complete_after = strip_prefix + strip_after + strip_suffix

        if (
            complete_after.startswith("if (")
            or complete_after.startswith("else")
            or complete_after.startswith("switch")
            or complete_after.startswith("while")
            or (
                complete_after.startswith("for")
                and (";" in strip_prefix and ";" in strip_suffix)
            )
        ):
            return "CONDITION"

        # if regex.match("[a-zA-Z_$0-9]*( )*.", strip_suffix):
        #     return "CHANGE_FUNCTION_SOURCE"

        if regex.match("[a-zA-Z_$0-9]*( )*=[^=]", suffix):
            if before.endswith(" "):
                return "USE_OLD_VARIABLE"

            if after.endswith(" "):
                return "USE_NEW_VARIABLE"

            if not " " in strip_before and not " " in strip_after:
                return "RENAME_VARIABLE"

        # if not (" " + prefix)[-1] in [",", ")", ".", "]", " "]:
        #     return "REWORD"
