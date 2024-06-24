# Використовуємо базовий образ Windows Server Core 2019
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# Встановлюємо .NET Framework 4.8
RUN powershell -Command \
    $ErrorActionPreference = 'Stop'; \
    Invoke-WebRequest -Uri https://download.visualstudio.microsoft.com/download/pr/2d6bb6b2-226a-4baa-bdec-798822606ff1/8494001c276a4b96804cde7829c04d7f/ndp48-x86-x64-allos-enu.exe -OutFile ndp48-x86-x64-allos-enu.exe ; \
    Start-Process ndp48-x86-x64-allos-enu.exe -ArgumentList '/quiet /norestart' -Wait ; \
    Remove-Item ndp48-x86-x64-allos-enu.exe -Force

# Перезавантажуємо контейнер для завершення встановлення .NET Framework 4.8
SHELL ["cmd", "/S", "/C"]
RUN powershell -Command "Restart-Computer -Force"

# Встановлюємо Python
RUN powershell -Command \
    $ErrorActionPreference = 'Stop'; \
    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe -OutFile python-3.11.0-amd64.exe ; \
    Start-Process python-3.11.0-amd64.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait ; \
    Remove-Item python-3.11.0-amd64.exe -Force

# Встановлюємо Chocolatey для подальшого встановлення ffmpeg
RUN powershell -Command \
    Set-ExecutionPolicy Bypass -Scope Process -Force; \
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; \
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Використовуємо Chocolatey для встановлення ffmpeg
RUN choco install ffmpeg -y

# Додаємо файли вашого проекту в контейнер
WORKDIR /app
COPY . .

# Встановлюємо залежності Python
RUN pip install --no-cache-dir -r requirements.txt

# Запускаємо ваш основний скрипт (змініть start.py на ваш основний скрипт)
CMD ["python", "start.py"]
