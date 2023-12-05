# CU-ST Radar Data Processor (CDP)

vers ~~ 2.0 Win

CDP aims to assist in analysis of spectral data dumped by CU-STR and obtain various functionalities from it. 


<p align="center" float="left">
  <img src="https://github.com/JunesDiary/cdp/main/cdp.jpg"  /> 
</p>


### Download and installation
Install the following libraries, as they are required by the code to function. 

1. tkinter
2. prettytable
3. scipy
4. Pillow

i.e. run the following:

```
pip install tk prettytable scipy Pillow
```

Rest libraries used are JSON, Scipy, Matplotlib, Numpy, os, sys, math must be there with proper python3 installation. Download the codes in this repo.

To run the code, open the cmd and move to the directory of the downloaded code. Then run the following:



```
python3 cdp.py
```


### Functionalities

1. Analysis of Active Mode data for generating Doppler information, U-V-W Wind generation and other tools.
2. Analysis of Passive Mode data for signal processing and noise management for experiments in Astronomy.
