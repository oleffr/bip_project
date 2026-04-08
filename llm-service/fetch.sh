# Запускаем контейнер с Python 3.11, монтируем текущую папку
# и скачиваем в неё пакеты нужных версий
docker run --rm -v $(pwd):/app -w /app python:3.11-slim \
pip download -r requirements.txt \
--dest packages \
--index-url https://pypi.org \
--timeout 1000
