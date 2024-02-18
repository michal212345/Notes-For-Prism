import os


class Prism_Notes_Variables(object):
    def __init__(self, core, plugin):
        self.version = "v2.0.0.beta13"
        self.pluginName = "Notes"
        self.pluginType = "Custom"
        self.platforms = ["Windows", "Linux", "Darwin"]
        self.pluginDirectory = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
