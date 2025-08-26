# Развертывание HR приложения на сервере

## Установка на сервер

### Ubuntu/Debian:
```bash
# 1. Обновляем систему
sudo apt update && sudo apt upgrade -y

# 2. Устанавливаем Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# 3. Клонируем проект
git clone git@github.com:retuam/hr.git
cd hr

# 4. Создаем виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# 5. Устанавливаем зависимости
pip install -r requirements.txt

# 6. Настраиваем переменные окружения
cp .env.production .env
nano .env  # Заполните реальными значениями

# 7. Загружаем credentials.json от Google Cloud в корень проекта

# 8. Запускаем приложение
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

### Systemd сервис (для автозапуска)

Создайте файл `/etc/systemd/system/hr-app.service`:

```ini
[Unit]
Description=HR Payroll Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/hr
Environment=PATH=/path/to/hr/venv/bin
ExecStart=/path/to/hr/venv/bin/streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Активация сервиса:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hr-app
sudo systemctl start hr-app
sudo systemctl status hr-app
```

## Настройка Nginx (опционально)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Безопасность

1. **Файрвол:**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. **SSL сертификат (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Мониторинг

Проверка логов:
```bash
# Docker
docker-compose logs -f hr-app

# Systemd
sudo journalctl -u hr-app -f
```

## Обновление приложения

```bash
# Docker
git pull
docker-compose down
docker-compose build
docker-compose up -d

# Прямая установка
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart hr-app
```

## Требования к серверу

- **CPU:** 2+ ядра
- **RAM:** 4+ GB
- **Диск:** 20+ GB свободного места
- **ОС:** Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **Порты:** 8501 (или 80/443 через Nginx)
