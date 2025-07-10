#!/bin/bash
set -e

# Загрузка переменных из .env
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Файл $ENV_FILE не найден!"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a


# Проверка наличия docker
if ! command -v docker &> /dev/null; then
  echo "Docker не найден. Установите его."
  exit 1
fi

# Проверка обязательных переменных
REQUIRED_VARS=(RABBITMQ_HOST RABBITMQ_PORT RABBITMQ_USER RABBITMQ_PASSWORD RABBITMQ_VHOST RABBITMQ_QUEUE RABBITMQ_MESSAGES RABBITMQ_MESSAGE_SIZE RABBITMQ_PRODUCERS RABBITMQ_CONSUMERS)
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Ошибка: переменная $var не задана в $ENV_FILE"
    exit 1
  fi
done

# Корректная обработка vhost для AMQP URI
if [ "$RABBITMQ_VHOST" = "/" ]; then
  VHOST_PATH=""
else
  VHOST_PATH="/$RABBITMQ_VHOST"
fi
AMQP_URI="amqp://$RABBITMQ_USER:$RABBITMQ_PASSWORD@$RABBITMQ_HOST:$RABBITMQ_PORT$VHOST_PATH"

echo "DEBUG: USER=$RABBITMQ_USER, PASS=$RABBITMQ_PASSWORD, HOST=$RABBITMQ_HOST, PORT=$RABBITMQ_PORT, VHOST=$RABBITMQ_VHOST"
echo "DEBUG: AMQP_URI=$AMQP_URI"

# Запуск теста производительности с помощью rabbitmq-perf-test (официальный образ)
echo "Запуск теста производительности RabbitMQ..."
docker run --rm --network=host pivotalrabbitmq/perf-test:latest \
  --uri "$AMQP_URI" \
  --queue $RABBITMQ_QUEUE \
  --producers $RABBITMQ_PRODUCERS \
  --consumers $RABBITMQ_CONSUMERS \
  --pmessages $RABBITMQ_MESSAGES \
  --size $RABBITMQ_MESSAGE_SIZE \
  --json-body > rabbitmq_perf_output.txt

echo "Тест завершен. Результаты сохранены в rabbitmq_perf_output.txt"
