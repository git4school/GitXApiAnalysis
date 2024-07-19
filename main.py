from git import Repo
import json
from tincan import Statement
import gittoxapi.differential
import gittoxapi.gitXApi
import os

import matplotlib.pyplot as plt
import debug
import pm4py
import copy
from pm4py.objects.log.obj import EventLog, Trace, Event

from post_process import (
    AddTagToEdition,
    PostProcessModifier,
    FillXApiMissingField,
    PreciseVerb,
    SplitMultipleFile,
    TurnDiffToEdition,
    AttachRefactor,
    TrimAtomic,
    IsolateCutPaste,
    RemoveNewLineAtEndOfFile,
    LineFuser,
    SplitImport,
)
from classification import (
    ClassificationProcess,
    RefactoringClassification,
    NaiveSystemEventClassification,
    EditionClassification,
    ImportClassification,
    AddBodyClassification,
)

if __name__ == "__main__":

    raw = None
    with open("original.json") as f:
        raw = json.load(f)
    initial_total = len(raw)
    initial_statements = [Statement(e) for e in raw]
    statements = copy.deepcopy(initial_statements)

    for event in statements:
        event.object.definition.extensions["git"] = [
            gittoxapi.differential.Differential(v)
            for v in event.object.definition.extensions["git"]
        ]

    processes: list[PostProcessModifier.PostProcessModifier] = [
        FillXApiMissingField.FillXApiMissingField(),
        SplitMultipleFile.SplitMultipleFile(),
        RemoveNewLineAtEndOfFile.RemoveNewLineAtEndOfFile(),
        SplitImport.SplitImport(),
        AttachRefactor.AttachRefactor(),
        IsolateCutPaste.IsolateCutPaste(),
        PreciseVerb.PreciseVerb(),
        LineFuser.LineFuser(),
        TurnDiffToEdition.TurnDiffToEdition(),
        AddTagToEdition.AddTagToEdition(),
        TrimAtomic.TrimAtomic(),
    ]

    for p in processes:
        statements = p.process(statements)
    print("ADDITIONS", len(statements) - initial_total)
    total = len(statements)

    with open("dump_s.json", "w") as f:
        f.write(json.dumps([stmt.as_version() for stmt in statements], indent=2))

    classifications: list[ClassificationProcess.Classification] = [
        NaiveSystemEventClassification.NaiveSystemEventClassification(),
        RefactoringClassification.RefactoringClassification(),
        EditionClassification.EditionClassification(),
        ImportClassification.ImportClassification(),
        AddBodyClassification.AddBodyClassification(),
    ]

    score = dict([(c.__class__.__name__, 0) for c in classifications])

    for s in statements:
        for p in classifications:
            score[p.__class__.__name__] += 1 if p.classify(s) else 0

    remaining = [
        stmt.as_version()
        for stmt in statements
        if len(stmt.context.extensions["classified"]) == 0
    ]

    score["remaining"] = len(remaining)

    print(score)

    print(
        "Initial:",
        initial_total,
        ", Total:",
        total,
        ", Remaining:",
        len(remaining),
        ", Progress:",
        (str((total - len(remaining)) * 100 / total) + " " * 4)[:4],
        "%",
    )

    with open("dump_remaining.json", "w") as f:
        f.write(
            json.dumps(
                remaining,
                indent=2,
            )
        )

    with open("dump_classified.json", "w") as f:
        f.write(
            json.dumps(
                [
                    stmt.as_version()
                    for stmt in statements
                    if len(stmt.context.extensions["classified"]) > 0
                ],
                indent=2,
            )
        )

    with open("dump_atomic.json", "w") as f:
        f.write(
            json.dumps(
                [
                    stmt.as_version()
                    for stmt in statements
                    if stmt.context.extensions["atomic"]
                ],
                indent=2,
            )
        )

    with open("dump_atomic_remaining.json", "w") as f:
        f.write(
            json.dumps(
                [
                    stmt.as_version()
                    for stmt in statements
                    if len(stmt.context.extensions["classified"]) == 0
                    and stmt.context.extensions["atomic"]
                ],
                indent=2,
            )
        )
    if debug.SHOW_GRAPH:
        classified_lines = []
        unclassified_lines = []
        classified_git = 0
        unclassified_git = 0

        for statement in statements:
            if not "git" in statement.object.definition.extensions:
                continue

            classified = len(statement.context.extensions["classified"]) > 0

            if classified:
                classified_git += 1
            else:
                unclassified_git += 1

            differentials = statement.object.definition.extensions["git"]

            for diff in differentials:
                if not diff.file.endswith(".java"):
                    continue
                if diff.parts == None:
                    continue
                for part in diff.parts:
                    if part == None or part.content == None:
                        continue
                    lines = sum([1 for l in part.content if not l.startswith(" ")])
                    if lines > 100 and not classified:
                        print(statement.object.id)
                    if classified:
                        classified_lines += [lines]
                    else:
                        unclassified_lines += [lines]

        fig, ax = plt.subplots(1, 2)

        sorted_classified_bins = list(set(classified_lines))
        sorted_classified_bins.sort()

        sorted_unclassified_bins = list(set(unclassified_lines))
        sorted_unclassified_bins.sort()
        max_i = max(
            max([classified_lines.count(v) for v in sorted_classified_bins]),
            max([unclassified_lines.count(v) for v in sorted_unclassified_bins]),
        )

        ax[0].hist(classified_lines, sorted_classified_bins)
        ax[0].set_title("Classified lines")
        ax[0].set_ylim([0, max_i])
        ax[1].hist(unclassified_lines, sorted_unclassified_bins)
        ax[1].set_title("Remaining lines")
        ax[1].set_ylim([0, max_i])
        plt.show()

    if debug.GENEREATE_CLASS_FILE:
        classes = set()

        for statement in statements:
            classes = classes.union(statement.context.extensions["classified"])
        for clazz in classes:
            file_name = "dump_clazz_" + clazz + ".json"
            if clazz in debug.CLASS_MASK:
                if os.path.isfile(file_name):
                    os.remove(file_name)
            else:
                with open(file_name, "w") as f:
                    f.write(
                        json.dumps(
                            [
                                stmt.as_version()
                                for stmt in statements
                                if clazz in stmt.context.extensions["classified"]
                            ],
                            indent=2,
                        )
                    )

    if debug.GENERATE_XES_FROM_INITIAL:
        keys = [st.object.id for st in initial_statements]

        event_log = EventLog()
        trace = Trace()

        for key in keys:
            event = Event()
            classes = set()
            for st in statements:
                if not key in st.object.id:
                    continue
                classified = st.context.extensions["classified"]

                if len(classified) == 0:
                    classes.add("UNKNOWN")
                else:
                    classes = classes.union(classified)
            if len(classes) == 0:
                classes.add("UNKNOWN")
            classes = list(classes)
            classes.sort()
            event["concept:name"] = "/".join(classes)
            event["org:resource"] = st.object.definition.description["en-US"]
            event["time:timestamp"] = st.timestamp
            trace.append(event)

        event_log.append(trace)

        pm4py.write_xes(event_log, "initial.xes")

    if debug.GENERATE_XES_FROM_CREATED:

        event_log = EventLog()
        trace = Trace()

        for st in statements:
            event = Event()
            classified = st.context.extensions["classified"]

            clazz = "UNKNOWN"
            if "REFACTORING" in classified or "WHITESPACE" in classified:
                clazz = "REFACTORING"
            else:
                if len(classified) > 1:
                    print(classified)
                elif len(classified) != 0:
                    clazz = classified.pop()

            event["concept:name"] = clazz
            event["org:resource"] = st.object.definition.description["en-US"]
            event["time:timestamp"] = st.timestamp
            trace.append(event)

        event_log.append(trace)

        pm4py.write_xes(event_log, "artificial.xes")
