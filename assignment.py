from tkinter import *
from PIL import Image,ImageTk


class Cell():
    

    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x
        self.ord = y
        self.size= size
        self.fill= False
        self.type = "Empty"
        self.rotation = 0
        self.robotImg = ImageTk.PhotoImage(Image.open("robot-1.jpg").resize((size-2,size-2)))
        self.triangleImg = ImageTk.PhotoImage(Image.open("triangle.jpg").resize((size-2,size-2)))
        self.boxImg = ImageTk.PhotoImage(Image.open("box.jpg").resize((size-2,size-2)))

    

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
            if self.type == "Robot":
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.robotImg)
            if self.type == "Triangle":
                self.triangleImg = ImageTk.PhotoImage(Image.open("triangle.jpg").rotate(self.rotation).resize((self.size-2,self.size-2)))
                self.master.create_image((xmin+xmax)/2,(ymin+ymax)/2, image=self.triangleImg)


class CellGrid(Canvas):
    def __init__(self,master, rowNumber, columnNumber, cellSize, *args, **kwargs):
        Canvas.__init__(self, master, width = cellSize * columnNumber , height = cellSize * rowNumber, *args, **kwargs)
        
        self.cellSize = cellSize
        self.currentType = "Obstacle"
        self.grid = []
        self.robotRow = -1
        self.robotCol = -1
        self.currentRotation = 0

        b1 = Button(master, text="Obstacle", fg="grey",command=(lambda: self.changeType("Obstacle")))
        b1.pack(side=RIGHT)
        b2 = Button(master, text="Box", fg="yellow",command=(lambda: self.changeType("Box")))
        b2.pack(side=RIGHT)
        b3 = Button(master, text="Triangle", fg="green",command=(lambda: self.changeType("Triangle")))
        b3.pack(side=RIGHT)
        b4 = Button(master, text="Robot", fg="blue",command=(lambda: self.changeType("Robot")))
        b4.pack(side=RIGHT)
        b5 = Button(master, text="0°", fg="black",command=(lambda: self.changeRotation(0)))
        b5.pack(side=RIGHT)
        b6 = Button(master, text="90°", fg="black",command=(lambda: self.changeRotation(-90)))
        b6.pack(side=RIGHT)
        b7 = Button(master, text="180°", fg="black",command=(lambda: self.changeRotation(-180)))
        b7.pack(side=RIGHT)
        b8 = Button(master, text="270°", fg="black",command=(lambda: self.changeRotation(90)))
        b8.pack(side=RIGHT)

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
        """ Switch if the cell is filled or not. """

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

    

if __name__ == "__main__" :
    app = Tk()

    grid = CellGrid(app, 10, 15, 50)
    grid.pack(side=LEFT)


    
    app.mainloop()