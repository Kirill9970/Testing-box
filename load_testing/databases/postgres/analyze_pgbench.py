import sys
import re
from pathlib import Path
from datetime import datetime

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчет pgbench</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
        h1 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 60%; margin: 20px 0; background: #fff; }}
        th, td {{ border: 1px solid #ccc; padding: 10px 16px; text-align: left; }}
        th {{ background: #e9ecef; }}
        .desc {{ margin-top: 30px; color: #555; }}
    </style>
</head>
<body>
    <h1>Результаты pgbench</h1>
    <table>
        <tr><th>Параметр</th><th>Значение</th></tr>
        <tr><td>Количество клиентов</td><td>{clients}</td></tr>
        <tr><td>Длительность теста (сек)</td><td>{duration}</td></tr>
        <tr><td>Масштаб (scale)</td><td>{scale}</td></tr>
        <tr><td>TPS (транзакций/сек)</td><td>{tps}</td></tr>
        <tr><td>Средняя задержка (мс)</td><td>{latency}</td></tr>
        <tr><td>Обработано транзакций</td><td>{transactions}</td></tr>
        <tr><td>Неудачных транзакций</td><td>{failed}</td></tr>
    </table>
    <div class="desc">
        <h2>Описание</h2>
        <ul>
            <li><b>TPS</b> — количество успешно обработанных транзакций в секунду. Чем выше, тем лучше производительность.</li>
            <li><b>Средняя задержка</b> — среднее время выполнения одной транзакции. Чем меньше, тем лучше.</li>
            <li><b>Количество клиентов</b> — сколько одновременных подключений имитировалось.</li>
            <li><b>Масштаб</b> — размер тестовой базы (чем больше, тем тяжелее нагрузка).</li>
        </ul>
    </div>
</body>
</html>
'''

def parse_pgbench_output(text):
    def search(pattern, default='-'):
        m = re.search(pattern, text, re.MULTILINE)
        return m.group(1) if m else default

    return {
        'clients': search(r'number of clients: (\d+)'),
        'duration': search(r'duration: (\d+) s'),
        'scale': search(r'scaling factor: (\d+)'),
        'tps': search(r'tps = ([\d\.]+)', '-'),
        'latency': search(r'latency average = ([\d\.]+) ms', '-'),
        'transactions': search(r'number of transactions actually processed: (\d+)'),
        'failed': search(r'number of failed transactions: (\d+)'),
    }

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 analyze_pgbench.py <pgbench_output.txt>')
        sys.exit(1)
    input_path = Path(sys.argv[1])
    # Абсолютный путь к reports/load/postgres/pgbench_report_<datetime>.html относительно корня проекта
    project_root = Path(__file__).resolve().parents[3]
    dt_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = project_root / 'reports' / 'load' / 'postgres' / f'pgbench_report_{dt_str}.html'
    with open(input_path, encoding='utf-8') as f:
        text = f.read()
    data = parse_pgbench_output(text)
    html = HTML_TEMPLATE.format(**data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'HTML-отчет сгенерирован: {output_path}')

if __name__ == '__main__':
    main() 