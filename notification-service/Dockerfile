# FROM python:3.13-slim

# WORKDIR /app

# # Install uv
# RUN pip install --no-cache-dir uv

# # Copy dependency files first (better layer caching)
# COPY pyproject.toml uv.lock* ./

# # Install dependencies
# RUN uv sync --no-dev

# # Copy the rest of the app
# COPY . .

# # Run the app using uv
# CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.13-slim

WORKDIR /app

# Install uv (only for build step)
RUN pip install --no-cache-dir uv

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock* ./

# RUN uv venv

# Install dependencies into .venv
RUN uv sync --no-dev --frozen

# Copy app code
COPY . .

# ✅ Use the venv directly
ENV PATH="/app/.venv/bin:$PATH"

# ✅ Run WITHOUT uv
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]