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
#
#3) It would be cool to optionally draw the boxes of the kd-tree!


import random
import numpy
import pygame #so that we can see some graphix yo!
import math #for square root


scaling = 500                       #while internally everything is done on the unit square, this is scaled before being displayed graphically
number_of_cities = 40
display = False                        # Set if you want to display the grid.

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

    def find_best(self, point):                #Input: a queried location. Output: the city location in the appropriate leaf of the tree **according to grid**
        if self.data[0] == 'leaf': return self.data[1]
        if self.data[0] == 'branch':
            axis = self.depth%2
            if point[axis] < self.data[1]: return self.left.find_best(point)
            if point[axis] >= self.data[1]: return self.right.find_best(point)
    def find_best_improved(self, point):                #Input: a queried location. Output: the city location in the appropriate leaf of the tree **according to euclidean distance**
        if self.data[0] == 'leaf':
            best = self.data[1]
            best_dist = math.sqrt((best[0]-point[0])**2+(best[1]-point[1])**2)
            return (best_dist,self.data[1])
        if self.data[0] == 'branch':
            axis = self.depth%2
            if point[axis] < self.data[1]:
                (best_dist,best) = self.left.find_best_improved(point)
                if best_dist < math.fabs(point[axis]-self.data[1]):
                    return (best_dist,best)
                else:
                    (alternative_dist,alternative) = self.right.find_best_improved(point)
                    if best_dist <= alternative_dist:
                        return (best_dist,best)
                    else:
                        return (alternative_dist,alternative)
            elif point[axis] >= self.data[1]:
                (best_dist,best) = self.right.find_best_improved(point)
                if best_dist < math.fabs(point[axis]-self.data[1]):
                    return (best_dist,best)
                else:
                    (alternative_dist,alternative) = self.left.find_best_improved(point)
                    if best_dist <= alternative_dist:
                        return (best_dist,best)
                    else:
                        return (alternative_dist,alternative)
                
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

#####build the kd-tree######

scaled_cities = [(int(scaling*x),int(scaling*y)) for (x,y) in cities]  #Scaled version of the cities for display

root = kdNode()
root.build_tree(cities)

######################

pygame.init()
screen = pygame.display.set_mode((scaling,scaling))
pygame.display.set_caption('Cities')

for city_location in scaled_cities:
    pygame.draw.circle(screen,(255,255,255),city_location,2,1)

pygame.display.update()



def display_grid(root,box_range):    #box_range consists of a triple (x_min,x_max,y_min,y_max) which is the box we are currently dividing
    (x_min,y_min,x_max,y_max) = box_range
    if root.data[0] == 'leaf':
        return
    elif root.data[0] == 'branch':
        axis = root.depth % 2
        median = int(scaling * root.data[1])
        if axis == 0:    # divides along x-axis so draw a vetical line at x = median
            pygame.draw.line(screen,(255,100,100),(median,y_min),(median,y_max))
            display_grid(root.left, (x_min,y_min,median,y_max))
            display_grid(root.right, (median,y_min,x_max,y_max))
        if axis == 1:    # divides along y-axis so draw a horizontal line at y = median
            pygame.draw.line(screen,(255,100,100),(x_min,median),(x_max,median))
            display_grid(root.left, (x_min,y_min,x_max,median))
            display_grid(root.right, (x_min,median,x_max,y_max))


if display: display_grid(root, (0,0,scaling,scaling))
running = 1

while running == 1:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = 0
    elif event.type == pygame.MOUSEBUTTONDOWN:               #on MOUSEBUTTONDOWN draw a white line from the clicked spot to the closest city
        (scaled_x,scaled_y) = event.pos
        x = float(scaled_x)/scaling                         
        y = float(scaled_y)/scaling
#        closest = root.find_best((x,y))
        (distance,closest) = root.find_best_improved((x,y))
        closest = map(lambda elem: int(scaling*elem),closest)  #scale it
        pygame.draw.line(screen,(255,255,255),(scaled_x,scaled_y),closest)
    elif event.type == pygame.MOUSEBUTTONUP:                    #on MOUSEBUTTONUP clear screen and redraw cities (thereby eliminating the line)
        screen.fill((0,0,0))
        if display: display_grid(root, (0,0,scaling,scaling))
        for city_location in scaled_cities:
            pygame.draw.circle(screen,(255,255,255),city_location,2,1)
    pygame.display.update()

    

        



