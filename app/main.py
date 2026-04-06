import logging
import time
import uuid

from fastapi import FastAPI
from fastapi import Request
from sqlalchemy import inspect, text

from app import models
from app.database import engine
from routers import auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def _ensure_users_columns() -> None:
	inspector = inspect(engine)
	if "users" not in inspector.get_table_names():
		return

	existing_columns = {column["name"] for column in inspector.get_columns("users")}
	missing_columns = {
		"verification_code_expires_at": "DATETIME",
		"refresh_token_hash": "VARCHAR",
		"refresh_token_expires_at": "DATETIME",
	}

	with engine.begin() as connection:
		for column_name, column_type in missing_columns.items():
			if column_name not in existing_columns:
				connection.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))


_ensure_users_columns()

logger = logging.getLogger("app.request")
if not logging.getLogger().handlers:
	logging.basicConfig(level=logging.INFO)


@app.get("/")
def root():
	return {"message": "FastAPI Authentication API is running", "docs": "/docs"}


@app.get("/health")
def health_check():
	return {"status": "ok"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
	request_id = str(uuid.uuid4())
	start = time.perf_counter()
	response = await call_next(request)
	duration_ms = (time.perf_counter() - start) * 1000

	logger.info(
		"request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
		request_id,
		request.method,
		request.url.path,
		response.status_code,
		duration_ms,
	)
	response.headers["X-Request-ID"] = request_id
	return response

app.include_router(auth.router)
