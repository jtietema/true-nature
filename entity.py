from direct.actor.Actor import Actor
from pandac.PandaModules import ActorNode, CollisionNode, CollisionHandlerQueue, ForceNode, LinearVectorForce
from pandac.PandaModules import CollisionRay, BitMask32, NodePath, CollisionSphere, CollisionTube

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
        fromObject = self.nodePath.attachNewNode(CollisionNode('colNode'))
        self.addSolids(fromObject)
        fromObject.show()

        self.world.cTrav.addCollider(fromObject, self.world.pusher)
        self.world.pusher.addCollider(fromObject, self.nodePath)
        
        self.postInit()
    
    def postInit(self):
        pass
    
    def addSolids(self, fromObject):
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 0.5))
        
    def validateMove(self):
        pass
        
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
    def postInit(self):
        self.getPhysicsObject().setMass(0.2)
    
    def addSolids(self, fromObject):
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 0.2))
    
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
        forceNode = ForceNode('forwardforce')
        self.nodePath.attachNewNode(forceNode)
        self.force = LinearVectorForce(0,-20,0)
#        self.force.setMassDependent(True)
        self.getPhysicsObject().setMass(80)
        self.force.setActive(False)
        forceNode.addForce(self.force)
        self.getPhysical(0).addLinearForce(self.force)
    
    def addSolids(self, fromObject):
        fromObject.node().addSolid(CollisionSphere(0, 0, 0.25, 0.3))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0.75, 0.3))
    
    def forceMove(self, timePassed):
        self.prevPos = self.nodePath.getPos()
        
        # process the controls
        if self.world.keys.isPressed('left'):
            self.nodePath.setH(self.nodePath.getH() + timePassed * 150)
        if self.world.keys.isPressed('right'):
            self.nodePath.setH(self.nodePath.getH() - timePassed * 150)
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
        



