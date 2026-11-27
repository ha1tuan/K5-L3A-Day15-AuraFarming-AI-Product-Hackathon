FROM python:3.11-slim
WORKDIR /app

# Cài thư viện từ cả file gốc và file của backend
COPY requirements.txt /tmp/req-root.txt
COPY codebase/backend/requirements.txt /tmp/req-be.txt
RUN pip install --no-cache-dir -r /tmp/req-root.txt -r /tmp/req-be.txt

# Copy toàn bộ code dự án để backend gọi được agent.py, ai.py, tools.py, tracing.py
COPY . .

WORKDIR /app/codebase/backend
ENV PYTHONPATH=/app:/app/codebase:/app/codebase/backend/src

RUN mkdir -p /app/var /app/traces
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]