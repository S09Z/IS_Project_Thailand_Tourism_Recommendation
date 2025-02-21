# Use an official Python image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Poetry files first for dependency installation
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install --no-cache-dir poetry==2.0.1

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application files
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
