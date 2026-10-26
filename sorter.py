import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path



CATEGORIES = {
    "Изображения": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".tiff"},
    "Документы": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".md"},
    "Видео": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Музыка": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Архивы": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Программы": {".exe", ".msi", ".deb", ".rpm", ".appimage", ".apk", ".dmg"},
    "Код": {".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".json", ".xml", ".sh"},
}
OTHER = "Прочее"

MONTHS = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]


LOG_NAME = ".sorter_log.json"


TEST_FILES = [
    "photo.jpg", "photo.JPG", "screenshot.png", "logo.svg",
    "report.pdf", "notes.txt", "budget.xlsx", "presentation.pptx",
    "movie.mp4", "clip.mkv",
    "song.mp3", "podcast.m4a",
    "archive.zip", "backup.tar.gz",
    "setup.exe", "installer.deb",
    "script.py", "index.html",
    "random.xyz", "no_extension",
]

MENU = """
==================== СОРТИРОВЩИК ====================
1 - Сортировать по типу файлов (Изображения, Документы, ...)
2 - Сортировать по дате (2026/10 Октябрь, ...)
3 - Отменить последнюю сортировку
4 - Создать тестовую папку ~/test с 20 файлами
0 - Выход
"""




def create_test_folder() -> Path:
    """Создаёт папку ~/test с 20 пустыми файлами. У файлов разные даты изменения."""
    folder = Path.home() / "test"
    folder.mkdir(exist_ok=True)
    now = time.time()
    for i, name in enumerate(TEST_FILES):
        file = folder / name
        file.touch()
        old = now - i * 20 * 24 * 3600
        os.utime(file, (old, old))
    print(f"Создана тестовая папка {folder} ({len(TEST_FILES)} файлов)")
    return folder


def get_category(file: Path) -> str:
    """Определяет категорию файла по расширению."""
    ext = file.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return OTHER


def get_date_folder(file: Path) -> Path:
    """Возвращает путь вида 2026/10 Октябрь по дате изменения файла."""
    date = datetime.fromtimestamp(file.stat().st_mtime)
    return Path(str(date.year)) / f"{date.month:02d} {MONTHS[date.month - 1]}"


def unique_path(destination: Path) -> Path:
    """Если файл с таким именем уже есть, добавляет (1), (2), ... к имени."""
    if not destination.exists():
        return destination
    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def remove_empty_dirs(folder: Path, stop: Path) -> None:
    """Удаляет пустую папку и пустые папки выше неё (но не дальше stop)."""
    while folder != stop and folder.is_dir():
        try:
            folder.rmdir()
        except OSError:
            break
        folder = folder.parent




def sort_folder(folder: Path, by: str, dry_run: bool = False) -> None:
    """Сортирует файлы из folder. by = "type" (по типу) или "date" (по дате)."""
    moves = []
    this_script = Path(__file__).resolve()

    for item in sorted(folder.iterdir()):

        if not item.is_file() or item.name.startswith(".") or item.resolve() == this_script:
            continue

        if by == "date":
            sub = get_date_folder(item)
        else:
            sub = Path(get_category(item))

        target_dir = folder / sub
        target = unique_path(target_dir / item.name)
        short = target.relative_to(folder)  

        if dry_run:
            print(f"[проверка] {item.name}  ->  {short}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(target))
            print(f"{item.name}  ->  {short}")
        moves.append({"from": item.name, "to": str(short)})

    if dry_run:
        print(f"\nГотово: было бы перемещено файлов: {len(moves)}")
        return

    if moves:
        
        log = {"time": datetime.now().isoformat(timespec="seconds"), "moves": moves}
        (folder / LOG_NAME).write_text(
            json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nГотово: перемещено файлов: {len(moves)}. Отменить можно пунктом 3.")
    else:
        print("\nНечего перемещать.")


def undo_last(folder: Path) -> None:
    """Возвращает файлы на места по записи последней сортировки."""
    log_file = folder / LOG_NAME
    if not log_file.exists():
        print("В этой папке нет записи о сортировке, отменять нечего.")
        return

    try:
        data = json.loads(log_file.read_text(encoding="utf-8"))
        moves = data["moves"]
    except (json.JSONDecodeError, KeyError):
        print("Файл записи повреждён, отмена невозможна.")
        return

    restored = 0
    for move in reversed(moves):
        src = folder / move["to"]
        dst = unique_path(folder / move["from"])
        if not src.exists():
            print(f"Пропущен (файл не найден): {move['to']}")
            continue
        shutil.move(str(src), str(dst))
        print(f"{move['to']}  ->  {dst.name}")
        remove_empty_dirs(src.parent, folder) 
        restored += 1

    log_file.unlink()
    print(f"\nГотово: возвращено файлов: {restored}")




def ask_folder() -> Path | None:
    """Спрашивает путь к папке. Если просто нажать Enter, берётся ~/test."""
    default = Path.home() / "test"
    text = input(f"Путь к папке (Enter - {default}): ").strip().strip('"').strip("'")
    folder = Path(text).expanduser() if text else default
    if not folder.is_dir():
        print(f"Ошибка: папка не найдена: {folder}")
        if not text:
            print("Создай тестовую папку пунктом 4.")
        return None
    return folder


def ask_yes_no(question: str) -> bool:
    return input(question).strip().lower() in ("д", "да", "y", "yes")


def main() -> None:
    try:
        while True:
            print(MENU)
            choice = input("Твой выбор: ").strip()

            if choice == "0":
                print("Пока!")
                break
            elif choice in ("1", "2"):
                folder = ask_folder()
                if folder is None:
                    continue
                dry = ask_yes_no("Только показать, что будет сделано, без перемещения? (д/н): ")
                print()
                sort_folder(folder, "type" if choice == "1" else "date", dry_run=dry)
            elif choice == "3":
                folder = ask_folder()
                if folder is None:
                    continue
                print()
                undo_last(folder)
            elif choice == "4":
                create_test_folder()
            else:
                print("Не понял. Введи цифру от 0 до 4.")
    except (EOFError, KeyboardInterrupt):
        print("\nПока!")


if __name__ == "__main__":
    main()
