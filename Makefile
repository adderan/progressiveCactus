
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

install: localInstall
	cp -r ${installname} ${installdir}
localInstall:
	mkdir ${installname}
	mkdir ${installname}/bin
	mkdir ${installname}/lib
	mkdir ${installname}/submodules
	cp -r submodules/tokyocabinet/bin ${installname}/bin/tokyocabinet
	cp -r python/bin/ ${installname}/bin/python
	cp -r submodules/kyotocabinet/bin ${installname}/bin/kyotocabinet
	cp -r submodules/kyototycoon/bin ${installname}/bin/kyototycoon
	cp -r submodules/phast/bin ${installname}/bin/phast
	cp -r submodules/kentToolBinaries ${installname}/bin/kentToolBinaries
	cp -r submodules/hdf5/bin ${installname}/bin/hdf5
	cp -r submodules/sonLib/bin ${installname}/bin/sonLib
	cp -r submodules/jobTree/bin ${installname}/bin/jobTree
	cp -r submodules/cactus/bin ${installname}/bin/cactus
	cp -r submodules/hal/bin ${installname}/bin/hal
	cp -r submodules/cactus2hal/bin ${installname}/bin/cactus2hal
	cp -r submodules/cactusTestData ${installname}/submodules/cactusTestData
	cp -r submodules/treeBuildingEvaluation/bin ${installname}/bin/treeBuildingEvaluation
	cp -r submodules/mafTools/bin ${installname}/bin/mafTools
	cp -r examples ${installname}/submodules/examples
	cp -r src/ ${installname}/src
	cp -r python ${installname}/
	cd submodules && find . -name '*.py' | cpio -pdm ../${installname}/lib/
	cp environmentForInstall ${installname}/environment
	cp bin/runProgressiveCactus.sh ${installname}/bin
	cp submodules/cactus/cactus_progressive_config.xml ${installname}/lib/cactus/cactus_progressive_config.xml

installClean:
	rm -rf ${installname}
	rm -rf ${installdir}
static:
	cd submodules && make static
dist: localInstall
	tar -zcvf progressiveCactus.tar.gz ${installname}
distClean:
	rm progressiveCactus.tar.gz
