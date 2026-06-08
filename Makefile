PREFIX ?= $(HOME)/.local
BINDIR ?= $(PREFIX)/bin

.PHONY: all clean install 01 02 03

all: 01 02 03

01:
	./ptf build 01

02:
	./ptf build 02

03:
	./ptf build 03

install:
	install -d "$(DESTDIR)$(BINDIR)"
	ln -sf "$(abspath ptf)" "$(DESTDIR)$(BINDIR)/ptf"

clean:
	rm -rf build/01 build/02 build/03
	rm -f puzzles/01-syscall-storm/input/data.txt
