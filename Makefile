PYTHON ?= python3

.PHONY: all clean 01 02 03

all: 01 02 03

01:
	$(PYTHON) pmystery.py build 01

02:
	$(PYTHON) pmystery.py build 02

03:
	$(PYTHON) pmystery.py build 03

clean:
	rm -rf build/01 build/02 build/03 runs/01 runs/02 runs/03
	rm -f puzzles/01-syscall-storm/input/data.txt

