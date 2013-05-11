#This program starts by generating a number of cities located at random coordinates.
#Then the program asks for a location (for now by text input, in the future by clicking the location)
#The program then identifies the closest city (ideally graphically somehow). It does so *not* by taking the minimum of all distances (which is O(n))
#but rather first builds a kd-tree (k-dimensional tree) which is a decision-tree which has the cities as leaves and each interior node
#has a "branching rule". A point queried in the future is placed at the root of the tree, follows the branching rules, and arrives at a leaf which determines the
#closest city. This algorithm is O(n log n) (at least on average). The branching rules are all of the form "x/y axis is less than/greater than a".
#The tree is constructed recursively by dividing the collection of remaining cities along an axis by the median value of that axis for the cities. The choice of axis is
#given by the depth in the tree (mod 2). When a colection consists of only one city, a leaf node is made for that city.

#Remaining issues
#1)Graphical interface: It should be that the cities are displayed graphically as small circles. To query a location, the user should click a point. The closest city should be indicated
#graphically somehow (perhaps by a line drawn to it from the clicked location?)
#
#2)Algorithm: The algorithm as it stands does not always find the city of closest Euclidean distance. The kd-tree divides the unit square into rectangles and when a point is queried it merely 
#returns the city in the same rectangle as the queried point. Instead the algorithm should go back up the tree and check some of the neighboring boxes as well.



import random
import numpy
import pygame #so that we can see some graphix yo!


scaling = 500                       #while internally everything is done on the unit square, this is scaled before being displayed graphically
number_of_cities = 20

class kdNode:    #A node of the kd-tree
    def __init__(self,depth = 0):
        self.data = None        #data consists of a pair: either ('leaf', (int,int)) where the second element denotes the city location at that leaf, or ('branch', int) where the second element
                                #determines the number along which which we divide the axis. (The axis choice is determined by depth and so does not need to be stored)
        self.depth = depth      #depth of the tree
        self.left = None        #left child node
        self.right = None       #right child node

    def build_tree(self, points):              #Input: collection of points (cities). Output: The kd-tree
        if len(points) == 1:
            self.data = ['leaf',points[0]]     #When there is only one point left, build a leaf node.
        else:
            axis = self.depth%2
            median = numpy.median([item[axis] for item in points])
            self.data = ['branch',median]                                #build the branching rule by the median of the points' values for the appropriate axis
            left_half = [item for item in points if item[axis] < median]
            right_half = [item for item in points if item[axis] >= median]
            self.left = kdNode(self.depth + 1)                           
            self.right = kdNode(self.depth + 1)
            self.left.build_tree(left_half)                              #Build the tree recursively
            self.right.build_tree(right_half)

    def find_best(self, point):                #Input: a queried location. Output: the city location in the appropriate leaf of the tree
        if self.data[0] == 'leaf': return self.data[1]
        if self.data[0] == 'branch':
            axis = self.depth%2
            if point[axis] < self.data[1]: return self.left.find_best(point)
            if point[axis] >= self.data[1]: return self.right.find_best(point)
    def  display_inorder(self):               #Standard in-order display of a tree. Useful for debugging.
        '''Displays the nodes of the tree in order from smallest to largest'''
        if self.left is not None:
            self.left.display_inorder()
        print self.data
        if self.right is not None:
            self.right.display_inorder()
        return        

cities = []

for i in range(number_of_cities):                    #Create the array of cities
    cities += [(random.random(),random.random())]    #Each of the cities is a tuple of randomly generated coordinates. The cities variable stores the cities as being in the unit square.

#build the kd-tree

scaled_cities = [(int(scaling*x),int(scaling*y)) for (x,y) in cities]  #Scaled version of the cities for display

root = kdNode()
root.build_tree(cities)

pygame.init()
screen = pygame.display.set_mode((scaling,scaling))
pygame.display.set_caption('Cities')

for city_location in scaled_cities:
    pygame.draw.circle(screen,(255,255,255),city_location,2,1)

pygame.display.update()


print "Give me a location. x = ?"
x_int = int(raw_input())                             #Coordinates are input in the scaled world
x = float(x_int)/scaling                             #then re-scaled back to the unit square.
print "y=?"
y_int = int(raw_input())
y = float(y_int)/scaling
closest = root.find_best((x,y))
closest = map(lambda x: int(scaling*x),closest)  #scale it

####draw a line from the queried location to the closest city###           ##THIS DOES NOT WORK FOR SOME REASON###
print (x_int,y_int)
print closest

pygame.draw.line(screen,(255,255,255),(x_int,y_int),closest)
pygame.display.update()
pygame.display.update()
#####

print "closest city is " + str(closest)

pause = raw_input()                         #a dummy input to pause the program from quitting 


