.PHONY: init fetch dbt gx checkpoint metrics all

init:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

fetch:
	python scripts/fetch_311.py

dbt:
	cd dbt && dbt deps || true
	cd dbt && dbt build --profiles-dir .

gx:
	python scripts/setup_gx.py

checkpoint:
	python scripts/run_checkpoint.py

metrics:
	python scripts/build_metrics.py

all: fetch dbt checkpoint metrics
