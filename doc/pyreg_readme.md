# pyreg  

[Shield-2018 Manual](https://www.biorxiv.org/content/biorxiv/early/2019/03/16/576595.full.pdf)


## Data

[Example Data](https://leviathan-chunglab.mit.edu/nature-protocols-2019/)

Command for retrieving the data
```sh
wget -P /media/gray/quetzspace/ -r --no-parent –Nh --cut-dirs 1 -R “index.html*” http://leviathan-chunglab.mit.edu/nature-protocols-2019/raw_data/ -o logfile
```

## Initial Shield-2018 setup

### Create container

Commands to forward X11 to the host so that we can display GUI apps running in the docker container, in the host. This also needs to be run every time the container is started.  

```sh
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
sudo rm -rf $XAUTH
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | sudo xauth -f $XAUTH nmerge -
```

Run once to create the docker with mapped folder (home).

This maps two directories, projects and data, from the host to the container. In our example, ``/home/gray/projects`` is mapped to ``projects``, and ``/ssd2`` is mapped to ``/data``. These mapped folders serve as a useful separation between docker files, keeping apps and scripts in one place and data in another.

```sh
docker pull chunglabmit/shield-2018:latest

docker run -it --network host --volume=/home/gray/projects:/projects:rw --volume=/ssd2:/data:rw --volume=/raid/docker_data:/raid:rw --volume=$XSOCK:$XSOCK:rw --volume=$XAUTH:$XAUTH:rw --env="XAUTHORITY=${XAUTH}" --env="DISPLAY"  chunglabmit/shield-2018
```

Once in the container, update the OS.
```sh
apt update
apt dist-upgrade
exit
```

### Container setup

Once created, inspect docker to get the name of the container just created, e.g. ``angry_stallman``. To start the container just created, run the following commands:


```sh
docker start angry_stallman
docker attach angry_stallman
```

You should now be in the container. Inspect that the directories are properly mapped. For example, ``ls /projects`` should contain your projects and ``ls /data`` should contain your data.

#### Download data

Please refer to Shield-2018 Manual, Equipment Setup section to download the full resolution example data. From now on, these instructions assume that you have downloaded the example data to the host into the folder mapped to the docker container. In our example, the data is downloaded in the host to  ``/ssd2`` and is mapped to ``/data`` in the container.

### Running the container 

Run the following commands to enter the docker container every time you log into or restart the host computer
```sh
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
sudo rm -rf $XAUTH
touch $XAUTH
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | sudo xauth -f $XAUTH nmerge -
```
Run only these commands if you are restarting the docker container
```sh
docker start container_name
docker attach container_name
```

### Protocol Usage

The following is an example of an entire ``pyreg`` image processing and registration run starting from the raw example data provided by Shield-2018. This protocol follows closely to the Shield-2018 manual (referenced at the top of this documentation), so it will be necessary to periodically consult the manual as you follow along. It is important to note that some steps generate files who's locations are provided in the function call, so be careful of where you specify output. If a step generates a file, but does not give the user a way to specify a location, assume the file is generated in the current directory. To begin, first install the required packages and verify their installation with ``--help``:

First enter into the docker container with the commands:
```sh
docker start angry_stallman
docker attach angry_stallman
```

Build dependencies for the destriping process

```sh
git -C /shield-2018/pystripe pull
python3 -m pip install dcimg
python3 -m pip install -e .
pystripe --help 
```

1.) Destripe the full-resolution example data, ``Ex_0_Em_0``:

```sh
pystripe -i  /data/raw_data/Ex_0_Em_0 -o /data/destriped_data/Ex_0_Em_0 -s1 256 -s2 256 -w db10 -c 3 -x 10 --dark 100
```

If you want to analyze the entire dataset, repeat step 1 for all other channels, ``Ex_1_Em_1`` and ``Ex_2_Em_2``

2.) Stitching together the LSFM images. First install the required packages: 

```sh
git -C /shield-2018/tsv pull
```

2.a) Create a stitching project file based on a single channel with the command:

```sh
terastitcher -1 --volin=/data/destriped_data/Ex_0_Em_0 --ref1=H --ref2=V --ref3=D --vxl1=1.8 --vxl2=1.8 --vxl3=2 --projout=/data/destriped_data/Ex_0_Em_0/xml_import.xml --sparse_data 
```

Repeat 2.a for all other channels, ``Ex_1_Em_1`` and ``Ex_2_Em_2`` 

2.b) Calculate the stack displacements using the command:

```sh
terastitcher -2 --projin=/data/destriped_data/Ex_0_Em_0/xml_import.xml --projout=/data/destriped_data/Ex_0_Em_0/xml_displacement.xml
```

Repeat 2.b for all other channels, ``Ex_1_Em_1`` and ``Ex_2_Em_2`` 

2.c) Generate a Terastitcher project file by entering the following command:

```sh
terastitcher -3 --projin=/data/destriped_data/Ex_0_Em_0/xml_displacement.xml --projout=/data/destriped_data/Ex_0_Em_0/xml_displproj.xml
```

Repeat 2.c for all other channels, ``Ex_1_Em_1`` and ``Ex_2_Em_2`` 

2.d) Use TSV to generate stitched images by entering the following command:

```sh
tsv-convert-2D-tif --xml-path /data/destriped_data/Ex_0_Em_0/xml_displproj.xml --output-pattern /data/stitched_data/Ex_0_Em_0_master/"{z:04d}.tiff" --compression 4 --ignore-z-offsets
``` 

Repeat 2.d for all other channels, ``Ex_1_Em_1`` and ``Ex_2_Em_2`` 

2.e) Inspect the stitched images in FIJI. TIFF images which can be imported directly into FIJI. 

3.) Atlas alignment with manual point refinement using nuggt

*OPTIONAL STEP* - If you intend to create your own set of points used in alignment or are not aligning your brain to the Allen Brain Atlas, please see the Shield-2018 manual section C, steps vi-xi for instructions

To begin the automated alignment process, first you must perform image correction that is unique to your data (e.g. flipping and cropping) - see Section C, step xii-xiii for more details. FOr the example data, we entered the following commands:
The files are included in the "/allen-mouse-brain-atlas" folder. 

|File Name | Description |
| ------------- |:-------------:|
| autofluorescence_25_half_sagittal.tif | a 3D image of the autofluorescence channel for the mid-sagittal sectioning of the Allen Mouse Brain atlas reference (to be used in place of "/reference/reference.tiff").|
| annotation_25_half_sagittal.tif | a 3D segmentation of the Allen Mouse Brain reference (to be used in place of "/reference/segmentation.tiff") |
| coords_25_half_sagittal.json | the coordinates of key points on the reference (to be used in place of "/reference/points.json") |
| AllBrainRegions.csv |  a mapping of region ID numbers in the segmentation to names of regions. |
```sh
rescale-image-for-alignment --input "/data/stitched_data/Ex_0_Em_0_master/*.tiff" --atlas-file /allen-mouse-brain-atlas/autofluorescence_25_half_sagittal.tif --output /data/downsampled_flip-x_flip-z_clip-y-0-9800.tiff --flip-x --flip-z --clip-y 0,9800
```

Repeat this step with any necessary adjustments for the other sets of images, ``Ex_1_Em_1`` and ``Ex_2_Em_2``

3.a) Perform the automated alignment with SITK:

```sh
sitk-align --moving-file /data/downsampled_flip-x_flip-z_clip-y-0-9800.tiff --fixed-file /allen-mouse-brain-atlas/autofluorescence_25_half_sagittal.tif --fixed-point-file /allen-mouse-brain-atlas/coords_25_half_sagittal.json --xyz --alignment-point-file /data/alignment.json
```

Align the other image sets with this command

4.) Manual refinement of image registration

The points file generated from the first alignment step must be refined to better represent a better mapping of the points from the moving image to the reference image. Run the following command to open a nuggt terminal:

```sh
nuggt-align --reference-image /allen-mouse-brain-atlas/autofluorescence_25_half_sagittal.tif --moving-image downsampled_flip-x_flip-z_clip-y-0-9800.tiff --points /data/alignment.json
```

Copy and paste the link produced by this step into a Chrome web browser, or any other WebGL enabled web browser.

Consult Section C, steps xvi-xxii of the Shield-2018 manual for explicit instructions on how to refine and warp the points.

After successfully refining the point set, save the point coordinates as described in Section C, step xxii. Saving the points should generate a JSON file of coordinates. 


5.) Conversion of JSON file format to SITK point format

The JSON file generated in step 4 is not in the correct format to be used in SITK alignment. Use the conversion script provided, chung_lab_point_converter.py, to convert the JSON script into a usable txt format. Simply provide the file location of the JSON file to the script and two txt file will be generated automatically, one for the reference points and one for the moving points (conventional names used for images to be registered). Save the file into a new folder, in this example the folder name is ``/data/round_1``.

6.) Second SITK alignment phase

This SITK alignment step makes use of the manually refined points generated earlier in the protocol by setting the alignment optimization metrics to include a corresponding points file. The following command is similar to the command in step 3a, only this command includes parameters to specify the point-based registration option and the location of the points file generated in step 5. The command to perform point-based SITK registration is:

 ```sh
sitk-align --moving-file /data/flip-x_flip-z_clip-y-0-9800.tiff --fixed-file /allen-mouse-brain-atlas/autofluorescence_25_half_sagittal.tif --aligned-file /data/round_2/r2_registration2.tif --transform-parameters-folder /data/round_2 --custom-points-registration True --custom-reference-points /data/round_1/reference_points.txt --custom-moving-points /data/round_1/moving_points.txt
```

 The ``--aligned-file`` parameter specifies the output location and name of the SITK alignment process, for us it is ``/data/round_2/r2_registration2.tif``. The ``--transform-parameters-folder`` parameter writes out the transform parameters generated by SITK to a given location, for us it is ``/data/round_2/``. The ``--custom-points-registration`` parameter is a boolean parameter to signal the use of point-based registration, set to ``True``. The ``--custom-reference-points`` parameter specifies the location and name of the txt file generated in step 5 containing the reference points, specifically ``/data/round_1/reference_points.txt``. The ``--custom-moving-points`` parameter specifies the location and name of the txt file generated in step 5 containing the moving points, specifically ``/data/round_1/moving_points.txt``.

The output of this step should be the registered images. This is the end of the protocol.

7.) Compute fluorescence statistics
```shell script
calculate-intensity-in-regions --input "/data/stitched_data/channel/*.tiff" --alignment /data/rescaled-alignment.json --reference-segmentation /reference/segmentation.tiff -- brain-regions-csv /reference/brain-regions.csv --output /data/results-level-7.csv --level 7

```
"--level" takes a value from 7 the finest granularity of the segmentation to 1 the coarsest granularity. 

## Time complexity 

### For processing full resolution example data: 
≈ 14 hours 
### For processing downsampled example data:
≈ 4 hours

