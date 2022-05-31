all:
	python stress_drop.py -d 2002-10-03-mw65 -N 512 --fmin 0.05 --fmax 5.0
	python stress_drop.py -d 2003-03-12-mw63 -N 512 --fmin 0.05 --fmax 5.0
	python stress_drop.py -d 2003-04-15-mw55 -N 512 --fmin 0.05 --fmax 5.0
