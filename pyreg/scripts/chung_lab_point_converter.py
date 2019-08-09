"""chung_lab_point_converter - convert the coordinate reference scheme in points files from [z,y,x] to [x,y,z]
Takes input from JSON point files from the refinement step of the Chung pipeline and outputs new text files (.txt) for
use in SITK alignment

Final output txt file format:

index
<number of points> 115
x y z
...

"""


import numpy as np
from os.path import join, dirname
import json


def import_json():
    # Import the JSON file that contains the "reference" and "moving" point data
    filename_alignment = input("Please provide full path to JSON point file: ")
    filename_alignment = str(filename_alignment)

    with open(filename_alignment) as r:
        alignment_json = json.load(r)

    return alignment_json


def convert_xyz(array=np.empty([0,0])):
    # Store the number of points in the files to set size of arrays
    size_pts = (np.shape(array))[0]

    # Empty arrays to store the final rearranged point data
    convert = np.empty([size_pts, 3])

    # Empty arrays to store x,y,z ref point data
    a = np.empty([size_pts, 1])
    b = np.empty([size_pts, 1])
    c = np.empty([size_pts, 1])

    # CONVERT REFERENCE POINT DATA
    ct = 0
    for i in array:
        a[ct] = float(i[0])
        b[ct] = float(i[1])
        c[ct] = float(i[2])
        ct += 1

    pos = 0
    ct = 0
    for i in convert:
        i[pos] = c[ct]
        pos += 1
        i[pos] = b[ct]
        pos += 1
        i[pos] = a[ct]
        pos = 0
        ct += 1

    return convert, size_pts


def write_txt_file(array=np.empty([0,0]), size_pts=0, filename=""):
    # Write out the converted reference point data into a text file
    root = dirname(__file__)
    with open(join(root, filename), "w+") as output:
        output.write("index \n")
        output.write(str(size_pts) + "\n")
        for i in array:
            output.write(str(i[0]) + " " + str(i[1]) + " " + str(i[2]) + "\n")
        output.close()

    return None


def main():
    alignment_json = import_json()

    ref_orig = np.array(alignment_json["reference"])
    mov_orig = np.array(alignment_json["moving"])

    ref_convert, ref_size = convert_xyz(array=ref_orig)
    mov_convert, mov_size = convert_xyz(array=mov_orig)

    write_txt_file(array=ref_convert, size_pts=ref_size, filename="reference_points.txt")
    write_txt_file(array=mov_convert, size_pts=mov_size, filename="moving_points.txt")


if __name__ == "__main__":
    main()
