#Revised version: instead of automatically adding in the upper and lower threhold, add in user input so that they control it
#This is more user friendly, and more convenient for dicom files that need different dimensions for the best output
import numpy as np
from stl import mesh
import operator
import skimage.measure as ski
import pydicom
import threading
import sys
import getopt
from os import walk
import re
import datetime

#Original code below:
stepsize = int(sys.argv[1])
lower_threshold = int(sys.argv[2])
upper_threshold = int(sys.argv[3])
filepath = sys.argv[4]
outfilename = sys.argv[5]

#New code designed for user input
#stepsize1 = input("Enter your preferred stepsize: ")
#lower_threshold1 = input("Enter your preferred lower threshold: ")
#upper_threshold1 = input("Enter your preferred upper threshold: ")
#filepath = input("What file path are your dicom files found in? ")
#outfilename = input("Name your new stl file: ")

#write values run by the user and time
x = datetime.datetime.now()
s = open("testlogfile.txt", "a")
text = "\n {} \n TEST VALUE \n stepsize: {} \n lower_threshold1: {} \n upper_threshold1: {} \n file name: {}"
s.write(text.format(x, stepsize1, lower_threshold1, upper_threshold1, outfilename))

#In order for the code to work, the stepsize and thresholds need to be integers
stepsize = int(stepsize1)
lower_threshold = int(lower_threshold1)
upper_threshold = int(upper_threshold1)

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


#Get names of all dicom files in the given path
file_names = []
for (dirpath, dirs, files) in walk(filepath):
    file_names.extend(files)
    break
r = re.compile(".*[.]dcm$")
file_names = list(filter(r.match, list(file_names)))

#Preliminary read for resolution
print("preliminary read")
tmpFileData = pydicom.dcmread(filepath+'/'+file_names[0])
xresolution, yresolution = tmpFileData.pixel_array.shape
sliceThickness = tmpFileData.SliceThickness
pixelSpacing = [float(tmpFileData.PixelSpacing[0]), float(tmpFileData.PixelSpacing[1])]

#Sort files by location in image
file_list = []
for s in file_names:
    tmpFileData = pydicom.dcmread(filepath+'/'+s).SliceLocation
    file_list.append(slicePosition(filepath+'/'+s, tmpFileData))

print("sorting by location")
file_list.sort()

def main():
        #Full read and import
        print("loading image data")
        totalimage = np.zeros((len(file_names), xresolution, yresolution))
        for i, slice_object in enumerate(file_list):
            a = pydicom.dcmread(slice_object.getName()).pixel_array
            a -= midpoint
            a[a > 0] = -a[a > 0]
            totalimage[i] = a


        #Pass to SCIKITfor marching cubes
        print("marching cubes")
        #Use second thread to prevent windows timing us out
        verts, faces, normals, values = ski.marching_cubes(totalimage, level = -threshold_width, step_size=stepsize, spacing=(sliceThickness, pixelSpacing[0], pixelSpacing[1]))

        #Convert Vertices to STL
        print("converting to stl")
        output_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                output_mesh.vectors[i][j] = verts[f[j],:]

        print("saving")
        output_mesh.save(outfilename+'.stl')
        print("finished")

t1 = threading.Thread(target = main)
t1.start()
t1.join()
