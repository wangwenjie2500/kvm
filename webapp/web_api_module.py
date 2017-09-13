#-*- coding:utf-8 -*-
from src import host_register
import logging
import re
from src.dbMgnt import redisMgnt
import json
from src import domain_control
from src import script
from src import disk_control


def checkJsonFormat(raw_msg):
    if isinstance(raw_msg, str):
        try:
            json.loads(raw_msg, encoding='utf-8')
        except ValueError:
            return False
        return True
    else:
        return False

class host:
    #host register function
    def hostRegister(self,tuple):
        try:
            str = tuple
            type = re.findall("(?<=\&)(.+?)(?=\&)", str)[0].split('=')[1]
            if type == 'register':
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "'{}'".format(ti[1])
                rcode = host_register.hostRegister(key['client'])
                if rcode == 200:
                    return {'code' : 200}
            if type == 'delete':
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "'{}'".format(ti[1])
                rcode = host_register.hostDelete(key['UUID'])
                if rcode == 200:
                    return {'code':200}
        except Exception,msg:
            print(msg)
            return {"error": 452}

    #host list
    def hostSelect(self,tuple):
        try:
            str = tuple
            type = re.findall("(?<=\&)(.+?)(?=\&)", str)[0].split('=')[1]
            if type == 'all':
                cod = re.findall("(?<=\%)(.+?)(?=\%)", str)
                k = redisMgnt().control(type='select', Dict=cod, table='host_nodeinfo')
                fk = []
                for i in k:
                    tmp = []
                    for m in range(len(i)):
                        if checkJsonFormat(i[m]):
                            g = json.loads(i[m])
                            tmp.append(g)
                        else:
                            tmp.append(i[m])
                    fd = dict(zip(cod, tmp))
                    fk.append(fd)
                return fk
            if type == 'only':
                cod = re.findall("(?<=\%)(.+?)(?=\%)", str)
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                # sheng cheng where zi duan
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "'{}'".format(ti[1])
                k = redisMgnt().control(type='select', Dict=cod, table='host_nodeinfo', Where=key)[0]
                tmp = []
                for m in range(len(k)):
                    if checkJsonFormat(k[m].encode('utf-8')):
                        g = json.loads(k[m])
                        tmp.append(g)
                    else:
                        tmp.append(k[m])
                fd = dict(zip(cod, tmp))
                return fd
        except Exception,msg:
            print(msg)
            return {"error":452}



class domain:
    def domainControl(self,tuple):
        try:
            str = tuple
            #get num zi duan de zhi
            type = re.findall("(?<=\&)(.+?)(?=\&)", str)[0].split('=')[1]
            if type == 'all':
                cod = re.findall("(?<=\%)(.+?)(?=\%)", str)
                k = redisMgnt().control(type='select', Dict=cod, table='domain_machineinfo')
                fk = []
                for i in k:
                    tmp = []
                    for m in range(len(i)):
                        if checkJsonFormat(i[m]):
                            g = json.loads(i[m])
                            tmp.append(g)
                        else:
                            tmp.append(i[m])
                    fd = dict(zip(cod, tmp))
                    fk.append(fd)
                return fk
            if type == 'only':
                cod = re.findall("(?<=\%)(.+?)(?=\%)", str)
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                # sheng cheng where zi duan
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "'{}'".format(ti[1])
                k = redisMgnt().control(type='select', Dict=cod, table='domain_machineinfo', Where=key)[0]
                tmp = []
                for m in range(len(k)):
                    if checkJsonFormat(k[m].encode('utf-8')):
                        g = json.loads(k[m])
                        tmp.append(g)
                    else:
                        tmp.append(k[m])
                fd = dict(zip(cod, tmp))
                return fd


        except Exception,msg:
            pass
    def domainCrontolInfo(self,tuple):
        try:
            str = tuple
            # get num zi duan de zhi
            type = re.findall("(?<=\&)(.+?)(?=\&)", str)[0].split('=')[1]
            bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
            key = {}
            for i in bd:
                key[i.split("=")[0].encode('utf-8')] = i.split("=")[1].encode('utf-8')
            if type == 'createMachine':
                f = domain_control.createMachine(data=key)
                return f
            else:
                f = domain_control.domain_crontrol_function(ACTION=type,UUID=key['UUID'])
                return f
        except Exception,msg:
            print(msg)


    def domainFlush(self,tuple):
        try:
            str = tuple
            type = re.findall("(?<=\&)(.+?)(?=\&)", str)[0].split('=')[1]
            if type == 'allDomain':
                return  domain_control.domain_control_refer(num='all')
            elif type == 'onlyDomain':
                cod = re.findall("(?<=\$)(.+?)(?=\$)", str)[0]
                UID = cod.split("=")[1]
                return domain_control.domain_control_refer(num='only',UUID=UID)
            elif type == 'onlyHost':
                cod = re.findall("(?<=\$)(.+?)(?=\$)", str)[0]
                UID = cod.split("=")[1]
                return domain_control.domain_control_refer(num='onlyHost', UUID=UID)
            elif type == 'allCheck':
                return domain_control.domain_control_monitor(num='all')
            elif type == 'onlyCheck':
                cod = re.findall("(?<=\$)(.+?)(?=\$)", str)[0]
                UID = cod.split("=")[1]
                return domain_control.domain_control_monitor(num='only',UUID=UID)
            elif type == 'vncinfo':
                return script.nodeVncPort()
            elif type == 'vncToken':
                return script.vncConfig()
            elif type == 'networkTarget':
                return script.networkTargetUseCheck()
        except Exception,msg:
            print(msg)
            return {"error": 452}



class disk:
    def __init__(self):
        pass
    def diskControl(self,tuple):
        try:
            str = tuple
            type = re.findall("(?<=\&)(.+?)(?=\&)", str)[0].split('=')[1]
            if type == 'all':
                cod = re.findall("(?<=\%)(.+?)(?=\%)", str)
                k = redisMgnt().control(type='select', Dict=cod, table='disk_diskregister')
                fk = []
                for i in k:
                    tmp = []
                    for m in range(len(i)):
                        if checkJsonFormat(i[m]):
                            g = json.loads(i[m])
                            tmp.append(g)
                        else:
                            tmp.append(i[m])
                    fd = dict(zip(cod, tmp))
                    fk.append(fd)
                return fk
            elif type == 'only':
                cod = re.findall("(?<=\%)(.+?)(?=\%)", str)
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                # sheng cheng where zi duan
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "'{}'".format(ti[1])
                k = redisMgnt().control(type='select', Dict=cod, table='disk_diskregister', Where=key)[0]
                tmp = []
                for m in range(len(k)):
                    if checkJsonFormat(k[m].encode('utf-8')):
                        g = json.loads(k[m])
                        tmp.append(g)
                    else:
                        tmp.append(k[m])
                fd = dict(zip(cod, tmp))
                return fd
            if type == 'create':
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                # sheng cheng where zi duan
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "{}".format(ti[1])
                rcode = disk_control.diskCreate(name=key['name'],size=key['size'])
                if rcode == 200:
                    return {'code' : 200}
            if type == 'delete':
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                # sheng cheng where zi duan
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "{}".format(ti[1])
                rcode = disk_control.diskDelete(UUID=key['UUID'])
                if rcode == 200:
                    return {'code' : 200}
                else:
                    return {'error' : 452}
            if type == 'resize':
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                # sheng cheng where zi duan
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "{}".format(ti[1])
                rcode = disk_control.diskResize(UUID=key['UUID'],size=key['size'])
                if rcode == 200:
                    return {'code' : 200}
                else:
                    return rcode
        except Exception,msg:
            return {"error": 452}

class image:
    def __init__(self):
        pass

    def imageControl(self,tuple):
        try:
            str = tuple
            type = re.findall("(?<=\&)(.+?)(?=\&)", str)[0].split('=')[1]
            if type == 'all':
                cod = re.findall("(?<=\%)(.+?)(?=\%)", str)
                k = redisMgnt().control(type='select', Dict=cod, table='imageregister')
                fk = []
                for i in k:
                    tmp = []
                    for m in range(len(i)):
                        if checkJsonFormat(i[m]):
                            g = json.loads(i[m])
                            tmp.append(g)
                        else:
                            tmp.append(i[m])
                    fd = dict(zip(cod, tmp))
                    fk.append(fd)
                return fk
            elif type == 'only':
                cod = re.findall("(?<=\%)(.+?)(?=\%)", str)
                bd = re.findall("(?<=\$)(.+?)(?=\$)", str)
                key = {}
                # sheng cheng where zi duan
                for i in bd:
                    ti = i.split('=')
                    key[ti[0]] = "'{}'".format(ti[1])
                k = redisMgnt().control(type='select', Dict=cod, table='imageregister', Where=key)[0]
                tmp = []
                for m in range(len(k)):
                    if checkJsonFormat(k[m].encode('utf-8')):
                        g = json.loads(k[m])
                        tmp.append(g)
                    else:
                        tmp.append(k[m])
                fd = dict(zip(cod, tmp))
                return fd
        except Exception,msg:
            print(msg)