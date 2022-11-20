from __future__ import unicode_literals

import requests
from datetime import datetime
from datetime import date
import time
import json
from time import time as timestamp
#from dashboard.models import *
from extract.models import *
import threading

# Get token
authToken=''
import subprocess

subprocess.call('/home/TVadmin/django_code/analytics_dashboard/dashboard/auth.sh', shell=True)

filepath = 'tvc-client.cookie'

with open(filepath) as fp:
   line = fp.readline()
   cnt = 1
   while line:
      if len(line.split('\t')) > 1:
         #authToken = line.split('\t')[6]
         authToken = line.split('\t')[6].split('\n')[0]
         print("authToken: ", authToken)
      line = fp.readline()
      cnt += 1

# Authentication
# Variables
jsondata = list()

headers = dict()
headers['Cookie'] = 'authToken=' + authToken
headers['User-Agent'] = 'curl/7.29.0'
headers['Accept'] = '*/*'

# URL: Domains
url_domains = 'http://tlspbnflow02/api/v1/config/collection/json/system/Domains?'

def burst_per_interface_hourly(interfaceId, DeviceIp, DeviceName, start_time=None, end_time=None):
   print(len(start_time), len(end_time))
   url = 'http://tlspbnflow02/api/v1/perfdata?ViewBy=Time&Metric=InBurst1&Metric=InBurst2&Metric=InBurst3&Metric=InBurst4&Metric=InOther&Metric=OutBurst1&Metric=OutBurst2&Metric=OutBurst3&Metric=OutBurst4&Metric=OutOther&minGranularity=MIN15&grid=true&period=CUSTOM_TIME&autoUpdate=false&startTime={}&endTime={}&nfinterfaceId={}&PortIfType=2&DeviceIp={}&DeviceName=RTRB1SHADU&CollectorId=0'.format(start_time, end_time, interfaceId, DeviceIp, DeviceName)
   response = requests.get(url, headers = headers, verify=False)
   return response.text

def periodic_function_interface_burst_out_start_end(interfaces, START, END, timestamp):
   #url_interfaces_by_domain = 'http://tlspbnflow02/api/v1/perfdata?OrderBy=TxUtilization&dir=DESC&ViewBy=Interface&Metric=RxUtilization&Metric=TxUtilization&Metric=RxThroughput&Metric=TxThroughput&Metric=RxPPS&Metric=TxPPS&Metric=Availability&Metric=CurrentStatus&wait=false&rowLimit=100000&searchFields=name,Interface.description&GroupSortColumn=&GroupSortDir=ASC&start=0&limit=10000&search=&period=LAST_60_MIN&autoUpdate=false'
   #response = requests.get(url_interfaces_by_domain, headers=headers, verify=False)
   #interfaces = json.loads(response.text)
   # print(interfaces['records'])
   date_en = str(datetime.fromtimestamp(timestamp)).split(' ')[0].split('-')
   date_fr = date_en[2] + '/' + date_en[1] + '/' + date_en[0]
   time_fr = str(datetime.fromtimestamp(timestamp)).split(' ')[1]
   print(date_fr, time_fr)
   for interface in interfaces['records']:
      # response = burst_per_interface(interface['Interface']['id'], interface['Interface']['deviceIp'], interface['Interface']['deviceName'])
      response = burst_per_interface_hourly(interface['Interface']['id'], interface['Interface']['deviceIp'], interface['Interface']['deviceName'], str(START) + '000' , str(END)+'000')
      response = json.loads(response)
      #print(response)
      if "records" in response.keys():
         #print(response)
         #time.sleep(5)
         for app in response['records']:
            #print(app['OutBurst1'],app['OutBurst2'],app['OutBurst3'],app['OutBurst4'])
            OutBurst1=0.0
            OutBurst2=0.0
            OutBurst3=0.0
            OutBurst4=0.0
            Burst1=0
            Burst2=0
            Burst3=0
            Burst4=0
            if app['OutBurst1'] is not None: OutBurst1= app['OutBurst1']
            if app['OutBurst2'] is not None: OutBurst2= app['OutBurst2']
            if app['OutBurst3'] is not None: OutBurst3= app['OutBurst3']
            if app['OutBurst4'] is not None: OutBurst4= app['OutBurst4']
            if OutBurst1 > 20: Burst1= 1
            if OutBurst2 > 20: Burst2= 1
            if OutBurst3 > 20: Burst3= 1
            if OutBurst4 > 20: Burst4= 1
            if Burst3==1 or Burst4==1:
               print(OutBurst1, OutBurst2, OutBurst3, OutBurst4)
               o1 = OutInterfaceBurst(date=date_fr, time=time_fr, site_name = interface['Site'][0]['name'], router = interface['Device']['name'], interface = interface['Interface']['name'], OutBurst1 = OutBurst1, OutBurst2 = OutBurst2, OutBurst3 = OutBurst3, OutBurst4 = OutBurst4, Burst1 = Burst1, Burst2 = Burst2, Burst3 = Burst3, Burst4 = Burst4)
               #o1.save()

def periodic_function_interface_burst_in_start_end(interfaces, START, END, timestamp):
   #url_interfaces_by_domain = 'http://tlspbnflow02/api/v1/perfdata?OrderBy=TxUtilization&dir=DESC&ViewBy=Interface&Metric=RxUtilization&Metric=TxUtilization&Metric=RxThroughput&Metric=TxThroughput&Metric=RxPPS&Metric=TxPPS&Metric=Availability&Metric=CurrentStatus&wait=false&rowLimit=100000&searchFields=name,Interface.description&GroupSortColumn=&GroupSortDir=ASC&start=0&limit=10000&search=&period=LAST_60_MIN&autoUpdate=false'
   #response = requests.get(url_interfaces_by_domain, headers=headers, verify=False)
   #interfaces = json.loads(response.text)
   # print(interfaces['records'])
   date_en = str(datetime.fromtimestamp(timestamp)).split(' ')[0].split('-')
   date_fr = date_en[2] + '/' + date_en[1] + '/' + date_en[0]
   time_fr = str(datetime.fromtimestamp(timestamp)).split(' ')[1]
   print(date_fr, time_fr)
   for interface in interfaces['records']:
      # response = burst_per_interface(interface['Interface']['id'], interface['Interface']['deviceIp'], interface['Interface']['deviceName'])
      response = burst_per_interface_hourly(interface['Interface']['id'], interface['Interface']['deviceIp'], interface['Interface']['deviceName'], str(START) + '000' , str(END)+'000')
      response = json.loads(response)
      #print(response)
      if "records" in response.keys():
         #print(response)
         #time.sleep(5)
         for app in response['records']:
            #print(app['OutBurst1'],app['OutBurst2'],app['OutBurst3'],app['OutBurst4'])
            InBurst1=0.0
            InBurst2=0.0
            InBurst3=0.0
            InBurst4=0.0
            Burst1=0
            Burst2=0
            Burst3=0
            Burst4=0
            if app['InBurst1'] is not None: InBurst1 = app['InBurst1']
            if app['InBurst2'] is not None: InBurst2= app['InBurst2']
            if app['InBurst3'] is not None: InBurst3= app['InBurst3']
            if app['InBurst4'] is not None: InBurst4= app['InBurst4']
            if InBurst1 > 20: Burst1= 1
            if InBurst2 > 20: Burst2= 1
            if InBurst3 > 20: Burst3= 1
            if InBurst4 > 20: Burst4= 1
            if Burst3==1 or Burst4==1:
               print(InBurst1, InBurst2, InBurst3, InBurst4)
               o1 = InInterfaceBurst(date=date_fr, time=time_fr, site_name = interface['Site'][0]['name'], router = interface['Device']['name'], interface = interface['Interface']['name'], InBurst1 = InBurst1, InBurst2 = InBurst2, InBurst3 = InBurst3, InBurst4 = InBurst4, Burst1 = Burst1, Burst2 = Burst2, Burst3 = Burst3, Burst4 = Burst4)
               #o1.save()

"""
EXPORT OUTINTERFACE
"""
from datetime import datetime
from time import time as timestamp
#local_timestamp = timestamp()
# 31/10/2022
local_timestamp = 1667170805
url_interfaces_by_domain = 'http://tlspbnflow02/api/v1/perfdata?OrderBy=TxUtilization&dir=DESC&ViewBy=Interface&Metric=RxUtilization&Metric=TxUtilization&Metric=RxThroughput&Metric=TxThroughput&Metric=RxPPS&Metric=TxPPS&Metric=Availability&Metric=CurrentStatus&wait=false&rowLimit=100000&searchFields=name,Interface.description&GroupSortColumn=&GroupSortDir=ASC&start=0&limit=10000&search=&period=LAST_60_MIN&autoUpdate=false'
response = requests.get(url_interfaces_by_domain, headers=headers, verify=False)
interfaces = json.loads(response.text)
for hour in range(1, 48):
   print("hour", hour)
   #END_TIME  = str(local_timestamp).split('.')[0] + '000'
   #START_TIME = str(local_timestamp - 262800).split('.')[0] + '000'
   END_TIME  = str(local_timestamp).split('.')[0]
   START_TIME = str(local_timestamp - 3600).split('.')[0]
   local_timestamp = local_timestamp - 3600
   try:
      periodic_function_interface_burst_out_start_end(interfaces, START_TIME, END_TIME, local_timestamp)
      periodic_function_interface_burst_in_start_end(interfaces, START_TIME, END_TIME, local_timestamp)
   except Exception:
      pass
