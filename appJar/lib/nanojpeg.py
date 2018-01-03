import array, sys
# NanoJPEG -- KeyJ's Tiny Baseline JPEG Decoder
# version 1.1 (2010-03-05)
# by Martin J. Fiedler <martin.fiedler@gmx.net>
# http://keyj.emphy.de/nanojpeg/
#
# This software is published under the terms of KeyJ's Research License,
# version 0.2. Usage of this software is subject to the following conditions:
# 0. There's no warranty whatsoever. The author(s) of this software can not
#    be held liable for any damages that occur when using this software.
# 1. This software may be used freely for both non-commercial and commercial
#    purposes.
# 2. This software may be redistributed freely as long as no fees are charged
#    for the distribution and this license information is included.
# 3. This software may be modified freely except for this license information,
#    which must not be changed in any way.
# 4. If anything other than configuration, indentation or comments have been
#    altered in the code, the original author(s) must receive a copy of the
#    modified code.
#
# Ported to python by Andras Suller <suller.andras@gmail.com>


###############################################################################
## DOCUMENTATION SECTION                                                     ##
## read this if you want to know what this is all about                      ##
###############################################################################

# INTRODUCTION
# ============
#
# This is a minimal decoder for baseline JPEG images. It accepts memory dumps
# of JPEG files as input and generates either 8-bit grayscale or packed 24-bit
# RGB images as output. It does not parse JFIF or Exif headers; all JPEG files
# are assumed to be either grayscale or YCbCr. CMYK or other color spaces are
# not supported. All YCbCr subsampling schemes with power-of-two ratios are
# supported, as are restart intervals. Progressive or lossless JPEG is not
# supported.
# Summed up, NanoJPEG should be able to decode all images from digital cameras
# and most common forms of other non-progressive JPEG images.
# The decoder is not optimized for speed, it's optimized for simplicity and
# small code. Image quality should be at a reasonable level. A bicubic chroma
# upsampling filter ensures that subsampled YCbCr images are rendered in
# decent quality. The decoder is not meant to deal with broken JPEG files in
# a graceful manner; if anything is wrong with the bitstream, decoding will
# simply fail.
# The code should work with every modern C compiler without problems and
# should not emit any warnings. It uses only (at least) 32-bit integer
# arithmetic and is supposed to be endianness independent and 64-bit clean.
# However, it is not thread-safe.


# COMPILE-TIME CONFIGURATION
# ==========================
#
# The following aspects of NanoJPEG can be controlled with preprocessor
# defines:
#
# _NJ_EXAMPLE_PROGRAM     = Compile a main() function with an example
#                           program.
# _NJ_INCLUDE_HEADER_ONLY = Don't compile anything, just act as a header
#                           file for NanoJPEG. Example:
#                               #define _NJ_INCLUDE_HEADER_ONLY
#                               #include "nanojpeg.c"
#                               int main(void) {
#                                   njInit();
#                                   // your code here
#                                   njDone();
#                               }
# NJ_USE_LIBC=1           = Use the malloc(), free(), memset() and memcpy()
#                           functions from the standard C library (default).
# NJ_USE_LIBC=0           = Don't use the standard C library. In this mode,
#                           external functions njAlloc(), njFreeMem(),
#                           njFillMem() and njCopyMem() need to be defined
#                           and implemented somewhere.
# NJ_USE_WIN32=0          = Normal mode (default).
# NJ_USE_WIN32=1          = If compiling with MSVC for Win32 and
#                           NJ_USE_LIBC=0, NanoJPEG will use its own
#                           implementations of the required C library
#                           functions (default if compiling with MSVC and
#                           NJ_USE_LIBC=0).
# NJ_CHROMA_FILTER=1      = Use the bicubic chroma upsampling filter
#                           (default).
# NJ_CHROMA_FILTER=0      = Use simple pixel repetition for chroma upsampling
#                           (bad quality, but faster and less code).


# API
# ===
#
# For API documentation, read the "header section" below.


# EXAMPLE
# =======
#
# A few pages below, you can find an example program that uses NanoJPEG to
# convert JPEG files into PGM or PPM. To compile it, use something like
#     gcc -O3 -D_NJ_EXAMPLE_PROGRAM -o nanojpeg nanojpeg.c
# You may also add -std=c99 -Wall -Wextra -pedantic -Werror, if you want :)


###############################################################################
## HEADER SECTION                                                            ##
## copy and pase this into nanojpeg.h if you want                            ##
###############################################################################

#ifndef _NANOJPEG_H
#define _NANOJPEG_H

# nj_result_t: Result codes for njDecode().
NJ_OK = 0           # no error, decoding successful
NJ_NO_JPEG = 1      # not a JPEG file
NJ_UNSUPPORTED = 2  # unsupported format
NJ_OUT_OF_MEM = 3   # out of memory
NJ_INTERNAL_ERR = 4 # internal error
NJ_SYNTAX_ERROR = 5 # syntax error
__NJ_FINISHED = 6   # used internally, will never be reported

# njInit: Initialize NanoJPEG.
# For safety reasons, this should be called at least one time before using
# using any of the other NanoJPEG functions.
#void njInit(void);

# njDecode: Decode a JPEG image.
# Decodes a memory dump of a JPEG file into internal buffers.
# Parameters:
#   jpeg = The pointer to the memory dump.
#   size = The size of the JPEG file.
# Return value: The error code in case of failure, or NJ_OK (zero) on success.
#nj_result_t njDecode(const void* jpeg, const int size);

# njGetWidth: Return the width (in pixels) of the most recently decoded
# image. If njDecode() failed, the result of njGetWidth() is undefined.
#int njGetWidth(void);

# njGetHeight: Return the height (in pixels) of the most recently decoded
# image. If njDecode() failed, the result of njGetHeight() is undefined.
#int njGetHeight(void);

# njIsColor: Return 1 if the most recently decoded image is a color image
# (RGB) or 0 if it is a grayscale image. If njDecode() failed, the result
# of njGetWidth() is undefined.
#int njIsColor(void);

# njGetImage: Returns the decoded image data.
# Returns a pointer to the most recently image. The memory layout it byte-
# oriented, top-down, without any padding between lines. Pixels of color
# images will be stored as three consecutive bytes for the red, green and
# blue channels. This data format is thus compatible with the PGM or PPM
# file formats and the OpenGL texture formats GL_LUMINANCE8 or GL_RGB8.
# If njDecode() failed, the result of njGetImage() is undefined.
#unsigned char* njGetImage(void);

# njGetImageSize: Returns the size (in bytes) of the image data returned
# by njGetImage(). If njDecode() failed, the result of njGetImageSize() is
# undefined.
#int njGetImageSize(void);

# njDone: Uninitialize NanoJPEG.
# Resets NanoJPEG's internal state and frees all memory that has been
# allocated at run-time by NanoJPEG. It is still possible to decode another
# image after a njDone() call.
#void njDone(void);

#endif//_NANOJPEG_H


###############################################################################
## CONFIGURATION SECTION                                                     ##
## adjust the default settings for the NJ_ defines here                      ##
###############################################################################

NJ_USE_LIBC = 1

NJ_USE_WIN32 = 0

NJ_CHROMA_FILTER = 1


###############################################################################
## EXAMPLE PROGRAM                                                           ##
## just define _NJ_EXAMPLE_PROGRAM to compile this (requires NJ_USE_LIBC)    ##
###############################################################################

# #ifdef  _NJ_EXAMPLE_PROGRAM

# #include <stdio.h>
# #include <stdlib.h>
# #include <string.h>

# int main(int argc, char* argv[]) {
#     int size;
#     char *buf;
#     FILE *f;

#     if (argc < 2) {
#         printf("Usage: %s <input.jpg> [<output.ppm>]\n", argv[0]);
#         return 2;
#     }
#     f = fopen(argv[1], "rb");
#     if (!f) {
#         printf("Error opening the input file.\n");
#         return 1;
#     }
#     fseek(f, 0, SEEK_END);
#     size = (int) ftell(f);
#     buf = malloc(size);
#     fseek(f, 0, SEEK_SET);
#     size = (int) fread(buf, 1, size, f);
#     fclose(f);

#     njInit();
#     if (njDecode(buf, size)) {
#         printf("Error decoding the input file.\n");
#         return 1;
#     }

#     f = fopen((argc > 2) ? argv[2] : (njIsColor() ? "nanojpeg_out.ppm" : "nanojpeg_out.pgm"), "wb");
#     if (!f) {
#         printf("Error opening the output file.\n");
#         return 1;
#     }
#     fprintf(f, "P%d\n%d %d\n255\n", njIsColor() ? 6 : 5, njGetWidth(), njGetHeight());
#     fwrite(njGetImage(), 1, njGetImageSize(), f);
#     fclose(f);
#     njDone();
#     return 0;
# }

#endif


###############################################################################
## IMPLEMENTATION SECTION                                                    ##
## you may stop reading here                                                 ##
###############################################################################

#ifndef _NJ_INCLUDE_HEADER_ONLY

# typedef struct _nj_code {
#     unsigned char bits, code;
# } nj_vlc_code_t;

class nj_vlc_code_t(object):
    def __init__(self):
        self.bits = 0
        self.code = 0

# typedef struct _nj_cmp {
#     int cid;
#     int ssx, ssy;
#     int width, height;
#     int stride;
#     int qtsel;
#     int actabsel, dctabsel;
#     int dcpred;
#     unsigned char *pixels;
# } nj_component_t;

class nj_component_t(object):
    def __init__(self):
        self.cid = 0
        self.ssx = 0
        self.ssy= 0
        self.width = 0
        self.height = 0
        self.stride = 0
        self.qtsel = 0
        self.actabsel = 0
        self.dctabsel = 0
        self.dcpred = 0
        self.pixels = None

# typedef struct _nj_ctx {
#     nj_result_t error;
#     const unsigned char *pos;
#     int size;
#     int length;
#     int width, height;
#     int mbwidth, mbheight;
#     int mbsizex, mbsizey;
#     int ncomp;
#     nj_component_t comp[3];
#     int qtused, qtavail;
#     unsigned char qtab[4][64];
#     nj_vlc_code_t vlctab[4][65536];
#     int buf, bufbits;
#     int block[64];
#     int rstinterval;
#     unsigned char *rgb;
# } nj_context_t;

class nj_context_t(object):
    def init(self):
        self.error = 0
        self.spos = None # new param. it stores the string what is indexed by pos
        self.pos = 0
        self.size = 0
        self.length = 0
        self.width = 0
        self.height = 0
        self.mbwidth = 0
        self.mbheight = 0
        self.mbsizex = 0
        self.mbsizey = 0
        self.ncomp = 0
        self.comp = [nj_component_t(), nj_component_t(), nj_component_t()]
        self.qtused = 0
        self.qtavail = 0
        self.qtab = [[0] * 64, [0] * 64, [0] * 64, [0] * 64]
        # nj_vlc_code_t vlctab[4][65536] = None
        self.vlctab = []
        for n in range(4):
            self.vlctab.append([nj_vlc_code_t() for i in range(65536)])
        self.buf = 0
        self.bufbits = 0
        self.block = [0] * 64
        self.rstinterval = 0
        self.rgb = None

# static nj_context_t nj;
nj = nj_context_t()

njZZ = [ 0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18,
    11, 4, 5, 12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28, 35,
    42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51, 58, 59, 52, 45,
    38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63 ]

def njClip(x):
    if x < 0: return 0
    if x > 0xFF: return 0xFF
    return x

W1 = 2841
W2 = 2676
W3 = 2408
W5 = 1609
W6 = 1108
W7 = 565

def njRowIDCT(blk, p):
    x1 = blk[p + 4] << 11
    x2 = blk[p + 6]
    x3 = blk[p + 2]
    x4 = blk[p + 1]
    x5 = blk[p + 7]
    x6 = blk[p + 5]
    x7 = blk[p + 3]
    if (not (x1 | x2 | x3 | x4 | x5 | x6 | x7)):
        v = blk[p + 0] << 3
        blk[p + 0] = v
        blk[p + 1] = v
        blk[p + 2] = v
        blk[p + 3] = v
        blk[p + 4] = v
        blk[p + 5] = v
        blk[p + 6] = v
        blk[p + 7] = v
        return
    x0 = (blk[p + 0] << 11) + 128
    x8 = W7 * (x4 + x5)
    x4 = x8 + (W1 - W7) * x4
    x5 = x8 - (W1 + W7) * x5
    x8 = W3 * (x6 + x7)
    x6 = x8 - (W3 - W5) * x6
    x7 = x8 - (W3 + W5) * x7
    x8 = x0 + x1
    x0 -= x1
    x1 = W6 * (x3 + x2)
    x2 = x1 - (W2 + W6) * x2
    x3 = x1 + (W2 - W6) * x3
    x1 = x4 + x6
    x4 -= x6
    x6 = x5 + x7
    x5 -= x7
    x7 = x8 + x3
    x8 -= x3
    x3 = x0 + x2
    x0 -= x2
    x2 = (181 * (x4 + x5) + 128) >> 8
    x4 = (181 * (x4 - x5) + 128) >> 8
    blk[p + 0] = (x7 + x1) >> 8
    blk[p + 1] = (x3 + x2) >> 8
    blk[p + 2] = (x0 + x4) >> 8
    blk[p + 3] = (x8 + x6) >> 8
    blk[p + 4] = (x8 - x6) >> 8
    blk[p + 5] = (x0 - x4) >> 8
    blk[p + 6] = (x3 - x2) >> 8
    blk[p + 7] = (x7 - x1) >> 8


#blk was a char *, but we need to use an array and an index instead.
#sout is an extra parameter: it is the string what we need to modify,
#and out is the position inside sout (index)
def njColIDCT(blk, p, sout, out, stride):
    x1 = blk[p + 8*4] << 8
    x2 = blk[p + 8*6]
    x3 = blk[p + 8*2]
    x4 = blk[p + 8*1]
    x5 = blk[p + 8*7]
    x6 = blk[p + 8*5]
    x7 = blk[p + 8*3]
    if (not (x1 | x2 | x3 | x4 | x5 | x6 | x7)):
        x1 = njClip(((blk[p + 0] + 32) >> 6) + 128)
        x0 = 8
        while x0:
            sout[out] = x1
            out += stride
            x0 -= 1
        return
    
    x0 = (blk[p + 0] << 8) + 8192
    x8 = W7 * (x4 + x5) + 4
    x4 = (x8 + (W1 - W7) * x4) >> 3
    x5 = (x8 - (W1 + W7) * x5) >> 3
    x8 = W3 * (x6 + x7) + 4
    x6 = (x8 - (W3 - W5) * x6) >> 3
    x7 = (x8 - (W3 + W5) * x7) >> 3
    x8 = x0 + x1
    x0 -= x1
    x1 = W6 * (x3 + x2) + 4
    x2 = (x1 - (W2 + W6) * x2) >> 3
    x3 = (x1 + (W2 - W6) * x3) >> 3
    x1 = x4 + x6
    x4 -= x6
    x6 = x5 + x7
    x5 -= x7
    x7 = x8 + x3
    x8 -= x3
    x3 = x0 + x2
    x0 -= x2
    x2 = (181 * (x4 + x5) + 128) >> 8
    x4 = (181 * (x4 - x5) + 128) >> 8
    sout[out] = njClip(((x7 + x1) >> 14) + 128)
    out += stride
    sout[out] = njClip(((x3 + x2) >> 14) + 128)
    out += stride
    sout[out] = njClip(((x0 + x4) >> 14) + 128)
    out += stride
    sout[out] = njClip(((x8 + x6) >> 14) + 128)
    out += stride
    sout[out] = njClip(((x8 - x6) >> 14) + 128)
    out += stride
    sout[out] = njClip(((x0 - x4) >> 14) + 128)
    out += stride
    sout[out] = njClip(((x3 - x2) >> 14) + 128)
    out += stride
    sout[out] = njClip(((x7 - x1) >> 14) + 128)


def njShowBits(bits):
    if (not bits): return 0
    while (nj.bufbits < bits):
        if (nj.size <= 0):
            nj.buf = (nj.buf << 8) | 0xFF
            nj.bufbits += 8
            continue
        
        newbyte = nj.spos[nj.pos]
        nj.pos += 1
        nj.size -= 1
        nj.bufbits += 8
        nj.buf = (nj.buf << 8) | newbyte
        if (newbyte == 0xFF):
            if (nj.size):
                marker = nj.spos[nj.pos]
                nj.pos += 1
                nj.size -= 1
                if marker == 0xD9:
                    nj.size = 0
                elif marker != 0:
                    if ((marker & 0xF8) != 0xD0):
                        raise Exception(NJ_SYNTAX_ERROR)
                    else:
                        nj.buf = (nj.buf << 8) | marker
                        nj.bufbits += 8
            else:
                raise Exception(NJ_SYNTAX_ERROR)
    nj.buf = nj.buf & ((1 << nj.bufbits) - 1)
    return (nj.buf >> (nj.bufbits - bits)) & ((1 << bits) - 1)

def njSkipBits(bits):
    if (nj.bufbits < bits):
        njShowBits(bits)
    nj.bufbits -= bits

def njGetBits(bits):
    res = njShowBits(bits)
    njSkipBits(bits)
    return res

def njByteAlign():
    nj.bufbits &= 0xF8

def njSkip(count):
    nj.pos += count
    nj.size -= count
    nj.length -= count
    if (nj.size < 0): raise Exception(NJ_SYNTAX_ERROR)

def njDecode16(pos):
    return (nj.spos[pos] << 8) | nj.spos[pos + 1]

def njDecodeLength():
    if (nj.size < 2):
        raise Exception(NJ_SYNTAX_ERROR)
    nj.length = njDecode16(nj.pos)
    if (nj.length > nj.size):
        raise Exception(NJ_SYNTAX_ERROR)
    njSkip(2)

def njSkipMarker():
    njDecodeLength()
    njSkip(nj.length)

def njDecodeSOF():
    ssxmax = 0
    ssymax = 0
    njDecodeLength()
    if (nj.length < 9):
        raise Exception(NJ_SYNTAX_ERROR)
    if (nj.spos[nj.pos] != 8):
        raise Exception(NJ_UNSUPPORTED)
    nj.height = njDecode16(nj.pos + 1)
    nj.width = njDecode16(nj.pos + 3)
    nj.ncomp = nj.spos[nj.pos + 5]
    njSkip(6)
    if nj.ncomp != 1 and nj.ncomp != 3:
        raise Exception(NJ_UNSUPPORTED)
    if (nj.length < (nj.ncomp * 3)):
        raise Exception(NJ_SYNTAX_ERROR)
    i = 0
    while i < nj.ncomp:
        c = nj.comp[i]
        c.cid = nj.spos[nj.pos]
        c.ssx = nj.spos[nj.pos + 1] >> 4
        if not c.ssx:
            raise Exception(NJ_SYNTAX_ERROR)
        if (c.ssx & (c.ssx - 1)):
            raise Exception(NJ_UNSUPPORTED)  # non-power of two
        c.ssy = nj.spos[nj.pos + 1] & 15
        if not c.ssy:
            raise Exception(NJ_SYNTAX_ERROR)
        if (c.ssy & (c.ssy - 1)):
            raise Exception(NJ_UNSUPPORTED)  # non-power of two
        c.qtsel = nj.spos[nj.pos + 2]
        if c.qtsel & 0xFC:
            raise Exception(NJ_SYNTAX_ERROR)
        njSkip(3)
        nj.qtused |= 1 << c.qtsel
        if (c.ssx > ssxmax): ssxmax = c.ssx
        if (c.ssy > ssymax): ssymax = c.ssy
        i += 1
    
    nj.mbsizex = ssxmax << 3
    nj.mbsizey = ssymax << 3
    nj.mbwidth = (nj.width + nj.mbsizex - 1) // nj.mbsizex
    nj.mbheight = (nj.height + nj.mbsizey - 1) // nj.mbsizey
    i = 0
    while i < nj.ncomp:
        c = nj.comp[i]
        c.width = (nj.width * c.ssx + ssxmax - 1) // ssxmax
        c.stride = (c.width + 7)
        c.stride = c.stride & 0x7FFFFFF8
        c.height = (nj.height * c.ssy + ssymax - 1) // ssymax
        c.stride = nj.mbwidth * nj.mbsizex * c.ssx // ssxmax
        if (((c.width < 3) and (c.ssx != ssxmax)) or ((c.height < 3) and (c.ssy != ssymax))):
                raise Exception(NJ_UNSUPPORTED)
        c.pixels = [0] * (c.stride * (nj.mbheight * nj.mbsizey * c.ssy // ssymax))
        i += 1
    if (nj.ncomp == 3):
        nj.rgb = [0] * (nj.width * nj.height * nj.ncomp)
    njSkip(nj.length)

def njDecodeDHT():
    counts = [0] * 16
    njDecodeLength()
    while (nj.length >= 17):
        i = nj.spos[nj.pos]
        if (i & 0xEC):
            raise Exception(NJ_SYNTAX_ERROR)
        if (i & 0x02):
            raise Exception(NJ_UNSUPPORTED)
        i = (i | (i >> 3)) & 3  # combined DC/AC + tableid value
        for codelen in range(1, 17): # 1 to 16
            counts[codelen - 1] = nj.spos[nj.pos + codelen]
        njSkip(17)
        vlc = 0
        remain = 65536
        spread = 65536
        for codelen in range(1, 17): # 1 to 16
            spread >>= 1
            currcnt = counts[codelen - 1]
            if not currcnt: continue
            if (nj.length < currcnt):
                raise Exception(NJ_SYNTAX_ERROR)
            remain -= currcnt << (16 - codelen)
            if (remain < 0):
                raise Exception(NJ_SYNTAX_ERROR)
            for ii in range(currcnt):
                code = nj.spos[nj.pos + ii]
                j = spread
                while j:
                    nj.vlctab[i][vlc].bits = codelen
                    nj.vlctab[i][vlc].code = code
                    vlc += 1
                    j -= 1
            njSkip(currcnt)
        while remain:
            remain -= 1
            nj.vlctab[i][vlc].bits = 0
            vlc += 1
    if (nj.length):
        raise Exception(NJ_SYNTAX_ERROR)

def njDecodeDQT():
    njDecodeLength()
    while (nj.length >= 65):
        i = nj.spos[nj.pos]
        if (i & 0xFC):
            raise Exception(NJ_SYNTAX_ERROR)
        nj.qtavail |= 1 << i
        for j in range(64):
            nj.qtab[i][j] = nj.spos[nj.pos + j + 1]
        njSkip(65)
    if (nj.length):
        raise Exception(NJ_SYNTAX_ERROR)

def njDecodeDRI():
    njDecodeLength()
    if (nj.length < 2):
        raise Exception(NJ_SYNTAX_ERROR)
    nj.rstinterval = njDecode16(nj.pos)
    njSkip(nj.length)

#code is an array with one element, since we need to return the code to the caller
def njGetVLC(vlc, code):
    value = njShowBits(16)
    bits = vlc[value].bits
    if not bits:
        raise Exception(NJ_SYNTAX_ERROR)
    njSkipBits(bits)
    value = vlc[value].code
    if code: code[0] = value
    bits = value & 15
    if not bits: return 0
    value = njGetBits(bits)
    if (value < (1 << (bits - 1))):
        value += ((-1) << bits) + 1
    return value

#sout is a new parameter, because we need to modify the passed in array, so
#out is now just the index in out
def njDecodeBlock(c, sout, out):
    code = [0]
    value = 0
    coef = 0
    for i in range(len(nj.block)):
        nj.block[i] = 0
    c.dcpred += njGetVLC(nj.vlctab[c.dctabsel], None)
    nj.block[0] = c.dcpred * nj.qtab[c.qtsel][0]
    while True: # do {
        value = njGetVLC(nj.vlctab[c.actabsel], code);
        if not code[0]: break  # EOB
        if (not (code[0] & 0x0F) and (code[0] != 0xF0)):
            raise Exception(NJ_SYNTAX_ERROR)
        coef += (code[0] >> 4) + 1
        if coef > 63:
            raise Exception(NJ_SYNTAX_ERROR)
        nj.block[njZZ[coef]] = value * nj.qtab[c.qtsel][coef]
        # } while (coef < 63);
        if coef >= 63: break
    coef = 0
    while coef < 64:
        njRowIDCT(nj.block, coef)
        coef += 8
    for coef in range(8):
        njColIDCT(nj.block, coef, sout, out + coef, c.stride)

def njDecodeScan():
    rstcount = nj.rstinterval
    nextrst = 0
    # nj_component_t* c;
    njDecodeLength()
    if (nj.length < (4 + 2 * nj.ncomp)):
        raise Exception(NJ_SYNTAX_ERROR)
    if (nj.spos[nj.pos] != nj.ncomp):
        raise Exception(NJ_UNSUPPORTED)
    njSkip(1)
    i = 0
    while (i < nj.ncomp):
        c = nj.comp[i]
        if (nj.spos[nj.pos] != c.cid):
            raise Exception(NJ_SYNTAX_ERROR)
        if (nj.spos[nj.pos + 1] & 0xEE):
            raise Exception(NJ_SYNTAX_ERROR)
        c.dctabsel = nj.spos[nj.pos + 1] >> 4
        c.actabsel = (nj.spos[nj.pos + 1] & 1) | 2
        njSkip(2)
        i += 1
    if (nj.spos[nj.pos] or (nj.spos[nj.pos + 1] != 63) or nj.spos[nj.pos + 2]):
        raise Exception(NJ_UNSUPPORTED)
    njSkip(nj.length)
    mbx = 0
    mby = 0
    while True:
        i = 0
        while (i < nj.ncomp):
            c = nj.comp[i]
            sby = 0
            while sby < c.ssy:
                sbx = 0
                while sbx < c.ssx:
                    njDecodeBlock(c, c.pixels, ((mby * c.ssy + sby) * c.stride + mbx * c.ssx + sbx) << 3)
                    if nj.error:
                        return
                    sbx += 1
                sby += 1
            i += 1
        mbx += 1
        if mbx >= nj.mbwidth:
            mbx = 0
            mby += 1
            if mby >= nj.mbheight: break
        rstcount -= 1
        if (nj.rstinterval and not rstcount):
            njByteAlign()
            i = njGetBits(16)
            if (((i & 0xFFF8) != 0xFFD0) or ((i & 7) != nextrst)):
                raise Exception(NJ_SYNTAX_ERROR)
            nextrst = (nextrst + 1) & 7
            rstcount = nj.rstinterval
            for i in range(3):
                nj.comp[i].dcpred = 0
    nj.error = __NJ_FINISHED

#if NJ_CHROMA_FILTER

CF4A = -9
CF4B = 111
CF4C = 29
CF4D = -3
CF3A = 28
CF3B = 109
CF3C = -9
CF3X = 104
CF3Y = 27
CF3Z = -3
CF2A = 139
CF2B = -11
def CF(x):
    return njClip(((x) + 64) >> 7)

def njUpsampleH(c):
    xmax = c.width - 3
    out = [0] * ((c.width * c.height) << 1)
    lin = 0
    lout = 0
    y = c.height
    while y:
        out[lout + 0] = CF(CF2A * c.pixels[lin + 0] + CF2B * c.pixels[lin + 1])
        out[lout + 1] = CF(CF3X * c.pixels[lin + 0] + CF3Y * c.pixels[lin + 1] + CF3Z * c.pixels[lin + 2])
        out[lout + 2] = CF(CF3A * c.pixels[lin + 0] + CF3B * c.pixels[lin + 1] + CF3C * c.pixels[lin + 2])
        for x in range(xmax):
            out[lout + (x << 1) + 3] = CF(CF4A * c.pixels[lin + x] + CF4B * c.pixels[lin + x + 1] + CF4C * c.pixels[lin + x + 2] + CF4D * c.pixels[lin + x + 3])
            out[lout + (x << 1) + 4] = CF(CF4D * c.pixels[lin + x] + CF4C * c.pixels[lin + x + 1] + CF4B * c.pixels[lin + x + 2] + CF4A * c.pixels[lin + x + 3])
        lin += c.stride
        lout += c.width << 1
        out[lout - 3] = CF(CF3A * c.pixels[lin - 1] + CF3B * c.pixels[lin - 2] + CF3C * c.pixels[lin - 3])
        out[lout - 2] = CF(CF3X * c.pixels[lin - 1] + CF3Y * c.pixels[lin - 2] + CF3Z * c.pixels[lin - 3])
        out[lout - 1] = CF(CF2A * c.pixels[lin - 1] + CF2B * c.pixels[lin - 2])
        y -= 1
    c.width <<= 1
    c.stride = c.width
    c.pixels = out

def njUpsampleV(c):
    w = c.width
    s1 = c.stride
    s2 = s1 + s1
    out = [0] * ((c.width * c.height) << 1)
    for x in range(w):
        cin = x
        cout = x
        out[cout] = CF(CF2A * c.pixels[cin] + CF2B * c.pixels[cin + s1])
        cout += w
        out[cout] = CF(CF3X * c.pixels[cin] + CF3Y * c.pixels[cin + s1] + CF3Z * c.pixels[cin + s2])
        cout += w
        out[cout] = CF(CF3A * c.pixels[cin] + CF3B * c.pixels[cin + s1] + CF3C * c.pixels[cin + s2])
        cout += w
        cin += s1
        y = c.height - 3
        while y:
            out[cout] = CF(CF4A * c.pixels[cin - s1] + CF4B * c.pixels[cin] + CF4C * c.pixels[cin + s1] + CF4D * c.pixels[cin + s2])
            cout += w
            out[cout] = CF(CF4D * c.pixels[cin - s1] + CF4C * c.pixels[cin] + CF4B * c.pixels[cin + s1] + CF4A * c.pixels[cin + s2])
            cout += w
            cin += s1
            y -= 1
        cin += s1
        out[cout] = CF(CF3A * c.pixels[cin] + CF3B * c.pixels[cin - s1] + CF3C * c.pixels[cin - s2])
        cout += w
        out[cout] = CF(CF3X * c.pixels[cin] + CF3Y * c.pixels[cin - s1] + CF3Z * c.pixels[cin - s2])
        cout += w
        out[cout] = CF(CF2A * c.pixels[cin] + CF2B * c.pixels[cin - s1])
    c.height <<= 1
    c.stride = c.width
    c.pixels = out

#else

# NJ_INLINE void njUpsample(nj_component_t* c) {
#     int x, y, xshift = 0, yshift = 0;
#     unsigned char *out, *lin, *lout;
#     while (c->width < nj.width) { c->width <<= 1; ++xshift; }
#     while (c->height < nj.height) { c->height <<= 1; ++yshift; }
#     out = njAllocMem(c->width * c->height);
#     if (!out) njThrow(NJ_OUT_OF_MEM);
#     lin = c->pixels;
#     lout = out;
#     for (y = 0;  y < c->height;  ++y) {
#         lin = &c->pixels[(y >> yshift) * c->stride];
#         for (x = 0;  x < c->width;  ++x)
#             lout[x] = lin[x >> xshift];
#         lout += c->width;
#     }
#     c->stride = c->width;
#     njFreeMem(c->pixels);
#     c->pixels = out;
# }

#endif

def njConvert():
    for i in range(nj.ncomp):
        c = nj.comp[i]
        if NJ_CHROMA_FILTER:
            while ((c.width < nj.width) or (c.height < nj.height)):
                if c.width < nj.width: njUpsampleH(c)
                if nj.error: return
                if c.height < nj.height: njUpsampleV(c)
                if nj.error: return
        else:
            if ((c.width < nj.width) or (c.height < nj.height)):
                njUpsample(c)
        if ((c.width < nj.width) or (c.height < nj.height)):
            raise Exception(NJ_INTERNAL_ERR)
            return
    if nj.ncomp == 3:
        # convert to RGB
        prgb = 0
        py  = 0
        pcb = 0
        pcr = 0
        yy = nj.height
        #print( 'nj.width: %s, nj.height: %s, strides: %s, %s, %s, lengths: %s, %s, %s, first few bytes: %s, %s, %s' % \
        #    (nj.width, nj.height, nj.comp[0].stride, nj.comp[1].stride, nj.comp[2].stride,
        #    len(nj.comp[0].pixels), len(nj.comp[1].pixels), len(nj.comp[2].pixels),
        #    nj.comp[0].pixels[0], nj.comp[0].pixels[1], nj.comp[0].pixels[2]))
        while yy:
            for x in range(nj.width):
                y = nj.comp[0].pixels[py + x] << 8
                # print 'len(nj.comp): %s, len(nj.comp[1].pixels): %s, pcb + x: %s, yy: %s, x: %s' % \
                #     (len(nj.comp), len(nj.comp[1].pixels), pcb + x, yy, x)
                cb = nj.comp[1].pixels[pcb + x] - 128
                cr = nj.comp[2].pixels[pcr + x] - 128
                nj.rgb[prgb] = njClip((y            + 359 * cr + 128) >> 8)
                prgb += 1
                nj.rgb[prgb] = njClip((y -  88 * cb - 183 * cr + 128) >> 8)
                prgb += 1
                nj.rgb[prgb] = njClip((y + 454 * cb            + 128) >> 8)
                prgb += 1
            py += nj.comp[0].stride
            pcb += nj.comp[1].stride
            pcr += nj.comp[2].stride
            yy -= 1
    elif (nj.comp[0].width != nj.comp[0].stride):
        # grayscale -> only remove stride
        # unsigned char *pin = &nj.comp[0].pixels[nj.comp[0].stride];
        # unsigned char *pout = &nj.comp[0].pixels[nj.comp[0].width];
        # int y;
        # for (y = nj.comp[0].height - 1;  y;  --y) {
        #     njCopyMem(pout, pin, nj.comp[0].width);
        #     pin += nj.comp[0].stride;
        #     pout += nj.comp[0].width;
        # }
        # nj.comp[0].stride = nj.comp[0].width;
        pass

def njInit():
    # njFillMem(&nj, 0, sizeof(nj_context_t));
    nj.init()

def njDone():
    pass

def njDecode(jpeg, size):
    njDone()
    nj.spos = jpeg
    nj.pos = 0
    nj.size = size & 0x7FFFFFFF
    if (nj.size < 2): return NJ_NO_JPEG
    if ((nj.spos[nj.pos] ^ 0xFF) | (nj.spos[nj.pos + 1] ^ 0xD8)): return NJ_NO_JPEG
    njSkip(2)
    while not nj.error:
        if ((nj.size < 2) or (nj.spos[nj.pos] != 0xFF)):
            return NJ_SYNTAX_ERROR
        njSkip(2)
        m = nj.spos[nj.pos - 1]
        if m == 0xC0: njDecodeSOF()
        elif m == 0xC4: njDecodeDHT()
        elif m == 0xDB: njDecodeDQT()
        elif m == 0xDD: njDecodeDRI()
        elif m == 0xDA: njDecodeScan()
        elif m == 0xFE: njSkipMarker()
        elif (m & 0xF0) == 0xE0:
            njSkipMarker()
        else:
            return NJ_UNSUPPORTED
    if (nj.error != __NJ_FINISHED): return nj.error
    nj.error = NJ_OK
    njConvert()
    return nj.error


def njGetWidth():
    return nj.width
def njGetHeight():
    return nj.height
def njIsColor():
    return (nj.ncomp != 1)
def njGetImage():
    return nj.comp[0].pixels if nj.ncomp == 1 else nj.rgb
def njGetImageSize():
    return nj.width * nj.height * nj.ncomp

#endif // _NJ_INCLUDE_HEADER_ONLY
