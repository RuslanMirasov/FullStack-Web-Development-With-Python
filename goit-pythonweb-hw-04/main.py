import argparse
import asyncio
import logging
import shutil
from pathlib import Path

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno >= logging.ERROR:
            color = RED
        elif getattr(record, "final", False):
            color = GREEN
        else:
            color = YELLOW
        return f"{color}{super().format(record)}{RESET}"


handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)


async def copy_file(file_path: Path, output_folder: Path) -> bool:
    try:
        ext = file_path.suffix.lstrip(".").lower() or "no_extension"
        target_dir = output_folder / ext
        await asyncio.to_thread(target_dir.mkdir, exist_ok=True, parents=True)
        destination = target_dir / file_path.name
        await asyncio.to_thread(shutil.copyfile, file_path, destination)
        logger.info(f"Copied {file_path} -> {destination}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy {file_path}: {e}")
        return False


async def read_folder(source_folder: Path, output_folder: Path) -> int:
    items = await asyncio.to_thread(list, source_folder.iterdir())
    tasks = []
    copied_count = 0
    for item in items:
        if item.is_dir():
            copied_count += await read_folder(item, output_folder)
        else:
            tasks.append(asyncio.create_task(copy_file(item, output_folder)))
    if tasks:
        results = await asyncio.gather(*tasks)
        copied_count += sum(results)
    return copied_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", required=True)
    parser.add_argument("-o", "--output", default="dist")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    source_folder = Path(args.source)
    output_folder = Path(args.output)

    if not source_folder.exists():
        logger.error(f"Source folder does not exist: {source_folder}")
        return

    output_folder.mkdir(exist_ok=True, parents=True)
    copied_count = await read_folder(source_folder, output_folder)
    logger.info(
        f"Done: sorted {copied_count} files from {source_folder} into {output_folder}",
        extra={"final": True},
    )


if __name__ == "__main__":
    asyncio.run(main())
