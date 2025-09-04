FROM python:3.12-slim

WORKDIR /app

# Создаем пользователя и группы
RUN groupadd -r chromeuser && useradd -r -g chromeuser -G audio,video chromeuser && \
    mkdir -p /home/chromeuser && chown -R chromeuser:chromeuser /home/chromeuser

# Обновляем и устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg \
    libpq-dev \
    gcc \
    unzip \
    curl \
    xvfb && \
    # Устанавливаем Google Chrome (современный способ без apt-key)
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    # Чистим кэш
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем ChromeDriver (совместимый с установленной версией Chrome)
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    echo "Устанавливаем ChromeDriver для версии Chrome: $CHROME_VERSION" && \
    \
    # Скачиваем совместимый ChromeDriver
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -q /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 && \
    \
    # Проверяем установку
    echo "Chrome version: $(google-chrome --version)" && \
    echo "ChromeDriver version: $(chromedriver --version)"

# Создаем необходимые директории с правильными правами ДО переключения пользователя
RUN mkdir -p /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix && \
    chown root:root /tmp/.X11-unix && \
    \
    mkdir -p /tmp/runtime-chromeuser && \
    chown -R chromeuser:chromeuser /tmp/runtime-chromeuser && \
    chmod 0700 /tmp/runtime-chromeuser

# Настраиваем переменные окружения
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV PATH="/usr/local/bin:${PATH}"
ENV HEADLESS=true
ENV NO_SANDBOX=true
ENV DISABLE_DEV_SHM_USAGE=true
ENV DISPLAY=:99
ENV XDG_RUNTIME_DIR=/tmp/runtime-chromeuser
ENV HOME=/tmp

# Устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Меняем владельца файлов приложения
RUN chown -R chromeuser:chromeuser /app

# Переключаемся на пользователя chromeuser
USER chromeuser

# Запускаем приложение БЕЗ Xvfb (используем --headless режим)
CMD ["sh", "-c", "python init_db.py && python telegram_bot.py"]