
virtPyDir = $(PWD)/python
virtPyEnv = ${virtPyDir}/bin/activate
virtPy = ${virtPyDir}/bin/python
prefix=progressiveCactus
export

.PHONY: all clean test ucsc ucscClean 

all : 
	cd submodules && make all

clean:
	cd submodules && make clean

test:
	cd submodules && make test

ucsc:
	cd submodules && make justUCSC

ucscClean:
	cd submodules && make justUCSCClean

minimalInstall: all
	mkdir ${prefix}
	mkdir ${prefix}/bin
	mkdir ${prefix}/lib
	mkdir ${prefix}/etc
	cp -r submodules/tokyocabinet/bin ${prefix}/bin/tokyocabinet
	cp -r python/bin/ ${prefix}/bin/python
	cp -r submodules/kyotocabinet/bin ${prefix}/bin/kyotocabinet
	cp -r submodules/kyototycoon/bin ${prefix}/bin/kyototycoon
	cp -r submodules/phast/bin ${prefix}/bin/phast
	cp -r submodules/kentToolBinaries ${prefix}/bin/kentToolBinaries
	cp -r submodules/hdf5/bin ${prefix}/bin/hdf5
	cp -r submodules/sonLib/bin ${prefix}/bin/sonLib
	cp -r submodules/jobTree/bin ${prefix}/bin/jobTree
	cp -r submodules/cactus/bin ${prefix}/bin/cactus
	cp -r submodules/hal/bin ${prefix}/bin/hal
	cp -r submodules/cactus2hal/bin ${prefix}/bin/cactus2hal
install_clean:
	rm -rf ${prefix}
