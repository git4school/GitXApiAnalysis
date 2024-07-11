from git import Repo
import json
from tincan import Statement
import gittoxapi.differential
import gittoxapi.gitXApi

from post_process import (
    PostProcessModifier,
    PreciseVerb,
    TrimDiff,
    TurnDiffToEdition,
    AttachRefactor,
    TurnDiffToStringEdition,
    TurnPureToAddOrDel,
)
from classification import (
    ClassificationProcess,
    RefactoringClassification,
    NaiveSystemEventClassification,
    StringEditionClassification,
    ReadmeClassification,
    GitIgnoreClassification,
    WhitespaceClassification,
    CommentModificationClassification,
    AppendOrRemoveConditionClassification,
    TyposClassification,
    BooleanSwitchingClassification,
    ChangeArgumentClassification,
)

if __name__ == "__main__":

    raw = None
    with open("original.json") as f:
        raw = json.load(f)
    print(len(raw))

    statements = [Statement(e) for e in raw]

    for e in statements:
        e.object.definition.extensions["git"] = [
            gittoxapi.differential.Differential(v)
            for v in e.object.definition.extensions["git"]
        ]

    processes: list[PostProcessModifier.PostProcessModifier] = [
        AttachRefactor.AttachRefactor(),
        # PreciseVerb.PreciseVerb(),
        # TrimDiff.TrimDiff(),
        # TurnDiffToEdition.TurnDiffToInsertion(),
        # TurnDiffToStringEdition.TurnDiffToStringEdition(),
        # TurnPureToAddOrDel.TurnPureToAddOrDel(),
    ]

    for p in processes:
        statements = p.process(statements)

    with open("dump_s.json", "w") as f:
        f.write(json.dumps([stmt.as_version() for stmt in statements], indent=2))

    classifications: list[ClassificationProcess.Classification] = [
        RefactoringClassification.RefactoringClassification(),
        # NaiveSystemEventClassification.NaiveSystemEventClassification(),
        # StringEditionClassification.StringEditionClassification(),
        # ReadmeClassification.ReadmeClassification(),
        # GitIgnoreClassification.GitIgnoreClassification(),
        # WhitespaceClassification.WhitespaceClassification(),
        # AppendOrRemoveConditionClassification.AppendOrRemoveConditionClassification(),
        # CommentModificationClassification.CommentModificationClassification(),
        # TyposClassification.TyposClassification(),
        # BooleanSwitchingClassification.BooleanSwitchingClassification(),
        # ChangeArgumentClassification.ChangeArgumentClassification(),
    ]

    score = dict([(c.__class__.__name__, 0) for c in classifications])

    for s in statements:
        for p in classifications:
            score[p.__class__.__name__] += 1 if p.classify(s) else 0

    remaining = [
        stmt.as_version()
        for stmt in statements
        if not (
            stmt.context != None
            and stmt.context.extensions != None
            and "classified" in stmt.context.extensions
        )
    ]

    score["remaining"] = len(remaining)

    print(score)

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
                    if (
                        stmt.context != None
                        and stmt.context.extensions != None
                        and "classified" in stmt.context.extensions
                    )
                ],
                indent=2,
            )
        )
