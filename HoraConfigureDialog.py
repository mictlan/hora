# -*- coding: utf-8 -*-

# HoraConfigureDialog.py
#
# Copyright (C) 2011 - Kevin Brown
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gobject
import gtk
import gconf

gconf_keys = {	'offset' : '/apps/rhythmbox/plugins/hora/offset', 
		'button' : '/apps/rhythmbox/plugins/hora/button' }


class HoraConfigureDialog (object):
	def __init__(self, builder_file):
		self.gconf = gconf.client_get_default()

		builder = gtk.Builder()
		builder.add_from_file(builder_file)

		self.dialog = builder.get_object('preferences_dialog')
		self.offset_combobox = builder.get_object("offset_combobox")
		self.button_combobox = builder.get_object("button_combobox")

		offset = self.gconf.get_string(gconf_keys['offset'])
		button = self.gconf.get_string(gconf_keys['button'])
		#if not offset or offset == "0":
			#index = 1
		#try:
			#format = format_list.index(format_text)
		#except ValueError:
			#format = 0
		if offset == "-1":
			index = 0
		elif offset == "1":
			index = 2
		else:
			index = 1
		if button == "Agregar a la Cola":
			b_index = 1
		else:
			b_index = 0
		# offset combobox
		self.offset_combobox.set_active(index)
		self.dialog.connect("response", self.dialog_response)
		self.offset_combobox.connect("changed", self.offset_combobox_changed)
		# button combobox
		self.button_combobox.set_active(b_index)
		self.dialog.connect("response", self.dialog_response)
		self.button_combobox.connect("changed", self.button_combobox_changed)		
		

	def get_dialog (self):
		return self.dialog

	def dialog_response (self, dialog, response):
		dialog.hide()

	def offset_combobox_changed (self, combobox):
		index = self.offset_combobox.get_active()
		if index == 0:
			offset = "-1"
		elif index == 2:
			offset = "1"
		else: 
			offset = "0"
		self.gconf.set_string(gconf_keys['offset'], str(offset))

	def button_combobox_changed (self, combobox):
		index = self.button_combobox.get_active()
		if index == 0:
			button = "En Caliente"
		else: 
			button = "Agregar a la Cola"
		self.gconf.set_string(gconf_keys['button'], str(button))
