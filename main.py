from tabulate import tabulate
import subprocess
import os
import re

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
        v = isDeviceModel(line)
        if v is not None:
            item["Model"] = v

        v = isSerialNumber(line)
        if v is not None:
            item["Serial"] = v

        v = isPowerOnHours(line)
        if v is not None:
            item["PowerOnHours"] = v

        v = isTemperature(line)
        if v is not None:
            item["Temperature"] = v

        v = isHealth(line)
        if v is not None:
            item["Health"] = v

    data.append(item)

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


def isHealth(line):
    pattern = re.compile('Reallocated_Sector_Ct')
    match = pattern.search(line)
    if match:
        keys = line.split()
        return keys[9]

    pattern = re.compile('Percentage Used:')
    match = pattern.search(line)
    if match:
        keys = line.split()
        return keys[2]

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

table = []
for item in data:
    table.append([item["Model"], item["Serial"], item["PowerOnHours"], item["Temperature"], item["Health"]])

headers = ["Model", "Serial", "Power On Hours", "Temperature", "Health"]
print(tabulate(table, headers, tablefmt="grid"))


