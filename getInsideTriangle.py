triangle = [(553,400),(778,100),(235,177)]

import pygame
from pygame import gfxdraw
import timeit
import numpy as np
from matplotlib.path import Path

pygame.init()

screen = pygame.display.set_mode((1280,658))

start = timeit.default_timer()

x, y = np.meshgrid(np.arange(1280), np.arange(658))
x = x.flatten()
y = y.flatten()
points = np.vstack((x,y)).T

p = Path(triangle)
grid = p.contains_points(points)
grid = np.argwhere(grid.reshape(658,1280)).tolist()

[pygame.gfxdraw.pixel(screen,point[1],point[0],(255,255,255)) for point in grid]

print(timeit.default_timer()-start)

pygame.display.update()
