FROM python:3.12

RUN pip install poetry

WORKDIR /app/

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
