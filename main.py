import math

import direct.directbase.DirectStart
from direct.task import Task
from direct.showbase.DirectObject import DirectObject

class World(DirectObject):
    def __init__(self):
        # load the street-scene
        street = loader.loadModel("models/course1/course1.egg")
        street.reparentTo(render)
        street.setScale(0.25, 0.25, 0.25)
        
        taskMgr.add(self.rotate, "RotateCamera")
    
    # make the camera rotate
    def rotate(self, task):
        angledegrees = task.time * 6.0
        base.camera.setH(base.camera.getH() + angledegrees)
        base.camera.setZ(3.0)
        base.camera.setP(-30)
        return Task.cont

w = World()
run()
