FROM python:3.12-slim AS builder

WORKDIR /install
COPY frontend_requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r frontend_requirements.txt && \
    pip install --no-cache-dir streamlit

# Copy only necessary app files
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app source
COPY .streamlit /.streamlit
COPY app.py .
COPY content_filtering.py .

EXPOSE 8080
ENV PORT=8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
