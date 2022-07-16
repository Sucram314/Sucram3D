def __unit(vector):
    d = (vector[0]**2+vector[1]**2+vector[2]**2)**0.5
    return [vector[0]/d,vector[1]/d,vector[2]/d]

def __crossproduct(vec1,vec2):
    return [(vec1[1]*vec2[2])-(vec1[2]*vec2[1]),(vec1[2]*vec2[0])-(vec1[0]*vec2[2]),(vec1[0]*vec2[1])-(vec1[1]*vec2[0])]

def __dotproduct(vec1,vec2):
    return vec1[0]*vec2[0]+vec1[1]*vec2[1]+vec1[2]*vec2[2]

def __matrixXvector(matrix,vector):
    return [__dotproduct(matrix[0],vector),__dotproduct(matrix[1],vector),__dotproduct(matrix[2],vector)]

def __transform(sphere,triangle):
    for i in range(3):
        triangle[1][i] -= triangle[0][i]
        triangle[2][i] -= triangle[0][i]
        sphere[0][i] -= triangle[0][i]
        triangle[0][i] = 0

    u = triangle[1]
    U = __unit(u)
    
    w = __crossproduct(u,triangle[2])
    W = __unit(w)

    V = __crossproduct(U,W)

    matrix = [[U[0],U[1],U[2]],
              [W[0],W[1],W[2]],
              [V[0],V[1],V[2]]]

    ninetyDegRoll = [[1,0,0],
                     [0,0,-1],
                     [0,1,0]]

    triangle[1] = __matrixXvector(matrix,triangle[1])
    triangle[2] = __matrixXvector(matrix,triangle[2])
    triangle[2] = __matrixXvector(ninetyDegRoll,triangle[2])
    sphere[0] = __matrixXvector(matrix,sphere[0])
    sphere[0] = __matrixXvector(ninetyDegRoll,sphere[0])

    if triangle[2][1]<0:
        triangle[2][1] *= -1
        sphere[0][1] *= -1

    return sphere,triangle

def __area(triangle):
    return 0.5*(triangle[0][0]*(triangle[1][1]-triangle[2][1])+triangle[1][0]*(triangle[2][1]-triangle[0][1])+triangle[2][0]*(triangle[0][1]-triangle[1][1]))

def closestpoint(sphere,triangle):
    p = [sphere[0][0],sphere[0][1]]
    if __area(triangle) == (__area([triangle[0],triangle[1],p])+__area([triangle[0],triangle[2],p])+__area([triangle[1],triangle[2],p])):
        p.append(0)
        return p
    else:
        for i in range(2):
            aboveBC = True if (p[1]>=(((triangle[1][1]-triangle[2][1])/(triangle[1][0]-triangle[2][0]))*(p[0]-triangle[1][0])+triangle[1][1])) else False
            aboveAC = True if (p[1]>=(((triangle[0][1]-triangle[2][1])/(triangle[0][0]-triangle[2][0]))*(p[0]-triangle[0][0])+triangle[0][1])) else False
            if p[1]>0:          
                if aboveAC and aboveBC:
                    return triangle[2]
                elif (aboveAC)and(not aboveBC):
                    a = (triangle[0][1]-triangle[2][1])/(triangle[0][0]-triangle[2][0])
                    b = triangle[0][1]-(triangle[0][0]*(triangle[0][1]-triangle[2][1]))/(triangle[0][0]-triangle[2][0])
                    p[0] = (-b*a+p[1]*a+p[0])/(1+a**2)
                    p[1] = a*p[0]+b
                elif (not aboveAC)and(aboveBC):
                    a = (triangle[1][1]-triangle[2][1])/(triangle[1][0]-triangle[2][0])
                    b = triangle[1][1]-(triangle[1][0]*(triangle[1][1]-triangle[2][1]))/(triangle[1][0]-triangle[2][0])
                    p[0] = (-b*a+p[1]*a+p[0])/(1+a**2)
                    p[1] = a*p[0]+b
            else:
                if aboveAC:
                    return triangle[0]
                elif aboveBC:
                    return triangle[1]
                else:
                    p[1] = 0

        p.append(0)
        return p

def __dist(p1,p2):
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)**0.5
 
def __collided(sphere,triangle):
    sphere,triangle = __transform(sphere,triangle)
    point = closestpoint(sphere,triangle)
    if (__dist(point,sphere[0])<sphere[1]):
        return True
    else:
        return False
    
