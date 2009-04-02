import sys

import direct.directbase.DirectStart
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import PandaNode, NodePath, Camera, TextNode
from pandac.PandaModules import Vec3, Vec4, BitMask32
from pandac.PandaModules import CollisionTraverser, CollisionNode
from pandac.PandaModules import CollisionHandlerQueue, CollisionRay
from direct.actor.Actor import Actor

from entity import Entity, Ralph, Baseball

class World(DirectObject):
    def __init__(self):
        self.isMoving = False
        
        base.win.setClearColor(Vec4(0, 0, 0, 1))
        
        # set defailt key actions
        self.keyMap = {"left": 0, "right": 0, "forward": 0, "backward": 0}
        
        # Load the environment in which Ralph will walk. Set its parent
        # to the render variable so that it is a top-level node.
        self.env = loader.loadModel('models/world/world.egg.pz')
        self.env.reparentTo(render)
        self.env.setPos(0, 0, 0)
        
        self.createCollisionHandlers()
        
        # Create an Actor instance for Ralph. We also specify the animation
        # models that we want to use as a dictionary, where we can use to
        # keys to refer to the animations later on. The start point of Ralph
        # is hardcoded in the world model somewhere, so we look that up.
        self.ralph = Ralph(self, self.env.find('**/start_point').getPos())
        self.ralph.model.reparentTo(render)
        
        # Create a floater object that always floats 2 units above Ralph.
        # We make sure that it is attached to Ralph by reparenting it to
        # Ralph's object instance.
        self.floater = NodePath(PandaNode('floater'))
        self.floater.reparentTo(self.ralph.model)
        self.floater.setZ(self.floater.getZ() + 2)
        
        # load baseball
        self.baseball = Baseball(self, self.ralph.model.getPos())
        self.baseball.model.reparentTo(render)
        
        # Disable any mouse input, including moving the camera around with
        # the mouse.
        base.disableMouse()
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.ralph.model.getX(), self.ralph.model.getY() + 10, 2)

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
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(base.camera.attachNewNode(camGroundCol), self.camGroundHandler)
        
                
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def move(self, task):
        # get the time passed since the last frame
        timePassed = globalClock.getDt()
        
        # update ralph
        self.ralph.forceMove(timePassed)
        
        # Do collision detection. This iterates all the collider nodes and 
        self.cTrav.traverse(render)
        
        # check if ralph's move is valid
        self.ralph.validateMove()
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.ralph.model.getPos())

        # Set the heading, pitch and roll of the camera.
        base.camera.setHpr(self.ralph.model.getHpr())
        
        base.camera.setY(base.camera, 10)
        
        camGroundEntry = self.getGroundEntry(self.camGroundHandler)
        if camGroundEntry is not None and camGroundEntry.getIntoNode().getName() == 'terrain':
            base.camera.setZ(camGroundEntry.getSurfacePoint(render).getZ() + 1.5)
        
        # Let the camera look at the floater object above Ralph.
        base.camera.lookAt(self.floater)
        
        return Task.cont
    
    def getGroundEntry(self, collisionHandler):
        # Put all the collision entries into a Python list so we can sort it,
        # properly.
        entries = []
        for i in range(collisionHandler.getNumEntries()):
            entries.append(collisionHandler.getEntry(i))
        
        # Sort the list by the collision points' Z values, making sure the
        # highest value ends up at the front of the list.
        entries.sort(lambda x, y: cmp(y.getSurfacePoint(render).getZ(),
                                      x.getSurfacePoint(render).getZ()))
        
        if len(entries) > 0:
            return entries[0]
        else:
            return None

w = World()
run()
