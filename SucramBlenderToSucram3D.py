import os

path = input("Enter path: ")
path = path.replace('"',"")
file = open(path,"r")
lines = file.readlines()
file.close()
lines = [x.replace("\n","") for x in lines]
linesToDel = []
for i in range(len(lines)-1):
    try:
        if(lines[i][0] == "#")or(lines[i][0] == "s")or(lines[i][0] == "o")or(lines[i] == ""):
            linesToDel.append(i)
    except:
        print(i)

linesToDel = linesToDel[::-1]

for idx in linesToDel:
    del lines[idx]

lines = [x.split(" ") for x in lines]

idxFace = 0
while lines[idxFace][0] != "f":
    idxFace += 1

file = open(os.path.abspath(os.getcwd())+"\\3D Engine Data.txt","w")
file.truncate(0)

for i in range(idxFace,len(lines),1):
    v1 = int(lines[i][1])
    v2 = int(lines[i][2])
    v3 = int(lines[i][3])
    v1x = lines[v1-1][1]
    v1y = lines[v1-1][2]
    v1z = lines[v1-1][3]
    v2x = lines[v2-1][1]
    v2y = lines[v2-1][2]
    v2z = lines[v2-1][3]
    v3x = lines[v3-1][1]
    v3y = lines[v3-1][2]
    v3z = lines[v3-1][3]
    file.write(str(v3x)+","+str(v3y)+","+str(v3z)+","+str(v2x)+","+str(v2y)+","+str(v2z)+","+str(v1x)+","+str(v1y)+","+str(v1z)+",255,255,255\n")

file.close()
