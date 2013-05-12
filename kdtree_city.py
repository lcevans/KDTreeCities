#In this program n cities are placed at randomly generated locations. The user can then click at a location and an algorithm will locate the nearest city.
#By implementing a kd-tree, the algorithm runs in O(log n) complexity rather than the naive O(n) algorithm of checking the distance to each city one by one and taking the minimum.
#
#Interface Notes:
#-Hit 'a' to toggle the choice of algorithm between the O(log n) kd-tree and the O(n) simple linear search 
#-Hit 'g' to toggle the grid on and off
#-Hit 'c' to toggle "color generation". Each city is assigned a color, random points are chosen, and a line is drawn to the nearest city in that cities color. Given some time, the colors 
# partition the space into colored regions closest to the respective cities.
#-Use the left mouse button to identify the closest city by euclidean distance
#-Use the right mouse button to identify the closest city by the kd-tree (if the grid is turned on this is the city in the same grid-rectangle as the mouse)

import random
import numpy
import pygame #For graphics and keyboard/mouse interface.

scaling = 1000                         #While internally everything is done on the unit square, everything is scaled before being displayed graphically
number_of_cities = 50                 
display = False                        #Toggles whether or not to display the grid.
color_gen = False                      #Toggles "color generation" mode
use_naive_algorithm = False            #Toggles which algorithm to use to compute the nearest city

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
            self.data = ['branch',median]                                #Build the branching rule by the median of the points' values for the appropriate axis
            left_half = [item for item in points if item[axis] < median]
            right_half = [item for item in points if item[axis] >= median]
            self.left = kdNode(self.depth + 1)                           
            self.right = kdNode(self.depth + 1)
            self.left.build_tree(left_half)                              #Build the tree recursively
            self.right.build_tree(right_half)

    def find_best(self, point):                #Input: a queried location. Output: the city location in the appropriate leaf of the tree **according to grid**
                                               #This is an O(log n) algorithm.
        if self.data[0] == 'leaf': return self.data[1]
        if self.data[0] == 'branch':
            axis = self.depth%2
            if point[axis] < self.data[1]: return self.left.find_best(point)
            if point[axis] >= self.data[1]: return self.right.find_best(point)


    def find_best_improved(self, point):       #Input: a queried location. Output: a tuple consisting of the (optimal distance)^2 
                                               #and the city location in the appropriate leaf of the tree **according to euclidean distance**
                                               #This is an O(log n) algorithm.
        if self.data[0] == 'leaf':
            best = self.data[1]
            best_dist_squared = (best[0]-point[0])**2+(best[1]-point[1])**2
            return (best_dist_squared,self.data[1])
        if self.data[0] == 'branch':
            axis = self.depth%2
            if point[axis] < self.data[1]:
                (best_dist_squared,best) = self.left.find_best_improved(point)
                if best_dist_squared < (point[axis]-self.data[1])**2:
                    return (best_dist_squared,best)
                else:
                    (alternative_dist_squared,alternative) = self.right.find_best_improved(point)
                    if best_dist_squared <= alternative_dist_squared:
                        return (best_dist_squared,best)
                    else:
                        return (alternative_dist_squared,alternative)
            elif point[axis] >= self.data[1]:
                (best_dist_squared,best) = self.right.find_best_improved(point)
                if best_dist_squared < (point[axis]-self.data[1])**2:
                    return (best_dist_squared,best)
                else:
                    (alternative_dist_squared,alternative) = self.left.find_best_improved(point)
                    if best_dist_squared <= alternative_dist_squared:
                        return (best_dist_squared,best)
                    else:
                        return (alternative_dist_squared,alternative)
                
    def  display_inorder(self):               #Standard in-order display of a tree. Useful for debugging.
        '''Displays the nodes of the tree in order from smallest to largest'''
        if self.left is not None:
            self.left.display_inorder()
        print self.data
        if self.right is not None:
            self.right.display_inorder()
        return        

#####Create the array of cities#####

cities = []

for i in range(number_of_cities):                    
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
        if axis == 0:    #Divides along x-axis so draw a vetical line at x = median
            pygame.draw.line(screen,(255,100,100),(median,y_min),(median,y_max))
            display_grid(root.left, (x_min,y_min,median,y_max))
            display_grid(root.right, (median,y_min,x_max,y_max))
        if axis == 1:    #Divides along y-axis so draw a horizontal line at y = median
            pygame.draw.line(screen,(255,100,100),(x_min,median),(x_max,median))
            display_grid(root.left, (x_min,y_min,x_max,median))
            display_grid(root.right, (x_min,median,x_max,y_max))

def draw_screen():
        screen.fill((0,0,0))
        if display: display_grid(root, (0,0,scaling,scaling))
        for city_location in scaled_cities:
            pygame.draw.circle(screen,(255,255,255),city_location,2,1)
    
def linear_search((x,y)):     #Simple O(n) linear search to find the closest city
    closest = cities[0]
    best_dist_squared = (cities[0][0]-x)**2+(cities[0][1]-y)**2
    for city in cities:
        new_dist_squared = (city[0]-x)**2+(city[1]-y)**2
        if new_dist_squared < best_dist_squared:
            best_dist_squared = new_dist_squared
            closest = city
    return closest

running = 1
while running == 1:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = 0
    elif event.type == pygame.MOUSEBUTTONDOWN:               #on MOUSEBUTTONDOWN draw a white line from the clicked spot to the closest city
        (scaled_x,scaled_y) = event.pos
        x = float(scaled_x)/scaling                         
        y = float(scaled_y)/scaling
        if event.button == 1:
            (distance_squared,closest) = root.find_best_improved((x,y))
        if event.button == 3:
            closest = root.find_best((x,y))
        closest = map(lambda elem: int(scaling*elem),closest)  #scale it
        pygame.draw.line(screen,(255,255,255),(scaled_x,scaled_y),closest)
            
    elif event.type == pygame.MOUSEBUTTONUP:                    #on MOUSEBUTTONUP clear screen and redraw cities (thereby eliminating the line)
        draw_screen()
    elif event.type == pygame.KEYDOWN:
        if event.unicode == 'g':
            display = not display
            draw_screen()
        if event.unicode == 'c':
            color_gen = not color_gen
            draw_screen()
        if event.unicode == 'a':
            use_naive_algorithm = not use_naive_algorithm
    if color_gen:                                               #when color_gen is True, query random points and draw a colored line to the nearest city in the appropriate color.
        (x,y) = (random.random(),random.random())
        (scaled_x,scaled_y) = (int(scaling*x),int(scaling*y))
        if not use_naive_algorithm:
            (distance_squared,closest) = root.find_best_improved((x,y))
        elif use_naive_algorithm:
            closest = linear_search((x,y))
        closest = map(lambda elem: int(scaling*elem),closest)  #scale it
        R = (13*closest[0]+19*closest[1]) % 206 + 50           #use a hash function to pick a color based on city location
        G = (5*closest[0]-11*closest[1]) % 206 + 50
        B = (47*closest[0]) % 206 + 50
        color = (R,G,B)
        pygame.draw.line(screen,color,(scaled_x,scaled_y),closest)       
    pygame.display.update()

    

        



