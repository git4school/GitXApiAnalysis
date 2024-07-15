from git import Repo
import json
from tincan import Statement
import gittoxapi.differential
import gittoxapi.gitXApi

from post_process import (
    AddTagToEdition,
    PostProcessModifier,
    FillXApiMissingField,
    PreciseVerb,
    TurnDiffToEdition,
    AttachRefactor,
    TrimAtomic,
)
from classification import (
    ClassificationProcess,
    RefactoringClassification,
    NaiveSystemEventClassification,
    EditionClassification,
)

if __name__ == "__main__":

    raw = None
    with open("original.json") as f:
        raw = json.load(f)

    statements = [Statement(e) for e in raw]

    for e in statements:
        e.object.definition.extensions["git"] = [
            gittoxapi.differential.Differential(v)
            for v in e.object.definition.extensions["git"]
        ]

    processes: list[PostProcessModifier.PostProcessModifier] = [
        FillXApiMissingField.FillXApiMissingField(),
        AttachRefactor.AttachRefactor(),
        PreciseVerb.PreciseVerb(),
        TurnDiffToEdition.TurnDiffToEdition(),
        AddTagToEdition.AddTagToEdition(),
        TrimAtomic.TrimAtomic(),
    ]

    for p in processes:
        statements = p.process(statements)
    total = len(raw)

    with open("dump_s.json", "w") as f:
        f.write(json.dumps([stmt.as_version() for stmt in statements], indent=2))

    classifications: list[ClassificationProcess.Classification] = [
        NaiveSystemEventClassification.NaiveSystemEventClassification(),
        RefactoringClassification.RefactoringClassification(),
        EditionClassification.EditionClassification(),
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
        "Total:",
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
                    if len(stmt.context.extensions["classified"]) > 0
                    and not stmt.context.extensions["atomic"]
                ],
                indent=2,
            )
        )
