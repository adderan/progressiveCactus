include include.mk

externalModules = zlib tokyocabinet kyotocabinet kyototycoon hdf5 pbs-drmaa clapack phast kentToolBinaries mafTools treeBuildingEvaluation
ucscModules = sonLib jobTree pinchesAndCacti matchingAndOrdering cactus hal cactus2hal

modules = ${externalModules} ${ucscModules}
#modules = ${ucsc}

.PHONY: all %.all justUCSC %.justUCSC envRefreshRule virtPyRule pbsDrmaaRule mafToolsRule treeBuildingEvaluationRule drmaaPythonRule zlibRule tokyocabinetRule kyotocabinetRule kyototycoonRule hdf5Rule clapackRule phastRule kentToolBinariesRule %.ucsc clean %.clean justUCSCClean %.justUCSCClean zlibClean cabinetClean pbsDrmaaClean hdf5Clean clapckClean phastClean kentToolBinariesClean mafToolsClean treeBuildingEvaluationClean test %.test datasets

all : virtPyRule zlibRule tokyocabinetRule kyotocabinetRule kyototycoonRule pbsDrmaaRule drmaaPythonRule clapackRule phastRule kentToolBinariesRule hdf5Rule ${ucscModules:%=ucsc.%}

justUCSC : ${ucscModules:%=ucsc.%}

virtPyRule :
	/usr/bin/python $(PWD)/virtualenv/virtualenv.py ${virtPyDir}
	. ${virtPyEnv} && cd $(PWD)/networkx && ${virtPy} setup.py install
	. ${virtPyEnv} && cd $(PWD)/psutil/ && ${virtPy} setup.py install
	. ${virtPyEnv} && cd $(PWD)/biopython/ && echo y | ${virtPy} setup.py install | cat
	
ifeq ($(enablePBSTorque), yes)
pbsDrmaaRule :
	cd pbs-drmaa &&./configure --prefix=$(PWD)/pbs-drmaa && make && make install

drmaaPythonRule :
	. ${virtPyEnv} && cd $(PWD)/drmaa-python/ && ${virtPy} setup.py install
else
pbsDrmaaRule :
	cd .

drmaaPythonRule :
	cd . 
endif

mafToolsRule:
	cd mafTools && make lib.all mafComparator.all
treeBuildingEvaluationRule:
	cd treeBuildingEvaluation && export PROGRESSIVE_CACTUS_DIR=../../ && make -e
zlibRule :
	cd zlib && ./configure --prefix=$(PWD)/zlib && make && make install

tokyocabinetRule :
	cd tokyocabinet &&./configure --prefix=$(PWD)/tokyocabinet ${ktlinkingflags} --disable-bzip --with-zlib=$(PWD)/zlib && make && make install

kyotocabinetRule :
	cd kyotocabinet &&./configure --prefix=$(PWD)/kyotocabinet ${ktlinkingflags} && make && make install

kyototycoonRule :
	cd kyototycoon &&./configure --prefix=$(PWD)/kyototycoon ${ktlinkingflags} --with-kc=$(PWD)/kyotocabinet && make && make install

ifneq ($(TARGETOS), Darwin)
CLAPACKPHASTFLAGS = CLAPACKPATH=$(PWD)/clapack
clapackRule :
	cd clapack && make f2clib && make blaslib && make lib
else
CLAPACKPHASTFLAGS = 
clapackRule :
	cd .
endif

ifdef ENABLE_PHYLOP
phastRule :
	cd phast/src && make $(CLAPACKPHASTFLAGS)
else
phastRule :
	cd .
endif

kentToolBinariesRule :
	cd kentToolBinaries && make

hdf5Rule :
	cd hdf5 &&./configure --prefix=$(PWD)/hdf5 --enable-cxx && CFLAGS=-std=c99 make -e && make install


# Important to export environment to override sonlib/include.mk
export

ucsc.%:
	cd $* && make

clean: cabinetClean hdf5Clean pbsDrmaaClean zlibClean clapackClean phastClean kentToolBinariesClean ${ucscModules:%=clean.%}

clean.%:
	cd $* && make clean

justUCSCClean: ${ucscModules:%=justUCSCClean.%}

justUCSCClean.%:
	cd $* && make clean

zlibClean:
	cd zlib && make clean

cabinetClean:
	cd kyotocabinet && make clean
	cd kyototycoon && make clean
	rm -f $(PWD)/tokyocabinet/lib/*.a $(PWD)/kyotocabinet/lib/*.a  $(PWD)/kyototycoon/lib/*.a

ifeq ($(enablePBSTorque), yes)
pbsDrmaaClean:
	cd pbs-drmaa && make clean
else
pbsDrmaaClean:
	cd .
endif

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

kentToolBinariesClean :
	cd kentToolBinaries && make clean

hdf5Clean:
	cd hdf5 && make clean

test: ${ucscModules:%=test.%}

test.%:
	. ${myEnv} && cd $* && make test

static: virtPyRule zlibRule tokyocabinetRule kyotocabinetRule kyototycoonRule pbsDrmaaRule drmaaPythonRule clapackRule phastRule kentToolBinariesRule hdf5Rule ${ucscModules:%=ucsc.%} mafToolsRule treeBuildingEvaluationRule 
