from tkinter import *

window = Tk()

window.title("Hereford High School Medical Modeling Project - GUI")

window.geometry('400x300')

#step size label
stepSize = Label(window, text="Step Size: ")
stepSize.grid(column=0, row=0)
#step size entry
stepSizeE = Entry(window,width=10)
stepSizeE.grid(column=1, row=0)

#lower threshold label
lowerThreshold = Label(window, text="Lower Threshold: ")
lowerThreshold.grid(column=0, row=1)
#lower threshold entry
lowerThresholdE = Entry(window,width=10)
lowerThresholdE.grid(column=1, row=1)

#upper threshold label
upperThreshold = Label(window, text="Upper Threshold: ")
upperThreshold.grid(column=0, row=2)
#lower threshold entry
upperThresholdE = Entry(window,width=10)
upperThresholdE.grid(column=1, row=2)


def clicked():
    execfile('testScript.py')

btn = Button(window, text="Confirm Values", command=clicked)

btn.grid(column=3, row=0)

window.mainloop()