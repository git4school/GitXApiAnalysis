from typing import Callable
from tincan import Statement
from GitToXApi.differential import Differential
from identifier.tasks_identifier.TaskIdentifier import TaskIdentifier
from modifier.code_modifier.CodeModifier import CodeModifier
import copy


def is_it_copy_paste_accross_file(indexed):

    score = 0

    if len(indexed) == 0:
        return False

    for v1, v2 in zip(indexed[:-1], indexed[1:]):
        file1, start1, line1 = v1[0][0][1:4]
        file2, start2, line2 = v2[0][0][1:4]

        if file1 == file2 and abs(line1 - line2) == 1:
            score += 2

    for l in indexed:
        l = l[1][-1]
        if l.strip() in ["", "{", "}"]:
            score -= 1

    return score >= 3


def is_it_line_moved(indexed):

    indexed = [e for e in indexed if not e[1][-1].strip() in ["", "{", "}"]]
    return len(indexed) > 0


def consider_equal(s1: str, s2: str):
    def transform(s: str):
        return s.replace(" ", "").replace("\t", "").replace("\n", "")

    return transform(s1) == transform(s2)


def find_similarity(base: list[tuple[object, str]], change: list[tuple[object, str]]):

    indexed = [set() for _ in range(len(change))]

    maximum_match = 0

    for i in range(len(change)):
        for j in range(len(base)):
            if consider_equal(change[i][1], base[j][1]):
                indexed[i].add(j)

        if len(indexed[i]) > maximum_match:
            maximum_match = len(indexed[i])

    used = set()

    def set_value(i, v):
        used.add(v)
        indexed[i] = [v]

    for i, v in zip(range(len(indexed)), indexed):
        not_used = v.difference(used)
        if len(not_used) == 1:
            v = not_used.pop()
            set_value(i, v)

    for i, v in zip(range(len(indexed)), indexed):
        if type(v) == set and len(v.difference(used)) == 1:
            v = v.pop()
            set_value(i, v)
        elif type(v) == set:
            indexed[i] = v.difference(used)

    for i in range(len(indexed)):
        if len(indexed[i]) == 1:
            v = indexed[i][0]
            if i > 0 and type(indexed[i - 1]) == set:
                difference = indexed[i - 1].difference(used)
                if len(difference) >= 1 and (v - 1) in difference:
                    set_value(i - 1, v - 1)

            if i < len(indexed) - 1 and type(indexed[i + 1]) == set:
                difference = indexed[i + 1].difference(used)
                if len(difference) >= 1 and (v + 1) in difference:
                    set_value(i + 1, v + 1)
    return [
        (base[v.pop()], change[i])
        for v, i in zip(indexed, range(len(indexed)))
        if len(v) == 1
    ]


RANGE = 10


def extract_change(begin_i, end_i, i, st_getter, addition):

    change = []
    differentials = []
    thisDifferentials = []

    for k in range(begin_i, end_i):
        st = st_getter(k)

        if st != None and "git" in st.object.definition.extensions:
            current = st.object.definition.extensions["git"]
            differentials += current
            if k == i:
                thisDifferentials += current

            for diff in current:
                if diff.parts == None:
                    continue
                for part in diff.parts:
                    content = part.content
                    change += [
                        (
                            (
                                st.object.id,
                                diff.file,
                                part.a_start_line if addition else part.b_start_line,
                                i,
                            ),
                            content[i][1:],
                        )
                        for i in range(len(content))
                        if content[i].startswith("-" if addition else "+")
                    ]

    return (change, differentials, thisDifferentials)


def split(statement, differentials, diff, k, intervals):
    part = CodeModifier.generate_sub_diffpart(diff.parts, k, intervals, True)

    newstatement: Statement = copy.deepcopy(statement)
    differentials.append((newstatement, False))
    key = statement.object.id + "_" + diff.file + "_" + str(intervals[0][0])
    newstatement.object.id = (
        "generated~cutpaste~" + newstatement.object.id + "~" + str(key)
    )

    newdifferential: Differential = Differential(diff.__dict__)
    newstatement.object.definition.extensions["git"] = [newdifferential]
    newstatement.context.extensions["origins"] = [statement.object.id]
    if "origins" in statement.context.extensions:
        newstatement.context.extensions["origins"] += statement.context.extensions[
            "origins"
        ]
    newdifferential.parts = []
    newdifferential.parts.append(part)


def process_finding(
    st_getter: any, i: int, search_range: int, addition: bool, is_it_copy_paste: any
):
    statement: Statement = st_getter(i)
    intervals = [
        i - search_range,
        i + search_range + 1,
    ]

    change, differentials, thisDifferential = extract_change(
        intervals[0], intervals[1], i, st_getter, addition
    )

    differentials = [d for d in differentials if d != None and d.parts != None]
    thisDifferential = [d for d in thisDifferential if d != None and d.parts != None]

    base = []
    differentials = []

    for i in range(len(thisDifferential)):
        diff = thisDifferential[i]
        for k in range(len(diff.parts)):
            part = diff.parts[k]
            base = []
            group = False
            for i in range(len(part.content)):
                line: str = part.content[i]

                if line.startswith("+" if addition else "-"):
                    group = True
                    base.append(
                        (
                            (
                                statement.object.id,
                                diff.file,
                                part.a_start_line if addition else part.b_start_line,
                                i,
                            ),
                            line[1:],
                        )
                    )
                elif group and len(base) > 0:
                    p = find_similarity(base, change)
                    if is_it_copy_paste(p):
                        interval = [
                            [v[1][0][-1], v[1][0][-1] + 1]
                            for v in p
                            if v[1][0][0] == statement.object.id
                            and v[1][0][-1]
                            <= (part.a_interval if addition else part.b_interval)
                        ] + [
                            [v[0][0][-1], v[0][0][-1] + 1]
                            for v in p
                            if v[0][0][0] == statement.object.id
                            and v[0][0][-1]
                            <= (part.b_interval if addition else part.a_interval)
                        ]
                        if len(interval) > 0:
                            interval.sort(key=lambda x: x[0])
                            split(statement, differentials, diff, k, interval)
                            break

                    base = []
                    group = False

    return differentials


class CutPasteTask(TaskIdentifier):

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:

        statement: Statement = st_getter(i)
        if TaskIdentifier.is_task_set(statement):
            return [statement]
        if not "git" in statement.object.definition.extensions:
            return [statement]
        returns = []

        same_file = process_finding(st_getter, i, 0, True, is_it_line_moved)

        for st in same_file:
            st: Statement = st[0]

        returns += same_file

        returns += process_finding(
            st_getter, i, True, RANGE, is_it_copy_paste_accross_file
        )
        returns += process_finding(
            st_getter, i, False, RANGE, is_it_copy_paste_accross_file
        )

        for r in returns:
            TaskIdentifier.set_task(r[0], "CutPaste", {})

        returns += [(statement, False)]

        return [r[0] for r in returns]
