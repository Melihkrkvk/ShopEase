BACKEND  := cd backend &&
FRONTEND := cd frontend &&

.PHONY: help \
        backend-install backend-dev backend-migrate backend-seed backend-reset \
        test test-unit test-integration test-cov \
        frontend-install frontend-dev \
        dev lint clean

# ── Default ───────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "ShopEase — available commands"
	@echo ""
	@echo "  Backend"
	@echo "    make backend-install     Install backend dependencies"
	@echo "    make backend-migrate     Run Alembic migrations"
	@echo "    make backend-seed        Seed database with sample data"
	@echo "    make backend-reset       migrate + seed in one step"
	@echo "    make backend-dev         Start backend dev server (port 8000)"
	@echo ""
	@echo "  Tests"
	@echo "    make test                Run all tests"
	@echo "    make test-unit           Run unit tests only"
	@echo "    make test-integration    Run integration tests only"
	@echo "    make test-cov            Run all tests with coverage report"
	@echo ""
	@echo "  Frontend"
	@echo "    make frontend-install    Install frontend dependencies"
	@echo "    make frontend-dev        Start frontend dev server (port 5173)"
	@echo ""
	@echo "  Other"
	@echo "    make dev                 Start both backend and frontend"
	@echo "    make clean               Remove build artifacts and cache files"
	@echo ""

# ── Backend ───────────────────────────────────────────────────────────────────
backend-install:
	$(BACKEND) uv sync

backend-migrate:
	$(BACKEND) uv run alembic upgrade head

backend-seed:
	$(BACKEND) uv run python seed.py

backend-reset: backend-migrate backend-seed

backend-dev:
	$(BACKEND) uv run uvicorn app.main:app --reload --port 8000

# ── Tests ─────────────────────────────────────────────────────────────────────
test:
	$(BACKEND) uv run pytest -v

test-unit:
	$(BACKEND) uv run pytest tests/unit/ -v

test-integration:
	$(BACKEND) uv run pytest tests/integration/ -v

test-cov:
	$(BACKEND) uv run pytest -v --cov=app --cov-report=term-missing

# ── Frontend ──────────────────────────────────────────────────────────────────
frontend-install:
	$(FRONTEND) npm install

frontend-dev:
	$(FRONTEND) npm run dev

# ── Dev (both) ────────────────────────────────────────────────────────────────
dev:
	@echo "Starting backend on :8000 and frontend on :5173 ..."
	@$(BACKEND) uv run uvicorn app.main:app --reload --port 8000 & \
	 $(FRONTEND) npm run dev

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."
