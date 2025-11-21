#!/usr/bin/env python3
"""
Веб-интерфейс для мониторинга системы автообновления BIR.BY
"""

import os
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from data_updater import DataUpdater

app = Flask(__name__)
updater = DataUpdater()

# HTML шаблон для веб-интерфейса
TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Мониторинг BIR.BY Auto-Updater</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center; }
        .card { background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .status-card { background: white; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }
        .status-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
        .status-label { color: #666; font-size: 0.9em; }
        .status-success { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-error { color: #dc3545; }
        .btn { background: #667eea; color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; margin: 5px; font-size: 16px; transition: all 0.3s; }
        .btn:hover { background: #5a6fd8; transform: translateY(-2px); }
        .btn-success { background: #28a745; }
        .btn-warning { background: #ffc107; color: #000; }
        .btn-danger { background: #dc3545; }
        .log-container { background: #1e1e1e; color: #fff; padding: 20px; border-radius: 10px; font-family: 'Courier New', monospace; max-height: 400px; overflow-y: auto; }
        .config-form { display: grid; gap: 15px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .quarters-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .quarter-card { border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; text-align: center; }
        .loading { text-align: center; padding: 50px; color: #666; }
        .timestamp { font-size: 0.8em; color: #999; }
        .refresh-btn { position: fixed; bottom: 20px; right: 20px; background: #28a745; width: 60px; height: 60px; border-radius: 50%; border: none; color: white; font-size: 20px; cursor: pointer; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏘️ BIR.BY Auto-Updater</h1>
            <p>Система автоматического обновления данных недвижимости</p>
            <div class="timestamp">Последнее обновление страницы: <span id="last-refresh">{{ current_time }}</span></div>
        </div>

        <div class="status-grid" id="status-grid">
            <div class="loading">Загрузка данных...</div>
        </div>

        <div class="card">
            <h2>🎛️ Управление</h2>
            <button class="btn btn-success" onclick="forceUpdate()">Принудительное обновление</button>
            <button class="btn btn-warning" onclick="checkChanges()">Проверить изменения</button>
            <button class="btn" onclick="refreshStatus()">Обновить статус</button>
        </div>

        <div class="card">
            <h2>📊 Статистика кварталов</h2>
            <div id="quarters-container">
                <div class="loading">Загрузка статистики...</div>
            </div>
        </div>

        <div class="card">
            <h2>📋 Логи системы</h2>
            <div id="logs-container">
                <div class="log-container">
                    <div class="loading">Загрузка логов...</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>⚙️ Конфигурация</h2>
            <div id="config-container">
                <div class="loading">Загрузка конфигурации...</div>
            </div>
        </div>
    </div>

    <button class="refresh-btn" onclick="refreshAll()" title="Обновить все">🔄</button>

    <script>
        let statusData = {};

        async function fetchStatus() {
            try {
                const response = await fetch('/api/status');
                statusData = await response.json();
                updateStatusGrid();
                updateQuartersStats();
            } catch (error) {
                console.error('Ошибка загрузки статуса:', error);
            }
        }

        function updateStatusGrid() {
            const grid = document.getElementById('status-grid');
            const lastUpdate = statusData.last_update || {};
            const config = statusData.config || {};
            
            grid.innerHTML = `
                <div class="status-card">
                    <div class="status-value status-success">${lastUpdate.total_objects || 0}</div>
                    <div class="status-label">Всего объектов</div>
                </div>
                <div class="status-card">
                    <div class="status-value status-success">${lastUpdate.quarters_count || 0}</div>
                    <div class="status-label">Кварталов</div>
                </div>
                <div class="status-card">
                    <div class="status-value ${lastUpdate.problematic_objects > 0 ? 'status-warning' : 'status-success'}">${lastUpdate.problematic_objects || 0}</div>
                    <div class="status-label">Проблемных объектов</div>
                </div>
                <div class="status-card">
                    <div class="status-value status-success">${config.check_interval_minutes || 60}м</div>
                    <div class="status-label">Интервал проверки</div>
                </div>
                <div class="status-card">
                    <div class="status-value">${lastUpdate.timestamp ? formatDate(lastUpdate.timestamp) : 'Неизвестно'}</div>
                    <div class="status-label">Последнее обновление</div>
                </div>
                <div class="status-card">
                    <div class="status-value ${config.enable_change_detection ? 'status-success' : 'status-warning'}">${config.enable_change_detection ? 'ВКЛ' : 'ВЫКЛ'}</div>
                    <div class="status-label">Детекция изменений</div>
                </div>
            `;
        }

        async function updateQuartersStats() {
            try {
                const response = await fetch('/api/quarters');
                const data = await response.json();
                const container = document.getElementById('quarters-container');
                
                if (data.quarters) {
                    const quartersHtml = Object.entries(data.quarters)
                        .sort(([,a], [,b]) => b.objects_count - a.objects_count)
                        .map(([name, stats]) => `
                            <div class="quarter-card">
                                <h4>${name}</h4>
                                <div style="margin: 10px 0;">
                                    <div><strong>${stats.objects_count}</strong> объектов</div>
                                    <div><strong>${stats.houses_count}</strong> домов</div>
                                </div>
                            </div>
                        `).join('');
                    
                    container.innerHTML = `<div class="quarters-grid">${quartersHtml}</div>`;
                } else {
                    container.innerHTML = '<div class="loading">Нет данных о кварталах</div>';
                }
            } catch (error) {
                console.error('Ошибка загрузки статистики кварталов:', error);
            }
        }

        async function loadLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                const container = document.getElementById('logs-container');
                
                container.innerHTML = `
                    <div class="log-container">
                        ${data.logs ? data.logs.split('\\n').slice(-50).join('<br>') : 'Логи не найдены'}
                    </div>
                `;
            } catch (error) {
                console.error('Ошибка загрузки логов:', error);
            }
        }

        async function loadConfig() {
            try {
                const container = document.getElementById('config-container');
                const config = statusData.config || {};
                
                container.innerHTML = `
                    <div class="config-form">
                        <div class="form-group">
                            <label>Интервал проверки (минуты):</label>
                            <input type="number" value="${config.check_interval_minutes || 60}" id="check_interval">
                        </div>
                        <div class="form-group">
                            <label>Принудительное обновление (часы):</label>
                            <input type="number" value="${config.force_update_hours || 24}" id="force_update_hours">
                        </div>
                        <div class="form-group">
                            <label>Детекция изменений:</label>
                            <select id="change_detection">
                                <option value="true" ${config.enable_change_detection ? 'selected' : ''}>Включено</option>
                                <option value="false" ${!config.enable_change_detection ? 'selected' : ''}>Выключено</option>
                            </select>
                        </div>
                        <button class="btn" onclick="saveConfig()">Сохранить конфигурацию</button>
                    </div>
                `;
            } catch (error) {
                console.error('Ошибка загрузки конфигурации:', error);
            }
        }

        async function forceUpdate() {
            if (!confirm('Запустить принудительное обновление данных?')) return;
            
            try {
                const response = await fetch('/api/force-update', { method: 'POST' });
                const result = await response.json();
                alert(result.message);
                setTimeout(fetchStatus, 2000);
            } catch (error) {
                alert('Ошибка обновления: ' + error.message);
            }
        }

        async function checkChanges() {
            try {
                const response = await fetch('/api/check-changes');
                const result = await response.json();
                alert(`Изменения ${result.changes_detected ? 'обнаружены' : 'не обнаружены'}\\n\\nОбъектов: ${result.data_count}`);
            } catch (error) {
                alert('Ошибка проверки: ' + error.message);
            }
        }

        function refreshStatus() {
            fetchStatus();
        }

        function refreshAll() {
            document.getElementById('last-refresh').textContent = new Date().toLocaleString('ru-RU');
            fetchStatus();
            loadLogs();
        }

        function formatDate(dateString) {
            try {
                return new Date(dateString).toLocaleString('ru-RU');
            } catch {
                return dateString;
            }
        }

        // Автообновление каждые 30 секунд
        setInterval(refreshAll, 30000);

        // Начальная загрузка
        window.onload = () => {
            fetchStatus();
            loadLogs();
            setTimeout(loadConfig, 1000);
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Главная страница"""
    return render_template_string(TEMPLATE, current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/api/status')
def api_status():
    """API: Получить статус системы"""
    try:
        status = updater.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quarters')
def api_quarters():
    """API: Получить статистику кварталов"""
    try:
        stats_file = Path('cache/update_stats.json')
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            return jsonify(stats)
        else:
            return jsonify({'quarters': {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def api_logs():
    """API: Получить логи"""
    try:
        log_file = Path('data_updater.log')
        if log_file.exists():
            logs = log_file.read_text(encoding='utf-8')
            return jsonify({'logs': logs})
        else:
            return jsonify({'logs': 'Логи не найдены'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/force-update', methods=['POST'])
def api_force_update():
    """API: Принудительное обновление"""
    try:
        success = updater.update_data(force=True)
        return jsonify({
            'success': success,
            'message': 'Обновление завершено успешно!' if success else 'Ошибка обновления'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500

@app.route('/api/check-changes')
def api_check_changes():
    """API: Проверить изменения"""
    try:
        changes_detected, change_info = updater.check_for_changes()
        return jsonify(change_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API: Управление конфигурацией"""
    if request.method == 'GET':
        return jsonify(updater.config)
    
    elif request.method == 'POST':
        try:
            new_config = request.json
            updater.config.update(new_config)
            updater._save_config()
            return jsonify({'success': True, 'message': 'Конфигурация сохранена'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500

if __name__ == '__main__':
    print("🌐 Запуск веб-интерфейса мониторинга BIR.BY Auto-Updater")
    print("📡 Доступен по адресу: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)




