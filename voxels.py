import pymel.core as py

directions = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]

grid = {}
grid[(0,0,0)] = 1
grid[(1,0,0)] = 0
grid[(-1,0,0)] = 1
grid[(0,1,0)] = 1


py.polyCube( w=1, h=1, d=1 )
for originalCoordinate in grid.keys():
    adjacentCoordinates = [tuple( sum( j ) for j in zip( i, originalCoordinate ) ) for i in directions]
    blockHere = grid[originalCoordinate]
    if blockHere:
        for newCoordinate in adjacentCoordinates:
            if not grid.get( newCoordinate, 0 ):
                newDirection = tuple( i[1]-i[0] for i in zip( originalCoordinate, newCoordinate ) )
                newSide = py.polyPlane( width = 1, height = 1, sx = 1, sy = 1 )[0]
                sideLocation = list( originalCoordinate )
                sideRotation = [0, 0, 0]
                if newDirection[0]:
                    if newDirection[0] > 0:
                        print originalCoordinate, "Facing X"
                        sideLocation[0] += 0.5
                        sideRotation[2] += -90
                    else:
                        print originalCoordinate, "Facing -X"
                        sideLocation[0] += -0.5
                        sideRotation[2] += 90
                if newDirection[1]:
                    if newDirection[1] > 0:
                        print originalCoordinate, "Facing Y"
                        sideLocation[1] += 0.5
                        sideLocation[1] += 0
                    else:
                        print originalCoordinate, "Facing -Y"
                        sideLocation[1] += -0.5
                        sideLocation[1] += 180
                if newDirection[2]:
                    if newDirection[2] > 0:
                        sideLocation[2] += 0.5
                        sideRotation[0] += 90
                        print originalCoordinate, "Facing Z"
                    else:
                        sideLocation[2] += -0.5
                        sideRotation[0] += -90
                        print originalCoordinate, "Facing -Z"
                print sideLocation
                py.move( newSide, sideLocation )
                py.rotate( newSide, sideRotation )
                        
