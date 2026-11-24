# El contexto de construccion es la raiz del proyecto.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalo las dependencias antes de copiar el codigo para aprovechar la cache.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# La aplicacion trabaja sin permisos de administrador.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/.archivos \
    && chown appuser:appuser /app/.archivos

COPY --chown=appuser:appuser backend ./backend
COPY --chown=appuser:appuser core ./core
COPY --chown=appuser:appuser database ./database
COPY --chown=appuser:appuser utils ./utils
COPY --chown=appuser:appuser scripts ./scripts
COPY --chown=appuser:appuser alembic ./alembic
COPY --chown=appuser:appuser main.py alembic.ini ./

USER appuser
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
