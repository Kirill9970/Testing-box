import sys
import re
from pathlib import Path
from datetime import datetime
import json

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчет RabbitMQ PerfTest</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
        h1 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 70%; margin: 20px 0; background: #fff; }}
        th, td {{ border: 1px solid #ccc; padding: 10px 16px; text-align: left; }}
        th {{ background: #e9ecef; }}
        .desc {{ margin-top: 30px; color: #555; }}
        .warn {{ color: #b30000; font-weight: bold; }}
        .ok {{ color: #006600; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Результаты RabbitMQ PerfTest</h1>
    <table>
        <tr><th>Параметр</th><th>Значение</th></tr>
        <tr><td>Продюсеров</td><td>{producers}</td></tr>
        <tr><td>Консьюмеров</td><td>{consumers}</td></tr>
        <tr><td>Всего отправлено сообщений</td><td>{total_sent}</td></tr>
        <tr><td>Всего получено сообщений</td><td>{total_received}</td></tr>
        <tr><td>Потери сообщений</td><td class="{loss_class}">{loss_info}</td></tr>
        <tr><td>Средний TPS (publish)</td><td>{avg_publish_rate} msg/s</td></tr>
        <tr><td>Максимальный TPS (publish)</td><td>{max_publish_rate} msg/s</td></tr>
        <tr><td>Средний TPS (consume)</td><td>{avg_consume_rate} msg/s</td></tr>
        <tr><td>Максимальный TPS (consume)</td><td>{max_consume_rate} msg/s</td></tr>
        <tr><td>Медианная задержка (мкс)</td><td>{median_latency}</td></tr>
        <tr><td>95-й перцентиль задержки (мкс)</td><td>{p95_latency}</td></tr>
    </table>
    <div class="desc">
        <h2>Как читать этот отчет</h2>
        <ul>
            <li><b>TPS (publish/consume)</b> — сколько сообщений в секунду отправлялось/получалось. Чем выше, тем лучше.</li>
            <li><b>Задержка</b> — время доставки сообщения от продюсера к консьюмеру. Чем меньше, тем лучше. Микросекунды (мкс): 1000 мкс = 1 мс.</li>
            <li><b>Потери сообщений</b> — если получено меньше, чем отправлено, это плохо (сообщения теряются!).</li>
        </ul>
        <h2>Советы по анализу</h2>
        <ul>
            <li><span class="ok">Нет потерь сообщений</span> — система работает корректно.</li>
            <li><span class="warn">Есть потери сообщений</span> — проверьте настройки брокера, очереди, нагрузку на сеть и память.</li>
            <li>Если задержка &gt; 1 000 000 мкс (1 сек) — это очень много, стоит оптимизировать систему.</li>
            <li>Сравнивайте TPS и задержки при разном количестве продюсеров/консьюмеров для поиска оптимума.</li>
        </ul>
    </div>
    <h2>Динамика TPS и задержки по времени</h2>
    <canvas id="tpsChart" width="800" height="300"></canvas>
    <script>
    const labels = {labels};
    const sent = {sent};
    const received = {received};
    const latency = {latency};
    const median = {median};
    const p95 = {p95};
    const data = {{
        labels: labels,
        datasets: [
            {{ label: 'Sent msg/s', data: sent, borderColor: 'blue', fill: false, yAxisID: 'y' }},
            {{ label: 'Received msg/s', data: received, borderColor: 'green', fill: false, yAxisID: 'y' }},
            {{ label: 'Median latency (мкс)', data: median, borderColor: 'orange', fill: false, yAxisID: 'y1' }},
            {{ label: '95th latency (мкс)', data: p95, borderColor: 'red', fill: false, yAxisID: 'y1' }}
        ]
    }};
    const config = {{{{
        type: 'line',
        data: data,
        options: {{{{
            interaction: {{{{ mode: 'index', intersect: false }}}},
            stacked: false,
            plugins: {{{{ legend: {{{{ position: 'top' }}}} }}}},
            scales: {{{{
                y: {{{{ type: 'linear', display: true, position: 'left', title: {{{{ display: true, text: 'msg/s' }}}} }}}},
                y1: {{{{ type: 'linear', display: true, position: 'right', title: {{{{ display: true, text: 'latency (мкс)' }}}}, grid: {{{{ drawOnChartArea: false }}}} }}}}
            }}}}
        }}}}
    }}}};
    new Chart(document.getElementById('tpsChart'), config);
    </script>
</body>
</html>
'''

def parse_perf_text(text):
    # Считаем продюсеров и консьюмеров
    producers = len(re.findall(r'starting producer #[0-9]+\b', text))
    consumers = len(re.findall(r'starting consumer #[0-9]+\b', text))
    # Парсим динамику по времени
    time_points = []
    sent_points = []
    received_points = []
    median_latency = []
    p95_latency = []
    for m in re.finditer(r'time ([\d\.]+) s, sent: (\d+) msg/s, received: (\d+) msg/s, min/median/75th/95th/99th consumer latency: [\d]+/(\d+)/(\d+)/(\d+)/(\d+) µs', text):
        t = float(m.group(1))
        sent = int(m.group(2))
        received = int(m.group(3))
        median = int(m.group(4))
        p95 = int(m.group(6))
        time_points.append(f"{t:.1f}s")
        sent_points.append(sent)
        received_points.append(received)
        median_latency.append(median)
        p95_latency.append(p95)
    # Итоговые значения
    total_sent = sum(sent_points)
    total_received = sum(received_points)
    max_publish_rate = max(sent_points) if sent_points else 0
    max_consume_rate = max(received_points) if received_points else 0
    avg_publish_rate = int(round(sum(sent_points)/len(sent_points))) if sent_points else 0
    avg_consume_rate = int(round(sum(received_points)/len(received_points))) if received_points else 0
    # Потери
    loss = total_sent - total_received
    if loss == 0:
        loss_info = 'Нет потерь'
        loss_class = 'ok'
    else:
        loss_info = f'Потеряно {loss} сообщений!'
        loss_class = 'warn'
    # Итоговые latency (по последней строке)
    latency_match = re.search(r'consumer latency min/median/75th/95th/99th (\d+)/(\d+)/(\d+)/(\d+)/(\d+)', text)
    median_latency_final = latency_match.group(2) if latency_match else '-'
    p95_latency_final = latency_match.group(4) if latency_match else '-'
    return {
        'producers': producers,
        'consumers': consumers,
        'total_sent': total_sent,
        'total_received': total_received,
        'loss_info': loss_info,
        'loss_class': loss_class,
        'avg_publish_rate': avg_publish_rate,
        'max_publish_rate': max_publish_rate,
        'avg_consume_rate': avg_consume_rate,
        'max_consume_rate': max_consume_rate,
        'median_latency': median_latency_final,
        'p95_latency': p95_latency_final,
        'labels': json.dumps(time_points, ensure_ascii=False),
        'sent': json.dumps(sent_points),
        'received': json.dumps(received_points),
        'latency': json.dumps(median_latency),
        'median': json.dumps(median_latency),
        'p95': json.dumps(p95_latency),
    }

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 analyze_rabbitmq_perf.py <rabbitmq_perf_output.txt>')
        sys.exit(1)
    input_path = Path(sys.argv[1])
    dt_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = Path(__file__).resolve().parents[3] / 'reports' / 'load' / 'rabbitmq' / f'rabbitmq_perf_report_{dt_str}.html'
    with open(input_path, encoding='utf-8') as f:
        text = f.read()
    metrics = parse_perf_text(text)
    html = HTML_TEMPLATE.format(**metrics)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'HTML-отчет сгенерирован: {output_path}')

if __name__ == '__main__':
    main()
