.PHONY: setup lint format typecheck test

setup:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check .
	black --check .

format:
	ruff check --fix .
	black .

typecheck:
	mypy packages/common

test:
	python -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('coverage') else 1)" \
		&& coverage run -m pytest && coverage report -m \
		|| (echo "coverage not installed; running pytest only" && pytest)
