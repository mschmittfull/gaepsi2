MPICC=cc
LDSHARED="$(MPICC) -shared"
all:
	LDSHARED=$(LDSHARED) CC=$(MPICC) python setup.py build_ext --inplace
