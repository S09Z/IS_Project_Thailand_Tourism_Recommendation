FROM python:3.12-slim

WORKDIR /app

COPY app/frontend/frontend_requirements.txt .
COPY .streamlit /app/.streamlit

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r frontend_requirements.txt

COPY app/frontend/ ./ 
COPY app/frontend/data /app/data

EXPOSE 8080
ENV PORT=8080

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
