# File Sorter

A simple command-line tool written in Python that organizes the files in a folder, either **by file type** or **by date**. Every sort can be **undone**, and a built-in **test folder** lets you try everything safely before touching real files.

> The program's menu and messages are in Russian, as are the category folder names it creates (see the table below).

## Features

- **Sort by type**: files are moved into category folders such as Images, Documents, Video, and so on.
- **Sort by date**: files are moved into `year/month` folders based on their last-modified date, for example `2026/10 Октябрь`.
- **Undo**: restores the files moved by the last sort and removes the folders that became empty.
- **Dry run**: shows what would happen without moving anything.
- **Test folder**: creates `~/test` with 20 empty files of different types and dates.
- **Safe by design**: existing files are never overwritten (a duplicate name gets ` (1)`, ` (2)`, ... added), and subfolders, hidden files, and the script itself are skipped.

## Requirements

- Python 3.10 or newer
- No third-party packages, only the standard library

## Quick start

### In PyCharm

1. Create a new project (Pure Python) and add `sorter.py` to it.
2. Right-click `sorter.py` and choose **Run 'sorter'**.
3. Use the menu in the Run window at the bottom.

### In a terminal

```bash
python sorter.py
```

## Menu

```
1 - Sort by file type (Изображения, Документы, ...)
2 - Sort by date (2026/10 Октябрь, ...)
3 - Undo the last sort
4 - Create the test folder ~/test with 20 files
0 - Exit
```

For options 1 to 3 the program asks for a folder path. Press **Enter** to use the default, `~/test`. For options 1 and 2 it also asks whether to run a dry run (`д` = yes, `н` = no).

### Try it safely

1. Choose `4` to create the test folder.
2. Choose `2`, press Enter for the path, and answer `н`. The files are sorted by date.
3. Choose `3` and press Enter. Everything goes back to where it was.

When you are comfortable, enter the path of a real folder, for example `/home/your-name/Downloads`.

## Categories

When sorting by type, the extension decides the folder (case-insensitive):

| Folder created | Meaning | Extensions |
| --- | --- | --- |
| Изображения | Images | jpg, jpeg, png, gif, bmp, webp, svg, heic, tiff |
| Документы | Documents | pdf, doc, docx, txt, rtf, odt, xls, xlsx, csv, ppt, pptx, md |
| Видео | Video | mp4, mkv, avi, mov, wmv, flv, webm |
| Музыка | Music | mp3, wav, flac, aac, ogg, m4a |
| Архивы | Archives | zip, rar, 7z, tar, gz, bz2, xz |
| Программы | Programs | exe, msi, deb, rpm, appimage, apk, dmg |
| Код | Code | py, js, html, css, java, c, cpp, json, xml, sh |
| Прочее | Other | everything else, including files with no extension |

To add or change categories, edit the `CATEGORIES` dictionary at the top of `sorter.py`.

## How undo works

After every sort that moves at least one file, the program writes a hidden file named `.sorter_log.json` inside the sorted folder. It records where each file came from and where it went. Choosing **Undo** reads that record, moves the files back, removes the folders that are now empty, and deletes the record.

Things to know:

- Undo reverts only the **last** sort of each folder.
- A sort that finds nothing to move does not overwrite the record, so you can still undo the previous one.
- If a file was moved or deleted after sorting, undo skips it and says so.
- If a file with the original name has appeared in the meantime, the restored file gets ` (1)` added to its name instead of overwriting it.

## Project structure

```
.
├── sorter.py    # the whole program
└── README.md
```

## Ideas for next steps

- A window with buttons using `tkinter`
- Sorting subfolders too (recursion)
- Finding duplicate files by content hash
- Keeping categories in a separate `categories.json` file
- Writing a log with the `logging` module
