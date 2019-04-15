# -*- coding: utf-8 -*-

import numpy


# lhedr - (C) 4-character label = 'hedr'
# itype - (I) header type = 2
# ftype - (C) 20-character variable defining file type = 'hist'
# fform - (C) 20-character variable defining file form = 'bin'
# date - (C) 80-character variable defining date file was written
# code - (C) 20-character variable identifying the code = 'PZFlex'
# user - (C) 240-character variable defining user name
# tag - (C) 280-character variable containing title and tag
# iversion - (I) file type version number
# nparts - (I) number of partitions for the model
# ipart - (I) partition number for this file
# intbyt - (I) number of bytes for standard integer
# irlbyt - (I) number of bytes for standard real number
# nch1 - (I) number of characters in string 1 variables = 20
# nch2 - (I) number of characters in string 2 variables = 80
# nch3 - (I) number of characters in string 3 variables = 200
# iextra1 - (I) unused extra integer 1
# iextra2 - (I) unused extra integer 2
# int12 - (I) integer value = 12
# nrecd - (I) number of data records on the file including the time record
# ntim - (I) number of time values for which time history data was saved
# ngrd - (I) number of 20-character words for grid name
# ndes - (I) number of 20-character words for description
# ntag - (I) number of 20-character words for curve tag
# nshift - (I) 1 = time shift for each record; 0 = no timeshift
# nlabl - (I) number of 20-character words for curve lable
# nindx - (I) number of indicies for each record
# ncord - (I) number of coordinates for each record
# nchr - (I) number of bytes per character word = 20
# nextra - (I) unused integer
# label - (C) 140-characer label and description for time record
# zero - (F) the number 0.0
# tstep - (F) time step of calculation
# i0 - (I) integer = 0
# tbegin - (F) start time = time(1)
# tshift - (F) time shift to add to time
# tend - (F) end time = time(ntim)
# tstart - (F) start time


# Hedr string. Literally the string 'hedr'. So useful.
HEDR_DTYPE = numpy.dtype('S4')

# Integer types.
INT_64_DTYPE = numpy.dtype('<i8')
INT_32_DTYPE = numpy.dtype('<i4')

# Floating point types.
FLOAT_64_DTYPE = numpy.dtype('<f8')
FLOAT_32_DTYPE = numpy.dtype('<f4')

# Fundamental string types.
STRING_1_DTYPE = numpy.dtype('S20')
STRING_2_DTYPE = numpy.dtype('S80')
STRING_3_DTYPE = numpy.dtype('S200')

# Byte spacing between data groups.
SPACING = 8



def read(filename):
    pass


def read_flxhst(filename):
    inttype = None
    floattype = None

    with open(filename, 'rb') as fid:
        # Determine data types used in the binary file.
        sizespec, = numpy.fromfile(fid, dtype=INT_32_DTYPE, count=1)
        if sizespec == 8:
            inttype = INT_32_DTYPE
            floattype = FLOAT_32_DTYPE
        elif sizespec == 12:
            inttype = INT_64_DTYPE
            floattype = FLOAT_64_DTYPE
        else: # TODO: throw exception here.
            pass

        #
        # Read the Header Record.
        #

        lhedr, = numpy.fromfile(fid, dtype=HEDR_DTYPE, count=1)
        itype, = numpy.fromfile(fid, dtype=inttype, count=1)

        fid.seek(SPACING, 1)

        (ftype, fform) = numpy.fromfile(fid, dtype=STRING_1_DTYPE, count=2)
        date, = numpy.fromfile(fid, dtype=STRING_2_DTYPE, count=1)
        code, = numpy.fromfile(fid, dtype=STRING_1_DTYPE, count=1)
        user, = numpy.fromfile(fid, dtype=STRING_3_DTYPE, count=1)
        (extra1, extra2) = numpy.fromfile(fid, dtype=STRING_1_DTYPE, count=2)

        fid.seek(SPACING, 1)

        title, = numpy.fromfile(fid, dtype=STRING_3_DTYPE, count=1)
        tag,   = numpy.fromfile(fid, dtype=STRING_2_DTYPE, count=1)

        fid.seek(SPACING, 1)

        (iversion, nparts, ipart, intbyte, irlbyte, nch1, nch2, nch3, iextra1,
            iextra2) = numpy.fromfile(fid, dtype=inttype, count=10)

        fid.seek(SPACING, 1)

        #
        # Read in the Base Record.
        #

        (int12, nrecd, ntim, ngrd, ndes, ntag, nshift, nlabl, nindx, ncrd, nchr,
            nxtra) = numpy.fromfile(fid, dtype=inttype, count=12)

        fid.seek(SPACING, 1)

        #
        # Read in the Time Record.
        #

        (label, dummy1, dummy2) = numpy.fromfile(fid, dtype=STRING_1_DTYPE, count=3)
        ldesc, = numpy.fromfile(fid, dtype=STRING_2_DTYPE, count=1)

        fid.seek(SPACING, 1)

        (zero1, zero2, tstep) = numpy.fromfile(fid, dtype=floattype, count=3)
        (i01, i02, i03) = numpy.fromfile(fid, dtype=inttype, count=3)
        (tbegin, tend, tshift) = numpy.fromfile(fid, dtype=floattype, count=3)

        # Read in time values.
        times = numpy.fromfile(fid, dtype=floattype, count=ntim)

        #
        # Read in the data records.
        #

        # Define the data record type.
        DATA_RECORD_DTYPE = numpy.dtype([
            ('label',   STRING_1_DTYPE),
            ('tag',     STRING_1_DTYPE),
            ('grid',    STRING_1_DTYPE),
            ('desc',    STRING_2_DTYPE),
            ('xcrd',    floattype),
            ('ycrd',    floattype),
            ('zcrd',    floattype),
            ('icrd',    inttype),
            ('jcrd',    inttype),
            ('kcrd',    inttype),
            ('datamin', floattype),
            ('datamax', floattype),
            ('tshift',  floattype),
            ('data',    floattype, ntim)
        ])

        # Pre-allocate memory to store the data records.
        records = numpy.zeros((nrecd - 1,), dtype=DATA_RECORD_DTYPE)

        # Temporary type that includes "spaces" in the data.
        TEMP_DATA_RECORD_DTYPE = numpy.dtype([
            ('unused2', INT_64_DTYPE),
            ('label',   STRING_1_DTYPE),
            ('tag',     STRING_1_DTYPE),
            ('grid',    STRING_1_DTYPE),
            ('desc',    STRING_2_DTYPE),
            ('unused1', INT_64_DTYPE),
            ('xcrd',    floattype),
            ('ycrd',    floattype),
            ('zcrd',    floattype),
            ('icrd',    inttype),
            ('jcrd',    inttype),
            ('kcrd',    inttype),
            ('datamin', floattype),
            ('datamax', floattype),
            ('tshift',  floattype),
            ('data',    floattype, ntim)
        ])

        for i in range(nrecd - 1):
            temp = numpy.fromfile(fid, dtype=TEMP_DATA_RECORD_DTYPE, count=1)
            # First entry is 8-byte spacing
            records[i][0] = temp[0][1]
            records[i][1] = temp[0][2]
            records[i][2] = temp[0][3]
            records[i][3] = temp[0][4]
            # Fifth entry is 8-byte spacing.
            records[i][4] = temp[0][6]
            records[i][5] = temp[0][7]
            records[i][6] = temp[0][8]
            records[i][7] = temp[0][9]
            records[i][8] = temp[0][10]
            records[i][9] = temp[0][11]
            records[i][10] = temp[0][12]
            records[i][11] = temp[0][13]
            records[i][12] = temp[0][14]
            records[i][13] = temp[0][15]

        filedata = {
            'lhedr': lhedr,
            'itype': itype,
            'ftype': ftype,
            'fform': fform,
            'date': date,
            'code': code,
            'user': user,
            'extra1': extra1,
            'extra2': extra2,
            'title': title,
            'tag': tag,
            'iversion': iversion,
            'nparts': nparts,
            'ipart': ipart,
            'intbyte': intbyte,
            'irlbyte': irlbyte,
            'nch1': nch1,
            'nch2': nch2,
            'nch3': nch3,
            'iextra1': iextra1,
            'iextra2': iextra2,
            'int12': int12,
            'nrecd': nrecd,
            'ntim': ntim,
            'ngrd': ngrd,
            'ndes': ndes,
            'ntag': ntag,
            'nshift': nshift,
            'nlabl': nlabl,
            'nindx': nindx,
            'ncrd': ncrd,
            'nchr': nchr,
            'nxtra': nxtra,
            'label': label,
            'dummy1': dummy1,
            'dummy2': dummy2,
            'ldesc': ldesc,
            'zero1': zero1,
            'zero2': zero2,
            'tstep': tstep,
            'i01': i01,
            'i02': i02,
            'i03': i03,
            'tbegin': tbegin,
            'tend': tend,
            'tshift': tshift,
            'times': times,
            'records': records
        }

        return filedata
    
    
