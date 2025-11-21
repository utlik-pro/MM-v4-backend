#!/usr/bin/env python3
import os, requests
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
agent_id = os.getenv('ELEVENLABS_AGENT_ID')

# 5 документов для теста (чтобы быстрее)
test_ids = [
    'qXtJqqEp0ZkcmJX4gc6v',  # 19-Yuzhnaya-Evropa
    'YKvNKCYwODU8AwJI7Muc',  # 26-Afrika
    'kL3zNCHbhtptIq25QNPm',  # 04-baza-znaniy
    'rQciMWgeCGRKhgheCzuJ',  # 00-obschie-svedeniya
    'wKmcKNykVwd3TFIxmQdc',  # 21-Zapadnyy
]

url = f'https://api.elevenlabs.io/v1/convai/agents/{agent_id}'
headers = {'xi-api-key': api_key, 'Content-Type': 'application/json'}

print("=" * 60)
print("Тестирование разных форматов payload")
print("=" * 60)

# Формат 1: {'ids': [...]}
print("\n1️⃣  Формат: conversation_config.knowledge_base = {'ids': [...]}")
payload1 = {
    'conversation_config': {
        'knowledge_base': {'ids': test_ids}
    }
}

try:
    r = requests.patch(url, headers=headers, json=payload1, timeout=30)
    print(f"   Статус: {r.status_code}")
    if r.status_code == 200:
        print("   ✅ УСПЕХ!")
    else:
        print(f"   ❌ Ошибка: {r.text[:150]}")
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:100]}")

# Формат 2: просто список
print("\n2️⃣  Формат: conversation_config.knowledge_base = [...]")
payload2 = {
    'conversation_config': {
        'knowledge_base': test_ids
    }
}

try:
    r = requests.patch(url, headers=headers, json=payload2, timeout=30)
    print(f"   Статус: {r.status_code}")
    if r.status_code == 200:
        print("   ✅ УСПЕХ!")
    else:
        print(f"   ❌ Ошибка: {r.text[:150]}")
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:100]}")

print("\n" + "=" * 60)
