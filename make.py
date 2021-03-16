#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
import csv
import json
from math import log
import codecs
import sys
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
rawData  = [];
freeList = [];

def setClass ( char ):
    if ( char == 'U' ):
        return 'CONFIG_TYPE_UNSIGNED';
    if ( char == 'S' ):
        return 'CONFIG_TYPE_SIGNED';
    if ( char == 'C' ):
        return 'CONFIG_TYPE_CHAR';
    if ( char == 'B' ):
        return 'CONFIG_TYPE_BITMAP';
    return '';

def makeDefineStr ( str, postfix = '' ):
    output = "";
    index  = 0;
    for i in range( len( str ) ):
        if ( str[i].isupper() == True ):
            output += str[index : i].upper() + "_";
            index   = i;
    if ( postfix != '' ):
        output += str[index : ].upper() + "_" + postfix;
    return output;

class bitMap:
    def __init__( self ):
        self.name  = "";
        self.mask  = 0;
        self.min   = 0;
        self.shift = 0;
        self.max   = 0xFFFF;
        self.str   = "";
        return;

class register(object):
    def __init__( self ):
        self.adr        = 0;
        self.name       = "";
        self.value      = 0;
        self.scale      = 1;
        self.min        = 0;
        self.max        = 0xFFFF;
        self.units      = "";
        self.type       = setClass( "U" );
        self.rw         = "rw";
        self.len        = 1;
        self.bitMapSize = 0;
        self.bit        = freeList[:];
        self.str        = "";
        return;
    def setAdr( self, n ):
        self.adr = n;
        return;
    def setName( self, n ):
        self.name = n
        return;
    def setValue( self, n ):
        self.value = n;
        return;
    def setScale( self, n ):
        self.scale = n;
        return;
    def setMin( self, n ):
        self.min = n;
        return;
    def setMax( self, n ):
        self.max = n;
        return;
    def setUnits( self, n ):
        self.units = n;
        return;
    def setType( self, n ):
        self.type = n;
        return;
    def setRW( self, n ):
        self.rw = n;
        return;
    def setLen( self, n ):
        self.len = n;
        return;
    def setStr( self, str ):
        self.str = str;
        return;

def bitMaskGen( len, cnt ):
    data = 0;
    for i in range(len):
        data = (data << 1) + 1;
    data = data << cnt;
    return data;

def orValue( value, n, s ):
    return value | (n << s);

def fix16_from_float( a ):
    temp = a * 0x00010000;
    if ( temp >= 0 ):
        temp += 0.5;
    else:
        temp += -0.5;
    return int( temp );

def cyrillic2hex ( symbol ):
    output = "0x0000";
    if ( len( symbol ) == 1 ):
        c   = symbol.encode( 'utf-8' );
        if ( len(c) == 1 ):
            output = hex( ord( symbol ) );
            output = output[0:2] + "00" + output[2:];
        else:
            output = hex( (c[0] << 8) + c[1] );
    output += 'U';
    return output;

#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
def readCSV ( fileName ):
    print( '>>Read CSV file...' );
    rawData = [];
    # Read raw data
    with open( fileName, mode='r', encoding='utf-8' ) as file:
        reader  = csv.DictReader( file, delimiter=';' );
        headers = reader.fieldnames;
        registerCounter = 0;
        for row in reader:
            rawData.append( row );
    # Parsing data to structure
    map          = [];
    bitCnt       = 0;
    curAdr       = 0;
    maxUnitsLen  = 0;
    regNumber    = 0;
    maxRegNumber = 0;
    for input in rawData:
        if input["name"][0] == "#":
            curAdr = 0;
        else:
            if ( input["name"] != "Reserved" ) and ( input["name"][0] != "$" ):
                if ( input["type"] != "B" ):
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
                    curAdr = curAdr +  1;
                    input["default"] = input["default"].replace( ',', '.' );
                    map[-1].setValue( int( float( input["default"] ) / scl ) );
                    map[-1].setStr( input["str"] );
                else:
                    if ( maxRegNumber < regNumber ):
                        maxRegNumber = regNumber;
                    map[-1].bitMapSize = map[-1].bitMapSize + 1;
                    map[-1].value      = int( map[-1].value );
                    bm       = bitMap();
                    bm.str   = input["str"];
                    bm.name  = input["name"];
                    bm.min   = int( input["min"] );
                    bm.max   = int( input["max"] );
                    bl       = int( input["length"] );
                    bm.mask  = bitMaskGen( bl, bitCnt );
                    bm.shift = bitCnt;
                    d        = int( input["default"] );
                    if ( d < bm.min ):
                        d = bm.min;
                    elif ( d > bm.max ):
                        d = bm.max;
                    map[-1].value = orValue( map[-1].value, d, bm.shift );
                    bitCnt = bitCnt + bl;
                    map[-1].bit.append( bm.__dict__ );
    print( 'Done!' );
    return [map, maxUnitsLen, maxRegNumber];
#*******************************************************************************
def makeJSON ( map, fileName, structName ):
    print( '>>Make JSON...' );
    if ( fileName == "no"):
        fileName = 'output.json'
    f = codecs.open( fileName, "w+", "utf-8" );
    f.write( 'var ' + structName + ' = [\n' );
    for row in map:
        f.write( '{\n' );
        f.write( '   "adr": ' + str( row.adr ) + ',\n' );
        maxRegNumber = row.adr + 1;
        f.write( '   "name": "' + row.name + '",\n' );
        if ( row.len == 1 ):
            f.write( '   "value": ' + str(row.value) + ',\n' );
            f.write( '   "default": ' + str(row.value) + ',\n' );
        else:
            f.write( '   "value": [' );
            for i in range( 0, row.len ):
                if row.type == 'C':
                    f.write( "' '" );
                else:
                    f.write( str( ( row.value >> 16 * i ) & 0xFFFF ) );
                if i < ( row.len - 1 ):
                    f.write( ', ' );
            f.write( '],\n' );
            f.write( '   "default": [' );
            for i in range( 0, row.len ):
                if row.type == 'C':
                    f.write( "' '" );
                else:
                    f.write( str( ( row.value >> 16 * i ) & 0xFFFF ) );
                if i < ( row.len - 1 ):
                    f.write( ', ' );
            f.write( '],\n' );
        f.write( '   "scale": '      + str( row.scale )      + ',\n'  );
        f.write( '   "min": '        + str( row.min )        + ',\n'  );
        f.write( '   "max": '        + str( row.max )        + ',\n'  );
        f.write( '   "units": "'     + row.units             + '",\n' );
        f.write( '   "type": "'      + row.type              + '",\n' );
        f.write( '   "rw": "'        + row.rw                + '",\n' );
        f.write( '   "len": '        + str( row.len )        + ',\n'  );
        f.write( '   "bitMapSize": ' + str( row.bitMapSize ) + ',\n'  );
        f.write( '   "bit": ' );
        if ( row.bitMapSize > 0 ):
            f.write( '[\n       ' );
            for bit in row.bit:
                f.write( '{\n' );
                f.write( '           "name": "' + bit['name']         + '",\n' );
                f.write( '           "mask": '  + str( bit['mask'] )  +  ',\n' );
                f.write( '           "max": '   + str( bit['max'] )   + ',\n'  );
                f.write( '           "min": '   + str( bit['min'] )   + ',\n'  );
                f.write( '           "shift": ' + str( bit['shift'] ) + ',\n'  );
                f.write( '       },' );
            f.write( '\n   ]\n' );
        else:
            f.write( '[]\n' );
        f.write( '},' );
    f.write( '];\n' );
    f.write( 'module.exports.dataReg = dataReg;' );
    f.close();
    print( 'Done!' );
    return;
#************************************* C ***************************************
class metaDataC ():
    maxBitMapSize     = 0;
    configStorageSize = 0;
    minScale          = 0;
    maxScale          = 0;
    bitAdresses       = "";
    totalSize         = 0;

def makeC_config ( map, fileName, structName ):
    print( ">>Make C configuration...");
    if ( fileName == "no"):
        fileName = 'config.c'
    meta = metaDataC();
    f    = codecs.open( fileName, "w+", "utf-8" );
    f.write( "/*\n" );
    f.write( " */\n" );
    f.write( "#include   \"config.h\"\n" );
    f.write( "\n" );
    postArray       = "eConfigReg* const " + structName + "Reg[SETTING_REGISTER_NUMBER]  = { ";
    dictionaryArray = "const char*       " + structName + "Dictionary[SETTING_REGISTER_NUMBER] = { ";
    maxValueLen     = 0;
    for row in map:
        if ( row.bitMapSize > 0 ):
            bitAdr = 0;
            f.write( "const eConfigBitMap " + row.name + "BitMap[" + str(row.bitMapSize) + "U] = \n" );
            f.write( "{\n" );
            first = 0;
            for bm in row.bit:
                meta.totalSize += 5;
                first     += 1;
                f.write( "   { " );
                f.write( str( bm["mask"]  ) + "U, " );
                f.write( str( bm["shift"] ) + "U "  );
                f.write( "},     // " + bm["name"] + "\n" );
                defStr = "";
                defStr += "#define   " + makeDefineStr( bm["name"], "ADR" );
                for i in range( len( defStr ), 55, 1 ):
                    defStr += " ";
                defStr      += str( bitAdr ) + 'U';
                defStr      += "\r\n";
                meta.bitAdresses += defStr;
                bitAdr      += 1;
            f.write( '};\n' );
        if ( row.rw == "r" ):
            f.write( "const " )
        f.write( "uint16_t " + row.name + "Value[" + str(row.len) + "U] = { " );
        if ( row.len > maxValueLen ):
            maxValueLen = row.len;
        meta.totalSize += 17;
        for i in range( 0, row.len ):
            meta.totalSize += 2;
            if row.type == 'C':
                f.write("0x0020U");
            else:
                f.write( str( ( row.value >> 16 * i ) & 0xFFFF ) + "U" );
            if i < ( row.len - 1 ):
                f.write( ", " );
        f.write( " };\n" );
        f.write( "const eConfigAttributes " + row.name + "Atrib =\n{\n" );
        f.write( "   .adr        = " + str( row.adr )   + "U,\n" );
        if ( row.scale < meta.minScale ):
            meta.minScale = row.scale;
        if ( row.scale > meta.maxScale ):
            meta.maxScale = row.scale;
        if ( row.scale >= 0 ):
            f.write( "   .scale      = " + str( int( row.scale ) ) + "U,\n" );
        else:
            f.write( "   .scale      = " + str(row.scale) + ",\n" );
        f.write( "   .min        = " + str( row.min )   + "U,\n" );
        if ( row.max > 65535 ):
            row.max = 65535;
        f.write( "   .max        = " + str( row.max )   + "U,\n" );
        f.write( "   .units      = { " );
        i = 0;
        l = list( row.units );
        while i < maxUnitsLen:
            if len( row.units ) > i:
                f.write( cyrillic2hex( l[i] ) );
            else:
                f.write( "0x0020U" );
            if i != ( maxUnitsLen - 1 ):
                f.write( ", " );
            i = i + 1;
        f.write( " },\n" );
        if ( row.bitMapSize > 0 ):
            f.write( "   .type       = " + setClass( 'B' ) + ",\n" );
        else:
            f.write( "   .type       = " + setClass( row.type ) + ",\n" );
        f.write( "   .len        = " + str( row.len )   + "U,\n" );
        f.write( "   .bitMapSize = " + str( row.bitMapSize ) + "U,\n" );
        if ( row.bitMapSize > 0 ):
            f.write( "   .bitMap     = " + row.name + "BitMap\n" );
        else:
            f.write( "   .bitMap     = NULL,\n" );
        if ( row.bitMapSize > meta.maxBitMapSize ):
            meta.maxBitMapSize = row.bitMapSize;
        meta.configStorageSize += ( row.len * 2 ) + 1;
        f.write( '};\n' );
        if ( row.rw == "r" ):
            f.write( "const " );
        f.write( "eConfigReg " + row.name + " =\n" );
        postArray       += "&" + row.name + ", ";
        dictionaryArray += '"' + row.str + '", ';
        f.write( '{\n');
        f.write( "   .atrib = &" + row.name + "Atrib,\n" );
        f.write( "   .value = " + row.name + "Value,\n" );
        f.write( "};\n" );
        f.write( "/*----------------------------------------------------------------*/\n" );
    f.write( "\n" );
    postArray       = postArray[:-1];
    postArray       = postArray[:-1];
    dictionaryArray = dictionaryArray[:-1];
    dictionaryArray = dictionaryArray[:-1];
    f.write( postArray + "};\n" );
    f.write( dictionaryArray + "};\n" );
    f.write( "const fix16_t     scaleMulArray[CONFIG_SCALE_NUM] = { " );
    for i in range( meta.maxScale - meta.minScale + 1 ):
        f.write( str( fix16_from_float ( pow( 10, ( meta.minScale + i ) ) ) ) );
        if ( i < ( meta.maxScale - meta.minScale ) ):
            f.write( "," );
        f.write( " " );
    f.write( "};\n" );
    f.close();
    print( "Done! ");
    return meta;
#************************************** C **************************************
def makeC_output (  map, fileName, structName ):
    if ( fileName == "no"):
        fileName = 'output.c'
    meta = metaDataC();
    f    = codecs.open( fileName, "w+", "utf-8" );
    f.write( "/*\n" );
    f.write( " */\n" );
    f.write( "#include   \"config.h\"\n" );
    f.write( "#include   \"output.h\"\n" );
    f.write( "\n" );
    postArray       = "eConfigReg* const " + structName + "Reg[OUTPUT_REGISTER_NUMBER]  = { ";
    dictionaryArray = "const char*       " + structName + "Dictionary[OUTPUT_REGISTER_NUMBER] = { ";

#************************************** H **************************************
def makeH_config ( map, meta, fileName ):
    print( ">>Make H..." );
    if ( fileName == "no"):
        fileName = 'output.h'
    maxLen = 0;
    for row in map:
        if row.len > maxLen:
            maxLen = row.len
    maxConfigSize = maxUnitsLen * 2 + 1 + maxLen * 2 + meta.maxBitMapSize * 3;
    f = codecs.open( fileName,"w+","utf-8" );
    f.write( "/*\n" );
    f.write( " * Configuration file from 'config.csv'\n" );
    f.write( " */\n" );
    f.write( "/*----------------------------------------------------------------------*/\n" );
    f.write( "#ifndef INC_CONFIG_H_\n" );
    f.write( "#define INC_CONFIG_H_\n" );
    f.write( "/*----------------------- Includes -------------------------------------*/\n" );
    f.write( "#include \"stm32f2xx_hal.h\"\n" );
    f.write( "#include \"fix16.h\"\n" );
    f.write( "/*------------------------ Define --------------------------------------*/\n" );
    f.write( "#define   MAX_UNITS_LENGTH             " + str( maxUnitsLen ) + "U\n" );
    f.write( "#define   MAX_BIT_MAP_LENGTH           " + str( meta.maxBitMapSize ) + "U\n" );
    f.write( "#define   SETTING_REGISTER_NUMBER      " + str( maxRegNumber + 1 ) + "U\n" );
    f.write( "#define   FILDS_TO_WRITE_NUMBER        3U\n" );
    f.write( "#define   BROADCAST_ADR                0xFFFFU\n" );
    f.write( "#define   MAX_VALUE_LENGTH             " + str( maxLen ) + "U\n" );
    f.write( "#define   CONFIG_MAX_SIZE              " + str( maxConfigSize ) + "U     // bytes\n" );
    f.write( "#define   CONFIG_TOTAL_SIZE            " + str( meta.configStorageSize ) + "U   // bytes\n" );
    f.write( "#define   MIN_CONFIG_SCALE             ( " + str( meta.minScale ) + " )\n" );
    f.write( "#define   MAX_CONFIG_SCALE             ( " + str( meta.maxScale ) + " )\n");
    f.write( "#define   CONFIG_SCALE_NUM             ( " + str( meta.maxScale - meta.minScale + 1 ) + " )\n");
    f.write( "\n" );
    f.write( "#define   CONFIG_REG_ADR_STR           \"adr\"\n" );
    f.write( "#define   CONFIG_REG_SCALE_STR         \"scale\"\n" );
    f.write( "#define   CONFIG_REG_VALUE_STR         \"value\"\n" );
    f.write( "#define   CONFIG_REG_MIN_STR           \"min\"\n" );
    f.write( "#define   CONFIG_REG_MAX_STR           \"max\"\n" );
    f.write( "#define   CONFIG_REG_UNITS_STR         \"units\"\n" );
    f.write( "#define   CONFIG_REG_TYPE_STR          \"type\"\n" );
    f.write( "#define   CONFIG_REG_RW_STATUS         \"rw\"\n" );
    f.write( "#define   CONFIG_REG_LEN_STR           \"len\"\n" );
    f.write( "#define   CONFIG_REG_BIT_MAP_SIZE_STR  \"bitMapSize\"\n" );
    f.write( "#define   CONFIG_REG_BIT_MAP_STR       \"bit\"\n" );
    f.write( "\n" );
    f.write( "#define   BIT_MAP_MASK_STR             \"mask\"\n" );
    f.write( "#define   BIT_MAP_SHIFT_STR            \"shift\"\n" );
    f.write( "#define   BIT_MAP_MIN_STR              \"min\"\n" );
    f.write( "#define   BIT_MAP_MAX_STR              \"max\"\n" );
    f.write( "/*----------------------- Structures -----------------------------------*/\n" );
    f.write( "typedef enum\n" );
    f.write( "{\n" );
    f.write( "  CONFIG_NO    = 0x00U,\n" );
    f.write( "  CONFIG_VALUE = 0x01U,\n" );
    f.write( "  CONFIG_SCALE = 0x02U,\n" );
    f.write( "  CONFIG_UNITS = 0x03U,\n" );
    f.write( "} CONFIG_FILD;\n\n" );
    f.write( "typedef enum\n" );
    f.write( "{\n" );
    f.write( "  CONFIG_TYPE_UNSIGNED  = 'U',\n" );
    f.write( "  CONFIG_TYPE_SIGNED    = 'S',\n" );
    f.write( "  CONFIG_TYPE_CHAR      = 'C',\n" );
    f.write( "  CONFIG_TYPE_BITMAP    = 'B',\n" );
    f.write( "} CONFIG_TYPE;\n\n" );
    f.write( "typedef struct __packed\n" );
    f.write( "{\n" );
    f.write( "  uint16_t  mask;\n" );
    f.write( "  uint8_t   shift;\n" );
    f.write( "} eConfigBitMap;\n" );
    f.write( "\n" );
    f.write( "typedef struct __packed\n" );
    f.write( "{\n" );
    f.write( "  uint16_t              adr;                     // R\n" );
    f.write( "  uint16_t              min;                     // R\n" );
    f.write( "  uint16_t              max;                     // R\n" );
    f.write( "  int8_t                scale;                   // R\n" );
    f.write( "  uint16_t              units[MAX_UNITS_LENGTH]; // R\n" );
    f.write( "  CONFIG_TYPE           type;                    // R\n" );
    f.write( "  uint8_t               len;                     // R\n" );
    f.write( "  uint8_t               bitMapSize;              // R\n" );
    f.write( "  eConfigBitMap const*  bitMap;                  // R\n" );
    f.write( "} eConfigAttributes;\n" );
    f.write( "\n" );
    f.write( "typedef struct __packed\n" );
    f.write( "{\n" );
    f.write( "  eConfigAttributes const* atrib;  // R\n" );
    f.write( "  uint16_t*                value;  // RW\n" );
    f.write( "} eConfigReg;\n" );
    f.write( "/*---------------------- Register addresses ----------------------------*/\n" );
    for row in map:
        strAdr = "";
        index  = 0;
        f.write( "#define   " );
        for i in range( len( row.name ) ):
            if ( row.name[i].isupper() == True ):
                strAdr += row.name[index : i].upper() + "_";
                index   = i;
        strAdr += row.name[index : ].upper() + "_ADR";
        f.write( strAdr );
        for i in range( len( strAdr ), 55, 1 ):
            f.write( " " );
        f.write( str( row.adr ) + 'U\n' );
    f.write( "/*---------------------- Bitmap addresses ------------------------------*/\n" );
    f.write( meta.bitAdresses );
    f.write( "/*------------------------- Extern -------------------------------------*/\n" );
    for row in map:
        f.write( "extern " );
        if ( row.rw == "r" ):
            f.write( "const " );
        f.write( "eConfigReg " + str( row.name ) + ";\n" );
    f.write( "extern eConfigReg* const configReg[SETTING_REGISTER_NUMBER];\n" );
    f.write( "extern const char*       dictionaryArray[SETTING_REGISTER_NUMBER];\n" );
    f.write( "extern const fix16_t     scaleMulArray[CONFIG_SCALE_NUM];\n" );
    f.write( "/*----------------------------------------------------------------------*/\n" );
    f.write( "#endif /* INC_CONFIG_H_ */\n" );
    f.close();
    print( "Done!" );
    return;
#******************************************************************************
def getArg ( args, key ):
    res = "no";
    for i in range( 0, len( args ) ):
        if ( args[i] == key ):
            res = args[i + 1];
    return res;
#******************************************************************************
if __name__ == "__main__":
    map = [];
    [map, maxUnitsLen, maxRegNumber] = readCSV( 'config.csv' );
    makeJSON( map, 'C:\PROJECTS\ENERGAN\web-face\js\config.js', 'dataReg' );
    metaData  = makeC_config( map, 'C:\PROJECTS\ENERGAN\energan_enb\data\Src\config.c', 'config' );
    makeH_config ( map, metaData, 'C:\PROJECTS\ENERGAN\energan_enb\data\Inc\config.h' );
    print( ">>Total size: " + str( metaData.totalSize ) );

    [map, maxUnitsLen, maxRegNumber]  = readCSV( 'outputData.csv' );
    makeJSON( map, 'C:\PROJECTS\ENERGAN\web-face\js\output.js', 'outputReg' );
    #metaData  = makeC( map, 'C:\PROJECTS\ENERGAN\energan_enb\data\Src\outputData.c', 'outputData' );
