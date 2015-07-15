
virtPyDir = $(PWD)/python
virtPyEnv = ${virtPyDir}/bin/activate
virtPy = ${virtPyDir}/bin/python

installname=progressiveCactus_v1.0
installdir=${prefix}/${installname}
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

install:
	mkdir ${installdir}
	mkdir ${installdir}/bin
	mkdir ${installdir}/lib
	mkdir ${installdir}/submodules
	cp -r submodules/tokyocabinet/bin ${installdir}/bin/tokyocabinet
	cp -r python/bin/ ${installdir}/bin/python
	cp -r submodules/kyotocabinet/bin ${installdir}/bin/kyotocabinet
	cp -r submodules/kyototycoon/bin ${installdir}/bin/kyototycoon
	cp -r submodules/phast/bin ${installdir}/bin/phast
	cp -r submodules/kentToolBinaries ${installdir}/bin/kentToolBinaries
	cp -r submodules/hdf5/bin ${installdir}/bin/hdf5
	cp -r submodules/sonLib/bin ${installdir}/bin/sonLib
	cp -r submodules/jobTree/bin ${installdir}/bin/jobTree
	cp -r submodules/cactus/bin ${installdir}/bin/cactus
	cp -r submodules/hal/bin ${installdir}/bin/hal
	cp -r submodules/cactus2hal/bin ${installdir}/bin/cactus2hal
	cp -r submodules/cactusTestData ${installdir}/submodules/cactusTestData
	cp -r examples ${installdir}/submodules/examples
	cp -r src/ ${installdir}/src
	cp -r python ${installdir}/
	cd submodules && find . -name '*.py' | cpio -pdm ${installdir}/lib
	cp installenv ${installdir}/environment
	cp bin/runProgressiveCactus.sh ${installdir}/bin
	cp submodules/cactus/cactus_progressive_config.xml ${installdir}/lib/cactus

installClean:
	rm -rf ${installdir}
static:
	cd submodules && make static
dist:
	tar -zcvf progressiveCactus.tar.gz -C ${prefix} ${installname}
distClean:
	rm progressiveCactus.tar.gz
