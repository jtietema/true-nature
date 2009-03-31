import direct.directbase.DirectStart
from direct.task import Task
import math

# load the street-scene
street = loader.loadModel("models/course1/course1")
street.reparentTo(render)
street.setScale(0.25, 0.25, 0.25)

# make the camera rotate
def rotate(task):
    angledegrees = task.time * 6.0
    base.camera.setH(base.camera.getH() + angledegrees)
    base.camera.setZ(3.0)
    base.camera.setP(-30)
    return Task.cont

def printCamera(task):
    print base.camera.getX(), base.camera.getY(), base.camera.getZ()
    return Task.cont

taskMgr.add(rotate, "RotateCamera")
#taskMgr.add(printCamera, "PrintCamera")
run()
