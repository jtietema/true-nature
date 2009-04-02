import sys

import direct.directbase.DirectStart
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import PandaNode, NodePath, Camera, TextNode
from pandac.PandaModules import Vec3, Vec4, BitMask32
from pandac.PandaModules import CollisionTraverser, CollisionNode
from pandac.PandaModules import CollisionHandlerQueue, CollisionRay
from pandac.PandaModules import ModifierButtons
from direct.actor.Actor import Actor
import keys

class World(DirectObject):
    def __init__(self):
        self.isMoving = False
        self.isWalking = False
        
        base.win.setClearColor(Vec4(0, 0, 0, 1))
        
        # set defailt key actions
        self.keyMap = {}
        
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
            'shift':        'shift'
        })
        
        # Schedule the move method to be executed in the game's main loop.
        taskMgr.add(self.move, 'move')
    
    
    
    def createCollisionHandlers(self):
        # Create a new collision traverser instance. We will use this to determine
        # if any collisions occurred after performing movement.
        self.cTrav = CollisionTraverser()
        
        ralphGroundRay = CollisionRay()
        ralphGroundRay.setOrigin(0, 0, 1000)
        ralphGroundRay.setDirection(0, 0, -1)
        ralphGroundCol = CollisionNode('ralphRay')
        ralphGroundCol.addSolid(ralphGroundRay)
        ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        ralphGroundColNp = self.ralph.attachNewNode(ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(ralphGroundColNp, self.ralphGroundHandler)
        
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
        
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def move(self, task):
        # get the time passed since the last frame
        timePassed = globalClock.getDt()
        
        startPos = self.ralph.getPos()
        
        # process the controls
        if self.keys.isPressed('left'):
            self.ralph.setH(self.ralph.getH() + timePassed * 300)
        if self.keys.isPressed('right'):
            self.ralph.setH(self.ralph.getH() - timePassed * 300)
        if self.keys.isPressed('forward'):
            self.ralph.setY(self.ralph, -(timePassed*25))
        if self.keys.isPressed('backward'):
            self.ralph.setY(self.ralph, timePassed*25)
        
        self.isWalking = self.keys.isPressed('shift')
        
        if self.keys.isPressed('forward') or self.keys.isPressed('backward'):
            if self.isMoving is False:
                if self.isWalking:
                    self.ralph.loop('walk')
                else:
                    self.ralph.loop('run')
                self.isMoving = True
        elif self.isMoving:
                self.ralph.stop()
                self.ralph.pose('walk', 5)
                self.isMoving = False
        
        # Do collision detection. This iterates all the collider nodes and 
        self.cTrav.traverse(render)
        
        # Iterate all the collisions that were found for Ralph's collision ray
        # and determine the highest value.
        ralphGroundEntry = self.getGroundEntry(self.ralphGroundHandler)
        if ralphGroundEntry is not None and ralphGroundEntry.getIntoNode().getName() == 'terrain':
            # Limit Ralph's Z to the highest Z found in the collision entries list.
            self.ralph.setZ(ralphGroundEntry.getSurfacePoint(render).getZ())
        else:
            # We are outside the map, or trying to access an area that we cannot enter.
            # Prevent the move.
            self.ralph.setPos(startPos)
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.ralph.getPos())

        # Set the heading, pitch and roll of the camera.
        base.camera.setHpr(self.ralph.getHpr())
        
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
