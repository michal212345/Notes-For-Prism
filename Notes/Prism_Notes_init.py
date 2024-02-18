from Prism_Notes_Variables import Prism_Notes_Variables
from Prism_Notes_Functions import Prism_Notes_Functions


class Prism_Notes(Prism_Notes_Variables, Prism_Notes_Functions):
    def __init__(self, core):
        Prism_Notes_Variables.__init__(self, core, self)
        Prism_Notes_Functions.__init__(self, core, self)
