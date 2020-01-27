# pyreg
Image registration package for python

# Introduction
The goal of this image processing pipeline is to be able to 
efficiently process 3D light-sheet images of mouse brains with a set of
cell bodies lit up via fluorescent tags from FisTRAP mice and immunohistochemically
based. 

# Steps of the Image Processing pipeline
1) preprocesing and quality control (destriping)
2) stitching data for atlas alignment
3) registering to a standard mouse atlas [The Allen CCF v3](http://help.brain-map.org/display/mousebrain/API) or 
  [Enhanced and Unified Anatomical Labeling for a Common Mouse Brain Atlas](https://www.biorxiv.org/content/10.1101/636175v1)
4) visualization (Vaa3d, Imaris, Arivis 4D, and FuJI)
5) segmenation and cell counting [U-Net: deep learning for cell counting, detection, and morphometry](https://www.nature.com/articles/s41592-018-0261-2)

# General stuff

Mounting the shared server as a normal drive on a linux machine. This line needs to be added the ``/etc/fstab`` file

```sh
sudo nano /etc/fstab
```
Then paste this line at the end
```sh
//quetzalcoatl.local/workspace/ /media/gray/quetzspace cifs user=gray,pass=lablab,file_mode=0777,dir_mode=0777,noperm 0 0
```

Read and write speed test for linux ssd, quetzalcoatl server, and window raid storage. Test was performed with this code:

```py
import os
import timeit

data = dict()

def read_all(path):
    data.clear()
    for root, dirs, files in os.walk(path):
        for f in files:
            with open(os.path.join(root,f), "rb") as fh:
                data[(root.replace(path,''),f)] = fh.read()


def write(path):
    for (root,f),content in data.items():
        # print(path,root)
        os.makedirs(os.path.join(path,root),exist_ok=True)
        with open(os.path.join(path,root,f), 'wb') as fh:
            fh.write(content)


print(timeit.timeit(setup="from __main__ import read_all", stmt="read_all('/home/gray/Desktop/LOC00001/')",number=1))
print(timeit.timeit(setup="from __main__ import read_all", stmt="read_all('/media/gray/quetzspace/Yu Lab Brain Data/Raw Data/deconvolution_input/VW0/CHN00/LOC00001/')",number=1))
print(timeit.timeit(setup="from __main__ import read_all", stmt="read_all('/raid/docker_data/LOC00001/')",number=1))

print(timeit.timeit(setup="from __main__ import write", stmt="write('/home/gray/Desktop/LOC00001-copy/')",number=1))
print(timeit.timeit(setup="from __main__ import write", stmt="write('/media/gray/quetzspace/Yu Lab Brain Data/Raw Data/deconvolution_input/VW0/CHN00/LOC00001-copy')",number=1))
print(timeit.timeit(setup="from __main__ import write", stmt="write('/raid/docker_data/LOC00001-copy')",number=1))
```
Results of two runs
```
RUN 1
~read~
ssd - 3.722733586007962
server - 9.70251502499741
raid - 3.9086415830097394
~write~
ssd - 4.040428158012219
server - 12.09031660000619
raid - 46.34526721299335

RUN 2
~read~
ssd - 3.83814213599544
server - 9.04114085699257
raid - 3.9069085770024685
~write~
ssd - 4.039209708003909
server - 11.972381725994637
raid - 47.36286968400236
```
