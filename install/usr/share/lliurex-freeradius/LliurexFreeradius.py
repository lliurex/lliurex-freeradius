#!/usr/bin/env python
# -*- coding: utf-8 -*
 

import os
import time
import sys
import threading
import queue
import subprocess

import N4dManager

try:
	import gi
	gi.require_version('Gtk', '3.0')
	from gi.repository import Gtk, GObject, GLib, Gio, Gdk
	
except Exception as e:
	print(e)
	

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import gettext
gettext.textdomain('lliurex-freeradius')
_ = gettext.gettext

RSRC_PATH="/usr/share/lliurex-freeradius/rsrc/"

DEBUG=True

class LliurexFreeradius:
	
	def __init__(self):
		
		self.n4d=N4dManager.N4dManager()
		self.first_run=True
		
	#def init
	
	
	def dprint(self,data):
		
		if DEBUG:
			data="[LliurexFreeRadius] %s"%data
			print(data)
			
	#def dprint
	
	def build_gui(self):
		
		builder=Gtk.Builder()
		builder.set_translation_domain('lliurex-freeradius')
		builder.add_from_file(RSRC_PATH+"lliurex-freeradius.ui")
		
		self.window=builder.get_object("window")
		self.main_box=builder.get_object("main_box")
		self.stack_label_box=builder.get_object("stock_label_box")
		self.stack_label=builder.get_object("stack_label")
		self.close_button=builder.get_object("close_button")
		self.msg_label_box=builder.get_object("msg_label_box")
		self.msg_label=builder.get_object("msg_label")
		
		self.build_stack()
		
		self.help_window=builder.get_object("help_window")
		self.llum_button=builder.get_object("llum_button")
		
		
		# This should go to a different file
		self.groups_box=builder.get_object("groups_box")
		self.filter_box=builder.get_object("filter_box")
		self.filter_frame=builder.get_object("filter_frame")
		self.enable_filtering_switch=builder.get_object("enable_filtering_switch")
		self.eap_switch=builder.get_object("eap_switch")
		self.allowed_groups_treeview=builder.get_object("allowed_groups_treeview")
		self.available_groups_treeview=builder.get_object("available_groups_treeview")
		self.add_button=builder.get_object("add_button")
		self.remove_button=builder.get_object("remove_button")
		self.back_to_initialization_button=builder.get_object("initialization_button")
		groups_box_label1=builder.get_object("groups_box_label1")
		groups_box_label2=builder.get_object("groups_box_label2")
		groups_box_label3=builder.get_object("groups_box_label3")
		groups_box_label4=builder.get_object("groups_box_label4")
		
		self.group_box_labels=[groups_box_label1,groups_box_label2,groups_box_label3,groups_box_label4]
		
		# ######################
		
		# To another file?
		
		self.initialization_box=builder.get_object("initialization_box")
		self.group_button=builder.get_object("group_button")
		init_label1=builder.get_object("init_label1")
		init_label2=builder.get_object("init_label2")
		init_label3=builder.get_object("init_label3")
		init_label4=builder.get_object("init_label4")
		init_label5=builder.get_object("init_label5")
		init_label6=builder.get_object("init_label6")
		self.init_box_labels=[init_label1,init_label2,init_label3,init_label4,init_label5,init_label6]
		self.radius_server_entry=builder.get_object("radius_server_entry")
		self.radius_password_entry=builder.get_object("radius_password_entry")
		self.radius_password_entry2=builder.get_object("radius_password_entry2")
		self.ldap_user_entry=builder.get_object("ldap_user_entry")
		self.ldap_password_entry=builder.get_object("ldap_password_entry")
		self.router_ip_entry=builder.get_object("router_ip_entry")
		self.initialize_button=builder.get_object("initialize_button")
		self.roadmin_help_button=builder.get_object("roadmin_help_button")
		
		# ########

		
		# To yet another file? 
		
		self.login_box=builder.get_object("login_box")
		self.login_button=builder.get_object("login_button")
		self.user_entry=builder.get_object("user_entry")
		self.password_entry=builder.get_object("password_entry")
		self.server_entry=builder.get_object("server_entry")
		
		self.login_button.grab_focus()
		
		# ################# #

		
		self.stack.add_titled(self.login_box,"login_box","Login")
		self.stack.add_titled(self.groups_box,"groups_box","Groups Management")
		self.stack.add_titled(self.initialization_box,"init_box","Initialization")
		self.main_box.pack_start(self.stack,True,True,10)
		
		
		self.connect_signals()
		self.set_css_info()
		self.set_data()
		
		self.window.show_all()
				
		GObject.threads_init()
		Gtk.main()
			
	#def build_gui
	
	
	def build_stack(self):
		
		self.stack=Gtk.Stack()
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack.set_transition_duration(500)
		
	#def build_stack
	
	
	def connect_signals(self):
		
		self.window.connect("destroy",Gtk.main_quit)
		self.close_button.connect("clicked",Gtk.main_quit)
		
		self.enable_filtering_switch.connect("notify::active",self.enable_filtering_switch_changed)
		self.eap_switch.connect("notify::active",self.eap_switch_changed)
		
		self.add_button.connect("clicked",self.add_clicked)
		self.remove_button.connect("clicked",self.remove_clicked)
		self.back_to_initialization_button.connect("clicked",self.back_to_initialization_clicked)
		self.group_button.connect("clicked",self.back_to_groups_clicked)
		self.initialize_button.connect("clicked",self.initialize_clicked)
		self.roadmin_help_button.connect("clicked",self.roadmin_help_clicked)
		self.login_button.connect("clicked",self.login_clicked)
		
		self.user_entry.connect("activate",self.entries_press_event)
		self.password_entry.connect("activate",self.entries_press_event)
		self.server_entry.connect("activate",self.entries_press_event)

		self.help_window.connect("delete_event",self.help_window_closed)
		self.llum_button.connect("clicked",self.open_llum_clicked)
		
		
	#def connect_signals
	
	
	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path(RSRC_PATH+"lliurex-freeradius.css")
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		
		self.window.set_name("WHITE_BACKGROUND")
		self.stack_label.set_name("STACK_LABEL")
		self.msg_label.set_name("REGULAR_LABEL")
		self.stack.set_name("LIGHT_BLUE")
		
		self.msg_label_box.set_name("LIGHT_BLUE")
		self.stack_label_box.set_name("LIGHT_BLUE")
				
		for label in self.group_box_labels:
			label.set_name("REGULAR_LABEL")
			
		for label in self.init_box_labels:
			label.set_name("INIT_LABEL")
		
	#def set-css_info	
	
	
	def set_data(self):
	
		self.stack_label.set_text(_("Login"))
	
		self.available_groups_liststore=Gtk.ListStore(str)
		self.available_groups_treeview.set_model(self.available_groups_liststore)
		self.available_groups_treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
		
		column=Gtk.TreeViewColumn(_("Groups"))
		renderer=Gtk.CellRendererText()
		column.pack_start(renderer,True)
		column.add_attribute(renderer,"text",0)
		self.available_groups_treeview.append_column(column)
		
		self.allowed_groups_liststore=Gtk.ListStore(str)
		self.allowed_groups_treeview.set_model(self.allowed_groups_liststore)
		self.allowed_groups_treeview.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
		
		column=Gtk.TreeViewColumn(_("Groups"))
		renderer=Gtk.CellRendererText()
		column.pack_start(renderer,True)
		column.add_attribute(renderer,"text",0)
		self.allowed_groups_treeview.append_column(column)
	
	#def set_data
		
	
	def populate_treeviews(self):
		
		self.available_groups_liststore.clear()
		self.allowed_groups_liststore.clear()
		
		for g in self.n4d.all_groups:
			if g not in self.n4d.allowed_groups:
				self.available_groups_liststore.append([g])
				
		for g in self.n4d.allowed_groups:
			self.allowed_groups_liststore.append([g])
		

		ret=self.n4d.get_switches_status()

		self.eap_switch.set_active(ret["eap"])
		self.enable_filtering_switch.set_active(ret["filter"])
		
		if not ret["filter"]:
			self.first_run=False
			self.set_filterbox_sensitive(False)
		
	#def populate_treeview
	
		
	def enable_filtering_switch_changed(self,widget,data):
		
		state=widget.get_active()
		if not self.first_run:
			ret=self.n4d.set_group_filtering(state)
		self.set_filterbox_sensitive(state)
		
		self.first_run=False
			
	#def enable_filtering_switch
	
	
	def eap_switch_changed(self,widget,data):
		
		state=widget.get_active()
		if not self.first_run:
			ret=self.n4d.set_eap_auth(state)
			self.msg_label.set_text(_("EAP Authentication protocol is %s")%(_("enabled") if state else _("disabled")))
		
	#def eap_switch_changed
	
	
	def set_filterbox_sensitive(self,state,ignore_msg_label=False):
		
		self.filter_box.set_sensitive(state)
		self.filter_frame.set_sensitive(state)
		if state:
			self.filter_box.set_name("")
			for label in self.group_box_labels[1:]:
				label.set_name("REGULAR_LABEL")
		else:
			self.filter_box.set_name("BLACK")
			for label in self.group_box_labels[1:]:
				label.set_name("REGULAR_LABEL_DISABLED")
		
		if not ignore_msg_label:
			self.msg_label.set_text(_("Group filtering is %s")%(_("enabled") if state else _("disabled")))
		
	#def set_filterbox_sensitive
	
	
	def add_clicked(self,widget):
		
		model,path_list= self.available_groups_treeview.get_selection().get_selected_rows()
		iters_to_remove=[]
		
		for item in path_list:
			
			group=model[item][0]
			ret=self.n4d.add_group_to_filter(group)
			iters_to_remove.append(model.get_iter(item))
			self.allowed_groups_liststore.append([group])
			
		for iter in iters_to_remove:
			model.remove(iter)
			
		if len(iters_to_remove)>0:
			self.msg_label.set_text(_("%s groups have been added to the 'Allowed groups' list")%len(iters_to_remove))
			
		self.available_groups_treeview.get_selection().unselect_all()
		self.allowed_groups_treeview.get_selection().unselect_all()
		
	#def add_clicked
	
	
	def remove_clicked(self,widget):
		
		model,path_list= self.allowed_groups_treeview.get_selection().get_selected_rows()
		iters_to_remove=[]
		
		for item in path_list:
			
			group=model[item][0]
			ret=self.n4d.remove_group_from_filter(group)
			iters_to_remove.append(model.get_iter(item))  
			self.available_groups_liststore.append([group])
			
		for iter in iters_to_remove:
			model.remove(iter)
			
		if len(iters_to_remove)>0:
			self.msg_label.set_text(_("%s groups have been removed from the 'Allowed groups' list")%len(iters_to_remove))
		
		self.available_groups_treeview.get_selection().unselect_all()
		self.allowed_groups_treeview.get_selection().unselect_all()

	#def add_clicked
	
	
	def initialize_clicked(self,widget):
		
		ret,data=self.check_initialize_input_data()
		
		if not ret:
			self.msg_label.set_markup("<b>"+data+"</b>")
			return False
			
		self.run_initialize(data)
		
	#def initialize_clicked
	
	
	def check_initialize_input_data(self):
		
		data={}
		data["radius_server"]=self.radius_server_entry.get_text()
		data["radius_password"]=self.radius_password_entry.get_text()
		data["radius_password2"]=self.radius_password_entry2.get_text()
		data["ldap_user"]=self.ldap_user_entry.get_text()
		data["ldap_password"]=self.ldap_password_entry.get_text()
		data["router_ip"]=self.router_ip_entry.get_text()
		
		if len(data["radius_server"])<1:
			return (False,_("Radius server entry field is empty"))
		
		if len(data["radius_password"])<1:
			return (False,_("Radius password entry field is empty"))
		
		if len(data["ldap_user"])<1:
			return (False,_("LDAP user entry field is empty"))

		if len(data["ldap_password"])<1:
			return (False,_("LDAP password entry field is empty"))
			
		if data["radius_password"] != data["radius_password2"]:
			return (False,_("Radius passwords do not match"))

		if len(data["router_ip"])<1:
			data["router_ip"]=""
		
		return (True,data)
		
	#def check_initialize_input_data
	

	def entries_press_event(self,widget):
		
		self.login_clicked(None)

	#def login_clicked

	
	def login_clicked(self,widget):
	
		user=self.user_entry.get_text()
		password=self.password_entry.get_text()
		server=self.server_entry.get_text()
				
		self.n4d.set_server(server)
		self.run_validate_user(user,password)
		
	#def login_clicked
	
	
	def back_to_initialization_clicked(self,widget=None):
		
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		
		if self.n4d.configured:
			self.group_button.show()
		else:
			self.group_button.hide()
		
		self.msg_label.set_text("")
		self.stack_label.set_text(_("Initialization"))
		self.stack.set_visible_child_name("init_box")
		self.window.queue_draw()
		
	#def back_to_initialization
	
	
	def back_to_groups_clicked(self,widget=None):
		
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack_label.set_text(_("Groups Management"))
		self.stack.set_visible_child_name("groups_box")
		self.window.queue_draw()
		
	#def back_to_groups
	
	def roadmin_help_clicked(self,widget):
		
		self.help_window.show()
		
	#def roadmin_help
	
	
	def help_window_closed(self,widget,event):
		
		self.help_window.hide()
		return True
		
	#def help_window_closed
	
	
	def open_llum_clicked(self,widget):
		
		subprocess.Popen(["llum"], preexec_fn=os.setpgrp)
		
	#def open_llum_clicked
		
	
	
	
	
	# THREADS FUNCTIONS ########################################
	
	def run_validate_user(self,user,password):
		
		self.login_button.set_sensitive(False)
		
		q=queue.Queue()
		t=threading.Thread(target=self.validate_user_thread,args=(user,password,q))
		t.daemon=True
		t.start()
		
		GLib.timeout_add(500,self.validate_user_listener,t,q)
		
	#def

	
	def validate_user_thread(self,user,password,queue_var):
	
		ret=self.n4d.validate_user(user,password)
		queue_var.put(ret)
		
	#def validate_user_thread

	
	def validate_user_listener(self,thread,queue_var):
		
		if thread.is_alive():
			return True
			
		ret,msg=queue_var.get()
		if not ret:
			self.msg_label.set_markup("<b>"+msg+"</b>")
		else:
			if not self.n4d.configured:
				self.back_to_initialization_clicked()
			else:
				self.populate_treeviews()
				self.back_to_groups_clicked()
		
		self.login_button.set_sensitive(True)
		
		return False
		
	#def validate_user_listener
	

	def run_initialize(self,data):
		
		self.initialize_button.set_sensitive(False)
		
		q=queue.Queue()
		t=threading.Thread(target=self.initialize_thread,args=(data,q))
		t.daemon=True
		t.start()
		
		GLib.timeout_add(500,self.initialize_listener,t,q)
		
	#def

	
	def initialize_thread(self,data,queue_var):
	
		ret=self.n4d.initialize(data)
		queue_var.put(ret)
		
	#def validate_user_thread

	
	def initialize_listener(self,thread,queue_var):
		
		if thread.is_alive():
			return True
			
		ret=queue_var.get()
		if not ret["status"]:
			self.msg_label.set_markup("<b>"+ret["msg"]+"</b>")
		else:
			self.populate_treeviews()
			self.back_to_groups_clicked()
		
		self.initialize_button.set_sensitive(True)
		
		return False
		
	#def validate_user_listener
	
	
	# ######################################################

	
#class LliurexFreeradius

if __name__=="__main__":
	
	lf=LliurexFreeradius()
	lf.build_gui()
