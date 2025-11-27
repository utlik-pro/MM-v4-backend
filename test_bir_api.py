import requests

try:
    r = requests.get('https://bir.by/ai/json_ai.php', timeout=30)
    print("HTTP status:", r.status_code)
    print("First 500 characters:", r.text[:500])
except Exception as e:
    print("Ошибка:", e)