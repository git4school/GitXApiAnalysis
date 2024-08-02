import json
import os
from GitToXApi.utils import deserialize_statements
from GitToXApi import Statement
from identifier.tasks_identifier import TaskIdentifier
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py import write_xes
from typing import Callable
from tincan.conversions.iso8601 import make_datetime

COMMIT_HASH_LENGTH = 40


def extract_list_of_class_set(path: str):
    if os.path.isdir(path):
        return [
            extract_list_of_class_set(path + "/" + f)
            for f in os.listdir(path)
            if f.endswith("_compressed.json")
        ]

    data = None
    with open(path) as f:
        try:
            data = json.load(f)
        except:
            print(path)
            return []

    initial = [d for d in data if len(d["id"]) == COMMIT_HASH_LENGTH]

    returns = dict(((i["id"], [i]) for i in initial))

    for d in data:
        if not "origins" in d:
            continue

        for o in d["origins"]:
            if o in returns:
                returns[o] += [d]

    return (path, data, [(k, returns[k]) for k in returns])


def class_counts():
    initial_data = extract_list_of_class_set("out")
    first_row = [d[1] for d in initial_data]
    data = [
        [(d["task"]["id"]) if "task" in d else "UNKNOWN" for d in group]
        for group in first_row
    ]

    mask = ["EmptyCommit"]

    data = [[d for d in group if not d in mask] for group in data]

    unique = list(set(x for d in data for x in d))

    counts: list[dict] = [dict((k, d.count(k)) for k in unique) for d in data]
    unique.sort(
        key=lambda k: -sum(d[k] * 1.0 / (sum(v for v in d.values())) for d in counts)
    )
    unique_index = dict((k, i) for i, k in enumerate(unique))

    co_occurrence_matrix = np.zeros((len(unique_index), len(initial_data)), dtype=float)
    for k in unique:
        for i in range(len(counts)):
            co_occurrence_matrix[unique_index[k]][i] = counts[i][k]

    for k in sorted(
        unique,
        key=lambda k: -np.mean(
            [co_occurrence_matrix[unique_index[k]][i] for i in range(len(counts))]
        ),
    ):
        unknowns = np.array(
            [co_occurrence_matrix[unique_index[k]][i] for i in range(len(counts))]
        )
        print(
            k,
            format(np.mean(unknowns), ".2f"),
            np.sum(unknowns),
            np.max(unknowns),
            np.min(unknowns),
            sep="],[",
        )

    for i in range(len(counts)):
        co_occurrence_matrix[:, i] /= sum(v for v in counts[i].values())

    scale = 2

    fig, ax = plt.subplots(figsize=(48 * scale, 36 * scale))

    sns.set(font_scale=2.25)
    b = sns.heatmap(
        co_occurrence_matrix,
        yticklabels=np.array(unique),
        xticklabels=np.array(
            ["" for d in initial_data]
        ),  # np.array([d[0][: d[0].rfind("_")] for d in initial_data]),
        annot=True,
        cmap="YlGnBu",
        cbar=True,
        fmt=".1%",
    )
    b.set_xticklabels(b.get_xticklabels(), size=50, rotation=90)
    b.set_yticklabels(b.get_yticklabels(), size=50)

    plt.savefig("counts.svg")


def class_co_occurence(initial_stmts, stms, filter, out):

    sets = dict([(st.object.id, set()) for st in initial_stmts])

    for st in stms:
        if not filter(st):
            continue
        task = TaskIdentifier.get_task(st)
        if task == None or not "origins" in st.context.extensions:
            continue
        found = False
        for key in st.context.extensions["origins"]:
            if not key in sets.keys():
                continue
            found = True
            sets[key].add(task[0])
        if not found:
            print(st.object.id)

    sets = sets.values()

    unique_elements = set().union(*sets)
    if "EmptyCommit" in unique_elements:
        unique_elements.remove("EmptyCommit")

    element_index = {elem: i for i, elem in enumerate(unique_elements)}
    n = len(unique_elements)

    # Initialize the co-occurrence matrix
    co_occurrence_matrix = np.zeros((n, n), dtype=float)

    # Fill the co-occurrence matrix
    for s in sets:
        for elem1 in s:
            if not elem1 in unique_elements:
                continue
            for elem2 in s:
                if not elem2 in unique_elements:
                    continue

                i, j = element_index[elem1], element_index[elem2]
                co_occurrence_matrix[i, j] += 1

    for e1 in unique_elements:
        i1 = element_index[e1]
        for e2 in unique_elements:
            i2 = element_index[e2]
            if i1 != i2:
                co_occurrence_matrix[i1, i2] /= co_occurrence_matrix[i1, i1]

    for e1 in unique_elements:
        i1 = element_index[e1]
        co_occurrence_matrix[i1, i1] = 1

    # Create a heatmap
    plt.figure(figsize=(48, 36))
    sns.heatmap(
        co_occurrence_matrix,
        xticklabels=unique_elements,
        yticklabels=unique_elements,
        annot=True,
        cmap="YlGnBu",
        cbar=True,
    )
    plt.title("Co-occurrence Heatmap")

    plt.savefig(out, format="svg")


def class_co_occurence_bt_source_test():
    initial_statements = None
    with open("cache/tp-welcome-2023-2024-Merlinpinpin1.json") as f:
        initial_statements = deserialize_statements(f)

    task_stmts = None
    with open("cache/tp-welcome-2023-2024-Merlinpinpin1_task.json") as f:
        task_stmts = deserialize_statements(f)

    class_co_occurence(initial_statements, task_stmts, lambda x: True, "all.svg")
    class_co_occurence(
        initial_statements,
        task_stmts,
        lambda st: ("name_path" in st.context.extensions)
        and ("test" in st.context.extensions["name_path"].lower()),
        "test.svg",
    )

    class_co_occurence(
        initial_statements,
        task_stmts,
        lambda st: ("name_path" in st.context.extensions)
        and (not "test" in st.context.extensions["name_path"].lower()),
        "source.svg",
    )


def generate_xes(
    stmts: list[dict],
    out,
    filter: Callable[[dict, str], bool],
    get_clazz: Callable[[dict], str],
):
    event_log = EventLog()
    trace = Trace()

    for st in stmts:
        event = Event()

        clazz = get_clazz(st)

        if clazz == None or not filter(st, clazz):
            continue

        event["concept:name"] = clazz
        event["time:timestamp"] = make_datetime(st["timestamp"])
        event["metadata"] = str(st)
        trace.append(event)

    event_log.append(trace)

    write_xes(event_log, out)


def generate_couple_xes(
    stmts: list[dict],
    out,
    filter: Callable[[dict, str], bool],
    get_clazz: Callable[[dict], str],
):
    event_log = EventLog()
    trace = Trace()

    pred = "START"

    for st in stmts:
        event = Event()

        clazz = get_clazz(st)

        if clazz == None or not filter(st, clazz):
            continue

        event["concept:name"] = pred + "\n" + clazz
        pred = clazz
        event["time:timestamp"] = make_datetime(st["timestamp"])
        event["metadata"] = str(st)
        trace.append(event)

    event_log.append(trace)

    write_xes(event_log, out)


def generate_couple_xes_for_dir(
    input,
    out,
    filter: Callable[[dict, str], bool],
    get_clazz: Callable[[dict], str],
):
    event_log = EventLog()

    for file in os.listdir(input):
        if not file.endswith("_compressed.json"):
            continue
        path = input + "/" + file
        data = None
        with open(path) as f:
            data = json.load(f)

        trace = Trace()

        pred = "START"

        for st in data:
            event = Event()

            clazz = get_clazz(st)

            if clazz == None or not filter(st, clazz):
                continue

            event["concept:name"] = pred + "\n" + clazz
            pred = clazz
            event["time:timestamp"] = make_datetime(st["timestamp"])
            event["metadata"] = str(st)
            trace.append(event)

        event = Event()
        event["concept:name"] = pred + "\nEND"
        event["time:timestamp"] = make_datetime(data[-1]["timestamp"])
        event["metadata"] = str({})
        trace.append(event)

        event_log.append(trace)

    write_xes(event_log, out)


def clazz_getter_from_task(st: dict):
    if "task" in st:
        return st["task"]["id"]
    return "UNKNOWN"


def generate_from_mapping_group():
    mapping = {}
    with open("mapping.json") as f:
        data = json.load(f)
        mapping = dict(data)

    def clazz_from_mapping(st: dict):
        task = clazz_getter_from_task(st)

        if task == "Completed":
            return "Completed"

        if not "name_path" in st:
            return None

        if not task in mapping:
            return None

        namepath = st["name_path"]

        namepath = namepath[: namepath.rfind(":")]
        namepath = namepath[namepath.rfind("/") + 1 :]

        if mapping[task] == None:
            return None

        case_type = "TEST" if namepath.lower().endswith("test.java") else "SOURCE"

        if mapping[task][case_type] == None:
            return None

        if case_type == "TEST":
            return "TEST"

        return case_type + ":" + mapping[task][case_type]

    def filter(st, clazz):
        return True

    generate_couple_xes_for_dir("out", "out.xes", filter, clazz_from_mapping)
