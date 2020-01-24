#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
import csv
import json
from time import gmtime, strftime
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
class bitMap:
    def __init__(self):
        self.name  = ""
        self.mask  = 0
        self.min   = 0
        self.shift = 0
        self.max   = 0xFFFF
    def setName(self, n):
        self.name = n
        return
    def getName(self):
        return self.name
    def setMask(self, n):
        self.mask = n
        return
    def getMask(self):
        return self.mask
    def setMin(self, n):
        self.min = n
        return
    def getMin(self):
        return self.min
    def setMax(self, n):
        self.max = n
        return
    def getMax(self):
        return self.max
    def setShift(self,n):
        self.shift = n
        return
    def getShift(self):
        return self.shift
    def __repr__(self):
        return "name:"+str(self.name)+";mask:"+str(self.mask)+";min:"+str(self.min)+";max:"+str(self.max)

class register(object):
    def __init__(self):
        self.page  = 0
        self.adr   = 0
        self.name  = ""
        self.value = 0
        self.scale = 1
        self.min   = 0
        self.max   = 0xFFFF
        self.units = ""
        self.type  = "U"
        self.len   = 1
        self.bit   = freeList[:]
    #def __repr__(self):
    #    return "page:"+str(self.page)+";adr:"+str(self.adr)+";name:"+str(self.name)+";value:"+str(self.value)+";scale:"+str(self.scale)+";min:"+str(self.min)+";max:"+str(self.max)+";units:"+str(self.units)+";type:"+str(self.type)+";len:"+str(self.len)+";bit:"+str(self.bit)
    def setPage(self, n):
        self.page = n
        return
    def getPage(self):
        return self.page
    def setAdr(self, n):
        self.adr = n
        return
    def getAdr(self):
        return self.adr
    def setName(self, n):
        self.name = n
        return
    def getName(self):
        return self.name
    def setValue(self, n):
        self.value = n
        return
    def getValue(self):
        return self.value
    def setScale(self, n):
        self.scale = n
        return
    def getScale(self):
        return self.scale
    def setMin(self, n):
        self.min = n
        return
    def getMin(self):
        return self.min
    def setMax(self, n):
        self.max = n
        return
    def getMax(self):
        return self.max
    def setUnits(self, n):
        self.units = n
        return
    def getType(self):
        return self.type
    def setType(self, n):
        self.type = n
        return
    def getType(self):
        return self.type
    def setLen(self, n):
        self.len = n
        return
    def getLen(self):
        return self.len
    def addBit(self):
        self.bit.append(bitMap().__dict__)
        return len(self.bit)-1
    def getBitData(self,n):
        return (self.value & self.bit[n].getMask()) >> self.bit[n].getShift()

def bitMaskGen(len, cnt):
    data = 0
    for i in range(len):
        data = (data << 1) + 1
    data = data << cnt
    return data

def orValue(value, n, s):
    return value | (n << s)
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
print ('******** Read CSV file ********')
# Read raw data
rawData = []
freeList = []
with open('config.csv') as file:
    reader  = csv.DictReader(file,delimiter=';')
    headers = reader.fieldnames
    registerCounter = 0
    for row in reader:
        rawData.append(row)
# Parsing data to structure
map     = []
bitCnt  = 0
curPage = 0
curAdr  = 0
maxRegNameLen  = 0
maxUnitsLen = 0
maxBitNameLen = 0
for input in rawData:
    if input["name"][0] == "#":
        curPage = input["name"][1:]
        curAdr  = 0
    else:
        if (input["name"] != "Reserved")and(input["name"][0] != "$"):
            if input["type"] != "B":
                bitCnt       = 0
                map.append(register())
                map[-1].setPage(curPage)
                map[-1].setAdr(curAdr)
                curAdr = curAdr + 1
                map[-1].setName(input["name"])
                if (len(input["name"]) > maxRegNameLen):
                    maxRegNameLen = len(input["name"])
                map[-1].setScale(float(input["scale"]))
                map[-1].setMin(float(input["min"]))
                map[-1].setMax(float(input["max"]))
                map[-1].setUnits(input["units"])
                if (len(input["units"]) > maxUnitsLen):
                    maxUnitsLen = len(input["units"])
                map[-1].setType(input["type"])
                map[-1].setLen(int(input["length"]))
                map[-1].setValue(float(input["default"]))
            else:
                map[-1].value = int(map[-1].value)
                bm = bitMap()
                bm.name = input["name"]
                bm.min  = int(input["min"])
                bl = int(input["length"])
                bm.mask = bitMaskGen(bl, bitCnt)
                bm.shift = bitCnt
                d = int(input["default"])
                if (d < bm.min):
                    d = bm.min
                elif (d > bm.max):
                    d = bm.max
                map[-1].value = orValue(map[-1].value, d, bm.shift )
                bitCnt = bitCnt + bl
                map[-1].bit.append(bm.__dict__)
#for row in map:
#    print(row)
print("Done!")
print ('********** Make JSON **********')
with open('config.json', 'w') as f:
    for row in map:
        json_string = json.dump(row.__dict__, f, indent=4)
print("Done!")
print ('****** Make Struct array ******')
time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
#****** H ******
f = open("config.h","w+")
f.write("/*\n")
f.write(" * Configuration file from 'config.csv'\n")
f.write(" * Make time: " + time + "\n")
f.write(" */\n")
f.write("#ifndef INC_CONFIG_H_\n");
f.write("#define INC_CONFIG_H_\n");
f.write("\n");
f.write("#define   MAX_UNITS_LENGTH     " + str(maxUnitsLen) + "\n")
f.write("\n")
f.write("typedef struct\n")
f.write("{\n")
f.write("  uint16_t  page;\n")
f.write("  uint16_t  adr;\n")
f.write("  float     scale;\n")
f.write("  uint16_t  value;\n")
f.write("  uint16_t  min;\n")
f.write("  uint16_t  max;\n")
f.write("  char      units[MAX_UNITS_LENGTH];\n")
f.write("  char      type;\n")
f.write("  uint8_t   len;\n")
f.write("} eConfigReg;\n")
f.write("\n")
f.write("typedef struct\n")
f.write("{\n")
f.write("  uint16_t  mask;\n")
f.write("  uint8_t   shift;\n")
f.write("  uint8_t   min;\n")
f.write("  uint8_t   max;\n")
f.write("} eConfigBitMap;\n")
f.write("\n")
f.write("#endif /* INC_CONFIG_H_ */\n")
f.close()
#****** C ******
f = open("config.c","w+")
f.write("/*\n")
f.write(" * Configuration file from 'config.csv'\n")
f.write(" * Make time: " + time + "\n")
f.write(" */\n")
f.write("#include   <config.h>\n")
f.write("\n")
for row in map:
    f.write("eConfigReg " + row.name + " =\n")
    f.write("{\n")
    f.write("   .page   = " + str(row.page)  + "U,\n")
    f.write("   .adr    = " + str(row.adr)   + "U,\n")
    f.write("   .scale  = " + str(row.scale) + ",\n")
    f.write("   .value  = " + str(int(row.value / row.scale)) + "U,\n")
    f.write("   .min    = " + str(int(row.min / row.scale))   + "U,\n")
    f.write("   .max    = " + str(int(row.max / row.scale))   + "U,\n")
    f.write("   .units  = '"+     row.units  + "',\n")
    f.write("   .type   = '"+     row.type   + "',\n")
    f.write("   .len    = " + str(row.len)   + "U\n")
    f.write("};\n")

f.close()
