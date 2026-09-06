.PHONY: test demo benchmark clean

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

demo:
	PYTHONPATH=src python -m execution_finality.demo

benchmark:
	PYTHONPATH=src python -m execution_finality.benchmark

clean:
	rm -rf .pytest_cache .mypy_cache build dist *.egg-info src/*.egg-info
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
