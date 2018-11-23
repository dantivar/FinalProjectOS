import binascii as ba
import math as m


def main(file):
    with open(file, 'rb') as f:
        f.seek(3)
        OEMName = str(f.read(8))
        
        f.seek(11)
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte = byte2 + byte1
        BPB_BytesPerSec = int(ba.hexlify(byte), 16)
        
        f.seek(13)
        byte = f.read(1)
        BPB_SecPerClus = int(ba.hexlify(byte), 16)
        
        f.seek(14)
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte = byte2 + byte1
        BPB_RsvdSecCnt = int(ba.hexlify(byte), 16)
        
        f.seek(16)
        byte = f.read(1)
        BPB_NumFATs = ba.hexlify(byte)
        BPB_NumFATs = int(BPB_NumFATs, 16)
        
        f.seek(17)
        byte1 = f.read(1)
        byte2 = f.read(1)
        byte = byte2 + byte1
        BPB_RootEntCnt = int(ba.hexlify(byte), 16)

        f.seek(19)
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

        f.seek(36)
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

        if  BPB_TotSec16 != 0:
            TotSec = BPB_TotSec16
        else:
            TotSec = BPB_TotSec32

        DataSec = TotSec - (BPB_RsvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors)        
        CountOfClusters = m.floor(DataSec / BPB_SecPerClus)
        
        #1 FAT12, 2 FAT16, 3 FAT32
        if CountOfClusters < 4085:
            FATType = 1
            FATTypes = "FAT12"
        elif CountOfClusters < 65525:
            FATType = 2
            FATTypes = "FAT16"
        else:
            FATType = 3
            FATTypes = "FAT32"

            fat32((firstSectorOfCluster(BPB_RootClus, BPB_SecPerClus, FirstDataSector)) * BPB_BytesPerSec, f, CountOfClusters * BPB_SecPerClus * BPB_BytesPerSec)
        ClusterSize = BPB_BytesPerSec * BPB_SecPerClus
        
        f.close()
        
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
        
        
def firstSectorOfCluster(n, secPerCluster, firstDataSector):
    return ((n - 2) * secPerCluster) + firstDataSector

def fat32(root, f, fs):
    print(root, fs)
    while root <= fs:
        f.seek(root)
        print(f.read(11))
        root = root + 64
    
main("/dev/sdb1")
