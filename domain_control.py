#-*- coding:utf-8 -*-
from dbMgnt import  redisMgnt
import domain_opera
import xmltodict
import script
import json
import ConfigParser
def checkJsonFormat(raw_msg):
    if isinstance(raw_msg, str):
        try:
            json.loads(raw_msg, encoding='utf-8')
        except ValueError:
            return False
        return True
    else:
        return False

# create XML , must to import command {"hostname","iso","beizhu","memory","disk","network",}
def createMachine(data):
    try:
        print(data)
        machineName = data['hostname']
        inHost = data['host']
        iso = data['iso']
        beizhu = data['beizhu']
        memoryUse = int(data['memory']) * 1024 * 1024
        cpuUse = data['cpu']
        disk = data['disk']
        network = data['network']
        # create a new domain xml
        with open('/git_csdn/kvm/temple/newMachine.xml') as f:
            newXML = f.read()
        domainXML = xmltodict.parse(newXML)
        domainXML['domain']['name'] = machineName
        domainXML['domain']['memory']['#text'] = memoryUse
        domainXML['domain']['currentMemory']['#text'] = memoryUse
        domainXML['domain']['vcpu']['#text'] = cpuUse
        aliveDISK = redisMgnt().control(type="select", Dict=['path', 'image'], table='disk_diskregister',
                                        Where={'UUID': "'{}'".format(disk)})
        dp = "{}{}".format(aliveDISK[0][0], aliveDISK[0][1])
        domainXML['domain']['devices']['disk'][0]['source']['@file'] = dp
        aliveIMAGE = redisMgnt().control(type="select", Dict=['path', 'image'], table='imageregister',
                                         Where={'UUID': '"{}"'.format(iso)})
        sp = "{}{}".format(aliveIMAGE[0][0], aliveIMAGE[0][1])
        domainXML['domain']['devices']['disk'][1]['source']['@file'] = sp
        target = script.getNetworkTarget()
        domainXML['domain']['devices']['interface']['target']['@dev'] = target
        domainXML['domain']['devices']['interface']['source']['@network'] = network
        aliveVNCPort = script.vncPortGet()
        domainXML['domain']['devices']['graphics']['@port'] = aliveVNCPort
        domainXML['domain']['devices']['graphics']['@autoport'] = 'no'
        domainXML['domain']['devices']['graphics']['@keymap'] = 'en-us'
        bronXML = xmltodict.unparse(domainXML)
        # get install host
        if inHost != 'auto':
            k = redisMgnt().control(type="select", Dict=['nodeIP'], table='host_nodeinfo',
                                    Where={'UUID': "'{}'".format(inHost)})
            host = k[0][0]
        if domain_opera.virConn(host).defineXML(bronXML) == 200:
            domain_control_refer(num='onlyHost',UUID=inHost)
            domain_control_monitor(num='only',UUID=redisMgnt().control(type='select',Dict=['UUID'],table='domain_machineinfo',Where={'vName':"'{}'".format(machineName)})[0][0])
            script.vncConfig()
            script.nodeVncPort()
            return {'code' : 200}
        else:
            return {'error': 451}
    except Exception, msg:
        print msg
#刷新所有节点的虚拟机信息
def domain_control_refer(num=None,UUID=None):
    try:
        if num == 'all':
            hostList = [ x[0] for x in  redisMgnt().control(type='select',Dict=['nodeIP'],table="host_nodeinfo") ]
            hostObj = [ domain_opera.virConn(x[0]) for x in  redisMgnt().control(type='select',Dict=['nodeIP'],table="host_nodeinfo") ]
            iL = []
            for d in range(len(hostList)):
                domainObjList = [ domain_opera.domain_edit(object=k) for k in hostObj[d].getAllDomains(flags=0)]
                inHost = hostList[d]
                for i in domainObjList:
                    st = i.isActive()
                    doc = i.dumpxml()
                    xdc = xmltodict.parse(xml_input=doc)
                    xobj = script.domainXMLjx(xml=xdc)
                    diskList = xobj.diskInfo()
                    grphList = xobj.graphicel()
                    netList = xobj.interfaceList()
                    confList = xobj.configInfo()
                    nC = {
                        'UUID': "'{}'".format(i.UUIDString()),
                        'inHost': "'{}'".format(inHost),
                        'vName': "'{}'".format(i.name()),
                        'rStatus': "'{}'".format(st),
                        'MaxMemory': "'{}'".format((confList['MaxMemory'])),
                        'CurMemory':  "'{}'".format(confList['CurMemory']),
                        'MaxCpu':  "'{}'".format(confList['MaxCpu']),
                        'CurCpu':  "'{}'".format(confList['CurCpu']),
                        'grapType':  "'{}'".format(grphList['grapType']),
                        'grapPort':  "'{}'".format(grphList['grapPort']),
                        'grapCType':  "'{}'".format(grphList['grapCType']),
                        'disk':  "'{}'".format(json.dumps(diskList)),
                        'network':  "'{}'".format(json.dumps(netList))
                    }
                    iL.append(nC)
            redisMgnt().control(type='delete',table='domain_machineinfo')
            for i in iL:
                redisMgnt().control(type="insert",Dict=i,table='domain_machineinfo')
            return {"code" : 200}
        elif num == 'only':
            hostList = [x[0] for x in redisMgnt().control(type='select', Dict=['nodeIP'], table="host_nodeinfo")]
            LK = []
            for k in range(len(hostList)):
                hostUUID = [ x.UUIDString() for x in domain_opera.virConn(hostList[k]).getAllDomains(flags=0)]
                hostObj = [domain_opera.domain_edit(object=x) for x in domain_opera.virConn(hostList[k]).getAllDomains(flags=0)]
                inHost = hostList[k]
                if hostObj:
                    for i in hostUUID:
                        if UUID in hostUUID:
                            ind = hostUUID.index(UUID)
                            OBJ = hostObj[ind]
                            st = OBJ.isActive()
                            doc = OBJ.dumpxml()
                            xdc = xmltodict.parse(xml_input=doc)
                            xobj = script.domainXMLjx(xml=xdc)
                            diskList = xobj.diskInfo()
                            grphList = xobj.graphicel()
                            netList = xobj.interfaceList()
                            confList = xobj.configInfo()
                            nC = {
                                'UUID': "'{}'".format(OBJ.UUIDString()),
                                'inHost': "'{}'".format(inHost),
                                'vName': "'{}'".format(OBJ.name()),
                                'rStatus': "'{}'".format(st),
                                'MaxMemory': "'{}'".format((confList['MaxMemory'])),
                                'CurMemory': "'{}'".format(confList['CurMemory']),
                                'MaxCpu': "'{}'".format(confList['MaxCpu']),
                                'CurCpu': "'{}'".format(confList['CurCpu']),
                                'grapType': "'{}'".format(grphList['grapType']),
                                'grapPort': "'{}'".format(grphList['grapPort']),
                                'grapCType': "'{}'".format(grphList['grapCType']),
                                'disk': "'{}'".format(json.dumps(diskList)),
                                'network': "'{}'".format(json.dumps(netList))
                            }
                            LK.append(nC)
                            break
                        else:
                            continue
            for i in LK:
                redisMgnt().control(type='delete',table='domain_machineinfo',Where={'UUID':"'{}'".format(UUID)})
                redisMgnt().control(type="insert",Dict=i,table='domain_machineinfo')
            return {"code" : 200}
        if num == 'onlyHost':
            #get the UUID -> ip
            inHost = redisMgnt().control(type='select',Dict=['nodeIP'],table='host_nodeinfo',Where={'UUID':"'{}'".format(UUID)})[0][0]
            #bron host object
            hostObj = [ domain_opera.domain_edit(object=x) for x in domain_opera.virConn(inHost).getAllDomains(flags=0)]
            if hostObj:
                domainObjectInfo = []
                for domainObject in hostObj:
                    st = domainObject.isActive()
                    doc = domainObject.dumpxml()
                    xdc = xmltodict.parse(xml_input=doc)
                    xobj = script.domainXMLjx(xml=xdc)
                    diskList = xobj.diskInfo()
                    grphList = xobj.graphicel()
                    netList = xobj.interfaceList()
                    confList = xobj.configInfo()
                    nC = {
                        'UUID': "'{}'".format(domainObject.UUIDString()),
                        'inHost': "'{}'".format(inHost),
                        'vName': "'{}'".format(domainObject.name()),
                        'rStatus': "'{}'".format(st),
                        'MaxMemory': "'{}'".format((confList['MaxMemory'])),
                        'CurMemory': "'{}'".format(confList['CurMemory']),
                        'MaxCpu': "'{}'".format(confList['MaxCpu']),
                        'CurCpu': "'{}'".format(confList['CurCpu']),
                        'grapType': "'{}'".format(grphList['grapType']),
                        'grapPort': "'{}'".format(grphList['grapPort']),
                        'grapCType': "'{}'".format(grphList['grapCType']),
                        'disk': "'{}'".format(json.dumps(diskList)),
                        'network': "'{}'".format(json.dumps(netList))
                    }
                    domainObjectInfo.append(nC)
                for i in domainObjectInfo:
                    redisMgnt().control(type='delete',table='domain_machineinfo',Where={'UUID':"{}".format(i['UUID'])})
                    redisMgnt().control(type='insert',table='domain_machineinfo',Dict=i)
                return {"code" : 200}
    except Exception,msg:
        print(msg)
        return {"error" : 454}



#刷新监控信息
def domain_control_monitor(num=None,UUID=None):
    try:
        if num == 'all':
            #Generate Host object  list
            hostObj = [domain_opera.virConn(x[0]) for x in
                       redisMgnt().control(type='select', Dict=['nodeIP'], table="host_nodeinfo")]
            #start cycle
            domainMonitorInfo = []
            for i in hostObj:
                for k in [ x for x in i.getAllDomains(flags=0)]:
                    domainObj = domain_opera.domain_edit(object=k)
                    if domainObj.isActive() == 0:
                        tmp = {
                         'UUID' : "'{}'".format(domainObj.UUIDString()),
                         'cpuLV': "'None'",
                         'memLv': "'None'",
                         'rss': "'None'",
                         'vName': "'{}'".format(domainObj.name()),
                         'rStatus': "'None'",
                         'disk': "'None'",
                         'network': "'None'"}
                        domainMonitorInfo.append(tmp)
                    else:
                        cl = domainObj.getcpuInfo()
                        ml = domainObj.getmemoryInfo()
                        di = redisMgnt().control(type='select',Dict=['network','disk'],table='domain_machineinfo',Where={'UUID':"'{}'".format(domainObj.UUIDString())})
                        f = json.loads(di[0][0])[0]
                        nl = domainObj.getinterfaceInfo(gdict=[f[f.keys()[0]]['netTarget']])
                        diskL = json.loads(di[0][1])
                        diski = []
                        for i in diskL:
                            if i[i.keys()[0]]['devType'] == 'disk':
                                diski.append(i.keys()[0])
                            else:
                                pass
                        dl = domainObj.getdiskInfo(gdict=diski)
                        dic = {
                            'cpuLV': "'%.2f%%'" % (
                                float(cl['system_time'] + float(cl['user_time'])) / cl['cpu_time'] / cl['cpuNr'] * 100),
                            'rStatus': "'running'",
                        }
                        if ml['virito'] == 0:
                            dic['memLv'] = "'None'"
                            dic['rss'] = "'{}'".format(ml['rss'])
                        elif ml['virito'] == 1:
                            dic['memLv'] = "'%.2f%%'" % (
                                (float(ml['available']) - float(ml['unused'])) / float(ml['available']) * 100)
                            dic['rss'] = "'{}'".format(ml['rss'])
                        dic['vName'] = "'{}'".format(domainObj.name())
                        dic['UUID'] = "'{}'".format(domainObj.UUIDString())
                        dic["network"] = "'{}'".format(json.dumps(nl))
                        dic["disk"] = "'{}'".format(json.dumps(dl))
                        domainMonitorInfo.append(dic)
            redisMgnt().control(type='delete',table='domain_checkinfo')
            for i in  domainMonitorInfo:
                redisMgnt().control(type='insert',Dict=i,table="domain_checkinfo")
            return {'code' : '200'}
        elif num == 'only':
            hostList = [x[0] for x in redisMgnt().control(type='select', Dict=['nodeIP'], table="host_nodeinfo")]
            domainMonitorInfo = []
            for k in range(len(hostList)):
                hostUUID = [x.UUIDString() for x in domain_opera.virConn(hostList[k]).getAllDomains(flags=0)]
                hostObj = [domain_opera.domain_edit(object=x) for x in
                           domain_opera.virConn(hostList[k]).getAllDomains(flags=0)]
                if UUID in hostUUID:
                    ind = hostUUID.index(UUID)
                    domainObj = hostObj[ind]
                    if domainObj.isActive() == 0:
                        tmp = {
                            'UUID': "'{}'".format(domainObj.UUIDString()),
                            'cpuLV': "'None'",
                            'memLv': "'None'",
                            'rss': "'None'",
                            'vName': "'{}'".format(domainObj.name()),
                            'rStatus': "'None'",
                            'disk': "'None'",
                            'network': "'None'"}
                        domainMonitorInfo.append(tmp)
                    else:
                        cl = domainObj.getcpuInfo()
                        ml = domainObj.getmemoryInfo()
                        di = redisMgnt().control(type='select', Dict=['network', 'disk'],
                                                 table='domain_machineinfo',
                                                 Where={'UUID': "'{}'".format(domainObj.UUIDString())})
                        f = json.loads(di[0][0])[0]
                        nl = domainObj.getinterfaceInfo(gdict=[f[f.keys()[0]]['netTarget']])
                        diskL = json.loads(di[0][1])
                        diski = []
                        for i in diskL:
                            if i[i.keys()[0]]['devType'] == 'disk':
                                diski.append(i.keys()[0])
                            else:
                                pass
                        dl = domainObj.getdiskInfo(gdict=diski)
                        dic = {
                            'cpuLV': "'%.2f%%'" % (
                                float(cl['system_time'] + float(cl['user_time'])) / cl['cpu_time'] / cl[
                                    'cpuNr'] * 100),
                            'rStatus': "'running'",
                        }
                        if ml['virito'] == 0:
                            dic['memLv'] = "'None'"
                            dic['rss'] = "'{}'".format(ml['rss'])
                        elif ml['virito'] == 1:
                            dic['memLv'] = "'%.2f%%'" % (
                                (float(ml['available']) - float(ml['unused'])) / float(ml['available']) * 100)
                            dic['rss'] = "'{}'".format(ml['rss'])
                        dic['vName'] = "'{}'".format(domainObj.name())
                        dic['UUID'] = "'{}'".format(domainObj.UUIDString())
                        dic["network"] = "'{}'".format(json.dumps(nl))
                        dic["disk"] = "'{}'".format(json.dumps(dl))
                        domainMonitorInfo.append(dic)
            redisMgnt().control(type='delete',table='domain_checkinfo',Where={'UUID':"'{}'".format(UUID)})
            for i in domainMonitorInfo:
                redisMgnt().control(type='insert', Dict=i, table="domain_checkinfo")
                return {'code': '200'}
    except Exception,msg:
        print(msg)
        return {"error" : 454}


#host stoarge info update
def storageUpdate():
    try:
        nl = [ x[0] for x in redisMgnt().control(type='select',Dict=['nodeIP'],table='host_nodeinfo')]
        cf = ConfigParser.ConfigParser()
        cf.read("/git_csdn/kvm/conf/kvm.conf")
        n = cf.get("storage","pool_name")
        redisMgnt().control(type='delete', table='storageinfo')
        for i in nl:
            obj = domain_opera.virConn(str(i)).getStoragePoolObject(str=n,type='name')
            m = domain_opera.storage_edit(_obj=obj).info()
            f = {}
            f['UUID'] = domain_opera.storage_edit(_obj=obj).uuid()
            f['inHost'] = i
            f['t_Usage'] = m['Usage']
            f['t_All'] = m['All']
            f['t_Free'] = m['Free']
            for k in f.keys():
                f[k] = "'{}'".format(f[k])
            redisMgnt().control(type='insert',Dict=f,table='storageinfo')
        return {'code' : 200}
    except Exception,msg:
        return {'error' : 452}

#domain crontol function
def domain_crontrol_function(UUID=None,ACTION=None,Dict=None):
    try:
        UUID = str(UUID).strip("\'")
        ACTION = ACTION
        domainInhost = redisMgnt().control(type='select',Dict=['inHost'],table='domain_machineinfo',Where={'UUID' : "'{}'".format(UUID)})[0][0]
        domainObject=domain_opera.virConn(domainInhost).getDomainObject(str=UUID,type='uuid')
        if ACTION == 'start':
            if domain_opera.domain_edit(object=domainObject).start() == 200:
                redisMgnt().control(type='update',Dict={'rStatus' : "'1'"},table='domain_machineinfo',Where={'UUID':"'{}'".format(UUID)})
                return {'code' : 200}
            else:
                return {'error' : 455}
        elif ACTION == 'destroy':
            if domain_opera.domain_edit(object=domainObject).destroy() == 200:
                redisMgnt().control(type='update', Dict={'rStatus': "'0'"}, table='domain_machineinfo',
                                Where={'UUID': "'{}'".format(UUID)})
                return {'code': 200}
            else:
                return {'error':455}
        elif ACTION == 'restart':
            if domain_opera.domain_edit(object=domainObject).reboot() == 200:
                redisMgnt().control(type='update', Dict={'rStatus': "'0'"}, table='domain_machineinfo',
                                    Where={'UUID': "'{}'".format(UUID)})
                return {'code': 200}
            else:
                return {'error':455}
        elif ACTION == 'delete':
            if domain_opera.domain_edit(object=domainObject).undefine() == 200:
                redisMgnt().control(type="delete", table='domain_machineinfo', Where={'UUID': "'{}'".format(UUID)})
                redisMgnt().control(type="delete", table='domain_checkinfo', Where={'UUID': "'{}'".format(UUID)})
                redisMgnt().control(type="update", table='disk_diskregister', Dict={'st': "'N'", 'Dhost': "' '"},
                                    Where={'Dhost': "'{}'".format(UUID)})
                return {'code': 200}
            else:
                return {'error':455}
        elif ACTION == 'ejectCDROM':
            pass

    except Exception,msg:
        print(msg)
        return {'error' : 453 }


