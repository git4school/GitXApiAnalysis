from GitToXApi import *
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py import write_xes
from identifier.tasks_identifier import TaskIdentifier


def generate_xes_from_initial(
    initial: list[Statement], created: list[Statement], out="out/initial.xes"
):
    keys = [st.object.id for st in initial]

    event_log = EventLog()
    trace = Trace()

    for key in keys:
        event = Event()
        classes = set()
        for st in created:
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

    write_xes(event_log, out)


def generate_xes_from_created(
    created: list[Statement], mask: list = ["EmptyCommit"], out="out/initial.xes"
):
    event_log = EventLog()
    trace = Trace()

    for st in created:
        event = Event()

        clazz = "UNKNOWN"
        task = TaskIdentifier.get_task(st)
        if task != None:
            clazz = task[0]

        if clazz in mask:
            continue

        event["concept:name"] = clazz
        event["time:timestamp"] = st.timestamp
        trace.append(event)

    event_log.append(trace)

    write_xes(event_log, out)
