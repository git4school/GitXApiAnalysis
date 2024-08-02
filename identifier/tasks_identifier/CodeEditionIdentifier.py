from typing import Callable
from tincan import Statement
from GitToXApi.differential import Differential
from identifier.tasks_identifier.TaskIdentifier import TaskIdentifier
import regex
import utils


def indentify_edition(prefix, before, after, suffix, tags):

    strip_prefix: str = prefix.strip()
    strip_before: str = before.strip()
    strip_after: str = after.strip()
    strip_suffix: str = suffix.strip()

    def is_removed(raw: str):
        return not raw in after and raw in before

    def is_added(raw: str):
        return raw in after and not raw in before

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

    before_line = prefix + before + suffix
    after_line = prefix + after + suffix

    token_subst = utils.find_token_substitution(before_line, after_line)

    if token_subst != None:
        if (not token_subst[0][-1]) and (not token_subst[1][-1]):
            token_subst = [token_subst[0][0], token_subst[1][0]]
            before_split_subst = before_line.split(token_subst[0])
            before_split_subst = [
                v.replace("\t", " ").replace(" ", "") for v in before_split_subst
            ]
            before_split_subst = [v for v in before_split_subst if len(v) > 0]

            if all(not v[0] in ["(", "."] for v in before_split_subst):
                if (
                    any(v[0] == "=" for v in before_split_subst)
                    and " "
                    in before_line[
                        : before_line.index(token_subst[0]) + len(token_subst[0])
                    ].strip()
                ):
                    return "RENAME_VARIABLE"
                return "CHANGE_VARIABLE_USED"
            else:
                return "CHANGE_METHOD_INVOCATED"

        elif token_subst[0][-1] and token_subst[1][-1]:
            return "CHANGE_LITTERAL_VALUE"
        else:
            if token_subst[0][-1]:
                return "LITTERAL_TO_VARIABLE"
            else:
                return "VARIABLE_TO_LITTERAL"

    if "STRING" in tags:
        return "STRING_EDITION"

    if "INSERT" in tags:
        if strip_prefix.endswith("return") and (
            strip_suffix.startswith(";") or len(strip_suffix) == 0
        ):
            return "ADD_RETURN_VALUE"

        if strip_prefix.endswith("=") and not strip_prefix.endswith("=="):
            if len(strip_before) == 0 and (strip_suffix == ";" or strip_suffix == ""):
                return "ADD_VARIABLE_VALUE"
            else:
                return "MODIFY_VARIABLE_VALUE"

    if len(strip_after) == 1 and "INSERT" in tags:
        return "TYPO_ADD"
    if len(strip_before) == 1 and "DELETE" in tags:
        return "TYPO_DEL"

    if "WORD_EDIT" in tags:
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

    complete_after = (strip_prefix + strip_after + strip_suffix).replace(" ", "")

    if (
        complete_after.startswith("if(")
        or complete_after.startswith("else")
        or complete_after.startswith("}else")
        or complete_after.startswith("switch")
        or complete_after.startswith("while")
        or (
            complete_after.startswith("for")
            and (";" in strip_prefix and ";" in strip_suffix)
        )
    ):
        return "CONDITION"

    if regex.match("[a-zA-Z_$0-9]*( )*=[^=]", suffix):
        if before.endswith(" "):
            return "USE_OLD_VARIABLE"

        if after.endswith(" "):
            return "USE_NEW_VARIABLE"

        if not " " in strip_before and not " " in strip_after:
            return "RENAME_VARIABLE"

    prefix_equal = -1 if not "=" in prefix else prefix.index("=")
    if prefix_equal != -1 and (
        prefix_equal != 0
        and (prefix_equal + 1 == len(prefix) or prefix[prefix_equal + 1] != "=")
    ):
        return "CHANGE_VARIABLE_VALUE"
    if (
        (len(strip_prefix) > 0 and len(strip_suffix) > 0)
        and strip_prefix[-1] in "(,"
        and strip_suffix[0] in ",)"
    ):
        if "INSERT" in tags or is_added(","):
            return "ADD_FUNCTION_PARAMETER"
        elif "DELETE" in tags or is_removed(","):
            return "REMOVE_FUNCTION_PARAMETER"
        return "EDIT_FUNCTION_PARAMETERS"

    if strip_prefix.startswith("return"):
        return "EDIT_RETURN_VALUE"


class CodeEditionIdentifier(TaskIdentifier):

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:

        statement = st_getter(i)

        if not "editions" in statement.context.extensions:
            return [statement]

        edition: dict = statement.context.extensions["editions"]

        prefix: str = edition["prefix"].replace("\t", "    ")
        before: str = edition["before"].replace("\t", "    ")
        after: str = edition["after"].replace("\t", "    ")
        suffix: str = edition["suffix"].replace("\t", "    ")
        tags: list[str] = edition["tags"]

        returns = indentify_edition(prefix, before, after, suffix, tags)
        if returns != None:
            TaskIdentifier.set_task(statement, returns, {})
        return [statement]
