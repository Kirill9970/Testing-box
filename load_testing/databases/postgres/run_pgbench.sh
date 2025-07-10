#!/bin/bash
set -e

# Загрузка переменных из .env (работает и с sudo)
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
  ENV_FILE=".env.example"
fi

export $(grep -v '^#' "$ENV_FILE" | xargs)

# Проверка наличия docker
if ! command -v docker &> /dev/null; then
  echo "Docker не найден. Установите его."
  exit 1
fi

# Проверка обязательных переменных
REQUIRED_VARS=(POSTGRES_HOST POSTGRES_PORT POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB PGBENCH_SCALE PGBENCH_CLIENTS PGBENCH_TIME)
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Ошибка: переменная $var не задана в $ENV_FILE"
    exit 1
  fi
done

# Экспорт пароля для pgbench
export PGPASSWORD="$POSTGRES_PASSWORD"

# Инициализация тестовой базы (если нужно)
echo "Инициализация базы для pgbench..."
sudo -E docker run --rm --network=host \
  -e PGPASSWORD="$POSTGRES_PASSWORD" \
  postgres:15 \
  pgbench -i -s "$PGBENCH_SCALE" -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB"

# Запуск теста
echo "Запуск pgbench..."
sudo -E docker run --rm --network=host \
  -e PGPASSWORD="$POSTGRES_PASSWORD" \
  postgres:15 \
  pgbench -c "$PGBENCH_CLIENTS" -T "$PGBENCH_TIME" -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB"
