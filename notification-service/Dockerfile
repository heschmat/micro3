FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --no-dev

# Copy the rest of the app
COPY . .

# Run the app using uv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
