from typing import Callable
from tincan import Statement


class Modifier:
    def __init__(self) -> None:
        pass

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        pass
