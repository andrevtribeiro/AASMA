setup:
	(cd initial_data && make setup)

run:
	python3 main.py 0.5 "decrescent" "MinimizeBuyPrice" 1 > results/results.out

clean:
	(cd initial_data && make clean)
	(cd results && make clean)

chart:
	python3 chart_script.py