# pylint: disable=possibly-used-before-assignment,no-name-in-module
# spell-checker: disable

from __future__ import annotations

from typing import TYPE_CHECKING

from scanner import identify_content

if (_IS_MAIN := __name__ == '__main__') or TYPE_CHECKING:
    import time
    from collections import Counter
    from concurrent.futures import ProcessPoolExecutor
    from pathlib import Path
    from pprint import pprint

    ROBLOX_CACHE_PATH = Path('~/AppData/Local/Temp/Roblox/http').expanduser()


def mp_identify() -> list[str]:
    with ProcessPoolExecutor() as e:
        results = list(
            e.map(identify_content, ROBLOX_CACHE_PATH.iterdir(), chunksize=500)
        )
    return results


def main() -> None:
    print('Identifying files...')
    start = time.perf_counter()
    a = mp_identify()
    end = time.perf_counter()

    c = Counter('Mesh' if i.startswith('Mesh') else i for i in a)
    total_time = round(end - start, 2)
    total_files = c.total()
    avg = round(total_time * 10_000 / total_files, 2)

    print(f'Done in {total_time}s.')
    print('Files:', total_files)
    print(f'Approximate time per 10k files: {avg}s')
    pprint(c)


if _IS_MAIN:
    main()
