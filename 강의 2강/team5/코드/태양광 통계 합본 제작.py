from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable, List, Tuple
from itertools import zip_longest

KOSIS_DIR = Path("../data/KOSIS/신재생 통계")

files = sorted(KOSIS_DIR.glob("*.csv"))

new_rows: list[list[str | int]] = [['지역','소계']]
for file in files:
    new_rows.append([0,0])
    with file.open('r', encoding='utf8') as f:
        reader = csv.reader(f)
        first = next(reader)
        second = next(reader)

        for idx in range(4, len(first)):
            if first[idx] == "기타":
                continue
            new_rows.append([first[idx], second[idx]])

with open('../data/KOSIS/신재생 통계/합본.csv', 'w', encoding='utf8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)