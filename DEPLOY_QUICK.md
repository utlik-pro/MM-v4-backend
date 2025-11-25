# 🚀 Быстрый старт: Деплой на Render.com

## За 5 минут

### 1️⃣ Push в GitHub
```bash
git add render.yaml .env.example .gitignore DEPLOY.md
git commit -m "Add Render.com deployment config"
git push origin main
```

### 2️⃣ Создайте Cron Job на Render

1. Откройте [render.com](https://render.com) → **New + → Cron Job**
2. Подключите репозиторий `MM-v4-backend`
3. Render автоматически обнаружит `render.yaml`

### 3️⃣ Добавьте секреты

В **Environment** вкладке добавьте:

```
ELEVENLABS_API_KEY = sk_16f32b46d79b58dac03f2dba0f666a95bd2d26507553840c
ELEVENLABS_AGENT_ID = agent_8901k4s5hkbkf7gsf1tk5r0a4g8t
```

### 4️⃣ Запустите

Нажмите **"Manual Deploy"** для первого запуска.

---

## ✅ Готово!

Теперь пайплайн работает автоматически каждый час:
```
bir.by → обработка → ElevenLabs KB → Agent (810 квартир)
```

**Стоимость:** $0/месяц

---

📖 **Подробная инструкция:** [DEPLOY.md](./DEPLOY.md)
