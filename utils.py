import javalang


def find_delim(lines: list[str], begin_col: int = None, begin_row: int = 0, delim="{"):

    delims = {"{": "}", "(": ")", "[": "]", "<": ">"}

    assert delim in delims

    begin_delim = delim
    end_delim = delims[delim]

    assert begin_col == None or lines[begin_row][begin_col] == begin_delim

    still_opened = 0 if begin_col == None else 1
    for line_i, line in zip(range(begin_row, len(lines)), lines[begin_row:]):
        if line_i == begin_row:
            line: str = line[(begin_col + 1) if begin_col != None else 0 :]
        if line.count(end_delim) < still_opened:
            still_opened -= line.count(end_delim)
            still_opened += line.count(begin_delim)
        else:
            for c_i, c in zip(range(len(line)), line):
                if c == begin_delim:
                    if begin_col == None:
                        begin_row = line_i
                        begin_col = c_i
                    still_opened += 1
                elif c == end_delim and begin_col != None:
                    still_opened -= 1
                if still_opened == 0 and begin_col != None:
                    return [
                        (begin_row, begin_col),
                        (line_i, c_i + (begin_col if (begin_row == line_i) else 0)),
                    ]

    return None


def tokenize(s: str) -> list[str]:
    tokens = list(javalang.tokenizer.tokenize(s, ignore_errors=True))
    return [(v.value, v.position, type(v).__name__) for v in tokens]


def find_token_identifier_substitution(s1: str, s2: str):

    IDENTIFIER_NAME = javalang.tokenizer.Identifier.__name__

    s1_tokens = tokenize(s1)
    s2_tokens = tokenize(s2)

    if len(s1_tokens) != len(s2_tokens):
        return

    if not all(s1_tokens[i][2] == s2_tokens[i][2] for i in range(len(s1_tokens))):
        return

    def is_equal(subst_origin: str, subs_dest: str):
        for i in range(len(s1_tokens)):
            if s1_tokens[i][2] != IDENTIFIER_NAME:
                if s1_tokens[i][0] != s2_tokens[i][0]:
                    return False
            else:
                if not (
                    (s1_tokens[i][0] == subst_origin and s2_tokens[i][0] == subs_dest)
                    or (s1_tokens[i][0] == s2_tokens[i][0])
                ):
                    return False
        return True

    # filter identifiers
    s1_identifiers = [v for v in s1_tokens if v[2] == IDENTIFIER_NAME]
    s2_identifiers = [v for v in s2_tokens if v[2] == IDENTIFIER_NAME]

    if len(s1_identifiers) != len(s2_identifiers):
        return

    for i in range(len(s1_identifiers)):
        if is_equal(s1_identifiers[i][0], s2_identifiers[i][0]):
            return (s1_identifiers[i][0], s2_identifiers[i][0])

    return
