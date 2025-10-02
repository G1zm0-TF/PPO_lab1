import os
import zipfile
import argparse
import sys

def create_archive(archive_name, file_paths):
    """Создаёт новый архив и добавляет в него указанные файлы."""
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
                print(f"Добавлен: {file_path}")
            else:
                print(f"Файл не найден: {file_path}", file=sys.stderr)
    print(f"Архив '{archive_name}' создан.")

def list_archive(archive_name):
    """Выводит содержимое архива."""
    if not os.path.exists(archive_name):
        print(f"Архив '{archive_name}' не найден.", file=sys.stderr)
        return
    with zipfile.ZipFile(archive_name, 'r') as zipf:
        print(f"Содержимое архива '{archive_name}':")
        for info in zipf.infolist():
            print(f"  {info.filename} ({info.file_size} байт)")

def add_to_archive(archive_name, file_paths):
    """Добавляет файлы в существующий архив."""
    if not os.path.exists(archive_name):
        print(f"Архив '{archive_name}' не существует. Создаём новый.", file=sys.stderr)
        create_archive(archive_name, file_paths)
        return

    # Создаём временный архив с существующим содержимым
    temp_name = archive_name + ".tmp"
    with zipfile.ZipFile(archive_name, 'r') as zip_read:
        with zipfile.ZipFile(temp_name, 'w', zipfile.ZIP_DEFLATED) as zip_write:
            # Копируем старые файлы
            for item in zip_read.infolist():
                data = zip_read.read(item.filename)
                zip_write.writestr(item, data)
            # Добавляем новые файлы
            for file_path in file_paths:
                if os.path.exists(file_path):
                    zip_write.write(file_path, os.path.basename(file_path))
                    print(f"Добавлен: {file_path}")
                else:
                    print(f"Файл не найден: {file_path}", file=sys.stderr)
    # Заменяем оригинальный архив
    os.replace(temp_name, archive_name)
    print(f"Файлы добавлены в архив '{archive_name}'.")

def remove_from_archive(archive_name, filenames):
    """Удаляет указанные файлы из архива."""
    if not os.path.exists(archive_name):
        print(f"Архив '{archive_name}' не найден.", file=sys.stderr)
        return

    temp_name = archive_name + ".tmp"
    removed = []
    with zipfile.ZipFile(archive_name, 'r') as zip_read:
        with zipfile.ZipFile(temp_name, 'w', zipfile.ZIP_DEFLATED) as zip_write:
            for item in zip_read.infolist():
                if item.filename not in filenames:
                    data = zip_read.read(item.filename)
                    zip_write.writestr(item, data)
                else:
                    removed.append(item.filename)
    os.replace(temp_name, archive_name)
    if removed:
        print(f"Удалены из архива '{archive_name}': {', '.join(removed)}")
    else:
        print("Нет файлов для удаления (указаны несуществующие имена).")

def main():
    parser = argparse.ArgumentParser(description="Простой архиватор на основе ZIP.")
    subparsers = parser.add_subparsers(dest='command', required=True, help="Команда")

    # Создание архива
    create_parser = subparsers.add_parser('create', help="Создать новый архив")
    create_parser.add_argument('archive', help="Имя архива (например, archive.zip)")
    create_parser.add_argument('files', nargs='+', help="Файлы для архивирования")

    # Просмотр содержимого
    list_parser = subparsers.add_parser('list', help="Просмотреть содержимое архива")
    list_parser.add_argument('archive', help="Имя архива")

    # Добавление файлов
    add_parser = subparsers.add_parser('add', help="Добавить файлы в архив")
    add_parser.add_argument('archive', help="Имя архива")
    add_parser.add_argument('files', nargs='+', help="Файлы для добавления")

    # Удаление файлов
    remove_parser = subparsers.add_parser('remove', help="Удалить файлы из архива")
    remove_parser.add_argument('archive', help="Имя архива")
    remove_parser.add_argument('files', nargs='+', help="Имена файлов внутри архива для удаления")

    args = parser.parse_args()

    if args.command == 'create':
        create_archive(args.archive, args.files)
    elif args.command == 'list':
        list_archive(args.archive)
    elif args.command == 'add':
        add_to_archive(args.archive, args.files)
    elif args.command == 'remove':
        remove_from_archive(args.archive, args.files)

if __name__ == "__main__":
    main()