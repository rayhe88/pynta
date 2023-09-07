# Map the FW-task on polaris single-queue allocation

""" Polaris Mapping """

import os
from datetime import datetime
import pickle


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

def readMapTxt(fname):
    maplist = []
    try:
        with open(fname, "r") as file:
            for line in file:
                num = int(line.strip())
                maplist.append(num)
    except FileNotFoundError:
        maplist = []

    return maplist


def writeMapTxt(fname, maplist):
    with open(fname, "w") as file:
        for num in maplist:
            file.write(str(num) + "\n")


def compare_returnmax(list1, list2):
    if list1 and list2:
        last1 = list1[-1]
        last2 = list2[-1]

        if last1 == last2:
            return last1
        else:
            return max(last1, last2)
    else:
        return None

class MapTaskToNodes():
    count = 0
    listCount = []
    dir_root = os.getcwd()
    fname = f'{dir_root}/map.txt'

    flag = True


    def __init__(self, _method=None):
        self.method = _method
        self.icount = MapTaskToNodes.count
        self.maplist = []

        if MapTaskToNodes.count == 0 and MapTaskToNodes.flag == True:
            if os.path.exists(MapTaskToNodes.fname):
                os.remove(MapTaskToNodes.fname)
                MapTaskToNodes.flag = False

        if self.method != 'MDMin':
            MapTaskToNodes.count += 1

        if MapTaskToNodes.count > 2:
            self.maplist = readMapTxt(MapTaskToNodes.fname)


        writeMapTxt(MapTaskToNodes.fname, MapTaskToNodes.listCount)

        if  compare_returnmax(self.maplist, MapTaskToNodes.listCount) == None:
             MapTaskToNodes.listCount.append(MapTaskToNodes.count)
        else:
             MapTaskToNodes.listCount.append(self.icount)





    def getCommand(self):

        #mynode = ["nodeX00", "nodeX01", "nodeX02", "nodeX03"]
        mynode = ["nodeY00", "nodeY01", "nodeY02", "nodeY03"]

        return "icount: {} Node {}".format(self.icount, mynode[self.icount % 4])

'''     if len(self.listNodes) == 0:
            command = 'mpiexec -n 4 --ppn 4 --depth=8 --cpu-bind depth --env OMP_NUM_THREADS=8 --env OMP_PLACES=cores {} -in PREFIX.pwi > PREFIX.pwo'.format(
                self.binary)
        else:
            idx = self.icount % self.nnodes
            command = 'mpiexec --hosts {} -n 4 --ppn 4 --depth=8 --cpu-bind depth --env OMP_NUM_THREADS=8 --env OMP_PLACES=cores {} -in PREFIX.pwi > PREFIX.pwo'.format(
                self.listNodes[idx], self.binary)

        return "count : {}".format(self.icount)
'''
