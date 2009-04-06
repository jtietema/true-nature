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

class Baseball(Entity):
    def getModel(self):
        return loader.loadModel("models/baseball/baseball.egg")

class Ralph(Entity):
    def getModel(self):
        return Actor('models/ralph/ralph.egg.pz', {
            'run': 'models/ralph/ralph-run.egg.pz',
            'walk': 'models/ralph/ralph-walk.egg.pz'
        })
    
    def postInit(self):
        self.isMoving = False
        self.model.setScale(0.2)
    
    def forceMove(self, timePassed):
        self.prevPos = self.model.getPos()
        
        # process the controls
        if self.world.keys.isPressed('left'):
            self.model.setH(self.model.getH() + timePassed * 150)
        if self.world.keys.isPressed('right'):
            self.model.setH(self.model.getH() - timePassed * 150)
        if self.world.keys.isPressed('forward'):
            self.model.setY(self.model, -(timePassed*25))
        if self.world.keys.isPressed('backward'):
            self.model.setY(self.model, timePassed*25)
        
        if self.world.keys.isPressed('forward') or self.world.keys.isPressed('backward'):
            if self.isMoving is False:
                self.model.loop('run')
                self.isMoving = True
        elif self.isMoving:
                self.model.stop()
                self.model.pose('walk', 5)
                self.isMoving = False

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
        self.setRandomDestination()
    
    def setDestination(self, x, y):
        self.model.lookAt(Point3(x, y, 0))
    
    def setRandomDestination(self):
        self.setDestination(random.randint(-120, 50), random.randint(-70, 50))
        
    def forceMove(self, timePassed):
        self.prevPos = self.model.getPos()
        self.model.setY(self.model, -(timePassed * self.speed))
    
    def validateMove(self):
        if not Entity.validateMove(self):
            self.setRandomDestination()
