CFLAGS := -g -std=c99 -Wall -Wformat=2
CFLAGS += -Wshadow -Wpointer-arith -Wunreachable-code
CFLAGS += -Wconversion -Wno-sign-conversion -Wbad-function-cast

# Se puede comentar durante el desarrollo.
CFLAGS += -Werror

# Usar Python 3 si se encuentra; Python 2 si no.
PYTHON := $(shell which python3 python python2 | sed -ne 's@.*/@@p;q')

test: abb_aux
	$(PYTHON) ./abb_test.py

abb_aux: abb.o abb_aux.o

# Dependencias adicionales.
-include deps.mk

clean:
	rm -f abb_aux *.o core vgcore.*

.PHONY: test clean
