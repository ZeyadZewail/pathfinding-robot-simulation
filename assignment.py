from tkinter import *
from PIL import Image,ImageTk
import threading

#heavily edited source code for basic grid representation
#https://stackoverflow.com/questions/30023763/how-to-make-an-interactive-2d-grid-in-a-window-in-python

class Cell():
    

    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x
        self.ord = y
        self.size= size
        self.fill= False
        self.type = "Empty"
        self.carrying = None
        self.NextTo = []
        self.rotation = 0
        self.robotImg = ImageTk.PhotoImage(Image.open("robot-1.jpg").resize((size-2,size-2)))
        self.robotBImg = ImageTk.PhotoImage(Image.open("robot-box.jpg").resize((size-2,size-2)))
        self.robotTImg = ImageTk.PhotoImage(Image.open("robot-triangle.jpg").resize((size-2,size-2)))
        self.triangleImg = ImageTk.PhotoImage(Image.open("triangle.jpg").resize((size-2,size-2)))
        self.boxImg = ImageTk.PhotoImage(Image.open("box.jpg").resize((size-2,size-2)))
        self.boxTargetImg = ImageTk.PhotoImage(Image.open("box_target.jpg").resize((size-2,size-2)))
        self.triangleTargetImg = ImageTk.PhotoImage(Image.open("triangle_target.jpg").resize((size-2,size-2)))


    def draw(self):
        """ order to the cell to draw its representation on the canvas """
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
                self.boxImg = ImageTk.PhotoImage(Image.open("box_target.jpg").rotate(self.rotation).resize((self.size-2,self.size-2)))
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.boxImg)
            if self.type == "Robot" and self.carrying == None:
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.robotImg)
            if self.type == "Robot" and self.carrying == "Box":
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.robotBImg)
            if self.type == "Robot" and self.carrying == "Triangle":
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.robotTImg)
            if self.type == "Triangle":
                self.triangleImg = ImageTk.PhotoImage(Image.open("triangle.jpg").rotate(self.rotation).resize((self.size-2,self.size-2)))
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.triangleImg)
            if self.type == "TriangleTarget":
                self.triangleTargetImg = ImageTk.PhotoImage(Image.open("triangle_target.jpg").rotate(self.rotation).resize((self.size-2,self.size-2)))
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.triangleTargetImg)


class CellGrid(Canvas):
    def __init__(self,master, rowNumber, columnNumber, cellSize, *args, **kwargs):
        Canvas.__init__(self, master, width = cellSize * columnNumber , height = cellSize * rowNumber, *args, **kwargs)
        
        self.cellSize = cellSize
        self.currentType = "Obstacle"
        self.grid = []
        self.robotRow = -1
        self.robotCol = -1
        self.currentRotation = 0
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
        b3 = Button(p1, text="Triangle", fg="blue",command=(lambda: self.changeType("Triangle")))
        b3.pack(side=TOP,fill=BOTH)
        b10 = Button(p1, text="TriangleTarget", fg="blue",command=(lambda: self.changeType("TriangleTarget")))
        b10.pack(side=TOP,fill=BOTH)
        b5 = Button(p1, text="0°", fg="black",command=(lambda: self.changeRotation(0)))
        b5.pack(side=TOP,fill=BOTH)
        b6 = Button(p1, text="90°", fg="black",command=(lambda: self.changeRotation(-90)))
        b6.pack(side=TOP,fill=BOTH)
        b7 = Button(p1, text="180°", fg="black",command=(lambda: self.changeRotation(-180)))
        b7.pack(side=TOP,fill=BOTH)
        b8 = Button(p1, text="270°", fg="black",command=(lambda: self.changeRotation(-270)))
        b8.pack(side=TOP,fill=BOTH)
        b11 = Button(p1, text="Start DFS", fg="red",command=(lambda: self.startDFS()))
        b11.pack(side=TOP,fill=BOTH)
        b12 = Button(p1, text="Clear Paths", fg="red",command=(lambda: self.clear()))
        b12.pack(side=TOP,fill=BOTH)

        for row in range(rowNumber):
            line = []
            for column in range(columnNumber):
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

    def _switch(self,cell,type):
        """ Switch the cell type. """

        if(type == "Robot"):
            if(self.robotRow == -1):
                self.robotRow = cell.ord
                self.robotCol = cell.abs 
            else:
                self.grid[self.robotRow][self.robotCol].type = "Empty"
                self.grid[self.robotRow][self.robotCol].draw()
                self.robotRow = cell.ord
                self.robotCol = cell.abs 
            cell.type = "Robot"
            
            
            
        else:
            if(cell.type == type):
                cell.type = "Empty"
                cell.rotation = 0
            else:
              cell.type = type
              cell.rotation = self.currentRotation
        
    def find_neighbours(self,cell):
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

    def carry(self,target):
        robot = self.grid[self.robotRow][self.robotCol]
        found = False
        for i in self.find_neighbours(robot):
            if(i.type == target):
                robot.carrying = target
                i.type = "Empty"
                robot.draw()
                i.draw()
                found = True

        if(found == False):
            print("No " +target + " in Sight")

    def dropitem(self,target):
        robot = self.grid[self.robotRow][self.robotCol]
        if(robot.carrying != None):
            target.type = robot.carrying
            print("Dropped "+ robot.carrying)
            robot.carrying = None
            target.draw()
            robot.draw()
        else:
            print("Not carrying anything")

    def clear(self):
        self.draw()


    def moveAlongPath(self,path):
        robot = self.grid[self.robotRow][self.robotCol]
        path[-1].carrying = robot.carrying
        robot.carrying = None
        self._switch(path[-1],"Robot")
        
        path[-1].draw()

    def startDFS(self):
        boxes = []
        triangles = []
        boxTargets = []
        triangleTargets = []
        robot = None

        for i in self.grid:
            for j in i:
                if(j.type == "Box"):
                    boxes.append(j)
                if(j.type == "BoxTarget"):
                    boxTargets.append(j)
                if(j.type == "Triangle"):
                    triangles.append(j)
                if(j.type == "TriangleTarget"):
                    triangleTargets.append(j)
                if(j.type == "Robot"):
                    robot = j

        if(robot != None):
            print("Robot at ("+str(robot.abs)+","+str(robot.ord)+")")
        else:
            print("Robot not found")

        if(len(boxes)>0):
            for i in boxes:
                print("Box at ("+str(i.abs)+","+str(i.ord)+") Orientation: "+str(i.rotation)+"°")
        else:
            print("No boxes found.")

        if(len(boxTargets)>0):
            for i in boxTargets:
                print("BoxTarget at ("+str(i.abs)+","+str(i.ord)+") Orientation: "+str(i.rotation)+"°")
        else:
            print("No box Targets found.")

        if(len(triangles)>0):
            for i in triangles:
                print("triangle at ("+str(i.abs)+","+str(i.ord)+") Orientation: "+str(i.rotation)+"°")
        else:
            print("No triangles found.")
        
        if(len(triangleTargets)>0):
            for i in triangleTargets:
                print("triangle Target at ("+str(i.abs)+","+str(i.ord)+") Orientation: "+str(i.rotation)+"°")
        else:
            print("No triangle Target found.")

        #self.grid[y][x] -> [ord][abs]
        for i in self.find_neighbours(robot):
            print(i.type)

        #DFS
        def DFS(target):
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
                for i in visited:
                    xmin = i.abs * i.size
                    xmax = xmin + i.size
                    ymin = i.ord * i.size
                    ymax = ymin + i.size
                    
                    self.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.pointImg)

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
                        if(reached):
                            path.append(next)
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
                        else:
                            fail = True
                            break  
                if(fail):
                    print("Failed to reach a " + target)
                if(target in self.find_neighbours(next) and fail == False):
                    
                    print("Reached a "+ target +" Succesfully.")       

                self.pointImg = ImageTk.PhotoImage(Image.open("point.jpg").rotate(180).resize((next.size-2,next.size-2)))
                visited.pop(0) 
                for i in visited:
                    xmin = i.abs * i.size
                    xmax = xmin + i.size
                    ymin = i.ord * i.size
                    ymax = ymin + i.size
                    
                    self.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.pointImg)
                return path

        if(len(boxTargets)>0):
                if(robot.carrying == "Box"):
                    self.moveAlongPath(DFS(boxTargets[0]))
                    self.dropitem(boxTargets[0])
                else:
                    if(len(boxes)>0):
                        self.moveAlongPath(DFS("Box"))
                        self.carry("Box")
                    else:
                     print("Not enough boxes for targets")       
        else:
            print("No targets")




if __name__ == "__main__" :
    app = Tk()

    grid = CellGrid(app, 10, 15, 50)
    grid.pack(side=LEFT)


    
    app.mainloop()