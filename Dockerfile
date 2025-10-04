# ===== BASE IMAGE =====
FROM python:3.12.11

# ===== INSTALL SYSTEM DEPENDENCIES =====
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    shared-mime-info \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ===== WORKDIR =====
WORKDIR /app

# ===== COPY FILES =====
COPY . .

# ===== INSTALL PYTHON DEPENDENCIES =====
RUN pip install --no-cache-dir -r requirements.txt

# ===== EXPOSE PORT =====
EXPOSE 8000

# ===== COMMAND =====
CMD ["uvicorn", "main:app/main"]
