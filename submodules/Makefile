include include.mk

externalModules = tokyocabinet kyotocabinet kyototycoon hdf5 pbs-drmaa clapack phast
ucscModules = sonLib pinchesAndCacti matchingAndOrdering cactus hal cactus2hal

modules = ${externalModules} ${ucscModules}
#modules = ${ucsc}

.PHONY: all %.all justUCSC %.justUCSC tokyocabinetRule kyotocabinetRule kyototycoonRule hdf5Rule clapackRule phastRule %.ucsc clean %.clean justUCSCClean %.justUCSCClean cabinetClean hdf5Clean clapckClean phastClean%.test

all : tokyocabinetRule kyotocabinetRule kyototycoonRule clapackRule phastRule hdf5Rule ${ucscModules:%=ucsc.%}

justUCSC : ${ucscModules:%=ucsc.%}


tokyocabinetRule :
	cd tokyocabinet &&./configure --prefix=$(PWD)/tokyocabinet --enable-static --disable-shared  --disable-bzip && make && make install

kyotocabinetRule :
	cd kyotocabinet &&./configure --prefix=$(PWD)/kyotocabinet --enable-static --disable-shared  && make && make install

kyototycoonRule :
	cd kyototycoon &&./configure --prefix=$(PWD)/kyototycoon --enable-static --disable-shared --with-kc=$(PWD)/kyotocabinet && make && make install

ifneq ($(TARGETOS), Darwin)
CLAPACKPHASTFLAGS = CLAPACKPATH=$(PWD)/clapack
clapackRule :
	cd clapack && make f2clib && make blaslib && make lib
else
clapackRule :
	cd .
endif

ifdef ENABLE_PHYLOP
phastRule :
	cd phast/src && make CLAPACKPATH=${PWD}/clapack
else
phastRule :
	cd .
endif

hdf5Rule :
	cd hdf5 &&./configure --prefix=$(PWD)/hdf5 --enable-cxx && CFLAGS=-std=c99 make -e && make install


# Important to export environment to override sonlib/include.mk
export

ucsc.%:
	cd $* && make

clean: cabinetClean hdf5Clean clapackClean phastClean ${ucscModules:%=clean.%}

clean.%:
	cd $* && make clean

justUCSCClean: ${ucscModules:%=justUCSCClean.%}

justUCSCClean.%:
	cd $* && make clean


cabinetClean:
	cd kyotocabinet && make clean
	cd kyototycoon && make clean
	rm -f $(PWD)/tokyocabinet/lib/*.a $(PWD)/kyotocabinet/lib/*.a  $(PWD)/kyototycoon/lib/*.a

ifneq ($(TARGETOS), Darwin)
clapackClean :
	cd clapack && make clean
else
clapackClean :
	cd .
endif

ifdef ENABLE_PHYLOP
phastClean :
	cd phast/src && make clean
else
phastClean :
	cd .
endif

hdf5Clean:
	cd hdf5 && make clean

test: ${ucscModules:%=test.%}

