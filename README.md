# Wavelet_basis
Analyzes audio signal with one wavelet and then reconstructs the data with a different wavelet. 

The program takes as input one mono .wav file in 16 or 32 bit as well as the specification for
1)coefficient for analysis wavelet
2)coefficient for synthesis wavelet
then returns a mono .wav with the same bit depth. 

The wavelets are controlled by real coefficients alpha, beta with alpha the analysis parameter and beta the synthesis parameter. In particular the low-pass wavelets are the normalized versions of [alpha, 1 - alpha] and [beta, 1 - beta] respectively. 

![wavelets_-_filter_bank](https://cloud.githubusercontent.com/assets/28970919/26517272/43f8c42a-4263-11e7-9af8-43041a02a0d5.png)

The above image (courtesy of Wikipedia) shows the analysis stage. If we set alpha == beta the perfect reconstruction is guaranteed.
