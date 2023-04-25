# Map the FW-task on polaris single-queue allocation

""" Polaris Mapping """

import os


def getNodes():
    nodes_list = []
    nodefile = os.environ.get("PBS_NODEFILE")

    if nodefile is not None:
        with open(nodefile, 'r') as f:
            for line in f:
                nodes_list.append(line.strip('\n'))
    else:
        print("PBS_NODEFILE not found")

    return nodes_list


def getBin():
    binary = os.environ.get('QE_EXE')
    if binary is None:
        binary = '/lus/eagle/projects/catalysis_aesp/abagusetty/qe-7.1/build_cuda_nompiaware/bin/pw.x'

    return binary


class MapTaskToNodes():
    count = 0  # Class variable to count the number of instances created.
    # Every time I create a instance, this number increase.

    def __init__(self):
        self.icount = MapTaskToNodes.count
        self.listNodes = getNodes()
        self.nnodes = len(self.listNodes)
        self.binary = getBin()

        MapTaskToNodes.count += 1

    def getCommand(self):
        if len(self.listNodes) == 0:
            command = 'mpiexec -n 4 --ppn 4 --depth=8 --cpu-bind depth --env OMP_NUM_THREADS=8 --env OMP_PLACES=cores {} -in PREFIX.pwi > PREFIX.pwo'.format(
                self.binary)
        else:
            idx = self.icount % self.nnodes
            command = 'mpiexec --hosts {} -n 4 --ppn 4 --depth=8 --cpu-bind depth --env OMP_NUM_THREADS=8 --env OMP_PLACES=cores {} -in PREFIX.pwi > PREFIX.pwo'.format(
                self.listNodes[idx], self.binary)

        return command
