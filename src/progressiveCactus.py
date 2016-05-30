#!/usr/bin/env python

# Progressive Cactus Package
# Copyright (C) 2009-2012 by Glenn Hickey (hickey@soe.ucsc.edu)
# and Benedict Paten (benedictpaten@gmail.com)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import os
import sys
import xml.etree.ElementTree as ET
import math
import time
import random
import copy
from argparse import ArgumentParser
import imp
import socket
import signal
import traceback
import datetime

from sonLib.bioio import logger
from sonLib.bioio import getTempDirectory
from sonLib.bioio import system
from sonLib.bioio import popenCatch

from toil.lib.bioio import setLoggingFromOptions
from toil.job import Job

from cactus.progressive.multiCactusProject import MultiCactusProject
from cactus.shared.experimentWrapper import ExperimentWrapper
from cactus.shared.configWrapper import ConfigWrapper

from seqFile import SeqFile
from projectWrapper import ProjectWrapper
from jobStatusMonitor import JobStatusMonitor

def initParser():
    usage = "usage: runProgressiveCactus.sh [options] <seqFile> <workDir> <outputHalFile>\n\n"\
             "Required Arguments:\n"\
             "  <seqFile>\t\tFile containing newick tree and seqeunce paths"\
             " paths.\n"\
             "\t\t\t(see documetation or examples for format).\n"\
             "  <workDir>\t\tWorking directory (which can grow "\
             "exteremely large)\n"\
             "  <outputHalFile>\tPath of output alignment in .hal format."
    
    parser = ArgumentParser(usage=usage)

    #Progressive cactus arguments
    parser.add_argument("seqFile", help = "Seq file")
    parser.add_argument("workDir", help = "Work dir")
    parser.add_argument("outputHalFile", help = "Output HAL file")

    #Progressive Cactus Options
    parser.add_argument("--jobStore", dest="jobStore",
                      help="JobStore to use for Toil. If not given,\
                      the FileJobStore will be used.", default=None)
    parser.add_argument("--optionsFile", dest="optionsFile",
                      help="Text file containing command line options to use as"\
                      " defaults", default=None)
    parser.add_argument("--database", dest="database",
                      help="Database type: tokyo_cabinet or kyoto_tycoon"
                      " [default: %default]",
                      default="kyoto_tycoon")
    parser.add_argument("--outputMaf", dest="outputMaf",
                      help="[DEPRECATED use hal2maf on the ouput file instead] Path of output alignment in .maf format.  This option should be avoided and will soon be removed.  It may cause sequence names to be mangled, and use a tremendous amount of memory. ",
                      default=None)
    parser.add_argument("--configFile", dest="configFile",
                      help="Specify cactus configuration file",
                      default=None)
    parser.add_argument("--legacy", dest="legacy", action="store_true", help=
                      "Run cactus directly on all input sequences "
                      "without any progressive decomposition (ie how it "
                      "was originally published in 2011)",
                      default=False)
    parser.add_argument("--autoAbortOnDeadlock", dest="autoAbortOnDeadlock",
                      action="store_true",
                      help="Abort automatically when jobTree monitor" +
                      " suspects a deadlock by deleting the jobTree folder." +
                      " Will guarantee no trailing ktservers but still " +
                      " dangerous to use until we can more robustly detect " +
                      " deadlocks.",
                      default=False)
    parser.add_argument("--overwrite", dest="overwrite", action="store_true",
                      help="Re-align nodes in the tree that have already" +
                      " been successfully aligned.",
                      default=False)
    parser.add_argument("--rootOutgroupDists", dest="rootOutgroupDists",
                      help="root outgroup distance (--rootOutgroupPaths must " +
                      "be given as well)", default=None)
    parser.add_argument("--rootOutgroupPaths", dest="rootOutgroupPaths", type=str,
                      help="root outgroup path (--rootOutgroup must be given " +
                      "as well)", default=None)
    parser.add_argument("--root", dest="root", help="Name of ancestral node (which"
                      " must appear in NEWICK tree in <seqfile>) to use as a "
                      "root for the alignment.  Any genomes not below this node "
                      "in the tree may be used as outgroups but will never appear"
                      " in the output.  If no root is specifed then the root"
                      " of the tree is used. ", default=None)

    #Kyoto Tycoon Options
    ktGroup = parser.add_argument_group("kyoto_tycoon Options",
                          "Kyoto tycoon provides a client/server framework "
                          "for large in-memory hash tables and is available "
                          "via the --database option.")
    ktGroup.add_argument("--ktPort", dest="ktPort",
                       help="starting port (lower bound of range) of ktservers"
                       " [default: %default]",
                       default=1978)
    ktGroup.add_argument("--ktHost", dest="ktHost",
                       help="The hostname to use for connections to the "
                       "ktserver (this just specifies where nodes will attempt"
                       " to find the server, *not* where the ktserver will be"
                       " run)",
                       default=None)
    ktGroup.add_argument("--ktType", dest="ktType",
                       help="Kyoto Tycoon server type "
                       "(memory, snapshot, or disk)"
                       " [default: %default]",
                       default='memory')
    # sonlib doesn't allow for spaces in attributes in the db conf
    # which renders this options useless
    #ktGroup.add_argument("--ktOpts", dest="ktOpts",
    #                   help="Command line ktserver options",
    #                   default=None)
    ktGroup.add_argument("--ktCreateTuning", dest="ktCreateTuning",
                       help="ktserver options when creating db "\
                            "(ex #bnum=30m#msiz=50g)",
                       default=None)
    ktGroup.add_argument("--ktOpenTuning", dest="ktOpenTuning",
                       help="ktserver options when opening existing db "\
                            "(ex #opts=ls#ktopts=p)",
                       default=None)
    parser.add_argument_group(ktGroup)
 
    return parser

# Try to weed out errors early by checking options and paths
def validateInput(workDir, outputHalFile, options):
    try:
        if workDir.find(' ') >= 0:
            raise RuntimeError("Cactus does not support spaces in pathnames: %s"
                               % workDir)
        if not os.path.isdir(workDir):
            os.makedirs(workDir)
        if not os.path.isdir(workDir) or not os.access(workDir, os.W_OK):
            raise
    except:
        raise RuntimeError("Can't write to workDir: %s" % workDir)
    try:
        open(outputHalFile, "w")
    except:
        raise RuntimeError("Unable to write to hal: %s" % outputHalFile)
    if options.database != "tokyo_cabinet" and\
        options.database != "kyoto_tycoon":
        raise RuntimeError("Invalid database type: %s" % options.database)
    if options.outputMaf is not None:
        try:
            open(options.outputMaf, "w")
        except:
            raise RuntimeError("Unable to write to maf: %s" % options.outputMaf)
    if options.configFile is not None:
        try:
            ConfigWrapper(ET.parse(options.configFile).getroot())
        except:
            raise RuntimeError("Unable to read config: %s" % options.configFile)
    if options.database == 'kyoto_tycoon':
        if options.ktType.lower() != 'memory' and\
           options.ktType.lower() != 'snapshot' and\
           options.ktType.lower() != 'disk':
            raise RuntimeError("Invalid ktserver type specified: %s. Must be "
                               "memory, snapshot or disk" % options.ktType)    

# Go through a text file and add every word inside to an arguments list
# which will be prepended to sys.argv.  This way both the file and
# command line are passed to the option parser, with the command line
# getting priority. 
def parseOptionsFile(path):
    if not os.path.isfile(path):
        raise RuntimeError("Options File not found: %s" % path)
    args = []
    optFile = open(path, "r")
    for l in optFile:
        line = l.rstrip()
        if line:
            args += shlex.split(line)

# This source file should always be in progressiveCactus/src.  So
# we return the path to progressiveCactus/environment, which needs
# to be sourced before doing anything. 
def getEnvFilePath():
    path = os.path.dirname(sys.argv[0])
    envFile = os.path.join(path, '..', 'environment')
    assert os.path.isfile(envFile)
    return envFile

# If specified with the risky --autoAbortOnDeadlock option, we call this to
# force an abort if the jobStatusMonitor thinks it's hopeless.
# We delete the jobTreePath to get rid of kyoto tycoons.
def abortFunction(jtPath, options):
    def afClosure():
        sys.stderr.write('\nAborting due to deadlock (prevent with'
                         + '--noAutoAbort' +
                         ' option), and running rm -rf %s\n\n' % jtPath)
        system('rm -rf %s' % jtPath)
        sys.exit(-1)
    if options.autoAbortOnDeadlock:
        return afClosure
    else:
        return None
    
# Run cactus progressive on the project that has been created in workDir.
# Any jobtree options are passed along.  Should probably look at redirecting
# stdout/stderr in the future.
def runCactus(workDir, toilCommands, toilPath, options):
    envFile = getEnvFilePath()
    pjPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
                          '%s_project.xml' % ProjectWrapper.alignmentDirName)
    logFile = os.path.join(workDir, 'cactus.log')

    if options.overwrite:
        overwriteFlag = '--overwrite'
        system("rm -f %s" % logFile)
    else:
        overwriteFlag = ''

    logHandle = open(logFile, "a")
    logHandle.write("\n%s: Beginning Progressive Cactus Alignment\n\n" % str(
        datetime.datetime.now()))
    logHandle.close()
    cmd = '. %s && cactus_progressive.py %s --project %s %s >> %s 2>&1' % (envFile,
                                                                 toilCommands,
                                                                 pjPath,
                                                                 overwriteFlag,
                                                                 logFile)
    jtMonitor = JobStatusMonitor(toilPath, pjPath, logFile,
                                 deadlockCallbackFn=abortFunction(toilPath,
                                                                  options))
    if options.database == "kyoto_tycoon":
        jtMonitor.daemon = True
        jtMonitor.start()
        
    system(cmd)
    logHandle = open(logFile, "a")
    logHandle.write("\n%s: Finished Progressive Cactus Alignment\n" % str(
        datetime.datetime.now()))
    logHandle.close()

def checkCactus(workDir, options):
    pass

# Call cactus2hal to extract a single hal file out of the progressive
# alignmenet in the working directory.  If the maf option was set, we
# just move out the root maf.  
def extractOutput(workDir, outputHalFile, options):
    if options.outputMaf is not None:
        mcProj = MultiCactusProject()
        mcProj.readXML(
            os.path.join(workDir, ProjectWrapper.alignmentDirName,
                         ProjectWrapper.alignmentDirName + "_project.xml"))
        rootName = mcProj.mcTree.getRootName()
        rootPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
        rootName, rootName + '.maf')
        cmd = 'mv %s %s' % (rootPath, options.outputMaf)
        system(cmd)
    envFile = getEnvFilePath()
    logFile = os.path.join(workDir, 'cactus.log')
    pjPath = os.path.join(workDir, ProjectWrapper.alignmentDirName,
                          '%s_project.xml' % ProjectWrapper.alignmentDirName)
    logHandle = open(logFile, "a")
    logHandle.write("\n\n%s: Beginning HAL Export\n\n" % str(
        datetime.datetime.now()))
    logHandle.close()
    cmd = '. %s && cactus2hal.py %s %s >> %s 2>&1' % (envFile, pjPath,
                                                      outputHalFile, logFile)
    system(cmd)
    logHandle = open(logFile, "a")
    logHandle.write("\n%s: Finished HAL Export \n" % str(
        datetime.datetime.now()))
    logHandle.close()

def main():
    # init as dummy function
    cleanKtFn = lambda x,y:x
    stage = -1
    workDir = None
    try:
        parser = initParser()
        options, toilOptions = parser.parse_known_args()
        toilPath = os.path.join(options.workDir, "toil")
        if options.jobStore:
            toilOptions.append(options.jobStore)
            sys.argv.append(options.jobStore)
        else:
            toilOptions.append(toilPath)
            sys.argv.append(toilPath)
        Job.Runner.addToilOptions(parser)
        options = parser.parse_args()

        if (options.rootOutgroupDists is not None) \
        ^ (options.rootOutgroupPaths is not None):
            parser.error("--rootOutgroupDists and --rootOutgroupPaths must be " +
                         "provided together")
        
        if options.optionsFile != None:
            fileArgs = parseOptionsFile(options.optionsFile)
            options = parser.parse_args(fileArgs + sys.argv[1:])

        stage = 0
        setLoggingFromOptions(options)
        seqFile = SeqFile(options.seqFile)
        workDir = options.workDir
        outputHalFile = options.outputHalFile
        validateInput(workDir, outputHalFile, options)

        stage = 1
        print "\nBeginning Alignment"
        system("rm -rf %s" % toilPath) 
        projWrapper = ProjectWrapper(options, seqFile, workDir)
        projWrapper.writeXml()
        runCactus(workDir, " ".join(toilOptions), toilPath, options)
        #cmd = 'toil status --failIfNotComplete %s > /dev/null 2>&1 ' %\
        #3      toilPath
        #system(cmd)

        stage = 2
        print "Beginning HAL Export"
        extractOutput(workDir, outputHalFile, options)
        print "Success.\n" "Temporary data was left in: %s\n" \
              % workDir
        
        return 0
    
    except RuntimeError, e:
        sys.stderr.write("Error: %s\n\n" % str(e))
        if stage >= 0 and workDir is not None and os.path.isdir(workDir):
            sys.stderr.write("Temporary data was left in: %s\n" % workDir)
        if stage == 1:
            sys.stderr.write("More information can be found in %s\n" %
                             os.path.join(workDir, "cactus.log"))
        elif stage == 2:
            sys.stderr.write("More information can be found in %s\n" %
                             os.path.join(workDir, "cactus.log"))
        return -1

if __name__ == '__main__':
    sys.exit(main())
