import numpy as np
from stl import mesh
import operator
import skimage as ski
import pydicom
import threading
import sys
import getopt
from os import walk
import re

stepsize = int(sys.argv[1])
lower_threshold = int(sys.argv[2])
upper_threshold = int(sys.argv[3])
filepath = sys.argv[4]
outfilename = sys.argv[5]

midpoint = int((upper_threshold + lower_threshold)/2)
threshold_width = int((upper_threshold - lower_threshold)/2)

class slicePosition:
    def __init__(self, name, location):
        self.name = name
        self.location = location
    def getLocation(self):
        return self.location
    def getName(self):
        return self.name
    def __lt__(self, other):
        return self.location < other.location
    

#get names of all dicom files in the given path
file_names = []
for (dirpath, dirs, files) in walk(filepath):
    file_names.extend(files)
    break
r = re.compile(".*[.]dcm$")
file_names = list(filter(r.match, list(file_names)))

#preliminary read for resolution
print("preliminary read")
tmpFileData = pydicom.dcmread(filepath+'/'+file_names[0])
xresolution, yresolution = tmpFileData.pixel_array.shape
sliceThickness = tmpFileData.SliceThickness
pixelSpacing = [float(tmpFileData.PixelSpacing[0]), float(tmpFileData.PixelSpacing[1])]

#sort files by location in image
file_list = []
for s in file_names:
    tmpFileData = pydicom.dcmread(filepath+'/'+s).SliceLocation
    file_list.append(slicePosition(filepath+'/'+s, tmpFileData))

print("sorting by location")
file_list.sort()

def main():
        #full read and import
        print("loading image data")
        totalimage = np.zeros((len(file_names), xresolution, yresolution))
        for i, slice_object in enumerate(file_list):
            a = pydicom.dcmread(slice_object.getName()).pixel_array
            a -= midpoint
            a[a > 0] = -a[a > 0]
            totalimage[i] = a


        #Pass to SCIKITfor marching cubes
        print("marching cubes")
        # use second thread to prevent windows timing us out
        verts, faces, normals, values = ski.measure.marching_cubes_lewiner(totalimage, level = -threshold_width, step_size=stepsize, spacing=(sliceThickness, pixelSpacing[0], pixelSpacing[1]))

        #Convert Vertices to STL
        print("converting to stl")
        output_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                output_mesh.vectors[i][j] = verts[f[j],:]

        print("saving")
        output_mesh.save(outfilename)
        print("finished")

t1 = threading.Thread(target = main)
t1.start()
t1.join()