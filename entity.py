import random
import time

from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import ActorNode, CollisionNode, CollisionHandlerQueue, ForceNode, LinearVectorForce
from pandac.PandaModules import CollisionRay, BitMask32, NodePath, CollisionSphere, CollisionTube, Point3, AngularVectorForce

class Entity(ActorNode):
    def __init__(self, name, world, pos):
        ActorNode.__init__(self, name)
        
        self.nodePath = NodePath(self)
        
        self.world = world
        
        # init the model or the Actor
        self.model = self.getModel()
        self.model.reparentTo(self.nodePath)
        
        self.nodePath.setPos(*pos)
        
        self.prevPos = self.nodePath.getPos()
        
        # add actor to physics engine
        base.physicsMgr.attachPhysicalNode(self)
        
        # collision detection
        fromObject = self.nodePath.attachNewNode(CollisionNode(name))
        self.addSolids(fromObject)
        fromObject.show()

        self.world.cTrav.addCollider(fromObject, self.world.pusher)
        self.world.pusher.addCollider(fromObject, self.nodePath)
        
        self.postInit()
    
    def postInit(self):
        '''Subclasses can override this method to add stuff after the init'''
        pass
    
    def addSolids(self, fromObject):
        '''Subclasses can override this method to add sollids for collision
        detection to match their model and size. Below is a default'''
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 0.5))
        
    def validateMove(self):
        '''Deprecated'''
        pass
        
    def getGroundEntry(self, collisionHandler):
        '''Deprecated. Not used anymore'''
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
        # TODO: reparent model, leaves collision solids lying arround
        assert self.nodePath.getParent() == render
        
        self.model.setPos(0, 0, 0)
        self.model.reparentTo(joint)
        self.maintainScaleRelativeTo(model)
    
    def detachAt(self, pos):
        # TODO: reparent model, leaves collision solids lying arround
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

class Baseball(ItemEntity):
    def postInit(self):
        self.getPhysicsObject().setMass(0.2)
        self.model.setScale(0.5)
    
    def addSolids(self, fromObject):
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 0.2))
    
    def getModel(self):
        return loader.loadModel("models/baseball/baseball.egg")

class PlayerEntity(Entity):
    def postInit(self):
        self.isMoving = False
        self.model.setScale(0.2)
        
        # force stuff
        forceNode = ForceNode('forwardforce')
        self.nodePath.attachNewNode(forceNode)
        self.force = LinearVectorForce(0,-20,0)
#        self.force.setMassDependent(True)
        self.getPhysicsObject().setMass(80)
        self.force.setActive(False)
        forceNode.addForce(self.force)
        self.getPhysical(0).addLinearForce(self.force)
        
        self.turnLeft=AngularVectorForce(1,0,0) # Spin around the positive-x axis 
        forceNode.addForce(self.turnLeft) # Determine which positive-x axis we use for calculation
        self.getPhysical(0).addAngularForce(self.turnLeft) # Add the force to the object
        self.turnLeft.setActive(False)
        
        self.turnRight=AngularVectorForce(-1,0,0) # Spin around the positive-x axis 
        forceNode.addForce(self.turnRight) # Determine which positive-x axis we use for calculation
        self.getPhysical(0).addAngularForce(self.turnRight) # Add the force to the object
        self.turnRight.setActive(False)
        
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
    
    def addSolids(self, fromObject):
        fromObject.node().addSolid(CollisionSphere(0, 0, 0.25, 0.3))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0.75, 0.3))
    
    def dropItem(self):
        """Drop the item the player is currently holding, if any."""
        if self.item is None:
            return
        
        self.item.detachAt(self.nodePath.getPos())
        self.item = None

    def forceMove(self, timePassed):
        self.prevPos = self.nodePath.getPos()
        
        # process the controls
        if self.world.keys.isPressed('left'):
            self.turnLeft.setActive(True)
            self.turnRight.setActive(False)
        elif self.world.keys.isPressed('right'):
            self.turnRight.setActive(True)
            self.turnLeft.setActive(False)
        else:
            self.turnLeft.setActive(False)
            self.turnRight.setActive(False)
        
        if self.world.keys.isPressed('forward'):
            self.force.setActive(True)
            self.force.setAmplitude(1)
        elif self.world.keys.isPressed('backward'):
            self.force.setActive(True)
            self.force.setAmplitude(-1)
        else:
            # reset force
            self.force.setActive(False)
        if self.world.keys.isPressed('reset'):
            self.nodePath.setPos(self.world.env.find('**/start_point').getPos())
            self.nodePath.setZ(self.nodePath, 5)

        if self.world.keys.isPressed('forward') or self.world.keys.isPressed('backward'):
            if self.isMoving is False:
                self.model.loop('run')
                self.isMoving = True
        elif self.isMoving:
                self.model.stop()
                self.model.pose('walk', 5)
                self.isMoving = False

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


class Panda(Entity, DirectObject):
    def getModel(self):
        return Actor('models/panda/panda-model.egg.pz', {
            'walk': 'models/panda/panda-walk4.egg.pz'
        })
    
    def addSolids(self, fromObject):
        fromObject.node().addSolid(CollisionSphere(0, 0, 1.5, 1.5))
        fromObject.node().addSolid(CollisionSphere(0, -2, 1.5, 0.75))
    
    def postInit(self):
        random.seed()
        
        # The panda is huge! Scale it down so we can actually see it.
        self.model.setScale(0.005)
                
        self.speed = 2
        self.model.loop('walk')
        self.setRandomHeading()
        
        # accept collision events
        self.accept('col-panda-into', self.newHeadingCallback)
    
    def setRandomHeading(self):
        self.nodePath.setH(random.randint(0, 360))
        
    def forceMove(self, timePassed):
        self.prevPos = self.model.getPos()
        self.nodePath.setY(self.nodePath, -(timePassed * self.speed))
        if self.world.keys.isPressed('reset'):
            self.nodePath.setPos(self.world.env.find('**/start_point').getPos())
            self.nodePath.setZ(self.nodePath, 5)
    
    def newHeadingCallback(self, entry):
        if entry.getIntoNodePath().getName() != 'terrain':
            self.setRandomHeading()
    
    def validateMove(self):
        pass
