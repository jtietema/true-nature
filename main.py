import sys
import random

import direct.directbase.DirectStart
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import PandaNode, NodePath, Camera, TextNode
from pandac.PandaModules import Vec3, Vec4, BitMask32
from pandac.PandaModules import CollisionTraverser, CollisionNode
from pandac.PandaModules import CollisionHandlerQueue, CollisionRay
from pandac.PandaModules import ModifierButtons, CollisionHandlerPusher, LinearVectorForce, ForceNode, AngularEulerIntegrator
from pandac.PandaModules import WindowProperties
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText

import keys
import mouse

from entity import Entity, Ralph, Eve, Baseball, Panda

class World(DirectObject):
    def __init__(self):        
        base.win.setClearColor(Vec4(0, 0, 0, 1))
        
        # enable physics (and particle) engine 
        
        self.throwMode = False
        self.freelook = False
        
        self.score = OnscreenText('0', pos=(-1.32, 0.9), fg=(1, 1, 1, 1), bg=(0, 0, 0, 0.5), scale=0.1, align=TextNode.ALeft)
        
        # Load the environment in which Eve will walk. Set its parent
        # to the render variable so that it is a top-lplayerl node.
        self.env = loader.loadModel('models/world/world.egg.pz')
        self.env.reparentTo(render)
        self.env.setPos(0, 0, 0)
        
        self.createCollisionHandlers()
        
        # Create an Actor instance for Eve. We also specify the animation
        # models that we want to use as a dictionary, where we can use to
        # keys to refer to the animations later on. The start point of Eve
        # is hardcoded in the world model somewhere, so we look that up.
        self.player = Eve('Eve', self, self.env.find('**/start_point').getPos())
        #self.player.nodePath.setZ(self.player.nodePath.getZ() + 10)
        self.player.nodePath.reparentTo(render)
        
        # Create a floater object that always floats 2 units above Eve.
        # We make sure that it is attached to Eve by reparenting it to
        # Eve's object instance.
        self.floater = NodePath(PandaNode('floater'))
        self.floater.reparentTo(self.player.nodePath)
        self.floater.setZ(self.floater.getZ() + 2)
        
        # load baseball
        self.baseball = Baseball('baseball', self, self.player.nodePath.getPos())
        self.baseball.nodePath.reparentTo(render)
        self.player.pickUpItem(self.baseball)
        
        # Load the panda bear
        self.panda = Panda('panda', self, self.player.nodePath.getPos())
        self.panda.nodePath.reparentTo(render)
        
        # Disable controlling the camera using the mouse. Note that this does
        # not disable the mouse completely, it merely disables the camera
        # movement by mouse.
        base.disableMouse()
        
        self.hideMouseCursor()
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.player.nodePath.getX(), self.player.nodePath.getY() + 10, 2)
        
        # Disable modifier button compound events.
        base.mouseWatcherNode.setModifierButtons(ModifierButtons())
        base.buttonThrowers[0].node().setModifierButtons(ModifierButtons())

        # Register any control callbacks.
        self.accept('escape', sys.exit)
        self.accept('d', self.dropItem)
        self.accept('f', self.toggleFullscreen)
        
        self.accept('space', self.enterThrowMode)
        self.accept('space-up', self.leaveThrowMode)
        
        # Also make sure that we can, at any time, request the state (pressed
        # or not) for these keys.
        self.keys = keys.KeyStateManager()
        self.keys.registerKeys({
            'arrow_left':   'left',
            'arrow_right':  'right',
            'arrow_up':     'forward',
            'arrow_down':   'backward',
            'shift':        'shift',
            'r':            'reset'
        })
        
        self.mouse = mouse.MousePointerManager(0)
        
        # Schedule the move method to be executed in the game's main loop.
        taskMgr.add(self.update, 'update')
    
    def hideMouseCursor(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
    
    def toggleFullscreen(self):
        props = WindowProperties()
        props.setFullscreen(not base.win.getProperties().getFullscreen())
        base.win.requestProperties(props)
    
    def enableFreelook(self):        
        self.freelook = True

        # Make sure we reset the MouseMovementManager's last known mouse position,
        # so we don't get a huge delta on the first attempt.
        self.mouse.reset()
        
        base.camera.setP(0)
    
    def disableFreelook(self):
        self.freelook = False
    
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
        
        # register the collision pusher
        self.pusher = CollisionHandlerPusher()
        
        # register collision event pattern names
        self.pusher.addInPattern('col-%fn-into')
        
    
    def update(self, task):        
        # get the time passed since the last frame
        timePassed = globalClock.getDt()

        # update player
        self.player.forceMove(timePassed)
        self.panda.forceMove(timePassed)
        
        # Do collision detection. This iterates all the collider nodes
        self.cTrav.traverse(render)
        
        # check if player's move is valid
        self.player.validateMove()
        self.panda.validateMove()
        
        # Set the initial position for the camera as X, Y and Z values.
        base.camera.setPos(self.player.nodePath.getPos())
        
        if self.throwMode:
            # Position the camera a bit above the ground.
            base.camera.setZ(base.camera, 1.5)
            
            if self.freelook:
                mx, my = self.mouse.getDelta()
                
                h = -mx * 0.1
                p = -my * 0.1
                
                base.camera.setHpr(base.camera, h, p, 0)
                self.player.nodePath.setH(self.player.nodePath, h)
            else:
                # Set the heading, pitch and roll of the camera.
                base.camera.setHpr(self.player.nodePath.getHpr())
        else:
            # Set the heading, pitch and roll of the camera.
            base.camera.setHpr(self.player.nodePath.getHpr())
            
            # Position the camera somewhat behind the player.
            base.camera.setY(base.camera, 10)

            # Make sure the camera is above the ground.
            camGroundEntry = self.getGroundEntry(self.camGroundHandler)
            if camGroundEntry is not None and camGroundEntry.getIntoNode().getName() == 'terrain':
                base.camera.setZ(camGroundEntry.getSurfacePoint(render).getZ() + 1.5)

            # Let the camera look at the floater object above Eve.
            base.camera.lookAt(self.floater)
        
        return Task.cont
    
    def dropItem(self):
        self.player.dropItem()
    
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
        
    def enterThrowMode(self):
        self.throwMode = True
        self.player.enterStrafeMode()
        self.enableFreelook()
    
    def leaveThrowMode(self):
        self.throwMode = False
        self.player.leaveStrafeMode()
        self.disableFreelook()

w = World()
run()
