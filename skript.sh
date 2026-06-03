#!/data/data/com.termux/files/usr/bin/bash

echo "[1/7] Обновление Termux..."
pkg update -y && pkg upgrade -y

echo "[2/7] Установка зависимостей..."
pkg install -y proot-distro wget curl git python

echo "[3/7] Установка Ubuntu..."
proot-distro install ubuntu

echo "[4/7] Настройка Ubuntu..."

cat > $HOME/setup_ubuntu.sh << 'EOF'
#!/bin/bash

apt update
apt upgrade -y

apt install -y \
curl \
wget \
git \
python3 \
python3-pip \
python3-venv \
build-essential

echo "[+] Установка Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

mkdir -p /opt/ollama-web
cd /opt/ollama-web

echo "[+] Загрузка app.py..."
wget -O app.py https://raw.githubusercontent.com/vitoptg/ollama-on-android/main/app.py

pip3 install --break-system-packages \
flask \
requests

cat > /usr/local/bin/start-ollama-web << 'LAUNCH'
#!/bin/bash

ollama serve &
sleep 5

cd /opt/ollama-web
python3 app.py
LAUNCH

chmod +x /usr/local/bin/start-ollama-web

echo
echo "===================================="
echo "Установка завершена"
echo
echo "Запуск:"
echo "proot-distro login ubuntu"
echo "start-ollama-web"
echo "===================================="
EOF

chmod +x $HOME/setup_ubuntu.sh

echo "[5/7] Настройка Ubuntu..."
proot-distro login ubuntu -- bash /root/../data/data/com.termux/files/home/setup_ubuntu.sh

echo
echo "===================================="
echo "ГОТОВО"
echo
echo "Запуск Ubuntu:"
echo "proot-distro login ubuntu"
echo
echo "Запуск Ollama + WebUI:"
echo "start-ollama-web"
echo "===================================="
