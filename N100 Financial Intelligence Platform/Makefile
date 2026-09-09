PYTHON=python

load:
	$(PYTHON) src/etl/loader.py

validate:
	$(PYTHON) src/etl/validator.py

test:
	pytest -q

report:
	$(PYTHON) src/etl/validator.py

ratios:
	$(PYTHON) src/etl/ratios.py

dashboard:
	@echo "Dashboard module placeholder — database is ready."

api:
	@echo "API module placeholder — database is ready."

clean:
	rm -f nifty100.db
	rm -f output/*.csv
