import direct.directbase.DirectStart
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import PandaNode, NodePath, Camera, TextNode
from pandac.PandaModules import Vec3, Vec4, BitMask32
from direct.actor.Actor import Actor

class World(DirectObject):
    def __init__(self):
        base.win.setClearColor(Vec4(0, 0, 0, 1))
        
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
        
        taskMgr.add(self.move, 'move')
    
    def move(self, task):
        base.camera.lookAt(self.floater)

w = World()
run()
