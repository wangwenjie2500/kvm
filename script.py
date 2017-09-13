#!/usr/bin/env python
#-*- coding:utf-8 -*-
from random import Random
import ConfigParser
from dbMgnt import redisMgnt
import json
#创建一个随机ID
def random_str(randomlength=None):
    str1 = ""
    chars = 'abcdefghigklmnopqrstuvwxyz1234567890'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str1 += chars[random.randint(0, length)]
    return str1

#input domain Dict return data
class domainXMLjx:
    def __init__(self,xml):
        self.xml = xml

    def graphicel(self):
        a = self.xml['domain']['devices']['graphics']
        grapType = a['@type']
        grapPort = a['@port']
        grapCType = a['@autoport']
        return {
            'grapType': grapType,
            'grapPort': grapPort,
            'grapCType': grapCType,
        }

    def diskInfo(self):
        diskList = []
        a = self.xml['domain']['devices']['disk']
        if isinstance(a, list):
            for i in a:
                if i['@device'] == 'disk':
                    diskType = i['driver']['@type']
                    if i['source']['@file']:
                        diskList.append({i['target']['@dev']: {
                            'devType': i['@device'],
                            'devModle': diskType,
                            'devPath': i['source']['@file'],
                            'targetType': i['target']['@bus']
                        }})
                elif i['@device'] == 'cdrom':
                    diskType = i['driver']['@type']
                    if 'source' in i:
                        diskList.append(
                            {i['target']['@dev']: {
                                'devType': i['@device'],
                                'devModle': diskType,
                                'devPath': i['source']['@file'],
                                'targetType': i['target']['@bus']
                            }}
                        )
                    else:
                        diskList.append(
                            {i['target']['@dev']: {
                                'devType': i['@device'],
                                'devModle': diskType,
                                'targetType': i['target']['@bus'],
                                'devPath': 'None'
                            }
                            }
                        )

        else:
            if a['@device'] == 'disk':
                diskType = a['driver']['@type']
                if a['source']['@file']:
                    diskList.append({a['target']['@dev']: {
                        'devType': a['@device'],
                        'devModle': diskType,
                        'targetType': a['target']['@bus']
                    }})
            elif a['@device'] == 'cdrom':
                diskType = a['driver']['@type']
                if 'source' in a:
                    diskList.append(
                        {a['target']['@dev']: {
                            'devType': a['@device'],
                            'devModle': diskType,
                            'devPath': a['source']['@file'],
                            'targetType': a['target']['@bus']
                        }}
                    )
                else:
                    diskList.append(
                        {a['target']['@dev']: {
                            'devType': a['@device'],
                            'devModle': diskType,
                            'targetType': a['target']['@bus']
                        }}
                    )
        return diskList

    def configInfo(self):
        a = self.xml['domain']
        Mmemory = a['memory']['#text']
        if 'currentMemory' in a:
            Nmemory = a['currentMemory']['#text']
        else:
            Nmemory = 'None'
        Mcpu = a['vcpu']['#text']
        if '@current' in a['vcpu']:
            Ncpu = a['vcpu']['@current']
        else:
            Ncpu = 'None'
        return {
            'MaxMemory': Mmemory,
            'CurMemory': Nmemory,
            'MaxCpu': Mcpu,
            'CurCpu': Ncpu
        }

    def interfaceList(self):
        a = self.xml['domain']['devices']['interface']
        netList = []
        if isinstance(a, list):
            for i in a:
                netDevType = i['@type']
                netDevMac = i['mac']['@address']
                for m in i['source']:
                    netDevName = i['source'][m]
                if 'target' in a:
                    netTarget = a['target']['@dev']
                else:
                    netTarget = None
                netList.append({
                    netDevName: {
                        'netDevType': netDevType,
                        'netDevMac': netDevMac,
                        'netTarget': netTarget
                    }
                })
        else:
            netDevType = a['@type']
            netDevMac = a['mac']['@address']
            for m in a['source']:
                netDevName = a['source'][m]
                if 'target' in a:
                    netTarget = a['target']['@dev']
                else:
                    netTarget = None
            netList.append({
                netDevName: {
                    'netDevType': netDevType,
                    'netDevMac': netDevMac,
                    'netTarget': netTarget
                }
            })
        return netList

def vncConfig():
    try:
        cf = ConfigParser.ConfigParser()
        cf.read("/git_csdn/kvm/src/global.conf")
        vncPath = cf.get('vnc', 'vnc_path') + 'vnc_tokens'
        domL = []
        f = redisMgnt().control(type='select',Dict=['UUID','grapPort','inHost'],table='domain_machineinfo')
        for i in f:
            domL.append({i[0]:{'grapPort': i[1],'inHost':i[2]}})
        string = ''
        for i in domL:
            bs = '{}: {}:{}\n'.format(
                i.keys()[0],
                i[i.keys()[0]]['inHost'],
                i[i.keys()[0]]['grapPort']
            )
            string += bs
        with open(vncPath, 'w') as f:
            f.write(string)
        return {'code':200}
    except Exception:
        return {'error':452}

def nodeVncPort():
    try:
        tmp = []
        domL = []
        f = redisMgnt().control(type='select', Dict=['UUID', 'grapPort', 'inHost'], table='domain_machineinfo')
        for i in f:
            domL.append({i[0]: {'grapPort': i[1], 'inHost': i[2]}})
        for i in domL:
            tmp.append(i[i.keys()[0]]['grapPort'])
        cb = redisMgnt()
        cb.control(type='delete',table='vncinfo',)
        cb.control(type='insert',table='vncinfo',Dict={'PORT' : "'{}'".format(json.dumps(tmp))})
        return {'code' : 200}
    except Exception:
        return {'error':452}
def vncPortGet():
    cf = ConfigParser.ConfigParser()
    cf.read("/git_csdn/kvm/src/global.conf")
    port_min = int(cf.get('vnc', 'vnc_port_min'))
    port_max = int(cf.get('vnc', 'vnc_port_max'))
    m = json.loads(redisMgnt().control(type='select',Dict=['PORT'],table='vncinfo')[0][0])
    random = Random()
    rp = random.randint(port_min, port_max)
    if rp in m:
        return vncPortGet()
    else:
        return rp

# network target is use check
def networkTargetUseCheck():
    try:
        a = redisMgnt().control(type='select', Dict=['network', 'UUID'], table='domain_machineinfo')
        redisMgnt().control(type='delete', table='target')
        for i in a:
            UUID = i[1]
            k = json.loads(i[0])
            for s in k:
                target = s[s.keys()[0]]['netTarget']
                redisMgnt().control(type="insert",
                                          Dict={'target_UUID': '"{}"'.format(target), 'dhost_UUID': '"{}"'.format(UUID),
                                                'type': '"network"'}, table='target')
        return {'code' : 200}
    except Exception,msg:
        return {'error': 454}

#get new network target number
def getNetworkTarget():
    try:
        tr = Random().randint(500,5000)
        str = "vif1.{}".format(tr)
        #str = "vif1.65531"
        ff = redisMgnt().control(type="select",Dict=['dhost_UUID'],table='target',Where={'target_UUID':'"{}"'.format(str)})
        if ff:
            return getNetworkTarget()
        else:
            return str
    except Exception,msg:
        print(msg)



