import binascii as ba
import math as m
import sys

bytespersector = 0
sectorpercluster = 0
firstdatasector = 0

def main(file):
    global bytespersector
    global sectorpercluster
    global firstdatasector
    
    with open(file, 'rb') as f:
        f.seek(3)
        OEMName = str(f.read(8))

        byte1 = f.read(1)
        byte2 = f.read(1)
        byte = byte2 + byte1
        BPB_BytesPerSec = int(ba.hexlify(byte), 16)
        bytespersector = BPB_BytesPerSec
        
        byte = f.read(1)
        BPB_SecPerClus = int(ba.hexlify(byte), 16)
        sectorpercluster = BPB_SecPerClus
        
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte = byte2 + byte1
        BPB_RsvdSecCnt = int(ba.hexlify(byte), 16)
        
        byte = f.read(1)
        BPB_NumFATs = ba.hexlify(byte)
        BPB_NumFATs = int(BPB_NumFATs, 16)
        
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte = byte2 + byte1
        BPB_RootEntCnt = int(ba.hexlify(byte), 16)

        byte1 = f.read(1)
        byte2 = f.read(1)
        byte = byte2 + byte1
        BPB_TotSec16 = int(ba.hexlify(byte), 16)

        f.seek(22)
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte = byte2 + byte1
        BPB_FATSz16 = int(ba.hexlify(byte), 16)

        f.seek(32)
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte3 = f.read(1)
        byte4 = f.read(1)
        byte = byte4 + byte3 + byte2 + byte1
        BPB_TotSec32 = int(ba.hexlify(byte), 16)
        
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte3 = f.read(1)
        byte4 = f.read(1)
        byte = byte4 + byte3 + byte2 + byte1
        BPB_FATSz32 = int(ba.hexlify(byte), 16)

        f.seek(44)
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte3 = f.read(1)
        byte4 = f.read(1)
        byte = byte4 + byte3 + byte2 + byte1
        BPB_RootClus = int(ba.hexlify(byte), 16)
        
        RootDirSectors = m.ceil(((BPB_RootEntCnt * 32) + (BPB_BytesPerSec - 1)) / BPB_BytesPerSec) if BPB_RootEntCnt !=0 else 0

        if BPB_FATSz16 != 0:
            FATSz = BPB_FATSz16
        else:
            FATSz = BPB_FATSz32

        FirstDataSector = BPB_RsvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors
        firstdatasector = FirstDataSector
        
        if  BPB_TotSec16 != 0:
            TotSec = BPB_TotSec16
        else:
            TotSec = BPB_TotSec32

        DataSec = TotSec - (BPB_RsvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors)        
        CountOfClusters = m.floor(DataSec / BPB_SecPerClus)
        
        
        if CountOfClusters < 4085:
            FATType = 1
            FATTypes = "FAT12"
        elif CountOfClusters < 65525:
            FATType = 2
            FATTypes = "FAT16"
        else:
            FATType = 3
            FATTypes = "FAT32"

        ClusterSize = BPB_BytesPerSec * BPB_SecPerClus
        
        print("""OEM Name: {}
Bytes Per Sector: {}
Sectors Per Cluster: {}
Cluster Size: {}
Reserved Sectors: {}
Number Of FATs: {}
Number Of Sectors: {}
FAT Size: {}
NumberOfClusters: {}
FAT type: {}""".format(OEMName, BPB_BytesPerSec, BPB_SecPerClus, ClusterSize, BPB_RsvdSecCnt, BPB_NumFATs, TotSec, FATSz, CountOfClusters, FATTypes))
        fileList(FirstDataSector * BPB_BytesPerSec, f)
        f.close()
        

def firstSectorOfCluster(n, secPerCluster, firstDataSector):
    return ((n - 2) * secPerCluster) + firstDataSector


def fileList(offset, f):
    f.seek(offset)
    print("Volume name: {}".format(f.read(11)))
    print("**********************************")
    print("Files")
    
    fileListD(offset, f)
    print("**********************************")

def fileListD(offset, f, depth = 1):
   
    check1 = 10
    check2 = 10
          
    while check1 != 0:
        if check1 != 229:
            if check1 >= 64 and check1 < 80 and check2 == 15:
                offset = searchLongEntry(offset, f, depth)
            else:
                offset += 32
            f.seek(offset)
            check1 = int(ba.hexlify(f.read(1)), 16)
            
            f.seek(offset + 11)
            check2 = int(ba.hexlify(f.read(1)), 16)
        else:
            offset += 32
            f.seek(offset)

            check1 = int(ba.hexlify(f.read(1)), 16)

            f.seek(offset + 11)
            check2 = int(ba.hexlify(f.read(1)), 16)
     
    
def searchLongEntry(offset, f, depth):
    fullName = []
    string, offset, check1, check2 = LDIR_Name(offset, f)
    fullName.append(string)
    
    while check1 < 32 and check2 == 15:
        string, offset, check1, check2 = LDIR_Name(offset, f)
        fullName.append(string)

    fullName = ''.join(reversed(fullName))
    
    temp = (' ' * (depth *3)) + '|--'
    print(temp + fullName)
    
    if check2 == 16:
        temp = 32 + (firstSectorOfCluster(getNextCluster(offset, f), sectorpercluster, firstdatasector) * bytespersector)
        fileListD(temp, f, depth +1)
    return offset

def getNextCluster(offset, f):
    f.seek(offset + 20)
    byte1 = f.read(1)
    byte2 = f.read(1)
    
    byte = byte2 + byte1

    f.seek(offset + 26)

    byte1 = f.read(1)
    byte2 = f.read(1)

    byte = byte  + byte2 + byte1

    return int(ba.hexlify(byte), 16)
    
def LDIR_Name(offset, f):
    offset+=1
    f.seek(offset)
    
    string1 = f.read(10)
    string1 = cleanStr(string1)
    
    offset += 13
    f.seek(offset)
    
    string2 = f.read(12)
    string2 = cleanStr(string2)

    offset += 14
    f.seek(offset)

    string3 = f.read(4)
    string3 = cleanStr(string3)

    offset += 4
    
    check1 = int(ba.hexlify(f.read(1)), 16)

    f.seek(offset + 11)

    check2 = int(ba.hexlify(f.read(1)), 16)
    
    string = string1 + string2 + string3

    return string, offset, check1, check2

def cleanStr(string):
    string = [chr(c) for c in list(string) if c!=0 and c!=255]
    string = ''.join(string)
    return string


main(sys.argv[1])
