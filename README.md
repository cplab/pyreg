# pyreg
Image registration package for python


Docker with GUI
===============

Instructions for installing any docker container that will be displaying a GUI in the host.

```sh
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
sudo rm -rf $XAUTH
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | sudo xauth -f $XAUTH nmerge -
```
Run once to create the docker with mapped folder (home)
```sh
sudo docker run -it --volume=/home/:/container:rw --volume=$XSOCK:$XSOCK:rw --volume=$XAUTH:$XAUTH:rw --env="XAUTHORITY=${XAUTH}" --env="DISPLAY"  ubuntu:18.04
```


