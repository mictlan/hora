import rhythmdb, rb
import gobject, gtk
import time
import shutil
import gst
import thread
import gconf
import string

from HoraConfigureDialog import HoraConfigureDialog
#from HoraSource import HoraSource

gconf_keys = {	'offset' : '/apps/rhythmbox/plugins/hora/offset',
		'button' : '/apps/rhythmbox/plugins/hora/button' }

audio_file = "hora.spx"

class HoraPlugin(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)

	def activate(self, shell):

		self.shell = shell    
		print "activating Hora python plugin"
	        self.db = shell.get_property("db")
		
		
		print "register entry type"
		
		if hasattr(self.db, 'entry_register_type'):
			self.entry_type = self.db.entry_register_type("HoraEntryType")
		else:
			self.entry_type = HoraEntryType()
			self.db.register_entry_type(self.entry_type)
			 
		group = rb.rb_source_group_get_by_name("shared")
		self.source = gobject.new (HoraSource,
                    shell=self.shell,
                    entry_type=self.entry_type,
                    source_group=group,
                    plugin=self,
                    name=_("Hora"))
		
		self.shell.register_entry_type_for_source(self.source, self.entry_type)
        	self.shell.append_source (self.source, None)
		self.entry_type.get_playback_uri = self.hora_get_playback_uri
	        
		print "loading icon and button"
       		icon_file_name = self.find_file("hora.svg")
        	iconsource = gtk.IconSource()
        	iconsource.set_filename(icon_file_name)
        	iconset = gtk.IconSet()
        	iconset.add_source(iconsource)
        	iconfactory = gtk.IconFactory()
        	iconfactory.add("hora-button", iconset)
        	iconfactory.add_default()

		action = gtk.Action ('Hora', 
                     _('Hora'), 
                     _('Que hora Es?'),
                     "hora-button")
		action.connect('activate', self.hora, shell)
		self.action_group = gtk.ActionGroup('HoraActionGroup')
		self.action_group.add_action(action)
		ui_manager = shell.get_ui_manager()
		ui_manager.insert_action_group(self.action_group, 0)
		self.UI_ID = ui_manager.add_ui_from_string(ui_str)
		ui_manager.ensure_update()

		# add hora.spx
		fpath =  self.find_file(audio_file)
		self.uri = fpath
		gconf.client_get_default().set_string(gconf_keys['button'], "Agregar a la Cola")
		gconf.client_get_default().set_string(gconf_keys['offset'], "0")

		#self.gconf.set_string(gconf_keys['button'], "not queue")
		load_uri = "file://"+ self.uri

		entry = self.db.entry_lookup_by_location(self.uri)
         	if entry == None:
			print "add entry: "+ load_uri				
                	entry = self.db.entry_new(self.entry_type, load_uri)
			
			self.db.set(entry, rhythmdb.PROP_TITLE, "Didza Lube")
			self.db.set(entry, rhythmdb.PROP_ALBUM, "HORA")
		        self.db.set(entry, rhythmdb.PROP_ARTIST, "Radio Yaxhil")

	def create_configure_dialog(self, dialog=None):
	        if not dialog:
            		builder_file = self.find_file("hora-prefs.ui")
            		dialog = HoraConfigureDialog (builder_file).get_dialog()
        	dialog.present()
        	return dialog

	def deactivate(self, shell):
		print "deactivating Hora python plugin"
	        ui_manager = shell.get_ui_manager()
        	ui_manager.remove_ui(self.UI_ID)
        	ui_manager.remove_action_group(self.action_group)
        	self.action_group = None
        	ui_manager.ensure_update()
		self.db.entry_delete_by_type(self.entry_type)
        	self.db.commit()
        	self.db = None
        	self.entry_type = None
		self.source.delete_thyself()
        	self.source = None
		del self.shell
		del self.UI_ID
		del self.uri
		print "unset gconf keys"
		gconf.client_get_default().unset(gconf_keys['offset'])
		gconf.client_get_default().unset(gconf_keys['button'])


	def hora(self, event, shell):
		load_uri = "file://"+ self.uri
		button = gconf.client_get_default().get_string(gconf_keys['button'])
		#button = gconf.get_string(gconf_keys['button'])
	        if button == "Agregar a la Cola":		
			# list of queue
			print "queue selected in button configuration"
			Q_LIST = []
			queue = shell.props.queue_source
			for treerow in queue.props.base_query_model:
				entry, path = list(treerow)
				type_hora = self.entry_type
			        type_this = entry.get_entry_type()
        			if type_this == type_hora:
					id=self.db.entry_get(entry, rhythmdb.PROP_ENTRY_ID)
					Q_LIST.append(int(id))
					#Q_LIST.append(shell.props.db.entry_get(entry, rhythmdb.PROP_LOCATION))
			if not len(Q_LIST) == 0:
				my_file =  string.split(self.uri, "/")[-1:][0]
				print my_file, Q_LIST
				base, ext = string.split(my_file, ".")
				path = string.split(self.uri, 'hora')[0]
				uri = path+ "hora/"+ base+ str(len(Q_LIST))+ "."+ ext
				entry = self.db.entry_lookup_by_location(uri)
				load_uri = "file://"+ uri
				#print "add to queue:", load_uri
            			if entry == None:
					print "add new entry"				
                			entry = self.db.entry_new(self.entry_type, load_uri)
			print "add to queue: ", load_uri
			shell.add_to_queue(load_uri)
			
		else:
			print "direct play selected in button configuration"
			self.build_audio_file(self.uri)
			shell.props.shell_player.pause()
			speaker = gst.element_factory_make("playbin2")
			speaker.set_property('uri', load_uri)
			speaker.set_state(gst.STATE_PLAYING)
			shell.props.shell_player.play()
			time.sleep(4)		
			speaker.set_state(gst.STATE_NULL)

	def hora_get_playback_uri(self, entry):
		#url = "file://"+ self.uri
		url = self.shell.props.db.entry_get(entry, rhythmdb.PROP_LOCATION)
		url =  string.split(url, "file://")[1]
		print url
		self.build_audio_file(url)
		url = "file://"+ url
		return url
		
	def build_audio_file(self, url):
		"""build audio file from time library"""
		print "build "+ url
		HRS = str(time.localtime().tm_hour)
		#offset from system time
		offset = gconf.client_get_default().get_string(gconf_keys['offset'])
        	if offset != "0":
			if HRS == "0":
				HRS = "12"
            			HRS = int(HRS) + int(offset)
		HRS = str(HRS)
		if len(HRS) == 1:
			HRS = "0"+ HRS
		MIN = str(time.localtime().tm_min)
        	# MIN = "0" # to test MIN = 00
		if len(MIN) == 1:
			MIN = "0"+ MIN
		if MIN == "00":
			print "Es la "+ HRS+ " en punto"
			HRS = HRS+ "_0"
			print "out file: "+ url
			dest = open(url,'wb')
			print dest
			HRS_STR = "/audio/HRS"+ HRS+ ".spx"
			print HRS_STR
			fhour = self.find_file(HRS_STR)

			# copy file should be done with gst
			#print "copy %s  to %s" % (fhour, dest)
			shutil.copyfileobj(open(fhour,'rb'), dest)
			dest.close()

		#build audio file
		else:
			print "son las: %s:%s" % (HRS, MIN)
			MIN_STR = "/audio/MIN"+ MIN+ ".spx"
			fmin = self.find_file(MIN_STR)
			print "out file: "+ url
			dest = open(url,'wb')
			print dest
			HRS_STR = "/audio/HRS"+ HRS+ ".spx"
			print HRS_STR
			fhour = self.find_file(HRS_STR)

			# copy file should be done with gst
			#print "copy %s  to %s" % (fhour, dest)
			shutil.copyfileobj(open(fhour,'rb'), dest)
			#print "copy %s  to %s" % (fmin, dest)
			shutil.copyfileobj(open(fmin,'rb'), dest)
			dest.close()

		return

class HoraEntryType(rhythmdb.EntryType):
    def __init__(self):
        rhythmdb.EntryType.__init__(self, name='hora-entry-type')

class HoraSource(rb.BrowserSource):
    def __init__(self):
        rb.BrowserSource.__init__(self)
gobject.type_register(HoraSource)

ui_str = \
"""<ui> 
  <menubar name="MenuBar"> 
    <menu name="ControlMenu" action="Control"> 
	  <placeholder name="PluginPlaceholder">
		<menuitem name="Hora" action="Hora"/>
	  </placeholder>
    </menu>
  </menubar>
  <toolbar name="ToolBar">
	  <placeholder name="PluginPlaceholder">
		<toolitem name="Hora" action="Hora"/>
	  </placeholder>
  </toolbar>
</ui>"""
