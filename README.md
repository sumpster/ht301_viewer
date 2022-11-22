# ht301_hacklib
ht-301 thermal camera opencv python lib.

Supported thermal cameras:
- Hti HT-301
- Xtherm T3S, thanks to Angel-1024!

It's a very simple hacked together lib, might be useful for somebody,  
uses `matplotlib` which is a little bit on the slow side,  
or pure `opencv` - much faster but with less features.

Tested on ubuntu 20.04:

```
$ ./pyplot.py
keys:
    'h'      - help
    'q'      - quit
    ' '      - pause, resume
    'd'      - set diff
    'x','c'  - enable/disable diff, enable/disable annotation diff
    'f'      - full screen
    'u'      - calibrate
    't'      - draw min, max, center temperature
    'e'      - remove user temperature annotations
    'w'      - save to file date.png
    'r'      - save raw data to file date.npy
    ',', '.' - change color map
    'a', 'z' - auto exposure on/off, auto exposure type
    left, right, up, down - set exposure limits

mouse:
    left  button - add Region Of Interest (ROI)
    right button - add user temperature annotation
```
![pyplot output](docs/pyplot-output1.png)
![pyplot output](docs/pyplot-output2.png)

View saved ('r' key) raw data file:
```
$ ./pyplot.py 2022-09-11_18:49:07.npy
```

Opencv version:
```
$ ./opencv.py -h
usage: opencv.py [-h] [-c COLORMAP] [-s {1,2,3}] [-r FROM TO] [-nl] [-nm]

optional arguments:
  -h, --help            show this help message and exit
  -c COLORMAP, --colormap COLORMAP
                        color map used for thermal gradient (bone, inferno, jet, turbo, ...)
  -s {1,2,3}, --scale {1,2,3}
                        scaling factor for video size (default 2)
  -r FROM TO, --range FROM TO
                        specify visualized temperature range (default auto)
  -nl, --no-legend      hide color map legend
  -nm, --no-markers     hide min/max/center temperature markers
  ```
![opencv output](docs/opencv-output.png)
