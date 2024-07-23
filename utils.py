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
