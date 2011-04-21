# -*- coding: utf-8 -*-

# JamendoSource.py
#
# Copyright (C) 2007 - Guillaume Desmottes
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

# Parts from "Magnatune Rhythmbox plugin" (stolen from rhythmbox's MagnatuneSource.py)
#     Copyright (C), 2006 Adam Zimmerman <adam_zimmerman@sfu.ca>

import rb, rhythmdb

import os
import gobject
import gtk
import gnome, gconf
import xml
import gzip
import datetime

class HoraSource(rb.HoraSource):
	__gproperties__ = {
		'plugin': (rb.Plugin, 'plugin', 'plugin', gobject.PARAM_WRITABLE|gobject.PARAM_CONSTRUCT_ONLY),
	}

	def __init__(self):

		rb.HoraSource.__init__(self, name=_("Hora"))

		# catalogue stuff
		self.__db = None
		self.__activated = False

		#self.__hora_dir = rb.find_user_cache_file("hora")
		#if os.path.exists(self.__hora_dir) is False:
		#	os.makedirs(self.__hora_dir, 0700)


	def do_set_property(self, property, value):
		if property.name == 'plugin':
			self.__plugin = value
		else:
			raise AttributeError, 'unknown property %s' % property.name

	def do_impl_can_delete (self):
		return False
|	|	
	def do_impl_activate(self):
		if not self.__activated:
			shell = self.get_property('shell')
			self.__db = shell.get_property('db')
			self.__entry_type = self.get_property('entry-type')

			self.__activated = True

		rb.BrowserSource.do_impl_activate (self)


