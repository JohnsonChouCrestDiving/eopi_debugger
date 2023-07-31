class serverNoResponse(Exception):
    def __init__(self, From):
        super().__init__()
        self.msg = From
    def __str__(self):
        return self.msg
    
class noConnServer(Exception):
    def __init__(self):
        super().__init__()

class conditionShort(Exception):
    def __init__(self, whatCondition):
        super().__init__()
        self.msg = whatCondition
    def __str__(self):
        return self.msg
    
class serverDisconn(Exception):
    def __init__(self):
        super().__init__()
    