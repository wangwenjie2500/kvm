# -*- coding:utf-8 -*-
from src import domain_opera as dom
import re
import pexpect
import script
import logging
import dbMgnt

'''
获取节点信息类
有两种模式，一种是带地址、用户参数，适用于注册新的节点，一种是不带用户参数，适用于查询已存在的节点
'''
class getNodeInfo:
    def __init__(self, *args):
        if args:
            self.nodeIP = args[0]
            self.nodeUSER = 'root'

    def getNodeMemroy(self):
        try:
            nodeClient = pexpect.spawn('ssh root@{} free -m'.format(self.nodeIP))
            string = nodeClient.read().strip()
            sv = string.splitlines()
            del sv[0]
            return sv[0].split()[1]
        except Exception,msg:
            print(msg)

    def getNodeCpu(self):
        try:
            nodeClient = pexpect.spawn('ssh {}@{} {}'.format(self.nodeUSER, self.nodeIP, 'cat /proc/cpuinfo'))
            string = nodeClient.read()
            pysicalNumber = string.count('physical id')
            onlycoreTmp = re.search('cpu cores	: (\d{1})',string,re.S)
            onlycores = (onlycoreTmp.group().split(':', onlycoreTmp.group().count(':')))[1].strip()
            coreVersion = re.search('(?<=model name	: )(.+?)(?=GHz)', string)
            cv = [ pysicalNumber, onlycores, coreVersion.group()]
            return cv
        except Exception,msg:
            print(msg)

    def getHostInfo(self):
        try:
            ssh = pexpect.spawn('ssh {}@{} {}'.format(self.nodeUSER, self.nodeIP, 'uname -p'))
            getNodeSystemInfoPrcType = ssh.read().strip()
            ssh = pexpect.spawn('ssh {}@{} {}'.format(self.nodeUSER, self.nodeIP, 'uname -r'))
            getNodeSystemInfoKerType = ssh.read().strip()
            ssh = pexpect.spawn('ssh {}@{} {}'.format(self.nodeUSER, self.nodeIP, 'cat /etc/redhat-release'))
            getNodeSystemInfoVersion = ssh.read().strip()
            hv = [ getNodeSystemInfoKerType, getNodeSystemInfoPrcType, getNodeSystemInfoVersion]
            return hv
        except Exception,msg:
            print(msg)

    def getInfo(self):
        a = self.getNodeMemroy()
        b = self.getNodeCpu()
        c = self.getHostInfo()
        hi = {"mt" :a,  #节点内存总量
                           "pcn" : b[0], #节点物理处理器总数
                           "opn" : b[1], #节点处理机逻辑核数
                           "pve" : b[2], #节点处理器型号
                           "kve" : c[0], #节点内核型号
                           "cjg" : c[1], #节点处理器架构
                           "sve" : c[2] #节点系统版本
        }
        return hi

def hostRegister(host):
    try:
        nodeInfo =  getNodeInfo(host).getInfo()
        id = script.random_str(randomlength=36)
        nodeRegInfo = {
            "nodeIP": '{}'.format(host),
            "nodeSTATUS": "'0'",
            "nodeMem": "'{}'".format(nodeInfo['mt']),
            "nodeCpu": "'{}'".format(int(nodeInfo['pcn']) * int(nodeInfo['opn'])),
            "nodeCpuVersion": "'{}'".format(nodeInfo['pve']),
            "nodeKernelVersion": "'{}'".format(nodeInfo['kve']),
            "nodeKenrelJ": "'{}'".format(nodeInfo['cjg']),
            "nodeSysVersion": "'{}'".format(nodeInfo['sve']),
            "UUID":"'{}'".format(id)
        }
        f = dbMgnt.redisMgnt().control(type='insert',Dict=nodeRegInfo,table='host_nodeinfo')
        return f
    except Exception,msg:
        print(msg)

def hostDelete(host):
    try:
        f = dbMgnt.redisMgnt().control(type='delete',table='host_nodeinfo',Where={'UUID':"{}".format(host)})
        return f
    except Exception,msg:
        print(msg)