#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
import csv
import json
from time import gmtime, strftime
from math import log
import codecs
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
        self.adr     = 0
        self.name    = ""
        self.value   = 0
        self.scale   = 1
        self.min     = 0
        self.max     = 0xFFFF
        self.units   = ""
        self.type    = "U"
        self.rw      = "rw"
        self.len     = 1
        self.bitMapSize = 0
        self.bit     = freeList[:]
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
    def setRW(self, n):
        self.rw = n
        return;
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
curAdr      = 0
maxUnitsLen = 0
regNumber   = 0
maxRegNumber = 0;
for input in rawData:
    if input["name"][0] == "#":
        curAdr  = 0
    else:
        if ( input["name"] != "Reserved")and(input["name"][0] != "$"):
            if input["type"] != "B":
                regNumber += 1;
                bitCnt     = 0;
                map.append( register() );
                map[-1].setAdr( curAdr );
                map[-1].setName( input["name"] );
                input["scale"] = input["scale"].replace( ',', '.' );
                scl = float( input["scale"] );
                sclPow = log( scl, 10 );
                if ( sclPow < 0 ):
                    sclPow = sclPow - 1;
                sclPow = int( sclPow );
                map[-1].setScale( sclPow );
                input["min"] = input["min"].replace( ',', '.' );
                map[-1].setMin( int( float( input["min"] ) / scl ) );
                input["max"] = input["max"].replace( ',', '.' );
                map[-1].setMax( int( float( input["max"] ) / scl ) );
                map[-1].setUnits( input["units"] );
                if ( len( input["units"] ) > maxUnitsLen ):
                    maxUnitsLen = len( input["units"] );
                map[-1].setType( input["type"] );
                map[-1].setLen( int( input["length"] ) );
                map[-1].setRW( input["rw"] )
                curAdr = curAdr +  1;#map[-1].len
                input["default"] = input["default"].replace( ',', '.' );
                map[-1].setValue( int( float( input["default"] ) / scl ) );
                #if input["name"] == 'oilPressureAlarmLevel':
                #    print( str( map[-1].scale ) )
            else:
                if ( maxRegNumber < regNumber ):
                    maxRegNumber = regNumber;
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
#*******************************************************************************
print ('********** Make JSON **********')
f = codecs.open("C:\PROJECTS\ENERGAN\web-face\js\config.js","w+", "utf-8")
f.write("var dataReg = [\n")
for row in map:
    f.write('{\n')
    f.write('   "adr": ' + str(row.adr) + ',\n')
    f.write('   "name": "' + row.name + '",\n')
    if (row.len == 1):
        f.write('   "value": ' + str(row.value) + ',\n')
        f.write('   "default": ' + str(row.value) + ',\n')
    else:
        f.write('   "value": [');
        for i in range(0,row.len):
            if row.type == 'S':
                f.write( "' '" );
            else:
                f.write( str( ( row.value >> 16*i ) & 0xFFFF ) );
            if i < (row.len-1):
                f.write(", ")
        f.write("],\n")
        f.write('   "default": [');
        for i in range(0,row.len):
            if row.type == 'S':
                f.write( "' '" );
            else:
                f.write( str( ( row.value >> 16*i ) & 0xFFFF ) );
            if i < (row.len-1):
                f.write(", ")
        f.write("],\n")
    f.write('   "scale": ' + str(row.scale) + ',\n')
    f.write('   "min": ' + str(row.min) + ',\n')
    f.write('   "max": ' + str(row.max) + ',\n')
    f.write('   "units": "' + row.units + '",\n')
    f.write('   "type": "' + row.type + '",\n')
    f.write('   "rw": "' + row.rw + '",\n')
    f.write('   "len": ' + str(row.len) + ',\n')
    f.write('   "bitMapSize": ' + str(row.bitMapSize)  + ',\n')
    f.write('   "bit": ')
    if (row.bitMapSize > 0):
        f.write('[\n       ')
        for bit in row.bit:
            f.write('{\n')
            f.write('           "name": "' + bit['name'] + '",\n')
            f.write('           "mask": ' + str(bit['mask']) +  ',\n')
            f.write('           "min": ' + str(bit['min']) + ',\n')
            f.write('           "max": ' + str(bit['max']) + ',\n')
            f.write('           "shift": ' + str(bit['shift']) + ',\n')
            f.write('       },')
        f.write('\n   ]\n')
    else:
        f.write('[]\n')
    f.write('},')
f.write('];')
f.close()
with open('config.json', 'w') as f:
    for row in map:
        json_string = json.dump(row.__dict__, f, indent=4)
print("Done!")
#*******************************************************************************
maxLen = 0;
maxBitMapSize = 0;
for row in map:
    if row.len > maxLen:
        maxLen = row.len
print ('****** Make Struct array ******')
time = strftime( "%Y-%m-%d %H:%M:%S", gmtime() );
configStorageSize = 0;
#****** C ******
totalSize = 0;
f = codecs.open("C:\PROJECTS\ENERGAN\energan_enb\data\Src\config.c","w+","utf-8")
f.write("/*\n")
f.write(" * Configuration file from 'config.csv'\n")
f.write(" * Make time: " + time + "\n")
f.write(" */\n")
f.write("#include   \"config.h\"\n")
f.write("\n")
postArray = "eConfigReg* const configReg[SETTING_REGISTER_NUMBER] = { "
maxValueLen = 0;
for row in map:
    if (row.bitMapSize > 0):
        f.write("static eConfigBitMap " + row.name + "BitMap[" + str(row.bitMapSize) + "U] = \n")
        f.write("{\n")
        first = 0
        for bm in row.bit:
            totalSize += 5;
            first = first + 1
            f.write("   { ")
            f.write(str(bm["mask"]) + "U, ")
            f.write(str(bm["shift"]) + "U ")
            f.write("},     // " + bm["name"] + "\n")
        f.write("};\n")
    if (row.rw == "r"):
        f.write("const ")
    f.write("uint16_t " + row.name + "Value[" + str(row.len) + "U] = { ");
    if ( row.len > maxValueLen ):
        maxValueLen = row.len;
    totalSize += 17;
    for i in range(0,row.len):
        totalSize += 2;
        if row.type == 'S':
            f.write("' '");
        else:
            f.write(str((row.value >> 16*i) & 0xFFFF) + "U");
        if i < (row.len-1):
            f.write(", ")
    f.write(" };\n")

    f.write("const eConfigAttributes " + row.name + "Atrib =\n{\n" );
    f.write("   .adr        = " + str(row.adr)   + "U,\n")
    f.write("   .min        = " + str(row.min)   + "U,\n")
    if (row.max > 65535):
        row.max = 65535
    f.write("   .max        = " + str(row.max)   + "U,\n")
    f.write("   .type       = '"+ row.type   + "',\n")
    f.write("   .len        = " + str(row.len)   + "U,\n")
    f.write("   .bitMapSize = " + str(row.bitMapSize) + "U,\n")


    configStorageSize += ( row.bitMapSize * 3 ) + ( row.len * 2 ) + ( maxUnitsLen * 2 ) + 2;

    f.write("};\n");

    if (row.rw == "r"):
        f.write("const ")
    f.write("eConfigReg " + row.name + " =\n")
    postArray += "&" + row.name + ", "
    f.write("{\n")
    f.write("   .atrib      = &" + row.name + "Atrib,\n");
    if (row.scale >= 0):
        f.write("   .scale      = " + str(int(row.scale)) + "U,\n")
    else:
        f.write("   .scale      = " + str(row.scale) + ",\n")
    f.write("   .value      = " + row.name + "Value,\n")
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
    if ( row.bitMapSize > 0 ):
        if ( row.bitMapSize > maxBitMapSize ):
            maxBitMapSize = row.bitMapSize;
        f.write("   .bitMap     = " + row.name + "BitMap\n")
    else:
        f.write("   .bitMap     = NULL\n")
    f.write("};\n")
    f.write("/*----------------------------------------------------------------*/\n")
f.write("\n")
postArray = postArray[:-1]
postArray = postArray[:-1]
f.write(postArray + "};\n")
f.close()
#****** H ******
maxConfigSize = maxUnitsLen*2 + 1 + maxLen*2 + maxBitMapSize*3;
f = codecs.open("C:\PROJECTS\ENERGAN\energan_enb\data\Inc\config.h","w+","utf-8")
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
f.write("#define   SETTING_REGISTER_NUMBER      " + str(maxRegNumber) + "U\n")
f.write("#define   FILDS_TO_WRITE_NUMBER        3U\n")
f.write("#define   BROADCAST_ADR                0xFFFFU\n")
f.write("#define   MAX_VALUE_LENGTH             " + str( maxLen ) + "U\n" )
f.write("#define   CONFIG_MAX_SIZE              " + str( maxConfigSize ) + "U     // bytes\n" );
f.write("#define   CONFIG_TOTAL_SIZE            " + str( configStorageSize ) + "U   // bytes\n" );
f.write("\n")
f.write("#define   CONFIG_REG_ADR_STR           \"adr\"\n")
f.write("#define   CONFIG_REG_SCALE_STR         \"scale\"\n")
f.write("#define   CONFIG_REG_VALUE_STR         \"value\"\n")
f.write("#define   CONFIG_REG_MIN_STR           \"min\"\n")
f.write("#define   CONFIG_REG_MAX_STR           \"max\"\n")
f.write("#define   CONFIG_REG_UNITS_STR         \"units\"\n")
f.write("#define   CONFIG_REG_TYPE_STR          \"type\"\n")
f.write("#define   CONFIG_REG_RW_STATUS         \"rw\"\n")
f.write("#define   CONFIG_REG_LEN_STR           \"len\"\n")
f.write("#define   CONFIG_REG_BIT_MAP_SIZE_STR  \"bitMapSize\"\n")
f.write("#define   CONFIG_REG_BIT_MAP_STR       \"bit\"\n")
f.write("\n")
f.write("#define   BIT_MAP_MASK_STR             \"mask\"\n")
f.write("#define   BIT_MAP_SHIFT_STR            \"shift\"\n")
f.write("#define   BIT_MAP_MIN_STR              \"min\"\n")
f.write("#define   BIT_MAP_MAX_STR              \"max\"\n")
f.write("/*----------------------- Structures -----------------------------------*/\n")
f.write("typedef enum\n")
f.write("{\n")
f.write("  CONFIG_NO    = 0x00U,\n")
f.write("  CONFIG_VALUE = 0x01U,\n")
f.write("  CONFIG_SCALE = 0x02U,\n")
f.write("  CONFIG_UNITS = 0x03U,\n")
f.write("} CONFIG_FILD;\n\n")

f.write("typedef struct\n")
f.write("{\n")
f.write("  uint16_t  mask;\n")
f.write("  uint8_t   shift;\n")
f.write("} eConfigBitMap;\n")
f.write("\n")

f.write("typedef struct\n");
f.write("{\n");
f.write("  uint16_t         adr;         // R\n")
f.write("  uint16_t         min;         // R\n")
f.write("  uint16_t         max;         // R\n")
f.write("  uint16_t         type;        // R\n")
f.write("  uint8_t          len;         // R\n")
f.write("  uint8_t          bitMapSize;  // R\n")
f.write("} eConfigAttributes;\n")
f.write("\n")

f.write("typedef struct\n")
f.write("{\n")
f.write("  const eConfigAttributes* atrib;                   // R\n");
f.write("  signed char              scale;                   // RW\n")
f.write("  uint16_t*                value;                   // RW\n")
f.write("  uint16_t                 units[MAX_UNITS_LENGTH]; // RW\n")
f.write("  eConfigBitMap*           bitMap;                  // RW\n")
f.write("} eConfigReg;\n")

f.write("/*------------------------- Extern -------------------------------------*/\n")
for row in map:
    f.write("extern ");
    if (row.rw == "r"):
        f.write("const ");
    f.write("eConfigReg " + str( row.name ) + ";\n")
f.write("extern eConfigReg* const configReg[SETTING_REGISTER_NUMBER];\n")
f.write("/*----------------------------------------------------------------------*/\n")
f.write("#endif /* INC_CONFIG_H_ */\n")
f.close()
#******************************************************************************
print("Done! Total size: " + str( totalSize ) );
