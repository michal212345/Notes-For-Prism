from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher # type: ignore
import PrismCore # type: ignore 

import NotesBrowser
import logging, os, json, shutil

logger = logging.getLogger(__name__)

class MarkdownTextEdit(QTextEdit):
   
    clearSignal = Signal()
    saveSignal = Signal()
    setTextSignal = Signal(str)
    
    text = ""
    rightClick = False
    
    def __init__(self ,parent=None):
        super().__init__(parent)
        
        self.installEventFilter(self)
        self.textChanged.connect(self.text_Changed)
        self.setReadOnly(True)

        self.clearSignal.connect(self.clearText)
        self.setTextSignal.connect(self.setText)

    def text_Changed(self):
        self.text = self.toPlainText()

    def eventFilter (self, source, event):
        if event.type() == QEvent.FocusOut:

            # Check if the focus out event was caused by a mouse button release
            if event.reason() == Qt.FocusReason.PopupFocusReason:
                return True
            
            # You have to block signals or it will trigger text_changed and mess with the text
            self.blockSignals(True)
            
            self.setMarkdown(self.text)
            self.setReadOnly(True)
            
            self.blockSignals(False)
            self.saveSignal.emit()
            
        if event.type() == QEvent.FocusIn:
            
            if event.reason() == Qt.FocusReason.PopupFocusReason:
                return True
            
            self.blockSignals(True)
            
            self.setPlainText(self.text)
            self.setReadOnly(False)
            
            self.blockSignals(False)

        # Pass the event to the base class
        return super().eventFilter(source, event)

    def setText(self, text:str):
        self.text = text
        
        self.blockSignals(True)
        
        self.setMarkdown(text)
        
        self.blockSignals(False)
        
        self.setReadOnly(False)

    def clearText(self):
        self.clear()


class Prism_Notes_Functions(QDialog,NotesBrowser.Ui_dlg_NotesBrowser):
    pb=None
    loaded_import=False
    
    w_entities = None

    current_note=''
    
    def __init__(self, core: PrismCore.PrismCore, plugin):
        
        self.core = core
        
        QDialog.__init__(self)
        self.setupUi(self)
        
        self.plugin = plugin
        
        self.initialized = False
        self.projectBrowser = getattr(self.core,"pb")
        
        # Blender refuses to delete the widget
        self.w_contents.setVisible(False)
        self.w_contents.deleteLater()
        
        self.w_contents = MarkdownTextEdit()
        self.w_contents.setObjectName(u"w_contents")
        self.verticalLayout.addWidget(self.w_contents)
        

        self.w_contents.saveSignal.connect(self.saveCurrentText)
        
    # if returns true, the plugin will be loaded by Prism
    def isActive(self): 
        self.core.registerCallback("onProjectBrowserShow", self.addSelf, plugin=self)

        return True
    
    def addSelf(self,*args):
        self.loadLayout()
        self.core.pb.addTab("Notes",self)
    
    def entered(self, prevTab=None, *args, **kwargs):
        if not self.initialized:
            self.w_entities.getPage("Assets").blockSignals(True)
            self.w_entities.getPage("Shots").blockSignals(True)
            self.w_entities.blockSignals(True)
            self.w_entities.refreshEntities(defaultSelection=False)
            self.w_entities.getPage("Assets").blockSignals(False)
            self.w_entities.getPage("Shots").blockSignals(False)
            self.w_entities.blockSignals(False)

            self.initialized = True

        if prevTab:
            if hasattr(prevTab, "w_entities"):
                self.w_entities.syncFromWidget(prevTab.w_entities)
            elif hasattr(prevTab, "getSelectedData"):
                self.w_entities.navigate(prevTab.getSelectedData())
                
        self.tw_identifier.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tw_identifier.customContextMenuRequested.connect(self.onCustomContextMenuRequested)
        
    def onCustomContextMenuRequested(self, pos):
        
        # Get the item at the position
        item = self.tw_identifier.itemAt(pos)

        # Create the context menu
        contextMenu = QMenu()

        if not item:
            addNoteAction = QAction("Add Note", self)
            addNoteAction.triggered.connect(self.addNote)
            contextMenu.addAction(addNoteAction)
        
            addPresetAction = QAction("Add Preset", self)
            addPresetAction.triggered.connect(self.addPreset)
            contextMenu.addAction(addPresetAction)
        
        if isinstance(item, QTreeWidgetItem):
            deleteNoteAction = QAction("Delete Note", self)
            deleteNoteAction.triggered.connect(lambda: self.deleteNote(item))
            contextMenu.addAction(deleteNoteAction)
            
            renameNoteAction = QAction("Rename Note", self)
            renameNoteAction.triggered.connect(lambda: self.renameNote(item))
            contextMenu.addAction(renameNoteAction)
            
            makePresetAction = QAction("Make Preset", self)
            makePresetAction.triggered.connect(lambda: self.makePreset(item))
            contextMenu.addAction(makePresetAction)
        
        contextMenu.exec_(self.tw_identifier.mapToGlobal(pos))
    
    def addPreset(self):
        
        def onAddPreset():
            name = new_name.text()
            path = os.path.join(self.getPathFromEntity(),"Notes")
            
            note_path:str = os.path.join(path,name+".md")
            
            if os.path.exists(note_path):
                self.core.popup("That note already exists!", "Warning.")
                return
            
            shutil.copyfile(os.path.join(Pipeline_path,"Notes","Presets",listWidget.currentItem().text()+".md"),note_path)
            
            baseJson = {
                "Name":name,
                "LastEdited":str(self.core.username),
                "Created":str(self.core.username)
            }
            
            with open(note_path.replace('.md','.json'), 'w') as f:
                json.dump(baseJson,f)
            
            try:
                entityType = self.getCurrentEntity()["type"]
            except KeyError:
                return
            
            #self.w_entities.navigate(None,True)
            self.entityChanged(entityType)
            
            newDialog.close()
        
        newDialog = QDialog()
        newDialog.setWindowTitle("Add Preset")
        
        layout = QVBoxLayout()
        newDialog.setLayout(layout)
        
        name_label = QLabel("Choose a preset")
        layout.addWidget(name_label)
        
        listWidget = QListWidget()
        layout.addWidget(listWidget)
        
        Pipeline_path = self.core.projects.getPipelineFolder()
        
        # List all files in notes preset folder
        presets = [f for f in os.listdir(os.path.join(Pipeline_path,"Notes","Presets")) if f.endswith(".md")]
        
        for preset in presets:
            item = QListWidgetItem()
            item.setText(preset.replace(".md",""))
            listWidget.addItem(item)
            
        new_name_label = QLabel("Enter a new name for the preset")
        layout.addWidget(new_name_label)
        
        new_name = QLineEdit()
        layout.addWidget(new_name)
        
        button = QPushButton("Add")
        button.clicked.connect(onAddPreset)
        layout.addWidget(button)
        
        newDialog.exec_()
        
    def makePreset(self, item:QTreeWidgetItem):
        name = item.text(0)
        path = os.path.join(self.getPathFromEntity(),"Notes")
        
        note_path = os.path.join(path,name+".md")
        
        with open(note_path,'r') as f:
            text = f.read()
        
        Pipeline_path = self.core.projects.getPipelineFolder()
        
        preset_path = os.path.join(Pipeline_path,"Notes","Presets")
        
        with open(os.path.join(preset_path,name+".md"),'w') as f:
            f.write(text)
        
        self.core.popup(f"Note '{name}' has been added as a preset.", "Success")
    
    def renameNote(self, item:QTreeWidgetItem):
        name = item.text(0)
        path = os.path.join(self.getPathFromEntity(),"Notes")
        
        old_note_path = os.path.join(path,name+".md")
        old_note_json = old_note_path.replace(".md",".json")
        
        newName, ok = QInputDialog.getText(self, 'Rename Note', 'Enter the new name of the note:')
        if not ok:
            return
        
        if os.path.exists(os.path.join(path,newName+".json")):
            self.core.popup("That note already exists!", "Warning.")
            return
        
        # Update the config with the last edited user & new name
        config = self.readConfig(old_note_json)
        config["Name"] = newName
        config["LastEdited"] = str(self.core.username)
        
        self.updateConfig(old_note_json,config)
        
        os.rename(old_note_path,os.path.join(path,newName+".md"))
        os.rename(old_note_json,os.path.join(path,newName+".json"))
        
        item.setText(0,newName)
        
        self.setCurrentText(newName,os.path.join(path,newName+".md"))
     
    def deleteNote(self, item:QTreeWidgetItem):
        name = item.text(0)
        path = self.getPathFromEntity()
        
        note_path = os.path.join(path,"Notes",name+".md")
        note_json = note_path.replace(".md",".json")
        
        if os.path.exists(note_path):
            os.remove(note_path)
        
        if os.path.exists(note_json):
            os.remove(note_json)
        
        self.tw_identifier.takeTopLevelItem(self.tw_identifier.indexOfTopLevelItem(item))
        
        self.clearSignal.emit()
        
    def addNote(self):
        # add item to self.tw_identifier
    
        # make a popup to get the name of the note
        name, ok = QInputDialog.getText(self, 'Add Note', 'Enter the name of the note:')
        if not ok:
            return
    
        item = QTreeWidgetItem()
        item.setText(0, name)
        self.tw_identifier.addTopLevelItem(item)
        
        path = self.getPathFromEntity()
        
        if not self.checkForNotes(path):
            self.createNotesPath(path)
        
        path = os.path.join(path, "Notes")
        
        if os.path.exists(file:=os.path.join(path,name+".json")):
            self.core.popup("That note already exists!", "Warning.")
            return
        
        baseJson = {
            "Name":name,
            "LastEdited":str(self.core.username),
            "Created":str(self.core.username)
        }
        
        with open(file, 'w') as f:
            json.dump(baseJson,f)
            
        if os.path.exists(file:=os.path.join(path,name+".md")):
            self.core.popup("That note already exists!", "Warning.")
        
        with open(file, '+w') as f:
            f.writelines(" ")
            
        self.setCurrentText(name,file)
       
    def closeEvent(self, event=None):
        self.closing.emit()

    def loadLayout(self):
        import EntityWidget # type: ignore

        if not self.w_entities:
        
            self.w_entities = EntityWidget.EntityWidget(core=self.core, refresh=False, mode="notes")
            self.splitter.insertWidget(0, self.w_entities)

            cData = self.core.getConfig()
            brsData = cData.get("browser", {})

            if "expandedAssets_" + self.core.projectName in brsData:
                self.aExpanded = brsData["expandedAssets_" + self.core.projectName]

            if "expandedSequences_" + self.core.projectName in brsData:
                self.sExpanded = brsData["expandedSequences_" + self.core.projectName]

            self.w_entities.getPage("Assets").setSearchVisible(
                brsData.get("showAssetSearch", False)
            )

            self.w_entities.getPage("Shots").setSearchVisible(brsData.get("showShotSearch", False))

            if "showSearchAlways" in brsData:
                self.w_entities.getPage("Assets").setShowSearchAlways(
                    brsData["showSearchAlways"]
                )
                self.w_entities.getPage("Shots").setShowSearchAlways(
                    brsData["showSearchAlways"]
                )

            if len(self.w_entities.getLocations()) > 1 or (self.projectBrowser and len(self.projectBrowser.locations) > 1):
                self.versionLabels.insert(3, "Location")

            self.setStyleSheet("QSplitter::handle{background-color: transparent}")
            
            preset_path = os.path.join(self.core.projects.getPipelineFolder(),"Notes")
            
            if not os.path.exists(preset_path):
                os.mkdir(preset_path)
                os.mkdir(os.path.join(preset_path,"Presets"))
        
        # Connect signals to shot/asset list
        self.w_entities.getPage("Assets").itemChanged.connect(lambda: self.entityChanged("asset"))
        self.w_entities.getPage("Shots").itemChanged.connect(lambda: self.entityChanged("shot"))
        self.w_entities.tabChanged.connect(self.onTabChanged)
        self.tw_identifier.itemClicked.connect(self.note_QTWItem)

    def readConfig(self,path:str):
        with open(path, 'r') as f:
            return json.load(f)

    def updateConfig(self,path:str,config:dict):
        with open(path, 'w') as f:
            json.dump(config,f)

    def checkForNotes(self, path):
        if os.path.exists(path):
            if os.path.exists(os.path.join(path,"Notes")):
                return True
            
        return False
                
    def createNotesPath(self,path):
        os.mkdir(os.path.join(path,"Notes"))

    def note_QTWItem(self, item:QTreeWidgetItem, column:int):
        name = item.text(column)
        try:
            path = self.getPathFromEntity()
        except KeyError:
            # I actually dont know why this happens 
            return
        
        self.setCurrentText(name,os.path.join(path,"Notes",name+".md"))

    def setCurrentText(self,name,note_path:str):
        self.w_contents.clearSignal.emit()
        
        self.current_note = name
        
        with open(note_path,'r') as f:
            self.w_contents.setTextSignal.emit( f.read() )
            
    # This code is very prone to errors and should be handled better
    def saveCurrentText(self):
        
        if self.current_note == '':
            return
        
        try:
            path = self.getPathFromEntity()
        except KeyError:
            # If keyError then there is no entity selected
            return
    
        # Get the path for the note
        note_path = os.path.join(path,"Notes",self.current_note+".md")
        
        # Get the config for the note
        config = self.readConfig(note_path.replace(".md",".json"))
        
        # Update the config with the last edited user
        config["LastEdited"] = str(self.core.username)
        
        self.updateConfig(note_path.replace(".md",".json"),config)
        
        with open(note_path,'w') as f:
            try:
                f.write(self.w_contents.text)
            except UnicodeEncodeError as e: # Had to add this incase of encoding errors EG Emojis :sob:
                self.core.popup(f"Error saving note: \n {e}", "Error")
                return

    def entityChanged(self, entityType):

        def create_notes_list(path):
            notes_list = []
            
            for item in os.listdir(path):
                if os.path.isfile(file:= os.path.join(path,item)):
                    noteInfo = None
                    if file.endswith(".json"):
                        noteInfo = self.readConfig(file)
                        
                        note = QTreeWidgetItem()
                        note.setText(0, noteInfo["Name"])
                        
                        notes_list.append(note)
            return notes_list

        entity = self.getCurrentEntity()

        if "type" not in entity:
            return
        
        self.tw_identifier.clear()
        self.w_contents.clearSignal.emit()
        
        if entityType == "asset":
                if entity["type"] == "assetFolder":
                    #TODO: Add support for notes in folders.
                    #ATM i dont think its necessary
                    return
                elif entity["type"] == "asset":
                    
                    # Get path for given 'asset'
                    path = self.getPathFromEntity()
                    
                    # Check if notes path exists in for the asset
                    if not self.checkForNotes(path):
                        self.createNotesPath(path)
                        # exit pre-emptively
                        return
                    else:
                        # Add it to the notes list
                        path = os.path.join(path,"Notes")
                else:
                    self.core.popup("This type is not supported.","Warning")
                        
        elif entityType == "shot":
            
            try:
                path = self.getPathFromEntity()
            except KeyError:
                # If you get a KeyError that means its a shot folder...
                return
                    
            if not self.checkForNotes(path):
                self.createNotesPath(path)
                return
            
            path = os.path.join(path,"Notes")
          
        self.tw_identifier.blockSignals(True)  
        for note in create_notes_list(path):
            self.tw_identifier.addTopLevelItem(note)
        self.tw_identifier.blockSignals(False)
    
    def onTabChanged(self):
        # Clear tw
        self.tw_identifier.clear()
        
        # Gets current page name from entity widget
        self.w_contents.clearSignal.emit()
        
        try:
            entityType = self.getCurrentEntity()["type"]
        except KeyError:
            return
        
        #self.w_entities.navigate(None,True)
        self.entityChanged(entityType)

    # Clean up paths given by Prism
    def getPathFromEntity(self):
        entity = self.getCurrentEntity()
        if entity["type"] == "asset":
            return entity["paths"][0]
        elif entity["type"] == "shot":
            # If prism dev ever reads this, please make the path for shots the more similar to assets
            return entity["paths"][0]["path"] 

    # This gets the first selected item from asset/shot list
    def getCurrentEntity(self) -> dict:
        return self.w_entities.getCurrentPage().getCurrentData()

    # This gets all selected items from asset/shot list
    def getCurrentEntities(self):
        return self.w_entities.getCurrentPage().getCurrentData(returnOne=False)

    # Add refreshUi code when pressing refresh
    # Without this it throws an error when pressing refresh
    def refreshUI(self, *args, **kwargs):
        pass

    # Has to stay? Without it an error is raised when prism closes
    # I think its related to saving data 
    def getSelectedContext(self, *args):
        pass