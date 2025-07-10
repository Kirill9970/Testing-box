# Тестирование производительности PostgreSQL с помощью pgbench (Docker)

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и укажите параметры вашей локальной базы данных:
   ```bash
   cp .env.example .env
   # отредактируйте .env
   ```
2. Установите Docker, если он не установлен.
3. Запустите тест:
   ```bash
   bash run_pgbench.sh | tee pgbench_output.txt
   ```

## Как это работает
- Скрипт запускает pgbench внутри официального контейнера postgres (только pgbench, без сервера базы).
- Контейнер использует сеть host (`--network=host`), чтобы видеть вашу локальную базу на Linux.
- Все параметры подключения берутся из .env.

## Параметры .env
- POSTGRES_HOST — адрес сервера PostgreSQL (обычно localhost)
- POSTGRES_PORT — порт PostgreSQL (обычно 5432)
- POSTGRES_USER — пользователь
- POSTGRES_PASSWORD — пароль
- POSTGRES_DB — база данных
- PGBENCH_SCALE — масштаб теста (количество строк)
- PGBENCH_CLIENTS — количество клиентов
- PGBENCH_TIME — время теста (сек)

## Требования
- Локально установленный PostgreSQL (сервер)
- Docker

## Примечания
- Скрипт рассчитан на Linux. На Mac/Windows потребуется другой способ проброса сети (host.docker.internal).
