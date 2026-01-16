import argparse
import bz2
import tarfile
import time
import sys
from pathlib import Path
from compression import zstd
import os


# Нужео в случае, когда вводится имя без .tar
def normalize_archive_name(name: str) -> str:
    """Добавляет '.tar' перед расширением, если его нет."""
    name = name.lower()
    if name.endswith('.tar.zst') or name.endswith('.tar.bz2'):
        return name  # уже в правильном формате
    if name.endswith('.zst'):
        return name[:-4] + '.tar.zst'
    if name.endswith('.bz2'):
        return name[:-4] + '.tar.bz2'

# опреляет метод архивации
def get_compression(path: str):
    path = path.lower()
    if path.endswith('.zst'):
        return 'zstd'
    elif path.endswith('.bz2'):
        return 'bz2'
    else:
        raise ValueError("Неподдерживаемый формат файла. Нужно использовать .tar.zst или .tar.bz2")
    
# рисует прогресс бар
def progress_bar(iterable, total=None, desc="Processing"):
    if total is None:
        total = len(iterable) if hasattr(iterable, '__len__') else 0
    count = 0
    def update():
        nonlocal count
        count += 1
        if total > 0:
            pct = count / total
            bar = '█' * int(40 * pct) + '-' * (40 - int(40 * pct))
            sys.stdout.write(f'\r{desc}: |{bar}| {pct:.1%}')
        else:
            sys.stdout.write(f'\r{desc}: {count} items')
        sys.stdout.flush()
    try:
        for item in iterable:
            yield item
            update()
    finally:
        print()

# архивирует файлы
def compress(source: str, target: str, benchmark: bool):
    src = Path(source)
    if not src.exists():
        print(f"Ошибка: Путь {source} не найден.", file=sys.stderr)
        sys.exit(1)
    
    compression = get_compression(target)
    start = time.time()
    target = normalize_archive_name(target)

    # Собираем файлы
    if src.is_file():
        files = [src]
        base = src.parent
    else:
        files = [f for f in src.rglob('*') if f.is_file()]
        base = src.parent
    
    if compression == 'zstd':
        if len(files) == 1:
            with open(files[0], 'rb') as f_in:
                with zstd.open(target, 'wb') as f_out:
                    while True:
                        chunk = f_in.read(1024 * 1024)
                        if not chunk:
                            break
                        f_out.write(chunk)
        else:
            with zstd.open(target, 'wb') as f_out:
                with tarfile.open(fileobj=f_out, mode='w|') as tar:
                    for file in progress_bar(files, desc="Архивация"):
                        tar.add(file, arcname=file.relative_to(base))
    elif compression == 'bz2':
        with bz2.BZ2File(target, 'wb') as f_out:
            with tarfile.open(fileobj=f_out, mode='w|') as tar:
                for file in progress_bar(files, desc="Архивация"):
                    tar.add(file, arcname=file.relative_to(base))
    
    end = time.time() - start
    if benchmark:
        print(f"Архивация длилась {end:.2f} секунд.")

# разархивирует файлы
def extract(archive_path: str, output_dir: str, benchmark: bool):
    archive_path = normalize_archive_name(archive_path)
    if not Path(archive_path).exists():
        print(f"Ошибка: Архив {archive_path} не найден.", file=sys.stderr)
        sys.exit(1)
    
    compression = get_compression(archive_path)
    start = time.time()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if compression == 'zstd':
        with tarfile.open(archive_path, 'r:zst') as tar:
            members = tar.getmembers()
            for member in progress_bar(members, desc="Извлечение"):
                tar.extract(member, path=out_dir)
    elif compression == 'bz2':
        with tarfile.open(archive_path, 'r:bz2') as tar:
            members = tar.getmembers()
            for member in progress_bar(members, desc="Извлечение"):
                tar.extract(member, path=out_dir)
    
    end = time.time() - start
    if benchmark:
        print(f"Разархивация длилась {end:.2f} секунд.")

def main():
    parcer = argparse.ArgumentParser(
        description="Заархивировать/разархивировать файлы формата .tar.zst или .tar.bz2"
    )
    parcer.add_argument("action", choices=['archive', 'extract'], help="Действие для выполнения")
    parcer.add_argument("source", help="Источник: file/dir(archive) | .tar.zst/.tar.bz2, .tar опционально (extract)")
    parcer.add_argument("target", help="Целевой файл: .tar.zst/.tar.bz2, .tar опционально(archive) | директория(extract)")
    parcer.add_argument("--benchmark", action='store_true', help="Показать время выполнения архивации/разархивации")

    args = parcer.parse_args()
    if args.action == 'archive':
        compress(args.source, args.target, args.benchmark)
    else:
        extract(args.source, args.target, args.benchmark)

if __name__ == "__main__":
    main()
