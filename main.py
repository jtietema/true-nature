import sys

import direct.directbase.DirectStart
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import PandaNode, NodePath, Camera, TextNode
from pandac.PandaModules import Vec3, Vec4, BitMask32
from direct.actor.Actor import Actor

class World(DirectObject):
    def __init__(self):
        base.win.setClearColor(Vec4(0, 0, 0, 1))
        
        # set defailt key actions
        self.keyMap = {"left": 0, "right": 0, "forward": 0, "backward": 0}
        
        # Load the environment in which Ralph will walk. Set its parent
        # to the render variable so that it is a top-level node.
        self.env = loader.loadModel('models/world.egg.pz')
        self.env.reparentTo(render)
        self.env.setPos(0, 0, 0)
        
        # Create an Actor instance for Ralph.
        self.ralph = Actor('models/ralph.egg.pz', {
            'run': 'models/ralph-run.egg.pz',
            'walk': 'models/ralph-walk.egg.pz'
        })
        self.ralph.reparentTo(render)
        self.ralph.setPos(self.env.find('**/start_point').getPos())
        
        self.floater = NodePath(PandaNode('floater'))
        self.floater.reparentTo(self.ralph)
        self.floater.setZ(self.floater.getZ() + 2)
        
        base.disableMouse()
        base.camera.setPos(self.ralph.getX() + 10, self.ralph.getY() + 10, 50)
        
        # init the control callbacks
        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left", 1])
        self.accept("arrow_right", self.setKey, ["right", 1])
        self.accept("arrow_up", self.setKey, ["forward", 1])
        self.accept("arrow_down", self.setKey, ["backward", 1])
        
        self.accept("arrow_left-up", self.setKey, ["left", 0])
        self.accept("arrow_right-up", self.setKey, ["right", 0])
        self.accept("arrow_up-up", self.setKey, ["forward", 0])
        self.accept("arrow_down-up", self.setKey, ["backward", 0])
        
        taskMgr.add(self.move, 'move')
    
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def move(self, task):
        # get the time passed since the last frame
        timePassed = globalClock.getDt()
        
        # process the controls
        if self.keyMap["left"] != 0:
            self.ralph.setH(self.ralph.getH() + timePassed * 300)
        if self.keyMap["right"] != 0:
            self.ralph.setH(self.ralph.getH() - timePassed * 300)
        if self.keyMap["forward"] != 0:
            self.ralph.setY(self.ralph, -(timePassed*25))
        if self.keyMap["backward"] != 0:
            self.ralph.setY(self.ralph, timePassed*25)
        
        base.camera.lookAt(self.floater)
        return Task.cont

w = World()
run()
