import json
from tincan import Statement
import GitToXApi.differential
from tincan import Context
import copy
from identifier import *
from modifier import *
import debug
import shutil
import os
import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event


def format_statement(st: Statement) -> Statement:
    if st.context == None:
        st.context = Context()

    if st.context.extensions == None:
        st.context.extensions = dict()

    return st


def exec_modifier(statements: list[Statement], identifier: CodeModifier):
    st_getter = lambda x: statements[x] if 0 <= x < len(statements) else None
    processed = {}
    i = 0
    while i < len(statements):
        st: Statement = st_getter(i)
        if TaskIdentifier.is_task_set(st):
            i += 1
            continue
        last_id = st.object.id
        if last_id in processed:
            i += 1
            continue
        processed[last_id] = True

        returns = identifier.process_statement(st_getter, i)
        statements = statements[:i] + returns + statements[i + 1 :]

    return statements


def dump(
    name: str, statements: list[Statement], filter: Callable[[Statement], bool]
) -> None:
    with open("out/" + name + ".json", "w") as f:
        f.write(
            json.dumps(
                [stmt.as_version() for stmt in statements if filter(stmt)],
                indent=2,
            )
        )


if __name__ == "__main__":

    raw = None
    with open("original.json") as f:
        raw = json.load(f)
    initial_total = len(raw)
    initial_statements = [format_statement(Statement(e)) for e in raw]
    statements = copy.deepcopy(initial_statements)

    for event in statements:
        event.object.definition.extensions["git"] = [
            GitToXApi.differential.Differential(v)
            for v in event.object.definition.extensions["git"]
        ]

    statements = [s for s in statements]

    code_modifiers = [
        PreciseVerbModifier(),
        NotSourceTask(),
        RefactoringMinerTask(),
        TrimEditionContentModifier(),
        LineBreakAndSpacingChangeTask(),
        CutPasteTask(),
        EditionDetectionModifier(),
        CodeEditionIdentifier(),
        PackageTask(),
        ImportTask(),
        ClassTask(),
        FunctionTask(),
        AnnotationTask(),
        EmptyLineChangeTask(),
        ForTask(),
        IfTask(),
        ReturnTask(),
        VariableDeclarationTask(),
        MethodInvocationTask(),
        BlockTask(),
        SyntaxTypo(),
    ]

    code_modifiers += [
        RemoveEmptyCodePartModifier(),
        RemoveEmptyDifferentialModifier(),
        EmptyGitTaskIdentifier(),
    ]

    for modif in code_modifiers:
        statements = exec_modifier(statements, modif)

    shutil.rmtree("out", ignore_errors=True)
    os.mkdir("./out")

    scores = {"UNKNOWN": 0}

    for st in statements:
        if TaskIdentifier.is_task_set(st):
            task = TaskIdentifier.get_task(st)[0]
            if not task in scores:
                scores[task] = 0
            scores[task] += 1
        else:
            scores["UNKNOWN"] += 1

    for k in scores:
        if k in debug.CLASS_MASK:
            continue
        safe_name: str = k.lower().replace(" ", "_")
        dump(
            safe_name,
            statements,
            lambda x: "task" in x.context.extensions
            and x.context.extensions["task"]["id"] == k,
        )
    dump(
        "unknown",
        statements,
        lambda x: not "task" in x.context.extensions,
    )

    scores = [(k, scores[k]) for k in scores]
    scores.sort(key=lambda v: -v[1])

    [
        print(k, v, (str(v * 100 / len(statements)) + "    ")[:4], "%")
        for (k, v) in scores
    ]

    if debug.GENERATE_XES_FROM_INITIAL:
        keys = [st.object.id for st in initial_statements]

        event_log = EventLog()
        trace = Trace()

        for key in keys:
            event = Event()
            classes = set()
            for st in statements:
                task = TaskIdentifier.get_task(st)
                if task == None or not "origins" in st.context.extensions:
                    continue
                if not key in st.context.extensions["origins"]:
                    continue
                classes.add(task[0])
            if len(classes) == 0:
                classes.add("UNKNOWN")
            classes = list(classes)
            classes.sort()
            event["concept:name"] = "/".join(classes)
            event["org:resource"] = st.object.definition.description["en-US"]
            event["time:timestamp"] = st.timestamp
            trace.append(event)

        event_log.append(trace)

        pm4py.write_xes(event_log, "out/initial.xes")

    if debug.GENERATE_XES_FROM_CREATED:

        event_log = EventLog()
        trace = Trace()

        for st in statements:
            event = Event()

            clazz = "UNKNOWN"
            task = TaskIdentifier.get_task(st)
            if task != None:
                clazz = task[0]

            if clazz == "EmptyCommit":
                continue

            event["concept:name"] = clazz
            event["time:timestamp"] = st.timestamp
            trace.append(event)

        event_log.append(trace)

        pm4py.write_xes(event_log, "out/artificial.xes")
