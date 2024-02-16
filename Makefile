lint:
	python -m black .
	python -m ruff .

run:
	uvicorn app.main:app --reload

benchmark:
	env endpoint=io/simple locust --config locust/master.conf -f locust/benchmark.py -i 1000
