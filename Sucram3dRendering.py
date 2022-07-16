import pygame
from pygame import gfxdraw
import math
import copy
import os

clipMode = False
outlines = False
off = 100

pygame.init()

a = pygame.image.load("C:\\Users\\marcu\\OneDrive\\Pictures\\Saved Pictures\\unnamed.jpg")
pygame.display.set_icon(a)
pygame.display.set_caption("Sucram3D")

clock = pygame.time.Clock()

width = 1280
height = 658

screen = pygame.display.set_mode([width,height])

bg = (0,0,0)

zFar = 1000
zNear = 0.1+(8/90)
FOV = 170
Camera = [0,0,0]
LookDir = [0,0,1]
Yaw = 0

speed = 0.05

yRot45 = [[math.cos(math.radians(45)),0,math.sin(math.radians(45)),0],
          [0,1,0,0],
          [-math.sin(math.radians(45)),0,math.cos(math.radians(45)),0],
          [0,0,0,1]]

data = []

with open(os.path.abspath(os.getcwd())+"\\3D Engine Data.txt") as f:
    lines = f.readlines()
    lastline = lines[-1]
    lines = [line[:-1] for line in lines[:-1]]
    lines.append(lastline)
    for line in lines:
        temp = line.split(",")
        temp = [float(x) for x in temp]
        data.append([[temp[0],temp[1],temp[2]],[temp[3],temp[4],temp[5]],[temp[6],temp[7],temp[8]],(temp[9],temp[10],temp[11])])

def dotproduct(vec1,vec2):
    if len(vec1)==3:
        return vec1[0]*vec2[0]+vec1[1]*vec2[1]+vec1[2]*vec2[2]
    elif len(vec1)==4:
        return vec1[0]*vec2[0]+vec1[1]*vec2[1]+vec1[2]*vec2[2]+vec1[3]*vec2[3]

def crossproduct(vec1,vec2):
    return [vec1[1]*vec2[2]-vec1[2]*vec2[1],vec1[2]*vec2[0]-vec1[0]*vec2[2],vec1[0]*vec2[1]-vec1[1]*vec2[0]]

def unit(vec):
    d = (vec[0]**2+vec[1]**2+vec[2]**2)**0.5
    return [vec[0]/d,vec[1]/d,vec[2]/d]

def matrix4Xvector(matrix,vector):
    x = dotproduct(matrix[0],vector)
    y = dotproduct(matrix[1],vector)
    z = dotproduct(matrix[2],vector)
    w = dotproduct(matrix[3],vector)
    return [x,y,z,w]

def matrix3Xvector(matrix,vector):
    return [dotproduct(matrix[0],vector),dotproduct(matrix[1],vector),dotproduct(matrix[2],vector)]

def pointatmatrix(pos,target,up):
    newForward = unit([target[0]-pos[0],target[1]-pos[1],target[2]-pos[2]])

    a = [newForward[0]*dotproduct(up,newForward),newForward[1]*dotproduct(up,newForward),newForward[2]*dotproduct(up,newForward)]
    newUp = unit([up[0]-a[0],up[1]-a[1],up[2]-a[2]])

    newRight = crossproduct(newUp,newForward)

    matrix = [[newRight[0],newRight[1],newRight[2],0],
              [newUp[0],newUp[1],newUp[2],0],
              [newForward[0],newForward[1],newForward[2],0],
              [pos[0],pos[1],pos[2],1]]
    
    return matrix

def quickinverse(matrix):
    a = [matrix[0][0],matrix[1][0],matrix[2][0]]
    b = [matrix[0][1],matrix[1][1],matrix[2][1]]
    c = [matrix[0][2],matrix[1][2],matrix[2][2]]
    t = [matrix[3][0],matrix[3][1],matrix[3][2]]
    
    newMatrix = [[matrix[0][0],matrix[1][0],matrix[2][0],-dotproduct(t,a)],
                 [matrix[0][1],matrix[1][1],matrix[2][1],-dotproduct(t,b)],
                 [matrix[0][2],matrix[1][2],matrix[2][2],-dotproduct(t,c)],
                 [0,0,0,1]]

    return newMatrix

def avg(triangle):
    return [(triangle[0][0]+triangle[1][0]+triangle[2][0])/3,(triangle[0][1]+triangle[1][1]+triangle[2][1])/3,(triangle[0][2]+triangle[1][2]+triangle[2][2])/3]

def vecIntersectPlane(planeNormal,planePoint,lineBegin,lineEnd):
    planeNormal = unit(planeNormal)
    d = -dotproduct(planeNormal,planePoint)
    ad = dotproduct(lineBegin[:3],planeNormal)
    bd = dotproduct(lineEnd[:3],planeNormal)
    t = (-d-ad)/(bd-ad)
    lineBegintoEnd = [lineEnd[0]-lineBegin[0],lineEnd[1]-lineBegin[1],lineEnd[2]-lineBegin[2]]
    linetoIntersect = [lineBegintoEnd[0]*t,lineBegintoEnd[1]*t,lineBegintoEnd[2]*t]
    return [lineBegin[0]+linetoIntersect[0],lineBegin[1]+linetoIntersect[1],lineBegin[2]+linetoIntersect[2]]

def dist(planeNormal,planePoint,point):
    planeNormal = unit(planeNormal)
    return (planeNormal[0]*point[0]+planeNormal[1]*point[1]+planeNormal[2]*point[2]-dotproduct(planeNormal,planePoint))

def TrianglePlaneClip(planeNormal,planePoint,triangle):
    triangleout1 = None
    triangleout2 = None
    
    planeNormal = unit(planeNormal)

    insidePoints = []
    insidePointCount = 0
    outsidePoints = []
    outsidePointCount = 0

    d0 = dist(planeNormal,planePoint,triangle[0])
    d1 = dist(planeNormal,planePoint,triangle[1])
    d2 = dist(planeNormal,planePoint,triangle[2])

    if d0>=0:
        insidePoints.append(triangle[0])
        insidePointCount += 1
    else:
        outsidePoints.append(triangle[0])
        outsidePointCount += 1

    if d1>=0:
        insidePoints.append(triangle[1])
        insidePointCount += 1
    else:
        outsidePoints.append(triangle[1])
        outsidePointCount += 1

    if d2>=0:
        insidePoints.append(triangle[2])
        insidePointCount += 1
    else:
        outsidePoints.append(triangle[2])
        outsidePointCount += 1

    if insidePointCount == 0:
        return 0,[triangleout1,triangleout2]

    if insidePointCount == 3:
        triangleout1 = (copy.deepcopy(triangle))[:3]
        if clipMode:
            triangleout1.append((255,255,255))
        return 1,[triangleout1,triangleout2]

    if (insidePointCount == 1)and(outsidePointCount == 2):
        triangleout1 = [insidePoints[0],vecIntersectPlane(planeNormal,planePoint,insidePoints[0],outsidePoints[0]),vecIntersectPlane(planeNormal,planePoint,insidePoints[0],outsidePoints[1])]
        if clipMode:
            triangleout1.append((255,0,0))
        return 1,[triangleout1,triangleout2]

    if (insidePointCount == 2)and(outsidePointCount == 1):
        triangleout1 = [insidePoints[0],insidePoints[1],vecIntersectPlane(planeNormal,planePoint,insidePoints[0],outsidePoints[0])]
        triangleout2 = [insidePoints[1],triangleout1[2],vecIntersectPlane(planeNormal,planePoint,insidePoints[1],outsidePoints[0])]
        if clipMode:
            triangleout1.append((0,255,0))
            triangleout2.append((0,0,255))
        return 2,[triangleout1,triangleout2]
    

def project(data):
    projectedTriangles = []
    for triangle_ in data:
        triangle = copy.deepcopy(triangle_)

        for i in range(3):
            triangle[i] = [triangle[i][0],triangle[i][1]+10,triangle[i][2]+10]

        line1 = [triangle[1][0]-triangle[0][0],triangle[1][1]-triangle[0][1],triangle[1][2]-triangle[0][2]]
        line2 = [triangle[2][0]-triangle[0][0],triangle[2][1]-triangle[0][1],triangle[2][2]-triangle[0][2]]
        normal = unit(crossproduct(line1,line2))

        if dotproduct(normal,unit([triangle[0][0]-Camera[0],triangle[0][1]-Camera[1],triangle[0][2]-Camera[2]]))>0:
            vUp = [0,1,0]
            vTarget = [0,0,1]
            matCameraRot = [[math.cos(math.radians(Yaw)),0,math.sin(math.radians(Yaw)),0],
                               [0,1,0,0],
                               [-math.sin(math.radians(Yaw)),0,math.cos(math.radians(Yaw)),0],
                               [0,0,0,1]]

            LookDir = matrix4Xvector(matCameraRot,[vTarget[0],vTarget[1],vTarget[2],1])

            light = LookDir[:3]
            light[0] *= -1
            light.append(1)
            light = matrix4Xvector(yRot45,light)
            del light[-1]

            dp = dotproduct(light,normal)
            
            vTarget = [Camera[0]+LookDir[0],Camera[1]+LookDir[1],Camera[2]+LookDir[2]]
            
            cameraMatrix = pointatmatrix(Camera,vTarget,vUp)
            viewMatrix = quickinverse(cameraMatrix)

            triangle[0] = matrix4Xvector(viewMatrix,[triangle[0][0],triangle[0][1],triangle[0][2],1])
            triangle[1] = matrix4Xvector(viewMatrix,[triangle[1][0],triangle[1][1],triangle[1][2],1])
            triangle[2] = matrix4Xvector(viewMatrix,[triangle[2][0],triangle[2][1],triangle[2][2],1])

            transformed = copy.deepcopy(triangle)

            count,clipped = TrianglePlaneClip([0,0,1],[0,0,zNear],triangle)

            ogtriangle = copy.deepcopy(triangle)

            for i in range(count):
                if not clipMode:
                    clipped[i].append(ogtriangle[3])
                triangle = copy.deepcopy(clipped[i])
                a = height/width
                f = 1/(math.tan(math.radians(FOV/2)))
                q = zFar/(zFar-zNear)

                matrix = [[a*f,0,0,0],
                          [0,f,0,0],
                          [0,0,q,1],
                          [0,0,zNear*q,0]]

                p1 = copy.deepcopy(triangle[0])
                p2 = copy.deepcopy(triangle[1])
                p3 = copy.deepcopy(triangle[2])

                if (len(p1)==3):
                    p1.append(1)
                if (len(p2)==3):
                    p2.append(1)
                if (len(p3)==3):
                    p3.append(1)

                p1 = matrix4Xvector(matrix,p1)
                p2 = matrix4Xvector(matrix,p2)
                p3 = matrix4Xvector(matrix,p3)

                if p1[3]!=0:
                    p1[0]/=p1[3]
                    p1[1]/=p1[3]
                    p1[2]/=p1[3]
                if p2[3]!=0:
                    p2[0]/=p2[3]
                    p2[1]/=p2[3]
                    p2[2]/=p2[3]
                if p3[3]!=0:
                    p3[0]/=p3[3]
                    p3[1]/=p3[3]
                    p3[2]/=p3[3]

                p1[0] = (-p1[0]+1)*0.5*width
                p1[1] = (-p1[1]+1)*0.5*height
                p2[0] = (-p2[0]+1)*0.5*width
                p2[1] = (-p2[1]+1)*0.5*height
                p3[0] = (-p3[0]+1)*0.5*width
                p3[1] = (-p3[1]+1)*0.5*height

                p1 = tuple(p1)
                p2 = tuple(p2)
                p3 = tuple(p3)

                colour = (triangle_[3][0]*((dp+1)/2),triangle_[3][1]*((dp+1)/2),triangle_[3][2]*((dp+1)/2))
                projectedTriangles.append([[p1[0],p1[1],p1[2]],[p2[0],p2[1],p2[2]],[p3[0],p3[1],p3[2]],colour,avg(transformed)[2]])

    return projectedTriangles

def draw(data):
    projectedTriangles = project(data)
    projectedTriangles = (sorted(projectedTriangles, key=lambda x : x[2]))[::-1]

    listOfTriangles = []

    for triangle in projectedTriangles:
        triangle.pop(-1)
        clipped = [None,None]

        nNewTriangles = 1
        listOfTriangles.append(triangle)

        for i in range(4):
            nTrianglestoAdd = 0
            while nNewTriangles>0:
                test = listOfTriangles.pop(0)
                if i==0:
                    nTrianglestoAdd,clipped = TrianglePlaneClip([0,1,0],[0,0+off,0],test)
                if i==1:
                    nTrianglestoAdd,clipped = TrianglePlaneClip([0,-1,0],[0,height-off,0],test)
                if i==2:
                    nTrianglestoAdd,clipped = TrianglePlaneClip([1,0,0],[0+off,0,0],test)
                if i==3:
                    nTrianglestoAdd,clipped = TrianglePlaneClip([-1,0,0],[width-off,0,0],test)

                for i in range(nTrianglestoAdd):
                    if not clipMode:
                        clipped[i].append(test[-1])
                    listOfTriangles.append(clipped[i])

                nNewTriangles -= 1

            nNewTriangles = len(listOfTriangles)
    
    for triangle in listOfTriangles:
        pygame.gfxdraw.filled_polygon(screen,((triangle[0][0],triangle[0][1]),(triangle[1][0],triangle[1][1]),(triangle[2][0],triangle[2][1])),triangle[3])
        pygame.gfxdraw.aapolygon(screen,((triangle[0][0],triangle[0][1]),(triangle[1][0],triangle[1][1]),(triangle[2][0],triangle[2][1])),(55,55,55) if outlines else triangle[3])
        
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    key = pygame.key.get_pressed()
    if key[pygame.K_SPACE]:
        Camera[1] += speed
    elif key[pygame.K_LSHIFT]:
        Camera[1] -= speed
        
    if key[pygame.K_w]:
        Camera[0] -= math.sin(math.radians(Yaw))*speed
        Camera[2] -= -math.cos(math.radians(Yaw))*speed

    elif key[pygame.K_s]:
        Camera[0] += math.sin(math.radians(Yaw))*speed
        Camera[2] += -math.cos(math.radians(Yaw))*speed

    if key[pygame.K_a]:
        Camera[0] += math.cos(math.radians(Yaw))*speed
        Camera[2] += math.sin(math.radians(Yaw))*speed

    elif key[pygame.K_d]:
        Camera[0] -= math.cos(math.radians(Yaw))*speed
        Camera[2] -= math.sin(math.radians(Yaw))*speed
    
    if key[pygame.K_LEFT]:
        Yaw -= 0.005*FOV
    elif key[pygame.K_RIGHT]:
        Yaw += 0.005*FOV

    screen.fill(bg)

    draw(data)

    pygame.display.update()

    clock.tick(120)
pygame.quit()
