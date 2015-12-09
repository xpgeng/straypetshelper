from time import strftime, localtime

now = strftime("%y%m%d%H%M%S" , localtime())
#time = strftime("%y\%m\%d-%H:%M:%S", localtime())
print now