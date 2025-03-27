FROM python:3.12-slim                    
WORKDIR /app                             

# 📦 COPY requirements แล้ว install
COPY ../../frontend_requirements.txt .   
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r frontend_requirements.txt

# 📁 COPY source code
COPY ../../app/frontend/ ./             
COPY ../../app/frontend/data /app/data   

EXPOSE 8080

ENV PORT=8080

CMD sh -c "streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0"
