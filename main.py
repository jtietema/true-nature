import sys

import direct.directbase.DirectStart
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import PandaNode, NodePath, Camera, TextNode
from pandac.PandaModules import Vec3, Vec4, BitMask32
from pandac.PandaModules import CollisionTraverser, CollisionNode
from pandac.PandaModules import CollisionHandlerQueue, CollisionRay
from pandac.PandaModules import ModifierButtons, PhysicsCollisionHandler, LinearVectorForce, ForceNode
from direct.actor.Actor import Actor
import keys

from entity import Entity, Ralph, Baseball

class World(DirectObject):
    def __init__(self):
        self.isMoving = False
        self.isWalking = False
        
        base.win.setClearColor(Vec4(0, 0, 0, 1))
        
        # enable physics (and particle) engine 
        base.enableParticles()
        
        # set defailt key actions
        self.keyMap = {}
        
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
        self.ralph = Ralph('ralph', self, self.env.find('**/start_point').getPos())
        self.ralph.nodePath.setZ(self.ralph.nodePath.getZ() + 10)
        self.ralph.nodePath.reparentTo(render)
        
        # Create a floater object that always floats 2 units above Ralph.
        # We make sure that it is attached to Ralph by reparenting it to
        # Ralph's object instance.
        self.floater = NodePath(PandaNode('floater'))
        self.floater.reparentTo(self.ralph.nodePath)
        self.floater.setZ(self.floater.getZ() + 2)
        
        # load baseball
        self.baseball = Baseball('baseball', self, self.ralph.nodePath.getPos())
        self.baseball.nodePath.reparentTo(render)
        
        # Disable any mouse input, including moving the camera around with
        # the mouse.
        base.disableMouse()
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.ralph.nodePath.getX(), self.ralph.nodePath.getY() + 10, 2)
        
        # Disable modifier button compound events.
        base.mouseWatcherNode.setModifierButtons(ModifierButtons())
        base.buttonThrowers[0].node().setModifierButtons(ModifierButtons())

        # init the control callbacks
        self.accept('escape', sys.exit)
        
        self.keys = keys.KeyStateManager()
        self.keys.registerKeys({
            'arrow_left':   'left',
            'arrow_right':  'right',
            'arrow_up':     'forward',
            'arrow_down':   'backward',
            'shift':        'shift',
            'r':            'reset'
        })
        
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
        camGroundColNp = base.camera.attachNewNode(camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(camGroundColNp, self.camGroundHandler)
        
        self.pusher = PhysicsCollisionHandler()
        
        # create gravity
        gravityFN=ForceNode('world-forces')
        gravityFNP=render.attachNewNode(gravityFN)
        gravityForce=LinearVectorForce(0,0,-9.81) #gravity acceleration
        gravityFN.addForce(gravityForce)

        base.physicsMgr.addLinearForce(gravityForce)

        
                
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def move(self, task):
        # get the time passed since the last frame
        timePassed = globalClock.getDt()

        # update ralph
        self.ralph.forceMove(timePassed)
        
        # Do collision detection. This iterates all the collider nodes
        self.cTrav.traverse(render)
        
        # check if ralph's move is valid
        self.ralph.validateMove()
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.ralph.nodePath.getPos())

        # Set the heading, pitch and roll of the camera.
        base.camera.setHpr(self.ralph.nodePath.getHpr())
        
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
