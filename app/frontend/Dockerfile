FROM python:3.12-slim

WORKDIR /app

COPY app/frontend/frontend_requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r frontend_requirements.txt

COPY app/frontend/ ./
COPY .streamlit /app/.streamlit

RUN mkdir -p /app/inputs
COPY app/frontend/inputs /app/inputs

EXPOSE 8080
ENV PORT=8080

CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
