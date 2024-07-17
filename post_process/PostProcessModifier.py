from tincan import *
from gittoxapi.differential import Differential, DiffPart


class PostProcessModifier:
    def __init__(self) -> None:
        pass

    def level(self):
        pass

    def trim_diff(diffpart: DiffPart) -> DiffPart:
        content = diffpart.content
        real_content = [
            i for i in range(len(content)) if not content[i].startswith(" ")
        ]
        if len(real_content) == 0:
            return None
        start_shift = min(real_content)
        end_shift = max(real_content)
        content = [
            v
            for (v, i) in zip(content, range(len(content)))
            if start_shift <= i <= end_shift
        ]

        newPart = DiffPart()

        newPart.content = content
        newPart.a_start_line = diffpart.a_start_line + start_shift
        newPart.a_interval = len([v for v in content if not v.startswith("-")])
        newPart.b_start_line = diffpart.b_start_line + start_shift
        newPart.b_interval = len([v for v in content if not v.startswith("+")])

        return newPart

    def is_in_comment(raw: str, i: int):

        if "//" not in raw[:i] and "/*" not in raw[:i]:
            return False

        # TODO check better if // pr /* is in string

        return True

    def is_in_string(raw: str, i: int):
        return raw[:i].count('"') * raw[i + 1 :].count('"') % 2 == 1

    def generate_sub_diffpart(
        parts: list[DiffPart],
        i: int,
        intervals: list[tuple[int, int]],
        modify_parent: bool,
    ):
        part = parts[i]

        assert all(
            interval[0] >= 0 and interval[1] <= len(part.content)
            for interval in intervals
        )

        newpart = DiffPart()
        newpart.a_start_line = part.a_start_line + min(
            interval[0] for interval in intervals
        )
        newpart.b_start_line = part.a_start_line + min(
            interval[0] for interval in intervals
        )

        start = min(interval[0] for interval in intervals)
        end = max(interval[1] for interval in intervals)

        extracted = part.content[start:end]

        for interval in intervals:
            for x in range(interval[0], interval[1]):
                if extracted[x - start][0] == "#":
                    continue
                else:
                    extracted[x - start] = "#" + extracted[x - start]

        extracted = [line for line in extracted if not line.startswith("+")]

        i = 0
        while i < len(extracted):
            line = extracted[i]

            if line.startswith("#"):
                i += 1
                continue

            if line.startswith("+"):
                extracted = extracted[:i] + extracted[i + 1 :]
            elif line.startswith("-"):
                extracted[i] = " " + line[1:]
            else:
                i += 1

        extracted = [l[1:] for l in extracted]

        before_content = [l for l in extracted if len(l) == 0 or not l.startswith("+")]
        after_content = [l for l in extracted if len(l) == 0 or not l.startswith("-")]

        newpart.a_interval = len(before_content)

        newpart.b_interval = len(after_content)

        newpart.content = extracted

        if not modify_parent:
            return newpart

        part.content = (
            part.content[:start]
            + [
                " " + l[1:] if len(l) > 0 else ""
                for l in extracted
                if len(l) == 0 or l[0] != "-"
            ]
            + part.content[end:]
        )

        shift = newpart.b_interval - newpart.a_interval

        part.a_interval += newpart.b_interval
        part.a_interval -= len(extracted) - len(after_content)

        for j in range(i + 1, len(parts)):
            part = parts[j]
            part.a_start_line += shift
            part.b_start_line += shift
        return newpart

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:
        """
        Returns a list where each statement is linked to a boolean which describe whether this statement*
        should be reprocessed by this modifier
        """
        pass

    def process(self, statements: list[Statement]):

        i = 0

        elements = [(s, not s.context.extensions["atomic"]) for s in statements]

        while i < len(statements):

            to_process = elements[i][1]

            if not to_process:
                i += 1
                continue

            l = self._process(
                lambda x: elements[x][0] if 0 <= x < len(elements) else None, i
            )

            if l == None:
                l = [(elements[i][0], False)]
            elements = elements[:i] + l + elements[i + 1 :]
        elements = [e[0] for e in elements]

        return [
            e
            for e in elements
            if not "git" in e.object.definition.extensions
            or any(
                [
                    any([p != None for p in diff.parts])
                    for diff in e.object.definition.extensions["git"]
                    if diff != None and diff.parts != None
                ]
            )
        ]
