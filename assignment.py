from tkinter import *
from PIL import Image,ImageTk
import time

#Extremely edited source code based on basic grid representation from:
#https://stackoverflow.com/questions/30023763/how-to-make-an-interactive-2d-grid-in-a-window-in-python

class Cell():
    

    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x #positional value on x axis
        self.ord = y #positional value on y axis
        self.size= size
        self.fill= False
        self.type = "Empty" #the cell type
        self.carrying = None #if the cell is a robot indicates what the robot is carrying
        self.score = -1 #stores the hueristic score used in A* 
        self.prev = "Empty" 
        self.NextTo = []
        self.rotation = 0 #stores the rotation angle of the cells
        self.robotImg = ImageTk.PhotoImage(Image.open("robot-1.jpg").resize((size-2,size-2)))
        self.robotBImg = ImageTk.PhotoImage(Image.open("robot-box_.jpg").resize((size-2,size-2)))
        self.boxImg = ImageTk.PhotoImage(Image.open("box.jpg").resize((size-2,size-2)))
        self.boxTargetImg = ImageTk.PhotoImage(Image.open("box_target.jpg").resize((size-2,size-2)))
        self.BoxDeliveredImg = ImageTk.PhotoImage(Image.open("box-delivered.jpg").resize((size-2,size-2)))

    def draw(self):
        """ order the cell to draw its representation on the tkinter canvas """
        if self.master != None :
            
            if self.type == "Obstacle":
                fill = "gray"
                outline = "black"

            if self.type == "Empty":
                fill = "white"
                outline = "black"

            xmin = self.abs * self.size
            xmax = xmin + self.size
            ymin = self.ord * self.size
            ymax = ymin + self.size

            if self.type in ["Obstacle","Empty"]:
                self.master.create_rectangle(xmin, ymin, xmax, ymax, fill = fill, outline = outline)
            if self.type == "Box":
                self.boxImg = ImageTk.PhotoImage(Image.open("box.jpg").rotate(self.rotation).resize((self.size-2,self.size-2)))
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.boxImg)
            if self.type == "BoxTarget":
                self.boxImg = ImageTk.PhotoImage(Image.open("box_target_.jpg").rotate(self.rotation).resize((self.size-2,self.size-2)))
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.boxImg)
            if self.type == "Robot" and self.carrying == None:
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.robotImg)
            if self.type == "Robot" and self.carrying == "Box":
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.robotBImg)
            if self.type == "BoxDelivered":
                self.BoxDeliveredImg = ImageTk.PhotoImage(Image.open("box-delivered_.jpg").rotate(self.rotation).resize((self.size-2,self.size-2)))
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.BoxDeliveredImg)


class CellGrid(Canvas):
    def __init__(self,master, rowNumber, columnNumber, cellSize, *args, **kwargs):
        Canvas.__init__(self, master, width = cellSize * columnNumber , height = cellSize * rowNumber, *args, **kwargs)
        
        self.cellSize = cellSize
        self.currentType = "Obstacle" #currently chosen cell type setting to place based on
        self.grid = [] #where our grid is stored
        self.robotRow = -1 #keep track of the robots location
        self.robotCol = -1  
        self.currentRotation = 0 #currently chosen rotation setting to place based on
        p1 = PanedWindow()
        p1.pack(side = RIGHT)
        b4 = Button(p1, text="Robot", fg="blue",command=(lambda: self.changeType("Robot")))
        b4.pack(side=TOP,fill=BOTH)
        b1 = Button(p1, text="Obstacle", fg="blue",command=(lambda: self.changeType("Obstacle")))
        b1.pack(side=TOP,fill=BOTH)
        b2 = Button(p1, text="Box", fg="blue",command=(lambda: self.changeType("Box")))
        b2.pack(side=TOP,fill=BOTH)
        b9 = Button(p1, text="BoxTarget", fg="blue",command=(lambda: self.changeType("BoxTarget")))
        b9.pack(side=TOP,fill=BOTH)
        b5 = Button(p1, text="0??", fg="black",command=(lambda: self.changeRotation(0)))
        b5.pack(side=TOP,fill=BOTH)
        b6 = Button(p1, text="90??", fg="black",command=(lambda: self.changeRotation(-90)))
        b6.pack(side=TOP,fill=BOTH)
        b7 = Button(p1, text="180??", fg="black",command=(lambda: self.changeRotation(-180)))
        b7.pack(side=TOP,fill=BOTH)
        b8 = Button(p1, text="270??", fg="black",command=(lambda: self.changeRotation(-270)))
        b8.pack(side=TOP,fill=BOTH)
        b11 = Button(p1, text="Start DFS", fg="red",command=(lambda: self.startDFS()))
        b11.pack(side=TOP,fill=BOTH)
        b12 = Button(p1, text="Start A*", fg="red",command=(lambda: self.startAstar()))
        b12.pack(side=TOP,fill=BOTH)
        b13 = Button(p1, text="Reset", fg="red",command=(lambda: self.reset()))
        b13.pack(side=TOP,fill=BOTH)

        for row in range(rowNumber):  #fill our grid represenation with the required cells
            line = []
            for column in range(columnNumber): #according to the required size
                line.append(Cell(self, column, row, cellSize))

            self.grid.append(line)
        self.robotCell= self.grid[0][0]
        #memorize the cells that have been modified to avoid many switching of state during mouse motion.
        self.switched = []

        #bind click action
        self.bind("<Button-1>", self.handleMouseClick)  
        #bind moving while clicking
        self.bind("<B1-Motion>", self.handleMouseMotion)
        #bind release button action - clear the memory of midified cells.
        self.bind("<ButtonRelease-1>", lambda event: self.switched.clear())

        self.draw()

    def reset(self): #reset the grid
        for i in self.grid:
            for j in i:
                j.type = "Empty"
                j.carrying = None
                j.rotation = 0
        self.draw()

    def _switch(self,cell,type):
        """ Switch the cell type. """

        if(type == "Robot"):
            if(self.robotRow == -1):
                self.robotRow = cell.ord
                self.robotCol = cell.abs 
            else:
                self.grid[self.robotRow][self.robotCol].type = self.grid[self.robotRow][self.robotCol].prev
                self.grid[self.robotRow][self.robotCol].draw()
                self.robotRow = cell.ord
                self.robotCol = cell.abs
            self.grid[self.robotRow][self.robotCol].prev = "Empty"
            cell.prev = cell.type
            cell.type = "Robot"
            
            
            
        else:
            if(cell.type == type):
                cell.type = "Empty"
                cell.prev = "Empty"
                cell.rotation = 0
            else:
              cell.type = type
              cell.prev = "Empty"
              cell.rotation = self.currentRotation
        
    def find_neighbours(self,cell): #finds the neighbours cells of a cell according to a certain order (anticlockwise)
        nextTo = []
        #right
        if(cell.abs != len(self.grid[0])-1):
            if(self.grid[cell.ord][cell.abs+1]):
                nextTo.append(self.grid[cell.ord][cell.abs+1])
        #up
        if(cell.ord != 0):
            if(self.grid[cell.ord-1][cell.abs]):
                nextTo.append(self.grid[cell.ord-1][cell.abs])
        #left
        if(cell.abs != 0):
            if(self.grid[cell.ord][cell.abs-1]):
              nextTo.append(self.grid[cell.ord][cell.abs-1])
        #down
        if(cell.ord != len(self.grid)-1):
            if(self.grid[cell.ord+1][cell.abs]):
                nextTo.append(self.grid[cell.ord+1][cell.abs])

        return nextTo

    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()

    def _eventCoords(self, event):
        row = int(event.y / self.cellSize)
        column = int(event.x / self.cellSize)
        return row, column

    def handleMouseClick(self, event):
        row, column = self._eventCoords(event)
        cell = self.grid[row][column]
        
        self._switch(cell,self.currentType)
        #cell._switch(self.currentType)
        
        cell.draw()
        #add the cell to the list of cell switched during the click
        self.switched.append(cell)

    def handleMouseMotion(self, event):
        row, column = self._eventCoords(event)
        cell = self.grid[row][column]

        if cell not in self.switched:
            #cell._switch(self.currentType)
            self._switch(cell,self.currentType)
            cell.draw()
            
            self.switched.append(cell)
    
    def changeType(self,type):
        self.currentType = type
    
    def changeRotation(self,rotation):
        self.currentRotation = rotation

    def carry(self,target): #takes a type and looks for it in the cells neighbours and picks it up
        robot = self.grid[self.robotRow][self.robotCol]
        found = False
        for i in self.find_neighbours(robot):
            if(found):
                break
            if(i.type == target):
                robot.carrying = target
                i.type = "Empty"
                robot.draw()
                i.draw()
                found = True

        if(found == False):
            print("No " +target + " in Sight")

    def dropitem(self,target): #attempts to drop current item at target
        robot = self.grid[self.robotRow][self.robotCol]
        dropType = None
        if(target in self.find_neighbours(robot)):
            if(robot.carrying == "Box"):
                dropType = "BoxDelivered"
        
            if(robot.carrying != None):
                target.type = dropType
                target.prev = "Empty"
                print("Dropped "+ robot.carrying)
                robot.carrying = None
                target.draw()
                robot.draw()
                return True
            else:
                return False
        else:
            return False

    def clear(self):
        self.draw()

    

    def moveAlongPath(self,path,delay): #takes a path and moves the robot along it
        
        prev = None
        for i in path:
            if(i != prev):
                robot = self.grid[self.robotRow][self.robotCol]
                temp = robot.carrying
                robot.carrying = None
                self._switch(i,"Robot")
                i.carrying = temp
                i.draw()
                self.update()
                self.master.after(delay)
            prev = i
                
        

    def print_num_delay(self,x,y,num,delay):
        self.create_text(x,y,fill="black",font="Times 20 bold",text=num)
        self.update()
        self.master.after(delay)

    def startDFS(self):
        boxes = []
        boxTargets = []
        robot = None
        animation_delay = 50
        
        def gridRead():
            nonlocal robot
            nonlocal boxes
            nonlocal boxTargets
            boxes = []
            boxTargets = []
            for i in self.grid:
                for j in i:
                    if(j.type == "Box"):
                        boxes.append(j)
                    if(j.type == "BoxTarget"):
                        boxTargets.append(j)
                    if(j.type == "Robot"):
                        robot = j

            if(robot != None):
                print("Robot at ("+str(robot.abs)+","+str(robot.ord)+")")
            else:
                print("Robot not found")

            if(len(boxes)>0):
                for i in boxes:
                    print("Box at ("+str(i.abs)+","+str(i.ord)+") Orientation: "+str(i.rotation)+"??")
            else:
                print("No boxes found.")

            if(len(boxTargets)>0):
                for i in boxTargets:
                    print("BoxTarget at ("+str(i.abs)+","+str(i.ord)+") Orientation: "+str(i.rotation)+"??")
            else:
                print("No box Targets found.")

            

        #self.grid[y][x] -> [ord][abs]
        
        #DFS
        def DFS(target):
            self.clear()
            

            if(type(target) == type(self.grid[0][0])):
                visited = []
                queue =[]
                path = []
                next = robot
                visited.append(robot)
                fail = False
                #backtrack when stuck
                while(target not in self.find_neighbours(next) and fail == False):
                        temp = next
                        path.append(next)
                        nodes = self.find_neighbours(next)
                        while(len(nodes)>0):
                            i = nodes.pop(0)
                            if(i.type == "Empty" and i not in visited):
                                queue.append(i)
                                visited.append(i)
                                next = i
                                break
                        if(next != robot):
                            if(temp == next):
                                next = visited[visited.index(temp)-1]
                        else:
                            fail = True
                            break  
                if(fail):
                    print("Failed to reach Object")
                if(target in self.find_neighbours(next) and fail == False):
                    path.append(next)
                    print("Reached "+ target.type +" Succesfully.")       

                self.pointImg = ImageTk.PhotoImage(Image.open("point.jpg").rotate(180).resize((next.size-2,next.size-2)))
                visited.pop(0)
                counter = 1 
                for i in visited:
                    xmin = i.abs * i.size
                    xmax = xmin + i.size
                    ymin = i.ord * i.size
                    ymax = ymin + i.size
                    
                    #self.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.pointImg)
                    #self.create_text((xmin+xmax)/2,(ymin+ymax)/2,fill="black",font="Times 20 bold",text=counter)
                    self.print_num_delay((xmin+xmax)/2,(ymin+ymax)/2,counter,animation_delay)
                    counter+=1
                    

                return path    
            elif(type(target) == type("str")):
                visited = []
                queue =[]
                path = []
                next = robot
                visited.append(robot)
                fail = False
                reached = False
                #backtrack when stuck
                while(reached == False and fail == False):
                        for i in self.find_neighbours(next):
                            if(i.type == target):
                                reached = True
                        path.append(next)
                        if(reached):
                            break
                        temp = next
                        
                        nodes = self.find_neighbours(next)
                        while(len(nodes)>0):
                            i = nodes.pop(0)
                            if(i.type == "Empty" and i not in visited):
                                queue.append(i)
                                visited.append(i)
                                next = i
                                break
                        if(next != robot):
                            if(temp == next):
                                next = visited[visited.index(temp)-1]
                                path.append(next)
                        else:
                            fail = True
                            break  
                if(fail):
                    print("Failed to reach a " + target)
                if(target in self.find_neighbours(next) and fail == False):
                    
                    print("Reached a "+ target +" Succesfully.")       

                self.pointImg = ImageTk.PhotoImage(Image.open("point.jpg").rotate(180).resize((next.size-2,next.size-2)))
                visited.pop(0)
                counter = 1 
                for i in visited:
                    xmin = i.abs * i.size
                    xmax = xmin + i.size
                    ymin = i.ord * i.size
                    ymax = ymin + i.size
                    
                    #self.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.pointImg)
                    self.print_num_delay((xmin+xmax)/2,(ymin+ymax)/2,counter,animation_delay)
                    counter+=1
                return path,fail

        gridRead()
        
        while(len(boxTargets)>0):
                if(robot.carrying == "Box"):
                    path,failed = DFS("BoxTarget")
                    
                    if(failed):
                        break
                    
                    self.moveAlongPath(path,50)
                    failed = self.dropitem(boxTargets[0])
                    if(not failed):
                        break
                else:
                    if(len(boxes)>0):
                        path,failed = DFS("Box")
                        if(failed):
                            break
                        self.moveAlongPath(path,50)
                        self.carry("Box")
                    else:
                     print("Not enough boxes for targets")
                     break       
                gridRead()
                

    def startAstar(self):

        boxes = []
        boxTargets = []
        robot = None
        animation_delay = 2
        
        def gridRead():
            nonlocal robot
            nonlocal boxes
            nonlocal boxTargets
            boxes = []
            boxTargets = []
            for i in self.grid:
                for j in i:
                    j.score = -1
                    if(j.type == "Box"):
                        boxes.append(j)
                    if(j.type == "BoxTarget" or j.prev == "BoxTarget"):
                        boxTargets.append(j)
                    if(j.type == "Robot"):
                        robot = j

            if(robot != None):
                print("Robot at ("+str(robot.abs)+","+str(robot.ord)+")")
            else:
                print("Robot not found")

            if(len(boxes)>0):
                for i in boxes:
                    print("Box at ("+str(i.abs)+","+str(i.ord)+") Orientation: "+str(i.rotation)+"??")
            else:
                print("No boxes found.")

            if(len(boxTargets)>0):
                for i in boxTargets:
                    print("BoxTarget at ("+str(i.abs)+","+str(i.ord)+") Orientation: "+str(i.rotation)+"??")
            else:
                print("No box Targets found.")

            
            
            

        def calculateHeuristic(): #calculates the heuristic scores of reachable destinations
            gridRead()
            self.clear()
            gDone=[]
            queue = [] #queue to keep BFS like order
            robot.score = 0
            queue.append(robot)
            gDone.append(robot)
            for i in self.find_neighbours(robot): #assigning score
                if(i.type != "Obstacle"):
                    i.score = 1
                    queue.append(i)
                    gDone.append(i)
                    xmin = i.abs * i.size
                    xmax = xmin + i.size
                    ymin = i.ord * i.size
                    ymax = ymin + i.size
                    self.print_num_delay((xmin+xmax)/2,(ymin+ymax)/2,i.score,animation_delay)

            while(len(queue)>0): #making sure all reachable boxes get a score
                current = queue.pop(0)
                for i in self.find_neighbours(current):
                    if(i.type in ["Empty","BoxTarget"] and i.score == -1):
                        i.score = current.score+1
                        queue.append(i)
                        gDone.append(i)
                        xmin = i.abs * i.size
                        xmax = xmin + i.size
                        ymin = i.ord * i.size
                        ymax = ymin + i.size
                        self.print_num_delay((xmin+xmax)/2,(ymin+ymax)/2,i.score,animation_delay)
                    if(i.type in ["Box"] and i.score == -1):
                        i.score = current.score+1
                        gDone.append(i)
                        xmin = i.abs * i.size
                        xmax = xmin + i.size
                        ymin = i.ord * i.size
                        ymax = ymin + i.size
                        self.print_num_delay((xmin+xmax)/2,(ymin+ymax)/2,i.score,animation_delay)
            self.clear()
            return gDone

        def findPath(target): #finds the shortest path to a target using heuristic score
            path = []
            if(target.score != -1):
                next = target
                while(next != robot):
                    min = 999
                    minOwner = None
                    for i in self.find_neighbours(next):
                        if(i == robot):
                            next = robot
                            break
                        elif(i.score < min and i.score != -1):
                            min = i.score
                            minOwner = i
                            next = minOwner
                    if(minOwner != None and next != robot):
                        path.append(minOwner)
            return reversed(path)
        
        
        def planner(): #planner algorithim
            candidates = calculateHeuristic()
            boxTargetz = []
            boxz = []
            for i in candidates:
                if(i.type == "BoxTarget" or i.prev =="BoxTarget"):
                    boxTargetz.append(i)
                for j in self.find_neighbours(i):
                    if(j.type == "Box"):
                        boxz.append(i)
            
            boxTargetsCount = len(boxTargetz)
            boxCount = len(boxz)
            if(boxTargetsCount > 0 or (boxCount > 0 and robot.carrying == None)):
                if(robot.carrying == None):
                    min = 999
                    minOwner = None
                    for i in boxz:
                        if(i.score < min):
                            min = i.score
                            minOwner = i
                    boxz.remove(minOwner)
                    if(minOwner != None):
                        self.moveAlongPath(findPath(minOwner),50)
                        self._switch(minOwner,"Robot")
                        minOwner.draw()
                        self.carry("Box")
                    planner() #recursive call to keep it going

                if(robot.carrying == "Box"):
                    max = -1
                    maxOwner = None
                    for i in boxTargetz:
                        if(i.score>max):
                            max = i.score
                            maxOwner = i
                    boxTargetz.remove(maxOwner)
                    if(maxOwner != None):
                        self.moveAlongPath(findPath(maxOwner),50)
                        self.dropitem(maxOwner)
                    planner() #recursive call to keep it going

        planner() #intital call when button is pressed
        
            


                

if __name__ == "__main__" :
    app = Tk()

    grid = CellGrid(app, 10, 15, 50)
    grid.pack(side=LEFT)


    
    app.mainloop()