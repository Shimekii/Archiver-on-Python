# Для архивации в некоторую директорию(dir) помещаются файлы, которые нужно заархивировать

python archiver.py archive <директория> <имя итого файла> [--benchmark]

Имя файла можно указывать как с .tar, так и без

# Для разархивации. Имя файла также указывается в двух форматах. С .tar и без

python archiver.py extract <путь_до_архива> <путь_куда_разархивировать> [--benchmark]

# Заархивировать файлы из папки dir в архив bz2Files.tar.bz2 с таймером

python archiver.py archive dir bz2Files.bz2 --benchmark

# Разархивировать файлы из архива zstFiles.tar.zst в папку zstDir с таймером

python archiver.py extract zstFiles.tar.zst zstDir --benchmark