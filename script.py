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

class register(object):
    def __init__(self):
        self.page    = 0
        self.adr     = 0
        self.name    = ""
        self.value   = 0
        self.scale   = 1
        self.min     = 0
        self.max     = 0xFFFF
        self.units   = ""
        self.type    = "U"
        self.len     = 1
        self.bitMapSize = 0
        self.bit     = freeList[:]
    def setPage(self, n):
        self.page = n
        return
    def setAdr(self, n):
        self.adr = n
        return
    def setName(self, n):
        self.name = n
        return
    def setValue(self, n):
        self.value = n
        return
    def setScale(self, n):
        self.scale = n
        return
    def setMin(self, n):
        self.min = n
        return
    def setMax(self, n):
        self.max = n
        return
    def setUnits(self, n):
        self.units = n
        return
    def setType(self, n):
        self.type = n
        return
    def setLen(self, n):
        self.len = n
        return

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
rawData  = []
freeList = []
with open('config.csv') as file:
    reader  = csv.DictReader(file,delimiter=';')
    headers = reader.fieldnames
    registerCounter = 0
    for row in reader:
        rawData.append(row)
# Parsing data to structure
map         = []
bitCnt      = 0
curPage     = 0
curAdr      = 0
maxUnitsLen = 0
regNumber   = 0
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
                input["scale"] = input["scale"].replace(',','.')
                map[-1].setScale(float(input["scale"]))
                input["min"] = input["min"].replace(',','.')
                map[-1].setMin(int(float(input["min"])/map[-1].scale))
                input["max"] = input["max"].replace(',','.')
                map[-1].setMax(int(float(input["max"])/map[-1].scale))
                map[-1].setUnits(input["units"])
                if (len(input["units"]) > maxUnitsLen):
                    maxUnitsLen = len(input["units"])
                map[-1].setType(input["type"])
                map[-1].setLen(int(input["length"]))
                input["default"] = input["default"].replace(',','.')
                map[-1].setValue(int(float(input["default"])/map[-1].scale))
            else:
                regNumber = regNumber + 1
                map[-1].bitMapSize = map[-1].bitMapSize + 1
                map[-1].value   = int(map[-1].value)
                bm = bitMap()
                bm.name = input["name"]
                bm.min  = int(input["min"])
                bm.max  = int(input["max"])
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
f.write("/*----------------------------------------------------------------------*/\n")
f.write("#ifndef INC_CONFIG_H_\n");
f.write("#define INC_CONFIG_H_\n");
f.write("/*----------------------- Includes -------------------------------------*/\n");
f.write("#include \"stm32f2xx_hal.h\"\n")
f.write("/*------------------------ Define --------------------------------------*/\n")
f.write("#define   MAX_UNITS_LENGTH             " + str(maxUnitsLen) + "U\n")
f.write("#define   SETTING_REGISTER_NUMBER      " + str(regNumber) + "U\n")
f.write("\n")
f.write("#define   CONFIG_REG_PAGE_STR          \"page\"\n")
f.write("#define   CONFIG_REG_ADR_STR           \"adr\"\n")
f.write("#define   CONFIG_REG_SCALE_STR         \"scale\"\n")
f.write("#define   CONFIG_REG_VALUE_STR         \"value\"\n")
f.write("#define   CONFIG_REG_MIN_STR           \"min\"\n")
f.write("#define   CONFIG_REG_MAX_STR           \"max\"\n")
f.write("#define   CONFIG_REG_UNITS_STR         \"units\"\n")
f.write("#define   CONFIG_REG_TYPE_STR          \"type\"\n")
f.write("#define   CONFIG_REG_LEN_STR           \"len\"\n")
f.write("#define   CONFIG_REG_BIT_MAP_SIZE_STR  \"bitMapSize\"\n")
f.write("#define   CONFIG_REG_BIT_MAP_STR       \"bit\"\n")
f.write("\n")
f.write("#define   BIT_MAP_MASK_STR             \"mask\"\n")
f.write("#define   BIT_MAP_SHIFT_STR            \"shift\"\n")
f.write("#define   BIT_MAP_MIN_STR              \"min\"\n")
f.write("#define   BIT_MAP_MAX_STR              \"max\"\n")
f.write("/*----------------------- Structures -----------------------------------*/\n")
f.write("typedef struct\n")
f.write("{\n")
f.write("  uint16_t  mask;\n")
f.write("  uint8_t   shift;\n")
f.write("  uint8_t   min;\n")
f.write("  uint8_t   max;\n")
f.write("} eConfigBitMap;\n")
f.write("\n")
f.write("typedef struct\n")
f.write("{\n")
f.write("  uint16_t         page;\n")
f.write("  uint16_t         adr;\n")
f.write("  float            scale;\n")
f.write("  uint16_t         value;\n")
f.write("  uint16_t         min;\n")
f.write("  uint16_t         max;\n")
f.write("  char             units[MAX_UNITS_LENGTH];\n")
f.write("  char             type;\n")
f.write("  uint8_t          len;\n")
f.write("  uint8_t          bitMapSize;\n")
f.write("  eConfigBitMap*   bitMap;\n")
f.write("} eConfigReg;\n")
f.write("/*------------------------- Extern -------------------------------------*/\n")
for row in map:
    f.write("extern eConfigReg " + str(row.name) + ";\n")
f.write("extern eConfigReg* configReg[SETTING_REGISTER_NUMBER];\n")
f.write("/*----------------------------------------------------------------------*/\n")
f.write("#endif /* INC_CONFIG_H_ */\n")
f.close()
#****** C ******
f = open("config.c","w+")
f.write("/*\n")
f.write(" * Configuration file from 'config.csv'\n")
f.write(" * Make time: " + time + "\n")
f.write(" */\n")
f.write("#include   \"config.h\"\n")
f.write("\n")
postArray = "static eConfigReg* configReg[SETTING_REGISTER_NUMBER] = { "
for row in map:
    if (row.bitMapSize > 0):
        f.write("static eConfigBitMap " + row.name + "BitMap[" + str(row.bitMapSize) + "U] = \n")
        f.write("{\n")
        first = 0
        for bm in row.bit:
            first = first + 1
            f.write("   { ")
            f.write(str(bm["mask"]) + "U, ")
            f.write(str(bm["shift"]) + "U, ")
            f.write(str(bm["min"]) + "U, ")
            f.write(str(bm["max"]) + "U ")
            f.write("},     // " + bm["name"] + "\n")
        f.write("};\n")
    f.write("static eConfigReg " + row.name + " =\n")
    postArray += "&" + row.name + ", "
    f.write("{\n")
    f.write("   .page       = " + str(row.page)  + "U,\n")
    f.write("   .adr        = " + str(row.adr)   + "U,\n")
    if (row.scale >= 1):
        f.write("   .scale      = " + str(int(row.scale)) + "U,\n")
    else:
        f.write("   .scale      = " + str(row.scale) + "F,\n")
    f.write("   .value      = " + str(row.value) + "U,\n")
    f.write("   .min        = " + str(row.min)   + "U,\n")
    f.write("   .max        = " + str(row.max)   + "U,\n")
    f.write("   .units      = {");
    i = 0;
    l = list(row.units);
    while i < maxUnitsLen:
        if len(row.units) > i:
            f.write("'" + l[i] + "'");
        else:
            f.write("' '");
        if i != ( maxUnitsLen - 1 ):
            f.write(", ");
        i = i + 1;
    f.write("},\n")
    f.write("   .type       = '"+ row.type   + "',\n")
    f.write("   .len        = " + str(row.len)   + "U,\n")
    if (row.bitMapSize > 0):
        f.write("   .bitMapSize = " + str(row.bitMapSize) + "U,\n")
        f.write("   .bitMap     = " + row.name + "BitMap\n")
    f.write("};\n")
f.write("\n")
postArray = postArray[:-1]
postArray = postArray[:-1]
f.write(postArray + "};\n")


f.close()
