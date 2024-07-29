from typing import Callable
from tincan import Statement
from GitToXApi.differential import DiffPart, Differential
from modifier.code_modifier import *


def is_in_comment(raw: str, i: int):

    if "//" not in raw[:i] and "/*" not in raw[:i]:
        return False

    # TODO check better if // pr /* is in string

    return True


def is_in_string(raw: str, i: int):
    return raw[:i].count('"') * raw[i + 1 :].count('"') % 2 == 1


def get_tags(prefix: str, before: str, after: str, suffix: str):
    tags = []
    if len(before.strip()) == 0:
        tags.append("INSERT")

    if len(after.strip()) == 0:
        tags.append("DELETE")

    if is_in_string(prefix + after + suffix, len(prefix)):
        tags.append("STRING")

    if (
        is_in_comment(prefix + after + suffix, len(prefix))
        or before.strip() in ["/*", "*/"]
        or after.strip() in ["/*", "*/"]
        or before.strip().startswith("//")
        or after.strip().startswith("//")
    ):
        tags.append("COMMENT")

    if before.strip().count(" ") == 0 and after.strip().count(" ") == 0:
        tags.append("WORD_EDIT")
    return tags


class EditionDetectionModifier(CodeModifier):

    def generator_prefix(self) -> str:
        return "edition"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        content = part.content

        splitting_parts = []

        for i1, i2 in zip(range(len(content) - 1), range(1, len(content))):

            insertion_begin_index = 1
            insertion_end_index = 0

            min_len = min(len(content[i1]), len(content[i2]))

            if min_len == 0 or not (
                (content[i1][0] == "+" and content[i2][0] == "-")
                or (content[i1][0] == "-" and content[i2][0] == "+")
            ):
                continue
            min_len_stripped = min(
                len(content[i1][1:].strip()), len(content[i2][1:].strip())
            )
            max_len_stripped = max(
                len(content[i1][1:].strip()), len(content[i2][1:].strip())
            )

            while (
                insertion_begin_index < min_len
                and content[i1][insertion_begin_index]
                == content[i2][insertion_begin_index]
            ):
                insertion_begin_index += 1

            while (
                insertion_end_index < min_len
                and content[i1][len(content[i1]) - insertion_end_index - 1]
                == content[i2][len(content[i2]) - insertion_end_index - 1]
                and min_len - insertion_end_index - 1 >= insertion_begin_index
            ):
                insertion_end_index += 1

            prefix = content[i1][1:insertion_begin_index]
            before = content[i1][
                insertion_begin_index : len(content[i1]) - insertion_end_index
            ]
            after = content[i2][
                insertion_begin_index : len(content[i2]) - insertion_end_index
            ]
            suffix = content[i2][len(content[i2]) - insertion_end_index :]

            if len(prefix.strip() + suffix.strip()) <= 0.2 * min_len and (
                min_len_stripped >= 4 or max_len_stripped >= 4
            ):
                continue
            splitting_parts.append(
                (
                    i1,
                    i2 + 1,
                    {
                        "prefix": prefix,
                        "before": before,
                        "after": after,
                        "suffix": suffix,
                        "tags": get_tags(prefix, before, after, suffix),
                    },
                )
            )

        def edition_applier(v: dict):
            def lambda_applier(statement):
                statement.context.extensions["editions"] = v

            return lambda_applier

        return [
            ([(i1, i2)], edition_applier(dict(v))) for (i1, i2, v) in splitting_parts
        ]

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        statement = st_getter(i)
        if "editions" in statement.context.extensions:
            return [statement]
        return super().process_statement(st_getter, i)
