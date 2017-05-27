"""
program takes inputs (1) file name (2) analysis coefficient (3) reconstruction coefficient
outputs a .wav file analyzed with a 1tap wavelet defined by coefficient (2) 
and reconstructs it with a 1tap wavelet defined by coefficient (3)
(1) must be a mono .wav in 16/32 bit
(2) & (3) should be floats beween 0 and 1 exclusive
for perfect reconstruction set both coefficients equal to each other
"""
import sys
import numpy as np
import wave
import struct
import time
from scipy import signal

samp_width = 0
samp_rate = 0
struct_symbol = ''
pad_amount = 0

def conv(x,c):
    """
    convolves 1D signal array 'x' with 1D filter array 'c'. 
    returns array same size as x
    """
    N = len(x)
    y = np.arange(N, dtype = np.float)
    l = len(c)-1
    for n in range(N):
        s = 0
        for m in range(max(l-n, 0), l+1):
            s += x[n-l+m] * c[l-m]
        y[n] = s
    return y

def convT(x,c):
    """
    convolves 1D signal array 'x' with 1D transposed filter array 'c'. 
    mimimcs multiplication by transpose of FIR filter c 
    returns array same size as x
    """
    N = len(x)
    y = np.arange(N, dtype = np.float)
    l = len(c)
    for n in range(N):
        s = 0
        for k in range(n, min(l+n, N)):
            s += x[k] * c[k-n]
        y[n] = s
    return y
    
def normalize(v):
    """
    return array with each element divided by the euclidean norm of array v
    """
    norm = 0
    for x in v:
        norm += x **2
    norm = np.sqrt(norm)
    return v / norm
    
def downsample(x):
    """
    given 1D array returns 1D array of half the size 
    containing the coefficients of input array with even index
    """
    l = int((len(x)+1)/2)
    y = np.zeros(l)
    for ii in range(len(x)):
        if ii % 2 == 0:
            y[int(ii/2)] = x[ii]
    return y

def upsample(x):
    """
    returns 1D array with 0s in between successive entries of input array
    has twice the length of the input
    """
    l = 2 * len(x)
    y = np.zeros(l)
    for ii in range(l):
        if ii % 2 == 0:
            y[ii] = x[int(ii/2)]
    return y

def wavelet_analysis(signal_, lpfilter, hpfilter):
    """
    gives array containing cascading wavelet coefficients starting with lower level. 
    Every entry is array with length a power of 2 except for last two, which have length 1 
    Succesive entries' length decreases by factor of 2 except last one. 
    """
    filterbank = []
    current_signal = signal_
    while len(current_signal) > 1:
        y = convT(current_signal, lpfilter)
        y = downsample(y)
        filterbank.append(y)
        z = convT(current_signal, hpfilter)
        z = downsample(z)
        current_signal = z
    filterbank.append(current_signal)
    return filterbank

def wavelet_synthesis(filterbank, lpfilter, hpfilter):
    """   
    synthesises wavelet coefficients according to given filter.
    input must have same structure type as outout of wavelet_analysis
    """
    bank = filterbank
    current_signal = bank.pop()
    while len(bank) > 0:
        current_signal = upsample(current_signal)
        current_signal = conv(current_signal, hpfilter)
        c = bank.pop()
        c = upsample(c)
        c = conv(c, lpfilter)
        current_signal = current_signal + c     
    return current_signal
    
def pad_array(x):
    """
    extends array to a length of power of 2 by padding with zeroes
    """
    l = len(x)
    e = np.log2(l)
    if e - int(e) == 0.0:
        return x
    ad = 2 ** (int(e)+1) -l
    z = np.zeros(ad)
    y = np.append(x, z)
    global pad_amount 
    pad_amount = len(z)
    return y
    
def wav_get_settings(file):
    """
    reads wav file and updates global sample width and sample rate parameters 
    for wav read/write
    """
    global samp_width
    global samp_rate
    W = wave.open(file, 'rb')
    samp_width = W.getsampwidth()
    samp_rate = W.getframerate()
    W.close()    

def wav_to_array(file):
    """
    input mono 16 or 32 bit wav file. 
    Outputs array containing the sequential amplitute of audio
    """
    W = wave.open(file, 'rb')
    L = W.getnframes()
    y = []
    for i in range(L):
        waveData = W.readframes(1)
        if samp_width == 2:
            data = struct.unpack('<h', waveData)
            y.append(int(data[0]))
        if samp_width == 4:            
            data = struct.unpack('i', waveData)
            y.append(int(data[0]))
    W.close()
    y = np.array(y)
    return y

def array_to_wav(x):
    """
    input 1D array. Converts entires to integer type based on global samp_width. 
    Writes sequence to audio file with global samp_rate. 
    Prints success statement
    """
    NAME = str(int(time.time())) + '.wav'
    W = wave.open(NAME, 'wb')
    W.setparams((1, samp_width, samp_rate, 0, 'NONE', 'not compressed'))
    for ii in x:
        if samp_width == 2:
            dat = np.int16(ii)
            waveData = struct.pack('<h', dat)
        if samp_width == 4:
            dat = np.int32(ii)
            waveData = struct.pack('i', dat)
        W.writeframes(waveData)
    W.close()
    print('Audio successfully exported as ' + NAME)
    
def depad_array(x):
    """
    removes trailing 0 entries inserted by pad_array function
    """
    y = x[0:(len(x) - pad_amount)]
    return y

if __name__ == "__main__":
    input1 = sys.argv[1]
    input2 = sys.argv[2]
    input3 = sys.argv[3]

    file = str(input1)
    alpha = float(input2)
    beta = float(input3)

    c = normalize([alpha, (1 - alpha)])
    d = normalize(signal.qmf(c))
    c0 = normalize([beta, (1 - beta)])
    d0 = normalize(signal.qmf(c0))

    wav_get_settings(file)
    z = wav_to_array(file)
    z0 = pad_array(z)
    z1 = wavelet_analysis(z0, c, d)
    z2 = wavelet_synthesis(z1, c0, d0)
    z3 = depad_array(z2)
    array_to_wav(z3)