#-*- coding:utf-8 -*-
from dbMgnt import  redisMgnt
import domain_opera
import xmltodict
import script
import json
import subprocess
import ConfigParser
from random import Random
import datetime

def diskRegister(path=None):
    def createName():
        str1 = ""
        chars = '1234567890ABCDEFabcdef'
        length = len(chars) - 1
        random = Random()
        for i in range(10):
            str1 += chars[random.randint(0, 13)]
        return str1
    id = createName()
    now = datetime.datetime.now()
    time = now.strftime("%Y:%m:%d %H:%M:%S")
    cf = ConfigParser.ConfigParser()
    cf.read("/git_csdn/kvm/src/global.conf")
    pool_name = cf.get("storage","pool_name")
    a = str(path).split('/')
    name = a[-1]
    del a[0]
    del a[-1]
    path = "/"
    for i in a:
        path += i + "/"
    rg = [{
        'image': name,
        'path': path,
        'time': "'{}'".format(time),
        'st' : "'N'",
        'UUID' : "'{}'".format(id),
    }]
    pyHost = redisMgnt().control(type='select',Dict=['UUID','nodeIP'],table='host_nodeinfo',Where={'nodeSTATUS':"'0'"})
    for i in [ m[1] for m in pyHost ]:
        obj = domain_opera.virConn(i).getStoragePoolObject(pool_name,"name")
        domain_opera.storage_edit(obj).refer()
    hl = [ m[1] for m in pyHost]
    ho = hl[Random().randint(0,len(hl) -1 )]
    volObject = domain_opera.virConn(ho).getVolObj(rg[0]['path'] + rg[0]['image'])
    rg[0]['AllSize'] = "'{}'".format(domain_opera.vol_edit(volObject).size()["AllSize"])
    rg[0]['UseSize'] = "'{}'".format(domain_opera.vol_edit(volObject).size()["UseSize"])
    rg[0]['image'] = "'{}'".format(rg[0]['image'])
    rg[0]['path'] = "'{}'".format(rg[0]['path'])
    rcode = redisMgnt().control(type='insert',Dict=rg[0],table='disk_diskregister')
    if rcode == 200:
        return {'code' : 200}

def diskRefer(**kwargs):
    try:
        imageName = kwargs["image"]
        inhost = [x[0] for x in redisMgnt().control(type="select", Dict=['nodeIP'], table="host_nodeinfo")]
        path = "{}{}".format(redisMgnt().control(type="select", Dict=['path'], table="disk_diskregister",
                                                 Where={'image': '"{}"'.format(imageName)})[0][0], imageName)
        rn = Random().randint(0, len(inhost) - 1)
        obj = domain_opera.virConn(inhost[rn]).getVolObj(path)
        AllSize = domain_opera.vol_edit(obj).size()["AllSize"]
        UseSize = domain_opera.vol_edit(obj).size()["UseSize"]
        # print(AllSize)
        redisMgnt().control(type="update",Dict={'AllSize': '"{}"'.format(AllSize), 'UseSize': '"{}"'.format(UseSize)},table="disk_diskregister", Where={'image': '"{}"'.format(imageName)})
        return 200
    except Exception, msg:
        print(msg)

#disk is use check
def diskUseCheck():
    a1 = redisMgnt().control(type='select',Dict=['UUID'],table='domain_machineinfo')
    a = [ x[0] for x in a1]
    _tmp = {}
    m = [ x[0] for x in redisMgnt().control(type='select',Dict=['disk'],table='domain_machineinfo')]
    for k in a:
        for f in m:
            f = json.loads(f)
            for i in f:
                if i[i.keys()[0]]["devType"] == 'disk':
                    f = i[i.keys()[0]]["devPath"]
                    a = f.split("/")
                    name = a[-1]
                    del a[-1]
                    path = ""
                    for i in a:
                        path += i + "/"
                    DescHost = k
                    _tmp['{}{}'.format(path,name)] = DescHost
    disk1 = redisMgnt().control(type="select", table="disk_diskregister",
                                      Dict=['path', 'image', 'Dhost', 'st', 'UUID'])
    diskList = {}
    for i in disk1:
        diskList[i[4]] = {'path': i[0], 'image': i[1], 'Dhost': i[2], 'st': i[3]}
    for m in diskList.keys():
        str = "{}{}".format(diskList[m]['path'],diskList[m]['image'])
        if str in [ x for x in _tmp.keys()]:
            diskList[m]['st'] = "'Y'"
            diskList[m]['Dhost'] = "'{}'".format(_tmp[str])
        else:
            diskList[m]['st'] = "'N'"
            diskList[m]['Dhost'] = "' '"
        if diskRefer(image=diskList[m]['image']) == 200:
            diskList[m]['path'] = "'{}'".format(diskList[m]['path'])
            diskList[m]['image'] = "'{}'".format(diskList[m]['image'])
            redisMgnt().control(type='update',Dict=diskList[m],table='disk_diskregister',Where={'UUID':"'{}'".format(m)})

def diskCreate(**kwargs):
    try:
        type = "qcow2"
        name = kwargs["name"]
        size = kwargs["size"]
        cf = ConfigParser.ConfigParser()
        cf.read("/git_csdn/kvm/src/global.conf")
        image_path = cf.get('storage', 'pool_path')
        str = "qemu-img create -f {} {}/{} {}G".format(type, image_path, name, size)
        subprocess.Popen(str, shell=True, stdout=subprocess.PIPE)
        diskRegister("{}/{}.img".format(image_path, name))
        return 200
    except Exception:
        return {'error': 452}

def diskResize(**kwargs):
    try:
        UUID = kwargs["UUID"]
        size = int(kwargs["size"]) * 1024 * 1024 * 1024
        inhost = [ x[0] for x in redisMgnt().control(type="select",Dict=['nodeIP'],table="host_nodeinfo") ]
        f = redisMgnt().control(type="select", Dict=['path', 'image'], table="disk_diskregister",
                                Where={'UUID': '"{}"'.format(UUID)})
        path = f[0][0] + f[0][1]
        rn = Random().randint(0,len(inhost) - 1)
        obj = domain_opera.virConn(inhost[rn]).getVolObj(path)
        #print domainOpera.vol_edit(obj).size();
        domain_opera.vol_edit(obj).resize(size)
        #print domainOpera.vol_edit(obj).size();
        def diskRefer(**kwargs):
            try:
                UUID = kwargs["image"]
                inhost = [x[0] for x in redisMgnt().control(type="select", Dict=['nodeIP'], table="host_nodeinfo")]
                f = redisMgnt().control(type="select", Dict=['path', 'image'], table="disk_diskregister",
                                        Where={'UUID': '"{}"'.format(UUID)})
                path = f[0][0] + f[0][1]
                rn = Random().randint(0, len(inhost) - 1)
                obj = domain_opera.virConn(inhost[rn]).getVolObj(path)
                AllSize = domain_opera.vol_edit(obj).size()["AllSize"]
                UseSize = domain_opera.vol_edit(obj).size()["UseSize"]
                if AllSize * 1024 * 1024 * 1024 != kwargs['size']:
                    return diskRefer(image=kwargs['image'], size=kwargs['size'])
                else:
                    # print(AllSize)
                    redisMgnt().control(type="update",
                                        Dict={'AllSize': '"{}"'.format(AllSize), 'UseSize': '"{}"'.format(UseSize)},
                                        table="disk_diskregister", Where={'UUID': '"{}"'.format(UUID)})
                    return 200
            except Exception,msg:
                return {'error' : 451}
        recode = diskRefer(image=UUID,size=size)
        if recode == 200:
            return {'code' : 200}
        else:
            return recode
    except Exception,msg:
        print(msg)
def imageRegister(path=None,SysType=None):
    def createName():
        str1 = ""
        chars = 'abcdHIGKL1234567890'
        length = len(chars) - 1
        random = Random()
        for i in range(10):
            str1 += chars[random.randint(0, 13)]
        return str1
    id = createName()
    now = datetime.datetime.now()
    time = now.strftime("%Y:%m:%d %H:%M:%S")
    cf = ConfigParser.ConfigParser()
    cf.read("/git_csdn/kvm/conf/kvm.conf")
    image_path = cf.get('image', 'pool_path')
    a = str(path).split('/')
    name = a[-1]
    del a[0]
    del a[-1]
    path = "/"
    for i in a:
        path+= i + "/"
    rg = {
        'image' : '"{}"'.format(name),
        'path' : '"{}"'.format(path),
        'time' : '"{}"'.format(time),
        'UUID' : '"{}"'.format(id),
        'systemType' : '"{}"'.format(SysType),
    }
    redisMgnt().control(type='insert',Dict=rg,table="imageregister")

def diskDelete(**kwargs):
    try:
        UUID = kwargs["UUID"]
        inhost = [x[0] for x in redisMgnt().control(type="select", Dict=['nodeIP'], table="host_nodeinfo")]
        f = redisMgnt().control(type="select", Dict=['path','image'], table="disk_diskregister",
                                                 Where={'UUID': '"{}"'.format(UUID)})
        path = f[0][0] + f[0][1]
        rn = Random().randint(0, len(inhost) - 1)
        obj = domain_opera.virConn(inhost[rn]).getVolObj(path)
        domain_opera.vol_edit(obj).delete()
        redisMgnt().control(type="delete",table="disk_diskregister",Where={'UUID':'"{}"'.format(UUID)})
        return 200
    except Exception,msg:
        print(msg)
        return 202
