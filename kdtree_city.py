import random
import numpy
import pygame #so that we can see some graphix yo!


scaling = 500


class kdNode:
    def __init__(self,depth = 0):
        self.data = None
        self.depth = depth
        self.left = None
        self.right = None

    def build_tree(self, points):
        if len(points) == 1:
            self.data = ['leaf',points[0]]
        else:
            axis = self.depth%2
            median = numpy.median([item[axis] for item in points])
            self.data = ['branch',median]
            left_half = [item for item in points if item[axis] < median]
            right_half = [item for item in points if item[axis] >= median]
            self.left = kdNode(self.depth + 1)
            self.right = kdNode(self.depth + 1)
            self.left.build_tree(left_half)
            self.right.build_tree(right_half)

    def find_best(self, point):
        if self.data[0] == 'leaf': return self.data[1]
        if self.data[0] == 'branch':
            axis = self.depth%2
            if point[axis] < self.data[1]: return self.left.find_best(point)
            if point[axis] >= self.data[1]: return self.right.find_best(point)
    def  display_inorder(self):
        '''Displays the nodes of the tree in order from smallest to largest'''
        if self.left is not None:
            self.left.display_inorder()
        print self.data
        if self.right is not None:
            self.right.display_inorder()
        return        

cities = []

for i in range(20):
    cities += [(random.random(),random.random())]

#build the kd-tree

nice_cities = [(int(scaling*x),int(scaling*y)) for (x,y) in cities]

root = kdNode()
root.build_tree(cities)

pygame.init()
screen = pygame.display.set_mode((scaling,scaling))
pygame.display.set_caption('Cities')

for city_location in nice_cities:
    pygame.draw.circle(screen,(255,255,255),city_location,2,1)

pygame.display.update()


print "Give me a location. x = ?"
x_int = int(raw_input())
x = float(x_int)/scaling
print "y=?"
y_int = int(raw_input())
y = float(y_int)/scaling
closest = root.find_best((x,y))
closest = map(lambda x: int(scaling*x),closest)  #scale it

####Color the closest red###
print (x_int,y_int)
print closest

pygame.draw.line(screen,(255,255,255),(x_int,y_int),closest)
pygame.display.update()
pygame.display.update()
#####

print "closest city is " + str(closest)

pause = raw_input()


