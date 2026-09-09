install:
	python3 -m pip install -r requirements.txt

setup-test:
	python3 src/analytics/create_demo_data.py
	python3 src/analytics/run_engine.py

ratios:
	python3 src/analytics/run_engine.py

test:
	python3 -m pytest -q

screener:
	python3 src/analytics/screener.py

clean:
	rm -f nifty100.db
	rm -f output/*.csv
	rm -f output/*.log
