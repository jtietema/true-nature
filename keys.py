from direct.showbase.DirectObject import DirectObject

class KeyStateManager(DirectObject):
    def __init__(self):
        self.keyMap = {}
    
    def registerKeys(self, keys):
        if isinstance(keys, dict):
            [self.registerKey(key, alias) for key, alias in keys.items()]
        else:
            [self.registerKey(key) for key in keys]
    
    def registerKey(self, key, alias=None):
        if alias is None:
            alias = key
        
        self.keyMap[alias] = 0
        self.accept(key, self.onKeyPressed, [alias])
        self.accept(key + '-up', self.onKeyReleased, [alias])
    
    def onKeyPressed(self, key):
        self.keyMap[key] = 1
    
    def onKeyReleased(self, key):
        self.keyMap[key] = 0
    
    def isPressed(self, key):
        return self.keyMap[key] <> 0
    
    def getPressedKeys(self):
        return [key for key in self.keyMap if self.keyMap[key] <> 0]