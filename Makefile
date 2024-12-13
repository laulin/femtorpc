tests:
	python3 -m unittest discover -s test -p test_*.py

bench:
	python3 -m unittest discover -s test -p bench*.py