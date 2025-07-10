# Тестирование производительности RabbitMQ с помощью perf-test

## Быстрый старт

1. **Настройте параметры подключения**
   - Скопируйте и отредактируйте `.env`:
     ```
     RABBITMQ_HOST=localhost
     RABBITMQ_PORT=5672
     RABBITMQ_USER=guest
     RABBITMQ_PASSWORD=guest
     RABBITMQ_VHOST=/
     RABBITMQ_QUEUE=test_queue
     RABBITMQ_MESSAGES=10000
     RABBITMQ_MESSAGE_SIZE=256
     RABBITMQ_PRODUCERS=10
     RABBITMQ_CONSUMERS=10
     ```

2. **Запустите тест**
   ```bash
   bash run_rabbitmq_perf.sh | tee rabbitmq_perf_output.txt
   ```
   - Скрипт использует официальный Docker-образ `pivotalrabbitmq/perf-test`.
   - Результаты теста выводятся в консоль и сохраняются в файл `rabbitmq_perf_output.txt`.

3. **Сгенерируйте HTML-отчет**
   ```bash
   python3 analyze_rabbitmq_perf.py rabbitmq_perf_output.txt
   ```
   - Отчет будет создан в директории `reports/load/rabbitmq/` с уникальным именем по дате и времени.
   - Откройте отчет в браузере для наглядного анализа.

## Описание параметров .env
- `RABBITMQ_HOST` — адрес RabbitMQ-сервера
- `RABBITMQ_PORT` — порт (обычно 5672)
- `RABBITMQ_USER` / `RABBITMQ_PASSWORD` — логин и пароль
- `RABBITMQ_VHOST` — виртуальный хост (по умолчанию `/`)
- `RABBITMQ_QUEUE` — имя очереди для теста
- `RABBITMQ_MESSAGES` — сколько сообщений отправит каждый продюсер
- `RABBITMQ_MESSAGE_SIZE` — размер одного сообщения в байтах
- `RABBITMQ_PRODUCERS` — количество параллельных продюсеров
- `RABBITMQ_CONSUMERS` — количество параллельных консьюмеров

## Как читать отчет
- **TPS (publish/consume)** — сколько сообщений в секунду отправлялось/получалось. Чем выше, тем лучше.
- **Задержка** — время доставки сообщения от продюсера к консьюмеру. Чем меньше, тем лучше. 1000 мкс = 1 мс.
- **Потери сообщений** — если получено меньше, чем отправлено, это плохо (сообщения теряются!).
- **График** — показывает динамику TPS и задержек по времени.

## Советы по анализу
- <span style="color: #006600; font-weight: bold;">Нет потерь сообщений</span> — система работает корректно.
- <span style="color: #b30000; font-weight: bold;">Есть потери сообщений</span> — проверьте настройки брокера, очереди, нагрузку на сеть и память.
- Если задержка &gt; 1 000 000 мкс (1 сек) — это очень много, стоит оптимизировать систему.
- Сравнивайте TPS и задержки при разном количестве продюсеров/консьюмеров для поиска оптимума.

## Требования
- Docker
- Python 3.x (для анализа и генерации отчета)

## Пример запуска
```bash
bash run_rabbitmq_perf.sh | tee rabbitmq_perf_output.txt
python3 analyze_rabbitmq_perf.py rabbitmq_perf_output.txt
# Откройте отчет в reports/load/rabbitmq/...
```
