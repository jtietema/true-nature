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
        self.env = loader.loadModel('models/world/world.egg.pz')
        self.env.reparentTo(render)
        self.env.setPos(0, 0, 0)
        
        # Create an Actor instance for Ralph. We also specify the animation
        # models that we want to use as a dictionary, where we can use to
        # keys to refer to the animations later on. The start point of Ralph
        # is hardcoded in the world model somewhere, so we look that up.
        self.ralph = Actor('models/ralph/ralph.egg.pz', {
            'run': 'models/ralph/ralph-run.egg.pz',
            'walk': 'models/ralph/ralph-walk.egg.pz'
        })
        self.ralph.reparentTo(render)
        self.ralph.setScale(0.2)
        self.ralph.setPos(self.env.find('**/start_point').getPos())
        
        # Create a floater object that always floats 2 units above Ralph.
        # We make sure that it is attached to Ralph by reparenting it to
        # Ralph's object instance.
        self.floater = NodePath(PandaNode('floater'))
        self.floater.reparentTo(self.ralph)
        self.floater.setZ(self.floater.getZ() + 2)
        
        # Disable any mouse input, including moving the camera around with
        # the mouse.
        base.disableMouse()
        
        self.createCollisionHandlers()
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.ralph.getX(), self.ralph.getY() + 10, 2)

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
        
        # Schedule the move method to be executed in the game's main loop.
        taskMgr.add(self.move, 'move')
    
    def createCollisionHandlers(self):
        # Create a new collision traverser instance. We will use this to determine
        # if any collisions occurred after performing movement.
        self.cTrav = CollisionTraverser()
        
        camGroundRay = CollisionRay()
        camGroundRay.setOrigin(0, 0, 1000)
        camGroundRay.setDirection(0, 0, -1)
        camGroundCol = CollisionNode('camRay')
        camGroundCol.addSolid(camGroundRay)
        camGroundCol.setFromCollideMask(BitMask32.bit(0))
        camGroundCol.setIntoCollideMask(BitMask32.allOff())
        camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)
        
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
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.ralph.getX(), self.ralph.getY() + 10, 2)
        
        # Set the heading, pitch and roll of the camera.
        base.camera.setHpr(self.ralph.getH(), 0, 0)
        
        # Let the camera look at the floater object above Ralph.
        base.camera.lookAt(self.floater)
        
        return Task.cont

w = World()
run()
