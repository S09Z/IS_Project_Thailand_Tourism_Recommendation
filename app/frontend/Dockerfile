FROM python:3.12-slim

WORKDIR /app

# Copy the requirements file from the project root
COPY frontend_requirements.txt .
COPY .streamlit /app/.streamlit

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r frontend_requirements.txt

# Copy the frontend application code
COPY app/frontend/ ./ 
COPY ../../app/frontend/data /app/data   


# Expose the application port
EXPOSE 8080

ENV PORT=8080

# Command to run the application
CMD ["sh", "-c", "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"]

