#!/usr/bin/python

import requests, json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import xlwt
import xlrd
from xlwt import *

import time
from time import time as timestamp

DOMAINS_DICT = dict()
SITES_DOMAIN_DICT = dict()

local_timestamp = timestamp()
start_time = str(local_timestamp).split('.')[0] + '000'
end_time = str(local_timestamp + 3600).split('.')[0] + '000'
# Excel Conf
COL_WIDTH = 150 * 50

wb = xlwt.Workbook(encoding='utf-8')
front_style = xlwt.XFStyle()
al = xlwt.Alignment()
al.horz = xlwt.Alignment().HORZ_CENTER
al.vert = xlwt.Alignment().VERT_CENTER
front_style.alignment = al
front_style.font.bold = True
pattern = xlwt.Pattern()
pattern.pattern = xlwt.Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = xlwt.Style.colour_map['white']
front_style.pattern = pattern

fnt = Font()
fnt.name = 'Arial'
fnt.bold = True

borders = Borders()
borders.left = 6
borders.right = 6
borders.top = 6
borders.bottom = 6

alignment = Alignment()
alignment.horz = Alignment.HORZ_CENTER
alignment.vert = Alignment.VERT_CENTER

style = XFStyle()
style.font = fnt
style.borders = borders
style.alignment = alignment

columns = ['SITE NAME', 'ROUTER', 'INTERFACE', 'INT DESC', 'APPLICATION', 'APP DESC' , '% BW IN', '% BW OUT']

center_style = xlwt.easyxf("align: vert centre, horiz centre")

# Get token
authToken=''
import subprocess

subprocess.call('/home/TVadmin/source_codes/best/test/auth.sh', shell=True)

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

headers = dict()
headers['Cookie'] = 'authToken=' + authToken
headers['User-Agent'] = 'curl/7.29.0'
headers['Accept'] = '*/*'

# URL: Domains
url_domains = 'http://tlspbnflow02/api/v1/config/collection/json/system/Domains?'

def get_domain_sites(domain_id):
   url = 'http://tlspbnflow02/api/v1/config/collection/json/domain/{}/Sites?'.format(domain_id)
   response = requests.get(url, headers = headers, verify=False)
   return response.text

def get_site_applications(siteId):
   url = 'http://tlspbnflow02/api/v1/trafficanalysis?ViewBy=Application&ViewBy=ApplicationClass&Metric=TotalUtilization&Metric=TotalThroughput&Metric=TotalPPS&Metric=TotalFPS&period=LAST_60_MIN&startTime=1654588320000&endTime=1654591920000&siteId={}'.format(siteId)
   response = requests.get(url, headers = headers, verify=False)
   return response.text

def app_usage_per_interface(interfaceId, DeviceIp, DeviceName):
   # url = 'http://tlspbnflow02/api/v1/trafficanalysis?ViewBy=Application&ViewBy=ApplicationClass&Metric=TotalUtilization&Metric=TotalThroughput&Metric=TotalPPS&Metric=TotalFPS&Metric=InCap&Metric=OutCap&grid=true&CalcOthers=false&rowLimit=10000&pageAtSource=true&passSort=true&raw=true&start=0&limit=10&OrderBy=TotalUtilization&period=LAST_60_MIN&autoUpdate=false&nfinterfaceId={}&PortIfType=2&DeviceIp={}&DeviceName={}&CollectorId=0&SortColumn=TotalUtilization&SortDirection=DESC'.format(interfaceId, DeviceIp, DeviceName)
   url = 'http://tlspbnflow02/api/v1/trafficanalysis?MetricSpace=uptimenpv&ViewBy=Time&ViewBy=Application&Metric=TotalUtilization&Metric=RxUtilization&Metric=TxUtilization&Metric=InCap&Metric=OutCap&grid=true&OrderBy=RxUtilization&TopN=5&nfinterfaceId={}&PortIfType=2&DeviceIp={}&DeviceName={}&CollectorId=0&period=LAST_60_MIN&autoUpdate=false'.format(interfaceId, DeviceIp, DeviceName)
   response = requests.get(url, headers = headers, verify=False)
   return response.text

response = requests.get(url_domains, headers = headers, verify=False)

url_interfaces_by_domain = 'http://tlspbnflow02/api/v1/perfdata?OrderBy=TxUtilization&dir=DESC&ViewBy=Interface&Metric=RxUtilization&Metric=TxUtilization&Metric=RxThroughput&Metric=TxThroughput&Metric=RxPPS&Metric=TxPPS&Metric=Availability&Metric=CurrentStatus&wait=false&rowLimit=100000&searchFields=name,Interface.description&GroupSortColumn=&GroupSortDir=ASC&start=0&limit=10000&search=&period=LAST_60_MIN&autoUpdate=false'

response = requests.get(url_interfaces_by_domain, headers = headers, verify=False)

interfaces =  json.loads(response.text)

ws = wb.add_sheet('Intranet', True)

for col_num in range(len(columns)):
   ws.write(1, col_num, columns[col_num], style)
   ws.col(col_num).width = COL_WIDTH

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("date and time =", dt_string)
ws.write(0, 0, dt_string , center_style)
ws.col(0).width = COL_WIDTH

row_num = 2
for interface in interfaces['records']:
   print(interface)
   # print((interface['Interface']['id'], interface['Interface']['deviceIp'], interface['Interface']['deviceName']))
   response = app_usage_per_interface(interface['Interface']['id'], interface['Interface']['deviceIp'], interface['Interface']['deviceName'])
   response = json.loads(response)
   if "chart" in response.keys():
      #print(response)
      for app in response['records']:
         print(app['RxUtilization'], app['TxUtilization'])
         if (row_num<65536 and app['RxUtilization'] is not None and app['TxUtilization'] is not None) and (float(app['RxUtilization']) > 0.1 or float(app['TxUtilization']) > 0.1):
            ws.write(row_num, 0, interface['Site'][0]['name'] , center_style)
            ws.write(row_num, 1, interface['Device']['name'] , center_style)
            ws.write(row_num, 2, interface['Interface']['name'] , center_style)
            ws.write(row_num, 3, interface['Interface']['description'] , center_style)
            if app['Application'] is not None:
               ws.write(row_num, 4, app['Application']['name']  , center_style)
               ws.write(row_num, 5, app['Application']['description'] , center_style)
            else:
               ws.write(row_num, 4, ''  , center_style)
               ws.write(row_num, 5, '', center_style)
            ws.write(row_num, 6, app['RxUtilization'] , center_style)
            ws.write(row_num, 7, app['TxUtilization'] , center_style)
            row_num = row_num + 1

wb.save('app_interfaces_usage_new' + str(local_timestamp) + '.xls')
