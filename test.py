import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from scanner import identify_content


ROBLOX_CACHE_PATH = Path('~/AppData/LOCAL/Temp/Roblox/http').expanduser()


def mp_identify() -> list[str]:
    with ProcessPoolExecutor() as executor:
        results = list(
            executor.map(identify_content, ROBLOX_CACHE_PATH.iterdir(), chunksize=500)
        )
    return results


def main() -> None:
    start = time.perf_counter()
    a = mp_identify()
    end = time.perf_counter()

    print(f'Done in {end - start:.2f}s.')
    print('Files:', len(a))


if __name__ == '__main__':
    main()
