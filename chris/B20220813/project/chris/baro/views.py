from django.shortcuts import render

from django.http import HttpResponse
from django.http import JsonResponse
from datetime import datetime

from .models import NodeFixed
from .models import NodeChange
from .models import GpuChange
from .models import GpuFixed
from .models import DiskChange
from .models import DiskFixed

from pyfile.main import *
from pyfile.cpu import *
from pyfile.disk import *
from pyfile.gpu import *
from pyfile.node import *

import pymysql
import paramiko

conn = pymysql.connect(host='localhost', user='root', password='baro', db='HWMonitoring', charset='utf8')
cur = conn.cursor()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.20.115", port='22', username="oem", password='baro')  

ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect("192.168.20.114", port='22', username="oem", password='baro')  

admindb = AdminDB(conn, cur, ssh)
admindb2 = AdminDB(conn, cur, ssh2)
del1 = "DELETE FROM NODE_CHANGE;"
del2 = "DELETE FROM GPU_CHANGE;"
del3 = "DELETE FROM DISK_CHANGE;"
# del4 = "DELETE FROM NODE_FIXED"
# del5 = "DELETE FROM GPU_FIXED"
# del6 = "DELETE FROM DISK_FIXED"
cur.execute(del1)
cur.execute(del2)
cur.execute(del3)
# cur.execute(del4)
# cur.execute(del5)
# cur.execute(del6)
cur.execute("COMMIT;")
try :
    admindb.fixed_insert_db()
except :
    pass
try :
    admindb2.fixed_insert_db()
except :
    pass



# Create your views here.
def index(request):
    now = datetime.now()
    if request.method == "GET":
        nodeFixed = NodeFixed.objects.all()
        gpuFixed = GpuFixed.objects.all()
        diskFixed = DiskFixed.objects.all()
        return render(request, 'index.html', {"nodeFixed" : nodeFixed, "gpuFixed" : gpuFixed, "diskFixed" : diskFixed})

    if request.method == "POST":
        try:
            admindb.changed_insert_db()
        except :
            pass
        try:
            admindb2.changed_insert_db()
        except :
            pass


    nodeChange = (list(NodeChange.objects.all().filter(created_at__gt=now).values()))
    gpuChange = (list(GpuChange.objects.all().filter(created_at__gt=now).values()))
    diskChange = (list(DiskChange.objects.all().filter(create_at__gt=now).values()))

    data = {
        "nodeChange" : nodeChange, 
        "gpuChange" : gpuChange, 
        "diskChange" : diskChange, 
    }

    return HttpResponse(JsonResponse(data), content_type="application/json")

