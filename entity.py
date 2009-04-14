import random
import time

from direct.actor.Actor import Actor
from pandac.PandaModules import CollisionNode
from pandac.PandaModules import CollisionHandlerQueue, CollisionRay
from pandac.PandaModules import BitMask32, Point3


class Entity():    
    def __init__(self, world, pos):
        self.world = world
        # init the model or the Actor
        self.model = self.getModel()
        self.model.setPos(*pos)
        
        self.prevPos = self.model.getPos()
        
        # collision traversable
        self.cTrav = world.cTrav
        
        # collision detection with the ground
        groundRay = CollisionRay()
        groundRay.setOrigin(0, 0, 1000)
        groundRay.setDirection(0, 0, -1)
        groundCol = CollisionNode('camRay')
        groundCol.addSolid(groundRay)
        groundCol.setFromCollideMask(BitMask32.bit(0))
        groundCol.setIntoCollideMask(BitMask32.allOff())
        groundColNp = self.model.attachNewNode(groundCol)
        self.groundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(groundColNp, self.groundHandler)
        
        self.postInit()
    
    def postInit(self):
        pass
        
    def validateMove(self):
        entityGroundEntry = self.getGroundEntry(self.groundHandler)
        if entityGroundEntry is not None and entityGroundEntry.getIntoNode().getName() == 'terrain':
            # Limit Ralph's Z to the highest Z found in the collision entries list.
            self.model.setZ(entityGroundEntry.getSurfacePoint(render).getZ())
            return True
        else:
            # We are outside the map, or trying to access an area that we cannot enter.
            # Prevent the move.
            self.model.setPos(self.prevPos)
            return False
        
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


class ItemEntity(Entity):
    def attachTo(self, joint, model):
        assert self.model.getParent() == render
        
        self.model.setPos(0, 0, 0)
        self.model.reparentTo(joint)
        self.maintainScaleRelativeTo(model)
    
    def detachAt(self, pos):
        assert self.model.getParent() <> render
        
        self.model.reparentTo(render)
        self.model.setPos(pos)
        self.restoreScale()
    
    def maintainScaleRelativeTo(self, other):
        other_scale = other.getScale()[0]
        scale = self.model.getScale()[0]
        self.model.setScale(scale / other_scale)
        self.originalScale = scale
    
    def restoreScale(self):
        self.model.setScale(self.originalScale)
        del self.originalScale


class PlayerEntity(Entity):
    def postInit(self):
        self.isMoving = False
        self.model.setScale(0.2)

        self.rightHand = self.model.exposeJoint(None, 'modelRoot', 'RightHand')

        self.item = None
        
        # By default, the left and right keys rotate the player character.
        self.strafeMode = False
    
    def enterStrafeMode(self):
        self.strafeMode = True
    
    def leaveStrafeMode(self):
        self.strafeMode = False

    def pickUpItem(self, item):
        """Pick up an item. If the player is already holding an item, it is not picked
        up."""
        if self.item is not None:
            return

        item.attachTo(self.rightHand, self.model)
        self.item = item
    
    def dropItem(self):
        """Drop the item the player is currently holding, if any."""
        if self.item is None:
            return
        
        self.item.detachAt(self.model.getPos())
        self.item = None
    
    def handleControls(self, timePassed):
        if self.strafeMode:
            self.handleControlsStrafe(timePassed)
        else:
            self.handleControlsDefault(timePassed)
        
        if self.world.keys.isPressed('forward'):
            self.model.setY(self.model, timePassed * -25)
        if self.world.keys.isPressed('backward'):
            self.model.setY(self.model, timePassed * 25)
    
    def handleControlsStrafe(self, timePassed):
        if self.world.keys.isPressed('left'):
            self.model.setX(self.model, timePassed * 15)
        if self.world.keys.isPressed('right'):
            self.model.setX(self.model, timePassed * -15)
    
    def handleControlsDefault(self, timePassed):
        if self.world.keys.isPressed('left'):
            self.model.setH(self.model, timePassed * 150)
        if self.world.keys.isPressed('right'):
            self.model.setH(self.model, timePassed * -150)

    def forceMove(self, timePassed):
        self.prevPos = self.model.getPos()
        
        self.handleControls(timePassed)

        if self.world.keys.isPressed('forward') or self.world.keys.isPressed('backward'):
            if self.isMoving is False:
                self.model.loop('run')
                self.isMoving = True
        elif self.isMoving:
                self.model.stop()
                self.model.pose('walk', 5)
                self.isMoving = False


class Baseball(ItemEntity):    
    def getModel(self):
        return loader.loadModel("models/baseball/baseball.egg")
    
    def postInit(self):
        self.model.setScale(0.5)


class Ralph(PlayerEntity):
    def getModel(self):
        return Actor('models/ralph/ralph.egg.pz', {
            'run': 'models/ralph/ralph-run.egg.pz',
            'walk': 'models/ralph/ralph-walk.egg.pz'
        })


class Eve(PlayerEntity):
    def getModel(self):
        return Actor('models/eve/eve.egg', {
            'run': 'models/eve/eve-run.egg',
            'walk': 'models/eve/eve-walk.egg'
        })


class Panda(Entity):
    def getModel(self):
        return Actor('models/panda/panda-model.egg.pz', {
            'walk': 'models/panda/panda-walk4.egg.pz'
        })
    
    def postInit(self):
        random.seed()
        
        # The panda is huge! Scale it down so we can actually see it.
        self.model.setScale(0.005)
                
        self.speed = 200
        self.model.loop('walk')
        self.setRandomHeading()
    
    def setRandomHeading(self):
        self.model.setH(random.randint(0, 360))
        
    def forceMove(self, timePassed):
        self.prevPos = self.model.getPos()
        self.model.setY(self.model, -(timePassed * self.speed))
    
    def validateMove(self):
        if not Entity.validateMove(self):
            self.setRandomHeading()
