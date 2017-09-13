# -*- coding:utf-8 -*-
import libvirt


"""
create a kvm hypervisor connection format for 'driver+path'
Type : local/remote
    local : connection localhost hypervisor : defaults connection format : qemu:///system
    remote : connection remote hypervisor , defaults connection format : qemu+ssh://user@host/system
"""

"""
input a domains info (id or name or uuid )
 return the domains object
"""
#create a libvirt conn

class virConn():
    def __init__(self,*argv):
        try:
            self.conn = libvirt.open('qemu+ssh://root@{}/system'.format(argv[0]))
        except Exception,msg:
            print(msg)

    #get the host run all domain,and return a list, the fun() must host,user
    def getAllDomains(self,flags=None):
        try:
            getList = self.conn.listAllDomains()
            if flags == 1:
                return [x.name() for x in getList]
            elif flags == 0:
                return [x for x in getList]
        except Exception,msg:
            print(msg)
            return False
    #输入一个path,获取该卷的操作对象
    def getVolObj(self,path):
        try:
            obj = self.conn.storageVolLookupByPath(path=path)
            return obj
        except Exception,msg:
            print(msg)
    #加载一个xml
    def defineXML(self,xml):
        try:
            self.conn.defineXML(xml)
            return 200
        except Exception,msg:
            return 451

    #entry a domain info (name,uuid,id) return the domain object
    def getDomainObject(self,str,type):
        try:
            if type == 'id':
                object = self.conn.lookupByID(str)
                return object
            if type == 'uuid':
                object = self.conn.lookupByUUIDString(str)
                return object
            if type == 'name':
                object = self.conn.lookupByName(str)
                return object

        except Exception,msg:
            print(msg)

    def getStoragePoolObject(self, str, type):
        try:
            if type == 'name':
                object = self.conn.storagePoolLookupByName(str)

            if type == 'uuid':
                object = self.conn.storagePoolLookupByUUidString(str)
            return object
        except Exception,msg:
            print(msg)
    def getinfo(self):
        try:
            f = self.conn.getInfo()
            return f
        except Exception,msg:
            print(msg)

    def getInterfaceObject(self,str,type):
        try:

            if type == 'mac':
                object = self.conn.interfaceLookupByMACString(str)
                return object

            if type == 'name':
                object = self.conn.interfaceLookupByName(str)
                return object
        except Exception,msg:
            print(msg)
            return False

    def getDomainId(self,str):
        try:
            object = self.conn.listDomainsID()
            return object
        except Exception,msg:
            print(msg)
            return False

    def getHostname(self):
        try:
            object = self.conn.getHostname()
            return object
        except Exception,msg:
            print(msg)

    def getVersion(self):
        try:
            ob = self.conn.getVersion()
            return ob
        except Exception,msg:
            print(msg)

    def getMemoryStats(self):
        try:
            ob = self.conn.getMemoryStats(cellNum=-1) #get host memory status cellNum=-1 get free,total.cache,swap,cellNum=0 get free,total
            return ob
        except Exception,msg:
            print(msg)

    def getNetworks(self):
        try:
            ob = self.conn.listAllNetworks(flags=0)
            if ob:
                return [x.name() for x in ob]   #get host all network bridge name
        except Exception,msg:
            print(msg)

    def getInterfaces(self):
        try:
            ob = self.conn.listAllInterfaces(flags=0)
            return [x.name() for x in ob]     #get host all network interface name
        except Exception,msg:
            print(msg)

    def getDevices(self):
        try:
            ob = self.conn.listAllDevices(flags=0)  #get host all
            return [ x.name() for x in ob ]
        except Exception,msg:
            print(msg)

    def getStoragePools(self):
        try:
            ob = self.conn.listAllStoragePools(flags=0)
            return [ x.name() for x in ob]
        except Exception,msg:
            print(msg)

"""
    the class edit domains object
"""


class domain_edit:
    def __init__(self, object=None, **kwargs):
        self.domain_object = object

    def isActive(self):
        status = self.domain_object.isActive()
        return status

    def stop(self):
        status = self.domain_object.shutdown()
        if status == 0:
            return 200

    def start(self):
        status = self.domain_object.create()
        if status == 0:
            return 200


    def destroy(self):
        status = self.domain_object.destroy()
        if status == 0:
            return 200

    def reboot(self):
        status = self.domain_object.reboot()
        if status == 0:
            return 200

    def suspend(self):
        status = self.domain_object.suspend()
        if status == 0:
            return 200
            #

    def resume(self):
        status = self.domain_object.resume()
        if status == 0:
            return 200
            # 保存域当前状态

    def save(self, to=None):
        if to == 'None':
            return 506
        else:
            status = self.domain_object.save(to=to)
            if status == 0:
                return 200
                # 从xml字符串中定义这个域

    # def define(self, xml=None):
    #     if xml == 'None':
    #         return 506
    #     else:
    #         conn = create_con()
    #         dom_obj = conn.defineXML(xml=xml)
    #         status = dom_obj.createWithFlags(0)
    #         if status == 0:
    #             return 200
    #             # 取消定义域

    def undefine(self):
        status = self.domain_object.undefine()
        if status == 0:
            return 200

    def dumpxml(self):
        xmlstring = self.domain_object.XMLDesc()
        return xmlstring

    def UUIDString(self):
        UUID = self.domain_object.UUIDString()
        return UUID

    def name(self):
        name = self.domain_object.name()
        return name

    def getcpuInfo(self):
        # self.domain_object.info() 这个方法会返回一个列表，这个列表包含4个值从左到右分别为域状态,启动为1，关闭为0，最大内存，当前内存，cpu颗数，以及CPU总时间
        # self.domain_object.getCPUStats('1') 这个方法会返回一个列表，该列表中包含使用CPU的使用信息，每颗CPU一个字典，字典中包含key,{'cpu_time'},
        # {'system_time'},{'user_time'} 分别为CPU总时间，系统占用CPU时间，用户占用CPU时间，系统CPU消耗率为(User_Time + System_time)/Cpu_time ,
        # 如果想更精确需要除以CPU颗数获得平均值
        b = self.domain_object.info()[3]
        a = self.domain_object.getCPUStats('1')
        a1 = a[0]['system_time']
        a3 = a[0]['user_time']
        a2 = a[0]['cpu_time']
        # return '%.2f%%' % (float(a1) / float(a2) / a3 * 100)
        return {
            'cpuNr': b,
            'cpu_time': a2,
            'system_time': a1,
            'user_time': a3
        }

    def getmemoryInfo(self):
        # self.domain_object.memoryStats() 这个方法会返回一个列表，如果该虚拟机没有开启virito支持，那么会返回一个JSON包含三个key,分别为actual,swap_in,rss,
        # actual参数为虚拟机启动是占用系统内存，rss参数为虚拟机当前占用宿主机的内存，swap_in，只虚拟机当前占用宿主机缓存，虚拟机开启virito支持(开启方法见帮助文档),则会返回swap_out,
        # available,actual,major_fault,major_fault,swap_in,unused,minor_fault,
        # rss参数，unused代表虚拟机内部未使用的内存量，available代表虚拟机内部识别的总内存容量.
        a = self.domain_object.memoryStats()
        if len(a) == 8:
            return {
                'rss': a['rss'],
                'actual': a['actual'],
                'unused': a['unused'],
                'available': a['available'],
                'virito': 1
            }
        else:
            return {
                'rss': a['rss'],
                'actual': a['actual'],
                'virito': 0
            }

    def getdiskInfo(self,gdict):
        # self.domain_object.blockInfo(target)这个方法会返回一个列表，返回列表[target_totle,target_use,target_use]第三个我也不知道是干什么用的，第一个是该磁盘的读出总容量，第二个是该磁盘的已用容量
        targetInfo=[]
        for target in gdict:
            getInfo = self.domain_object.blockInfo(target)
            targetInfo.append({
                target : {'totle' : getInfo[0],
                          'use' : getInfo[1]}
            })
        return targetInfo

    def getinterfaceInfo(self,gdict):
        targetInfo=[]
        for target in gdict:
            if target == 'null':
                targetInfo.append({
                    target : None
                })
            else:
                c = self.domain_object.interfaceStats(target)
                targetInfo.append({target : {'rx_bytes': c[0],
                 'rx_packet': c[1],
                 'rx_err': c[2],
                 'rx_drop': c[3],
                 'tx_bytes': c[4],
                 'tx_packet': c[5],
                 'tx_err': c[6],
                 'tx_drop': c[7]}})
        return targetInfo

    def deviceUpdate(self,xml):
        status = self.domain_object.updateDeviceFlags(xml=xml,flags=0)
        if status == 0:
            return 200

# def offineMigrate(dom, inhost, dcon, ):
#     object = get_obj(inhost, 'name', dom)
#     a = object.blockInfo()

class vol_edit:
    def __init__(self,_obj):
        self.obj = _obj

    def size(self):
        try:
            size = self.obj.info()
            AllSize = int(round((size[1] / 1024 / 1024 /1024),0))
            UseSize = int(round((size[2] / 1024 / 1024 /1024),0))
            return { "AllSize" : AllSize, "UseSize" : UseSize}
        except Exception,msg:
            print(msg)

    def name(self):
        try:
            return self.obj.name()
        except Exception,msg:
            print(msg)

    def path(self):
        try:
            return self.obj.path()
        except Exception,msg:
            print(msg)

    def resize(self,size):
        try:
            self.obj.resize(capacity=size)
        except Exception,msg:
            print(msg)

    def delete(self):
        try:
            self.obj.delete(flags=0)
        except Exception,msg:
            print(msg)

class storage_edit:
    def __init__(self,_obj):
        self._obj = _obj

    def info(self):
        try:
            k = self._obj.info()
            k1 = int(k[1])/1024/1024/1024
            k2 = int(k[2])/1024/1024/1024
            k3 = int(k[3])/1024/1024/1024
            ID = k[0]
            return {
                "All" : k1,
                "Usage" : k2,
                "Free" : k3,
                "ID" : ID
            }
        except Exception,msg:
            print(msg)
    def uuid(self):
        try:
            return self._obj.UUIDString()
        except Exception,msg:
            print(msg)

    def refer(self):
        try:
            self._obj.refresh()
        except Exception,msg:
            print(msg)
