# Imagen oficial de Microsoft con Python y Playwright preinstalados
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Comando que se ejecutará al iniciar el contenedor
CMD ["python", "main.py"]
