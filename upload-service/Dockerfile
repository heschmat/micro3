FROM python:3.12-slim

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
# CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
