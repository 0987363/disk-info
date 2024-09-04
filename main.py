#from prettytable import PrettyTable
from tabulate import tabulate
import subprocess
#import wcwidth
import os
import re

#tabulate.WIDE_CHARS_MODE = True

directoryPath = '/dev'
sataPattern = re.compile(r'^sd.?$')
nvmePattern = re.compile(r'^nvme.?$')
data = []

def smartctl(dev):
    result = runSmartctl(os.path.join(directoryPath, dev))
    decodeSataInfo(result)


def decodeSataInfo(result):
    lines = str(result).splitlines()
    item = {}
    for line in lines:
        v = detectType(line)
        if v is not None:
            item["Type"] = v

        v = isDeviceModel(line)
        if v is not None:
            item["Model"] = v

        v = isSerialNumber(line)
        if v is not None:
            item["Serial"] = v

        v = isPowerOnHours(line)
        if v is not None:
            item["PowerOnHours"] = v.replace(",", "")

        v = isTemperature(line)
        if v is not None:
            item["Temperature"] = v

        v = isHealth(line)
        if v is not None:
            item["Health"] = v

        v = detectRead(line)
        if v is not None:
            item["Read"] = v

        v = detectWrite(line)
        if v is not None:
            item["Write"] = v


    if "Read" not in item:
        item["Read"] = ''
    if "Write" not in item:
        item["Write"] = ''
    data.append(item)

def detectRead(line):
    pattern = r'Data Units Read:.*\[(.*)\]'
    match = re.search(pattern, line)
    if match:
        return match.group(1)

def detectWrite(line):
    pattern = r'Data Units Written:.*\[(.*)\]'
    match = re.search(pattern, line)
    if match:
        return match.group(1)

def runSmartctl(dev):
    command =f"smartctl -a {dev}"
    result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, check=False)
    return result.stdout

def isDeviceModel(line):
    pattern = r'Device Model:\s+(.*)'
    match = re.search(pattern, line)
    if match:
        return match.group(1)

    pattern = r'Model Number:\s+(.*)'
    match = re.search(pattern, line)
    if match:
        return match.group(1)

def isSerialNumber(line):
    pattern = r'Serial Number:\s+(.*)'
    match = re.search(pattern, line)
    if match:
        return match.group(1)

def isTemperature(line):
    pattern = re.compile('Temperature_Celsius')
    match = pattern.search(line)
    if match:
        keys = line.split()
        return keys[9]

    pattern = re.compile('Temperature:')
    match = pattern.search(line)
    if match:
        keys = line.split()
        return keys[1]

def detectType(line):
    # SATA Version is:  SATA 3.2, 6.0 Gb/s (current: 6.0 Gb/s)
    pattern = r'SATA Version is:\s+(.*),.*'
    match = re.search(pattern, line)
    if match:
        return match.group(1)

    # NVMe Version:                       1.4
    pattern = r'NVMe Version:\s+(.*)'
    match = re.search(pattern, line)
    if match:
        return 'NVMe ' + match.group(1)


def isHealth(line):
    pattern = re.compile('Reallocated_Sector_Ct')
    match = pattern.search(line)
    if match:
        keys = line.split()
        return keys[9]+" Reallocated"

    pattern = re.compile('Percentage Used:')
    match = pattern.search(line)
    if match:
        keys = line.split()
        return keys[2] + " Percentage"

def isPowerOnHours(line):
    pattern = r'Power_On_Hours.+\s+(\d+)$'
    match = re.search(pattern, line)
    if match:
        return match.group(1)

    pattern = r'Power On Hours:\s+(.+)$'
    match = re.search(pattern, line)
    if match:
        return match.group(1)



diskList = []
for entry in os.scandir(directoryPath):
    if sataPattern.match(entry.name):
        diskList.append(entry.name)
    if nvmePattern.match(entry.name):
        diskList.append(entry.name)

diskList = sorted(diskList)

#print(f"匹配到文件：{diskList}")

for disk in diskList:
    smartctl(disk)

tableData = []
for item in data:
    tableData.append([item["Type"], item["Model"], item["Serial"], item["PowerOnHours"], item["Temperature"], item["Health"], item["Read"], item["Write"]])

tableHeader = ["Type", "Model", "Serial", "Power On Hours", "Temperature", "Health", "Read", "Write"]
print(tabulate(tableData, tableHeader, tablefmt="grid"))
#print(tabulate(tableData, tableHeader, tablefmt="grid", colglobalalign='left'))

#table = PrettyTable()
#table.field_names=tableHeader
#table.add_rows(tableData)
#print(table)

