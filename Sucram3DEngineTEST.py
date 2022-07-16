import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame import gfxdraw
import time
import math
import keyboard as k
import numpy as np
from matplotlib.path import Path

a = pygame.image.load("C:\\Users\\marcu\\OneDrive\\Pictures\\Saved Pictures\\Untitled_ico32.ico")
pygame.display.set_icon(a)

#important stuff
pygame.init()

myFont = pygame.font.SysFont("couriernew",20,bold=1)

#all variables
clock = pygame.time.Clock()
FPS = 60
speed = 0.4
extra = 5
sensitivity = (1/extra)*3
zClip = 1
speed *= 10/extra

off = 0

#screen
resolution = pygame.display.Info()
width = resolution.current_w
height = resolution.current_h
hwidth = (width/2)
hheight = (height/2)

#3d geometrical data and player data
data = []
p_x,p_y,p_z = (0,30,40)
p_xr = 0
p_yr = 0
p_FOV = 60*extra
p_r = 15
playerdata = [p_x,-p_y,p_z,p_xr,p_yr,p_FOV,p_r]

c = (p_FOV/extra)/(math.sqrt(2))

c1 = -1/math.tan(math.radians(c/2))
rightPlane = (1/math.sqrt(1+c1**2),0,c1/math.sqrt(1+c1**2))
c2 = -1/math.tan(math.radians(c/-2))
leftPlane = (-1/math.sqrt(1+c2**2),0,-c2/math.sqrt(1+c2**2))
c3 = -1/math.tan(math.radians((((width/height)*c))/2))
topPlane = (0,1/math.sqrt(1+c3**2),c3/math.sqrt(1+c3**2))
c4 = -1/math.tan(math.radians((((width/height)*c))/-2))
bottomPlane = (0,-1/math.sqrt(1+c4**2),-c4/math.sqrt(1+c4**2))

def dotproduct_(vec1,vec2):
    return vec1[0]*vec2[0]+vec1[1]*vec2[1]+vec1[2]*vec2[2]

dpnp1 = dotproduct_((0,0,-1),(0,0,-zClip))
dpnp2 = dotproduct_(rightPlane,(0,0,0))
dpnp3 = dotproduct_(leftPlane,(0,0,0))
dpnp4 = dotproduct_(topPlane,(0,0,0))
dpnp5 = dotproduct_(bottomPlane,(0,0,0))
dpnp6 = dotproduct_((0,1,0),(0,0,0))
dpnp7 = dotproduct_((0,-1,0),(0,height,0))
dpnp8 = dotproduct_((1,0,0),(0,0,0))
dpnp9 = dotproduct_((-1,0,0),(width,0,0))

#colours
bg = (0,0,0)
lines = (255,255,255)
light = (0,-1,10)
d = math.sqrt(light[0]**2+light[1]**2+light[2]**2)
light = (light[0]/d,light[1]/d,light[2]/d)

cosx = math.cos(math.radians(playerdata[3]))
cosy = math.cos(math.radians(playerdata[4]))
sinx = math.sin(math.radians(playerdata[3]))
siny = math.sin(math.radians(playerdata[4]))

#all the functions

def crossproduct(vec1x,vec1y,vec1z,vec2x,vec2y,vec2z):
    x = vec1y*vec2z-vec1z*vec2y
    y = vec1z*vec2x-vec1x*vec2z
    z = vec1x*vec2y-vec1y*vec2x
    magnitude = math.sqrt(x**2+y**2+z**2)
    try: return (x/magnitude,y/magnitude,z/magnitude)
    except: return (0,0,0)

def dotproduct(vec1x,vec1y,vec1z,vec2x,vec2y,vec2z): return vec1x*vec2x+vec1y*vec2y+vec1z*vec2z

def project(x,y,z,playerdata):
    x -= playerdata[0]
    y -= playerdata[1]
    z -= playerdata[2]
    x,y,z = (((z*siny)+(x*cosy)),y,((z*cosy)-(x*siny)))
    x,y,z = (x,((y*cosx)-(z*sinx)),((y*sinx)+(z*cosx)))
    return [x,y,z]
    
#poly clipping

def vecIntersectPlane(planeNormal,planePoint,lineBegin,lineEnd,dpnp):
    ad = dotproduct_(lineBegin,planeNormal)
    t = (dpnp-ad)/(dotproduct_(lineEnd,planeNormal)-ad)
    return [lineBegin[0]+(lineEnd[0]-lineBegin[0])*t,lineBegin[1]+(lineEnd[1]-lineBegin[1])*t,lineBegin[2]+(lineEnd[2]-lineBegin[2])*t]

def dist(planeNormal,planePoint,point,dpnp):
    return (dotproduct_(planeNormal,point)-dpnp)>=0

def TrianglePlaneClip(planeNormal,planePoint,triangle,dpnp):
    insidePoints = []
    outsidePoints = []

    if dist(planeNormal,planePoint,triangle[0],dpnp): insidePoints.append(triangle[0])
    else: outsidePoints.append(triangle[0])
    if dist(planeNormal,planePoint,triangle[1],dpnp): insidePoints.append(triangle[1])
    else: outsidePoints.append(triangle[1])
    if dist(planeNormal,planePoint,triangle[2],dpnp): insidePoints.append(triangle[2])
    else: outsidePoints.append(triangle[2])

    count = len(insidePoints)
    
    if count==0: return ()
    elif count==3: return ([[*x] for x in triangle],)
    elif count==1: return ([insidePoints[0],vecIntersectPlane(planeNormal,planePoint,insidePoints[0],outsidePoints[0],dpnp),vecIntersectPlane(planeNormal,planePoint,insidePoints[0],outsidePoints[1],dpnp)],)
    else:
        temp = vecIntersectPlane(planeNormal,planePoint,insidePoints[0],outsidePoints[0],dpnp)
        return ([insidePoints[0],insidePoints[1],temp],[insidePoints[1],temp,vecIntersectPlane(planeNormal,planePoint,insidePoints[1],outsidePoints[0],dpnp)])

def filltriangle(x1,y1,z1,x2,y2,z2,x3,y3,z3,playerdata,avg,rgb):
    triangles = []
    clipped = [TrianglePlaneClip((0,0,-1),(0,0,-zClip),[project(x1,y1,z1,playerdata),project(x2,y2,z2,playerdata),project(x3,y3,z3,playerdata)],dpnp1)]
    for clip in clipped: triangles.extend(clip)
    clipped = [TrianglePlaneClip(rightPlane,(0,0,0),triangle,dpnp2) for triangle in triangles]
    triangles = []
    for clip in clipped: triangles.extend(clip)
    clipped = [TrianglePlaneClip(leftPlane,(0,0,0),triangle,dpnp3) for triangle in triangles]
    triangles = []
    for clip in clipped: triangles.extend(clip)
    clipped = [TrianglePlaneClip(topPlane,(0,0,0),triangle,dpnp4) for triangle in triangles]
    triangles = []
    for clip in clipped: triangles.extend(clip)
    clipped = [TrianglePlaneClip(bottomPlane,(0,0,0),triangle,dpnp5) for triangle in triangles]
    triangles = []
    for clip in clipped: triangles.extend(clip)
    clipped = [TrianglePlaneClip((0,0,-1),(0,0,-zClip),triangle,dpnp1) for triangle in triangles]
    triangles = []
    for clip in clipped: triangles.extend(clip)

    listOfTriangles = []

    triangles = [[[playerdata[5]*(triangle[0][0]/-triangle[0][2])+hwidth,playerdata[5]*(triangle[0][1]/-triangle[0][2])+hheight,triangle[0][2]*extra],[playerdata[5]*(triangle[1][0]/-triangle[1][2])+hwidth,playerdata[5]*(triangle[1][1]/-triangle[1][2])+hheight,triangle[1][2]*extra],[playerdata[5]*(triangle[2][0]/-triangle[2][2])+hwidth,playerdata[5]*(triangle[2][1]/-triangle[2][2])+hheight,triangle[2][2]*extra]] for triangle in triangles]
    
    for triangle in triangles:
        tringles = []
        clipped = [TrianglePlaneClip((0,1,0),(0,0,0),triangle,dpnp6)]
        for clip in clipped: tringles.extend(clip)
        clipped = [TrianglePlaneClip((0,-1,0),(0,height,0),triangle_,dpnp7) for triangle_ in tringles]
        tringles = []
        for clip in clipped: tringles.extend(clip)
        clipped = [TrianglePlaneClip((1,0,0),(0,0,0),triangle_,dpnp8) for triangle_ in tringles]
        tringles = []
        for clip in clipped: tringles.extend(clip)
        clipped = [TrianglePlaneClip((-1,0,0),(width,0,0),triangle_,dpnp9) for triangle_ in tringles]
        tringles = []
        for clip in clipped: tringles.extend(clip)
        listOfTriangles.extend(tringles)

    return [([(triangle[0][0],triangle[0][1]),(triangle[1][0],triangle[1][1]),(triangle[2][0],triangle[2][1])],rgb,(triangle[0][2]+triangle[1][2]+triangle[2][2])/3) for triangle in listOfTriangles]

def drawTriangle(triangle):
    x, y = np.meshgrid(np.arange(width), np.arange(height))
    x = x.flatten()
    y = y.flatten()
    points = np.vstack((x,y)).T

    p = Path(triangle[0])
    grid = p.contains_points(points)
    grid = np.argwhere(grid.reshape(height,width)).tolist()

    [pygame.gfxdraw.pixel(screen,point[1],point[0],triangle[1]) for point in grid]

def text(text,pos,colour):
    screen.blit(myFont.render(text,1,colour),pos)

def ui(renderNum,time,dt):
    pygame.draw.rect(screen,(0,0,0),((0,0),(width,20)))
    text("Rendered "+str(renderNum).zfill(4)+ " triangles in "+format(time,".10f")+" seconds | "+str(round(1/time,None)).zfill(3)+" FPS | dt = "+str(dt),(0,0),(255,255,255))

def tringlepringle(data,playerdata,dt):
    screen.fill(bg)

    start = time.time()
    
    trianglesToRaster = []
    for tringle in data:
        if dotproduct(tringle[6][0],tringle[6][1],tringle[6][2],(tringle[1][0]-playerdata[0]),(tringle[1][1]-playerdata[1]),(tringle[1][2]-playerdata[2]))>0: trianglesToRaster.extend(filltriangle(tringle[0][0],tringle[0][1],tringle[0][2],tringle[1][0],tringle[1][1],tringle[1][2],tringle[2][0],tringle[2][1],tringle[2][2],playerdata,tringle[3],tringle[4]))
    for triangle in sorted(trianglesToRaster, key = lambda x: x[2]): drawTriangle(triangle)

    ui(len(trianglesToRaster),time.time()-start,dt)
    pygame.display.update()

def addtriangle(point1,point2,point3,rgb):
    crossx,crossy,crossz = crossproduct(point1[0]-point2[0],point1[1]-point2[1],point1[2]-point2[2],point2[0]-point3[0],point2[1]-point3[1],point2[2]-point3[2])
    shade = ((dotproduct(crossx,crossy,crossz,light[0],light[1],light[2])*-1 + 1)/2)
    data.append((point1,point2,point3,((point1[0]+point2[0]+point3[0])/3,(point1[1]+point2[1]+point3[1])/3,(point1[2]+point2[2]+point3[2])/3),(rgb[0]*shade,rgb[1]*shade,rgb[2]*shade),shade,(crossx,crossy,crossz)))
    
data = []

#tringle
with open(os.path.abspath(os.getcwd())+"\\3D Engine Data.txt") as f:
    lines = f.readlines()
    lastline = lines[-1]
    lines = [line[:-1] for line in lines[:-1]]
    lines.append(lastline)
    for line in lines:
        temp = line.split(",")
        temp = [float(x) for x in temp]
        addtriangle([temp[0],-temp[1],temp[2]],[temp[6],-temp[7],temp[8]],[temp[3],-temp[4],temp[5]],[temp[9],temp[10],temp[11]])

#main pygame loop
pygame.display.set_caption('Sucram3DEngine')
screen = pygame.display.set_mode([width,height],pygame.NOFRAME)

mid = (hwidth,hheight)

pygame.mouse.set_visible(0)
pygame.event.set_grab(1)
pygame.mouse.set_pos(mid)

tringlepringle(data,playerdata,0)

while 1:
    dt = clock.tick(FPS)/50
    
    playerdataog = [*playerdata]
    og = (playerdata[3],playerdata[4])
    
    pygame.event.get()

    mouseposx,mouseposy = pygame.mouse.get_pos()
    pygame.mouse.set_pos(mid)
    changex,changey = (hwidth-mouseposx,hheight-mouseposy)
    playerdata[4]-=changex*sensitivity
    playerdata[3]+=changey*sensitivity
    playerdata[3] = max(-89,min(playerdata[3],89))
    
    if og!=(playerdata[3],playerdata[4]): cosx,cosy,sinx,siny = (math.cos(math.radians(playerdata[3])),math.cos(math.radians(playerdata[4])),math.sin(math.radians(playerdata[3])),math.sin(math.radians(playerdata[4])))
    
    keys = pygame.key.get_pressed()
    mult = (2 if (keys[pygame.K_RCTRL] or keys[pygame.K_LCTRL]) else 1)*dt
    if keys[pygame.K_ESCAPE]: break
    if keys[pygame.K_d]:
        playerdata[0]+=(speed*cosy)*mult
        playerdata[2]+=(speed*siny)*mult
    elif keys[pygame.K_a]:
        playerdata[0]-=(speed*cosy)*mult
        playerdata[2]-=(speed*siny)*mult
    if keys[pygame.K_s]:
        playerdata[0]-=(speed*siny)*mult
        playerdata[2]+=(speed*cosy)*mult
    elif keys[pygame.K_w]:
        playerdata[0]+=(speed*siny)*mult
        playerdata[2]-=(speed*cosy)*mult
    if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
        playerdata[1]+=speed*mult
    elif keys[pygame.K_SPACE]:
        playerdata[1]-=speed*mult

    if playerdata!=playerdataog: tringlepringle(data,playerdata,dt)
    
pygame.quit()
