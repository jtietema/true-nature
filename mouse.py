import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from copy import copy

class MousePointerManager(DirectObject):
    """Calculates deltas for mouse movements."""
    
    def __init__(self, pointer_n=0):
        self.pointer_n = pointer_n
        
        self.reset()
    
    def getCenterPos(self):
        return (base.win.getXSize() / 2, base.win.getYSize() / 2)
        
    def getPos(self):
        """Safe method to get the current location of the mouse. If the cursor
        is outside the window, this method returns None instead of raising an
        exception."""
        # Apparently, Panda3D returns an object reference here. This leads to
        # the prevPos being updated implicitly once we call getMouse() again.
        # We work around this by extracting the relevant values from the object
        # and returning them as a tuple.
        md = base.win.getPointer(self.pointer_n)
        return (md.getX(), md.getY())
    
    def reset(self):
        """Moves the pointer back to the center of the screen."""
        self.movePointer(*self.getCenterPos())
    
    def movePointer(self, x, y):
        base.win.movePointer(self.pointer_n, x, y)
    
    def getDelta(self):
        """Returns the delta of the mouse movement since the previous call to
        this method. Since the coordinate system runs from (1,1) (top-left) to
        (-1,-1) (bottom-right), the value of the delta is somewhere between these
        two points."""        
        pos = self.getPos()
        centerX, centerY = self.getCenterPos()
        result = (pos[0] - centerX, pos[1] - centerY)
        self.movePointer(centerX, centerY)
        return result
