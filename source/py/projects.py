# -*- coding: utf-8 -*-

#print('Projekte')
import traceback
import uno
import unohelper
import os
import sys
tb = traceback.print_exc

ZEILENHOEHE = 22



class Projekt():
    
    def __init__(self,mb,pydevBrk):
        
        global pd
        pd = pydevBrk
        
        self.dialog = mb.dialog
        self.ctx = mb.ctx
        self.mb = mb
        self.pd = pydevBrk
   
    def erzeuge_neues_Projekt(self):
        
        geglueckt,self.mb.projekt_name = self.dialog_neues_projekt_anlegen()  

        if geglueckt:
            self.setze_pfade()
            
            if self.mb.projekt_name == self.mb.doc.Title.split('.odt')[0]:
                n1 = 'Das Projekt soll den gleichen Namen wie das zur Zeit geoeffnete Dokument erhalten. Das funktioniert nicht.'
                self.mb.Mitteilungen.nachricht(n1,"warningbox")
                return
                # Wenn das Projekt schon existiert, Abfrage, ob Projekt �berschrieben werden soll
                # funktioniert das unter Linux?? ############
            elif os.path.exists(self.mb.pfade['projekt']):
                n2 = r'Das Projekt existiert schon. Soll es geloescht und ueberschrieben werden?'
                # 16777216 Flag f�r YES_NO
                entscheidung = self.mb.Mitteilungen.nachricht(n2,"warningbox",16777216)
                # 3 = Nein oder Cancel, 2 = Ja
                if entscheidung == 3:
                    return
                elif entscheidung == 2:
                    try:
                        import shutil
                        # entfernt das vorhandene Projekt
                        shutil.rmtree(self.mb.pfade['projekt'])
                    except:
                        # scheint trotz Fehlermeldung zu funktionieren win7 OO/LO
                        pass
                    
            #pd()
        
        if geglueckt:
            try:
                self.erzeuge_Settings_Datei()
                self.erzeuge_Ordner_Struktur()             
                self.mb.class_Bereiche.leere_Dokument()        
                self.mb.class_Hauptfeld.start()             
                Eintraege = self.beispieleintraege2()
                self.erzeuge_Projekt_xml_tree()
                self.erzeuge_Eintraege_und_Bereiche(Eintraege)
                  
                Path = self.mb.pfade['settings']  
                self.mb.xml_tree.write(Path + '/ElementTree.xml')
                self.mb.xml_tree_settings.write(Path +'/settings.xml' )
                # nach dem Path f�r andere Betriebssysteme schauen !!!!!!!!
            except:
                tb()

                        
    def setze_pfade(self): 
          
        paths = self.mb.smgr.createInstance( "com.sun.star.util.PathSettings" )
        pHome = paths.Work_writable
        if sys.platform == 'linux':
            os.chdir( '//')# + pHome.split('///')[1] ) 
        # und Windows ??????????
        retval = os.getcwd()
        print ("Current working directory %s" % retval)   
        
        pNavi = pHome+'/Organon'
        pOrganon = pNavi.split('///')[1] 
        
        pProjekt = pOrganon + '/%s.organon' % self.mb.projekt_name
        pFiles = pProjekt + '/Files'
        pOdts = pProjekt + '/Files/odt'
        pSettings = pProjekt + '/Settings'
        
        self.mb.pfade.update({'home':pHome}) 
        self.mb.pfade.update({'projekt':pProjekt})      
        self.mb.pfade.update({'organon':pOrganon})
        self.mb.pfade.update({'files':pFiles})
        self.mb.pfade.update({'odts':pOdts})
        self.mb.pfade.update({'settings':pSettings})  
               
    def erzeuge_Ordner_Struktur(self):
        try:
            
            pfade = self.mb.pfade
            # Organon
            if not os.path.exists(pfade['organon']):
                os.makedirs(pfade['organon'])
            # Organon/<Projekt Name>
            if not os.path.exists(pfade['projekt']):
                os.makedirs(pfade['projekt'])
            # Organon/<Projekt Name>/Files
            if not os.path.exists(pfade['files']):
                os.makedirs(pfade['files'])
            # Organon/<Projekt Name>/Files
            if not os.path.exists(pfade['odts']):
                os.makedirs(pfade['odts'])   
            # Organon/<Projekt Name>/Settings
            if not os.path.exists(pfade['settings']):
                os.makedirs(pfade['settings'])
                 
            # Datei anlegen, die bei lade_Projekt angesprochen werden soll
            with open(pfade['projekt']+"/%s.organon" % self.mb.projekt_name, "w") as file:
                file.write('Dies ist eine Organon Datei. Goennen Sie ihr ihre Existenz.') 
                 
            # Setzen einer UserDefinedProperty um Projekt identifizieren zu k�nnen
            UD_properties = self.mb.doc.DocumentProperties.UserDefinedProperties
            has_prop = UD_properties.PropertySetInfo.hasPropertyByName('ProjektName')
            if has_prop:
                UD_properties.setPropertyValue('ProjektName',self.mb.projekt_name) 
            else:
                UD_properties.addProperty('ProjektName',1,self.mb.projekt_name) 
                     
            # damit von den Bereichen in die Datei verlinkt wird, muss sie gespeichert werden   
            Path = 'file:///'+self.mb.pfade['odts']+'/%s.odt' % self.mb.projekt_name
            self.mb.doc.storeAsURL(Path,())   
            #pd() 
        except:
            tb()
        #pd()
                       
    def dialog_neues_projekt_anlegen(self):
        
        Attr = (25,22,300,20,'zweiter_cont')    
        PosX,PosY,Width,Height,Name = Attr
        control, model = createControl(self.ctx,"FixedText",PosX,PosY,Width,Height,(),() )  
        model.Label = "Geben Sie einen Namen fuer das neue Projekt ein:"
            
        Attr = (25,50,250,20,'zweiter_cont')    
        PosX,PosY,Width,Height,Name = Attr   
        control1, model1 = createControl(self.ctx,"Edit",PosX,PosY,Width,Height,(),() ) 
        
        listener = neues_Projekt_Dialog_Listener(model1) 
        control1.addKeyListener(listener) 
        #pd()
        Attr = (50,100,80,30,'btn')    
        PosX,PosY,Width,Height,Name = Attr   
        control2, model2 = createControl(self.ctx,"Button",PosX,PosY,Width,Height,(),() )  
        model2.Label = 'OK'
        control2.addActionListener(listener) 
        control2.setActionCommand("OK")
        
        Attr = (150,100,80,30,'btn2')    
        PosX,PosY,Width,Height,Name = Attr   
        control3, model3 = createControl(self.ctx,"Button",PosX,PosY,Width,Height,(),() )  
        model3.Label = 'Abbrechen'
        control3.addActionListener(listener) 
        control3.setActionCommand("Abbruch")
        
            
        smgr = self.ctx.getServiceManager()
        
        # create the dialog model and set the properties
        dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", self.ctx)
           
        dialogModel.PositionX = 65
        dialogModel.PositionY = 65
        dialogModel.Width = 165
        dialogModel.Height = 100
        dialogModel.Title = "neues Projekt anlegen"
           
                  
        # create the dialog control and set the model
        controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", self.ctx);
        controlContainer.setModel(dialogModel);
                 
        # create a peer
        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", self.ctx);       
        controlContainer.setVisible(False);       
        controlContainer.createPeer(toolkit, None);
        
        controlContainer.addControl('text',control)
        controlContainer.addControl('name',control1)
        controlContainer.addControl('button',control2)
        controlContainer.addControl('button2',control3)
        
        controlContainer.addTopWindowListener(listener)
    
        geglueckt = controlContainer.execute()       
        controlContainer.dispose() 

        return geglueckt,model1.Text

# ===============================================================================================================  


    def lade_Projekt(self,filepicker = True):
        if self.mb.debug: print(self.mb.debug_time(),'lade_Projekt')
       
        # fehlt: wenn bereits ein Projekt geladen wurde, st�rzt oOO ab
        # daher: alles entfernen !!
        #self.mb.current_Contr.removeSelectionChangeListener(self.mb.VC_selection_listener)                  
        
        if filepicker:
            Filepicker = createUnoService("com.sun.star.ui.dialogs.FilePicker")
            Filepicker.execute()
            # see: https://wiki.openoffice.org/wiki/Documentation/DevGuide/Basic/File_Control

            if Filepicker.Files == '':
                return
            
            filepath = Filepicker.Files[0]
            # Wenn keine .organon Datei gew�hlt wurde
            if filepath.split('/')[-1].split('.')[1]  != 'organon':
                return
            
            self.mb.projekt_name = filepath.split('/')[-1].split('.')[0]       
#         pd()
#         # pr�ft, ob eine Organon Datei geladen ist
#         UD_properties = self.mb.doc.DocumentProperties.UserDefinedProperties
#         has_prop = UD_properties.PropertySetInfo.hasPropertyByName('ProjektName')
# 
#         if has_prop:
#             dialog_contr = self.mb.dialog.Controls
#             for contr in dialog_contr:
#                 contr.dispose()
#             pd()
        #pd()
        
        self.setze_pfade()
        self.mb.class_Bereiche.leere_Dokument() 
        self.lese_xml_settings_datei()       
        self.mb.class_Hauptfeld.erzeuge_Navigations_Hauptfeld() 
        self.mb.class_Hauptfeld.erzeuge_Scrollbar(self.mb.dialog,self.mb.ctx)       
        Eintraege = self.lese_xml_datei()
        self.erzeuge_Eintraege_und_Bereiche2(Eintraege) 
        
        # setzt die selektierte Zeile auf die erste Zeile
        self.mb.selektierte_zeile = self.mb.Hauptfeld.getByIdentifier(0).AccessibleContext
        self.mb.class_Zeilen_Listener.schalte_sichtbarkeit_der_Bereiche()
        
        

        # Wenn die UDProp verloren gegangen sein sollte, wieder setzen
        UD_properties = self.mb.doc.DocumentProperties.UserDefinedProperties
        has_prop = UD_properties.PropertySetInfo.hasPropertyByName('ProjektName')
        if not has_prop:
            UD_properties.addProperty('ProjektName',1,self.mb.projekt_name) 
        
        # damit von den Bereichen in die Datei verlinkt wird, muss sie gespeichert werden   
        Path = 'file:///'+self.mb.pfade['odts']+'/%s.odt' % self.mb.projekt_name
        self.mb.doc.storeAsURL(Path,()) 
        

    def speicher_Projekt(self):
 
        TS = self.mb.doc.TextSections
        total = len(TS.ElementNames)
        
        print('speichere ...')
        CB = self.mb.class_Bereiche

        # entferne Listener
        self.mb.dialog.removeWindowListener(self.mb.w_listener)
        self.mb.current_Contr.removeSelectionChangeListener(self.mb.VC_selection_listener)  
        
        StatusIndicator = self.mb.desktop.getCurrentFrame().createStatusIndicator()
        StatusIndicator.start('speichere Dokument, bitte warten!',total)

        # speichere gesamtes Dokument 
        Path = 'file:///'+self.mb.pfade['odts']+'/gesamtes_Dokument.odt'
        self.mb.doc.storeToURL(Path,())                
               
        prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        prop.Name = 'Hidden'
        prop.Value = True      

        newDoc = self.mb.doc.CurrentController.Frame.loadComponentFromURL("private:factory/swriter","_blank",0,(prop,))
        cur = newDoc.Text.createTextCursor()
        
        SFLink = uno.createUnoStruct("com.sun.star.text.SectionFileLink")
        SFLink.FileURL = Path
        
        #pd()
        zaehler = 1

       
        for i in range(TS.Count):
            
            sec = TS.getByIndex(i)
            
            # alle anderen Textsections ausschliessen
            # todo: auch in allen anderen Bereichen ausschliessen
            if 'OrganonSec' in sec.Name:
                
                try:
                    # alle 5 Dateien den Status Indicator erneuern
                    if zaehler%5 == 0:
                        newDoc.close(False)
                        StatusIndicator.setValue(zaehler)
                        StatusIndicator.setText(' Dateien gespeichert: %s von %s ' % (zaehler,total))
                        newDoc = self.mb.doc.CurrentController.Frame.loadComponentFromURL("private:factory/swriter","_blank",0,(prop,))
                        cur = newDoc.Text.createTextCursor()
                except:
                    pass
                       
                newSection = self.mb.doc.createInstance("com.sun.star.text.TextSection")
                newSection.setPropertyValue('FileLink',SFLink)
                newSection.setName(sec.Name)
                newSection.setPropertyValue("LinkRegion",sec.Name)
                               
                cur.gotoStart(False)
                cur.gotoEnd(True)
                # insert und remove bewirken Einf�gen und Entfernen der Section
                # der eingef�gte Inhalt aber bleibt
                newDoc.Text.insertTextContent(cur, newSection, True)
                newDoc.Text.removeTextContent(newSection)
                
                dateiname = self.mb.dict_bereiche['Bereichsname-ordinal'][sec.Name]
                Path2 = 'file:///'+self.mb.pfade['odts']+'/%s.odt' % dateiname
                newDoc.storeToURL(Path2,())

                zaehler += 1
        
        
        newDoc.close(False)
        StatusIndicator.end()
        # xml speichern
        Path = self.mb.pfade['settings'] + '/ElementTree.xml' 
        self.mb.xml_tree.write(Path)
        # Listener wieder aktivieren
        self.mb.dialog.addWindowListener(self.mb.w_listener)
        self.mb.current_Contr.addSelectionChangeListener(self.mb.VC_selection_listener)                  
            
      
    def erzeuge_Projekt_xml_tree(self):
        if self.mb.debug: print(self.mb.debug_time(),'erzeuge_Projekt_xml_tree')
        
        et = self.mb.ET       
        root = et.Element(self.mb.projekt_name)
        tree = et.ElementTree(root)
        self.mb.xml_tree = tree
        root.attrib['Name'] = 'root'
        
    def erzeuge_Settings_Datei(self):
        if self.mb.debug: print(self.mb.debug_time(),'erzeuge_Settings_Datei')
        
        et = self.mb.ET       
        root = et.Element('Settings')
        tree = et.ElementTree(root)
         
        et.SubElement(root,'tag1',sichtbar='ja')
        et.SubElement(root,'tag2',sichtbar='nein')
        et.SubElement(root,'tag3',sichtbar='nein')
        
        self.mb.tag1_visible = True
        self.mb.tag2_visible = False
        self.mb.tag3_visible = False
        
        self.mb.xml_tree_settings = tree
        
        
                       
    def erzeuge_Eintraege_und_Bereiche(self,Eintraege):
        if self.mb.debug: print(self.mb.debug_time(),'erzeuge_Eintraege_und_Bereiche')
        CB = self.mb.class_Bereiche
        CB.leere_Dokument()    ################################  rausnehmen
        CB.starte_oOO()
        
        Bereichsname_dict = {}
        ordinal_dict = {}
        Bereichsname_ord_dict = {}
        index = 0
        index2 = 0 
        for eintrag in Eintraege:
            # Navigation
            ordinal,parent,name,lvl,art,zustand,sicht,tag1,tag2,tag2 = eintrag   
                     
            index = self.mb.class_Hauptfeld.erzeuge_Verzeichniseintrag(eintrag,self.mb.class_Zeilen_Listener,index)
            self.mb.class_XML.erzeuge_XML_Eintrag(eintrag)  

            if sicht == 'ja':
                # index wird in erzeuge_Verzeichniseintrag bereits erh�ht, daher hier 1 abziehen
                self.mb.dict_zeilen_posY.update({(index-1)*ZEILENHOEHE:eintrag})
                self.mb.sichtbare_bereiche.append('OrganonSec'+str(index2))
                
            # Bereiche   
            inhalt = name
            path = CB.erzeuge_neue_Datei(index2,inhalt)
            CB.erzeuge_bereich(index2,path,sicht)            

            Bereichsname_dict.update({'OrganonSec'+str(index2):path})
            ordinal_dict.update({ordinal:'OrganonSec'+str(index2)})
            Bereichsname_ord_dict.update({'OrganonSec'+str(index2):ordinal})
            
            index2 += 1
        
        self.mb.dict_bereiche.update({'Bereichsname':Bereichsname_dict})
        self.mb.dict_bereiche.update({'ordinal':ordinal_dict})
        self.mb.dict_bereiche.update({'Bereichsname-ordinal':Bereichsname_ord_dict})

        CB.loesche_leeren_Textbereich_am_Ende()  
        self.mb.current_Contr.addSelectionChangeListener(self.mb.VC_selection_listener) 
        CB.schliesse_oOO()
        self.erzeuge_dict_ordner()


    def erzeuge_Eintraege_und_Bereiche2(self,Eintraege):
        if self.mb.debug: print(self.mb.debug_time(),'erzeuge_Eintraege_und_Bereiche2')

        CB = self.mb.class_Bereiche
        CB.leere_Dokument()    ################################  rausnehmen
        #CB.starte_oOO()
        
        self.erzeuge_dict_ordner()
        
        Bereichsname_dict = {}
        ordinal_dict = {}
        Bereichsname_ord_dict = {}
        index = 0
        index2 = 0 
        
        first_time = True
        
        for eintrag in Eintraege:
            # Navigation
            ordinal,parent,name,lvl,art,zustand,sicht,tag1,tag2,tag3 = eintrag   
                     
            index = self.mb.class_Hauptfeld.erzeuge_Verzeichniseintrag(eintrag,self.mb.class_Zeilen_Listener,index)
            
            if sicht == 'ja':
                # index wird in erzeuge_Verzeichniseintrag bereits erh�ht, daher hier 1 abziehen
                self.mb.dict_zeilen_posY.update({(index-1)*ZEILENHOEHE:eintrag})
                self.mb.sichtbare_bereiche.append('OrganonSec'+str(index2))
                
            # Bereiche   
            path = 'file:///' + self.mb.pfade['odts'] + '/%s.odt' % ordinal
            CB.erzeuge_bereich(index2,path,sicht) 
            
            if first_time:       
                # Viewcursor an den Anfang setzen, damit 
                # der Eindruck eines schnell geladenen Dokuments entsteht   
                self.mb.viewcursor.gotoStart(False)
                first_time = False
            
            Bereichsname_dict.update({'OrganonSec'+str(index2):path})
            ordinal_dict.update({ordinal:'OrganonSec'+str(index2)})
            Bereichsname_ord_dict.update({'OrganonSec'+str(index2):ordinal})
            
            index2 += 1

        self.mb.dict_bereiche.update({'Bereichsname':Bereichsname_dict})
        self.mb.dict_bereiche.update({'ordinal':ordinal_dict})
        self.mb.dict_bereiche.update({'Bereichsname-ordinal':Bereichsname_ord_dict})
        
         
        CB.loesche_leeren_Textbereich_am_Ende() 
       
        self.mb.current_Contr.addSelectionChangeListener(self.mb.VC_selection_listener) 
        #CB.schliesse_oOO()
        
    
                   
    def erzeuge_dict_ordner(self):
        if self.mb.debug: print(self.mb.debug_time(),'erzeuge_dict_ordner')

        tree = self.mb.xml_tree
        root = tree.getroot()
        
        ordner = []
        self.mb.dict_ordner = {}
        
        alle_eintraege = root.findall('.//')
        
        
        ### Vielleicht gibt es eine M�glichkeit, den Baum nur einmal zu durchlaufen?
        ### Statt 1) Baum komplett durchlaufen 2) jeden Eintrag nochmals rekursiv durchlaufen
        ### Ziel: einmal durchlaufen und jedes Kind bei allen Elternelementen eintragen
        
        # Liste aller Ordner erstellen
        for eintrag in alle_eintraege:
            if eintrag.attrib['Art'] in ('dir','waste'):
                ordner.append(eintrag.tag)
        
        
        def get_tree_info(elem, dict,tag,helfer):
            helfer.append(elem.tag)
            # hier wird self.mb.dict_ordner geschrieben
            dict[tag] = helfer
            if elem.attrib['Zustand'] == 'auf':
                for child in list(elem):
                    get_tree_info(child, dict,tag,helfer)
        
        
        # F�r alle Ordner eine Liste ihrer Kinder erstellen -> self.mb.dict_ordner       
        for tag in ordner:
            dir = root.find('.//'+tag)
            helfer = []
            get_tree_info(dir,self.mb.dict_ordner,tag,helfer)


    def lese_xml_datei(self):
        if self.mb.debug: print(self.mb.debug_time(),'lese_xml_datei')

        pfad = self.mb.pfade['settings'] + '/ElementTree.xml'        
        self.mb.xml_tree = self.mb.ET.parse(pfad)
        root = self.mb.xml_tree.getroot()
        
        self.mb.kommender_Eintrag = int(root.attrib['kommender_Eintrag'])
        
        Elements = root.findall('.//')       
        Eintraege = []
        
        for elem in Elements:
             
            ordinal = elem.tag
            parent  = elem.attrib['Parent']
            name    = elem.attrib['Name']
            art     = elem.attrib['Art']
            lvl     = elem.attrib['Lvl'] 
            zustand = elem.attrib['Zustand'] 
            sicht   = elem.attrib['Sicht'] 
            tag1   = elem.attrib['Tag1'] 
            tag2   = elem.attrib['Tag2'] 
            tag3   = elem.attrib['Tag3'] 
            
            Eintraege.append((ordinal,parent,name,lvl,art,zustand,sicht,tag1,tag2,tag3))
            
        return Eintraege
    
    
    def lese_xml_settings_datei(self):
        if self.mb.debug: print(self.mb.debug_time(),'lese_xml_settings_datei')
        
        pfad = self.mb.pfade['settings'] + '/settings.xml'        
        self.mb.xml_tree_settings = self.mb.ET.parse(pfad)
        root = self.mb.xml_tree_settings.getroot()
      
        self.mb.tag1_visible = (root.find(".//tag1").attrib['sichtbar'] == 'ja')
        self.mb.tag2_visible = (root.find(".//tag2").attrib['sichtbar'] == 'ja')
        self.mb.tag3_visible = (root.find(".//tag3").attrib['sichtbar'] == 'ja')
    
        
        
       
        
    def beispieleintraege(self):
        
        Eintraege = [('nr0','root','Vorbemerkung',0,'pg','-','ja'),
                ('nr1','root','Projekt',0,'dir','auf','ja'),
                ('nr2','nr1','Titelseite',1,'pg','-','ja'),
                ('nr3','nr1','Kapitel1',1,'dir','auf','ja'),
                ('nr4','nr3','Szene1',2,'pg','-','ja'),
                ('nr5','nr3','Szene2',2,'pg','-','ja'),
                ('nr6','nr1','Kapitel2',1,'dir','auf','ja'),
                ('nr7','nr6','Szene1b',2,'pg','-','ja'),
                ('nr8','nr6','Szene2b',2,'pg','-','ja'),
                ('nr9','nr1','Interlude',1,'pg','-','ja'),
                ('nr10','nr1','Kapitel3',1,'dir','auf','ja'),
                ('nr11','nr1','Kapitel4',1,'dir','auf','ja'),
                ('nr12','nr11','UnterKapitel',2,'dir','zu','ja'),
                ('nr13','nr12','Szene3a',3,'pg','-','nein'),
                ('nr14','nr12','Szene3b',3,'pg','-','nein'),
                ('nr15','nr11','Szene3c',2,'pg','-','ja'),
                ('nr16','nr11','Szene3d',2,'pg','-','ja'),
                ('nr17','nr11','Kapitel4a',2,'dir','auf','ja'),
                ('nr18','nr1','Kapitel4b',1,'dir','auf','ja'),
                ('nr19','nr18','Szene4',2,'pg','-','ja'),
                ('nr20','root','Papierkorb',0,'waste','zu','ja')]
        
        return Eintraege

    def beispieleintraege2(self):
            
            Eintraege = [('nr0','root','Vorbemerkung',0,'pg','-','ja','leer','leer','leer'),
                    ('nr1','root','Projekt',0,'dir','auf','ja','leer','leer','leer'),
                    ('nr2','nr1','Titelseite',1,'pg','-','ja','leer','leer','leer'),
                    ('nr3','nr1','Kapitel1',1,'dir','auf','ja','leer','leer','leer'),
                    ('nr4','nr3','Szene1',2,'pg','-','ja','leer','leer','leer'),
                    ('nr5','nr3','Szene2',2,'pg','-','ja','leer','leer','leer'),
#                     ('nr6','nr1','Kapitel2',1,'dir','auf','ja'),
#                     ('nr7','nr6','Szene1b',2,'pg','-','ja'),
#                     ('nr8','nr6','Szene2b',2,'pg','-','ja'),
#                     ('nr9','nr1','Interlude',1,'pg','-','ja'),
#                     ('nr10','nr1','Kapitel3',1,'dir','auf','ja'),
#                     ('nr11','nr1','Kapitel4',1,'dir','auf','ja'),
#                     ('nr12','nr11','UnterKapitel',2,'dir','zu','ja'),
#                     ('nr13','nr12','Szene3a',3,'pg','-','nein'),
#                     ('nr14','nr12','Szene3b',3,'pg','-','nein'),
#                     ('nr15','nr11','Szene3c',2,'pg','-','ja'),
#                     ('nr16','nr11','Szene3d',2,'pg','-','ja'),
#                     ('nr17','nr11','Kapitel4a',2,'dir','auf','ja'),
#                     ('nr18','nr1','Kapitel4b',1,'dir','auf','ja'),
#                     ('nr19','nr18','Szene4',2,'pg','-','ja'),
                    ('nr6','root','Papierkorb',0,'waste','zu','ja','leer','leer','leer')]
            
            return Eintraege
        
    def test(self):
        print('test')
        try:
            
            pydevBrk()
        except:
            tb()




from com.sun.star.beans import XPropertyChangeListener
class VC_TextSection_Listener(unohelper.Base,XPropertyChangeListener): 
    def __init__(self,mb):
        self.mb = mb
        print('init vc')

    def propertyChange(self,ev):
        print(ev)




from com.sun.star.awt import XActionListener,XTopWindowListener,XKeyListener
from com.sun.star.awt.Key import RETURN
class neues_Projekt_Dialog_Listener(unohelper.Base,XActionListener,XTopWindowListener,XKeyListener): 
    def __init__(self,model):
        self.model = model

    def actionPerformed(self,ev):
        parent = ev.Source.AccessibleContext.AccessibleParent 
        cmd = ev.ActionCommand        
        if cmd == 'OK':
            parent.endDialog(1)
        if cmd == 'Abbruch':
            parent.endDialog(0)
               
    def windowClosed(self,ev):
        pass
            
    def keyPressed(self,ev):
        if ev.KeyCode == RETURN:
            parent = ev.Source.AccessibleContext.AccessibleParent 
            if self.model.Text == '':
                parent.endDialog(0)
            else:
                parent.endDialog(1)




from com.sun.star.task import XStatusIndicatorFactory
class Status_Indicator(unohelper.Base, XStatusIndicatorFactory):
    
    def createStatusIndicator(self):
        return self





        
        
        
        
################ TOOLS ################################################################

# Handy function provided by hanya (from the OOo forums) to create a control, model.
def createControl(ctx,type,x,y,width,height,names,values):
   smgr = ctx.getServiceManager()
   ctrl = smgr.createInstanceWithContext("com.sun.star.awt.UnoControl%s" % type,ctx)
   ctrl_model = smgr.createInstanceWithContext("com.sun.star.awt.UnoControl%sModel" % type,ctx)
   ctrl_model.setPropertyValues(names,values)
   ctrl.setModel(ctrl_model)
   ctrl.setPosSize(x,y,width,height,15)
   return (ctrl, ctrl_model)


def createUnoService(serviceName):
  sm = uno.getComponentContext().ServiceManager
  return sm.createInstanceWithContext(serviceName, uno.getComponentContext())





### get user data

# 
# def getOOoSetupNode(sNodePath):
#     prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
#     aConfigProvider = createUnoService("com.sun.star.configuration.ConfigurationProvider")
#     prop.Name = "nodepath"
#     prop.Value = sNodePath
#     return aConfigProvider.createInstanceWithArguments("com.sun.star.configuration.ConfigurationAccess", (prop,))
#     
#     setup = getOOoSetupNode("org.openoffice.UserProfile/Data")
                   

