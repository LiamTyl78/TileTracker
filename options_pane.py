import email
from math import fabs
import csv, tile_tracker

import re
import tkinter as tk
from tkinter import Frame, Scrollbar, messagebox, Button, Entry, LabelFrame
from tkinter.ttk import Treeview, Notebook

# 0 - refresh time


# def add_account(self):

class optionspane(tk.Toplevel):
    options_open = False
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    account_list_backup = []
    account_list_current = []
    geofences_backup = []
    geofences_current = []

    def __init__(self,parent):
        if optionspane.options_open == False:
            super().__init__(parent)
            self.transient(parent)
            self.grab_set()
            optionspane.options_open = True
            self.geometry("450x300")
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0,weight=1)
            self.title("Options")
            self.resizable(False,False)
            self.protocol("WM_DELETE_WINDOW",self.on_cancel)


            tab_control = Notebook(self)
            general_tab = Frame(tab_control)
            accounts_tab = Frame(tab_control)
            geofences_tab = Frame(tab_control)
            tab_control.add(general_tab,text="General")
            tab_control.add(accounts_tab,text="Accounts")
            tab_control.add(geofences_tab,text="Geofences")
            tab_control.grid(row=0, column=0, sticky="nsew",columnspan=2)
            geofences_tab.grid_rowconfigure(0, weight=1)
            geofences_tab.grid_columnconfigure(0, weight=1)

            
            group1 = LabelFrame(general_tab,text="Refresh Time (seconds)", padx=30,pady=15)
            group1.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="new")
            
            # account management screen

            acc_scrollbar = Scrollbar(accounts_tab,orient='vertical')
            accounts_label = LabelFrame(accounts_tab,text="Accounts")
            accounts_label.grid(sticky="new")

            accounts_tab.grid_rowconfigure(0, weight=1)
            accounts_tab.grid_columnconfigure(0, weight=1)
            accounts_label.grid_rowconfigure(0, weight=1)
            accounts_label.grid_columnconfigure(0, weight=1)

            acc_button_frame = Frame(accounts_tab)
            acc_button_frame.grid(row=1,column=0,pady=10)

            acc_add_button = Button(acc_button_frame,text="Add...",command=self.on_add_account)
            acc_remove_button = Button(acc_button_frame,text="Remove",command=self.on_remove_account)
            acc_edit_button = Button(acc_button_frame,text="Edit...",command=self.on_edit_account)
            acc_edit_button.grid(column=1,row=0,padx=5)
            acc_add_button.grid(column=0,row=0,padx=5)
            acc_remove_button.grid(column=2,row=0,padx=5)
            
            self.account_tree = Treeview(accounts_label, columns=('account','password'),show="headings")
            self.account_tree['columns'] = ('account','password')
            self.account_tree.column('account',width=60)
            self.account_tree.heading('account',text="Account")
            self.account_tree.column('password',width=60)
            self.account_tree.heading('password',text="Password")
            self.account_tree.grid(row=0,column=0,sticky="new")
            self.account_tree.config(yscroll=acc_scrollbar.set)
            acc_scrollbar.grid(column=1,row=0,sticky='ns')
            acc_scrollbar.config(command = self.account_tree.yview)

            self.refresh_account_tree()

            #end of account management screen

            #Geofences management screen
            geofences_label = LabelFrame(geofences_tab,text="Geofences")
            geofences_label.grid(row=0, column=0, columnspan=3, sticky="new")
            geofences_label.grid_rowconfigure(0, weight=1)
            geofences_label.grid_columnconfigure(0, weight=1)
            
            self.geofences_tree = Treeview(geofences_label,columns=('name','top_latitude','top_longitude','bot_latitude','bot_logitude'),show='headings')
            self.geofences_tree['columns'] = ('name','top_latitude','top_longitude','bot_latitude','bot_logitude','email')
            self.geofences_tree.grid(row=0,column=0,sticky="new")
            self.geofences_tree.column('name',width=60)
            self.geofences_tree.heading('name',text="Name")
            self.geofences_tree.column('top_latitude',width=60)
            self.geofences_tree.heading('top_latitude',text="Top Latitude")
            self.geofences_tree.column('top_longitude',width=60)
            self.geofences_tree.heading('top_longitude',text="Top Longitude")
            self.geofences_tree.column('bot_latitude',width=60)
            self.geofences_tree.heading('bot_latitude',text="Bottom Latitude")
            self.geofences_tree.column('bot_logitude',width=60)
            self.geofences_tree.heading('bot_logitude',text="Bottom Longitude")
            self.geofences_tree.column('email',width=60)
            self.geofences_tree.heading('email',text="Email")

            geo_vert_scrollbar = Scrollbar(geofences_tab,orient="vertical")
            geo_horz_scrollbar = Scrollbar(geofences_tab,orient="horizontal")
            self.geofences_tree.config(yscrollcommand=geo_vert_scrollbar.set)
            self.geofences_tree.config(xscrollcommand=geo_horz_scrollbar.set)
            geo_vert_scrollbar.grid(column=1,row=0,sticky="ns")
            geo_vert_scrollbar.config(command= self.geofences_tree.yview)
            geo_horz_scrollbar.grid(column=0,row=1,sticky="ew")
            geo_horz_scrollbar.config(command= self.geofences_tree.xview)

            geo_button_frame = Frame(geofences_tab)
            geo_button_frame.grid(row=2,column=0,pady=10)

            geo_add_button = Button(geo_button_frame,text="Add...",command=self.on_add_geofence)
            geo_remove_button = Button(geo_button_frame,text="Remove",command=self.on_remove_geofence)
            geo_edit_button = Button(geo_button_frame,text="Edit...",command=self.on_edit_geofence)
            geo_edit_button.grid(column=1,row=0,padx=5)
            geo_add_button.grid(column=0,row=0,padx=5)
            geo_remove_button.grid(column=2,row=0,padx=5)

            self.refresh_geofence_tree()
            
            #End Geofences management screen

            self.settings = optionspane.get_options()

            self.refresh_time = Entry(group1, relief="flat")
            self.refresh_time.insert(0,self.settings[0])
            self.refresh_time.grid(row=0,column=0)

            button_frame = Frame(self)
            button_frame.grid(row=1,column=0, pady=10)

            ok_button = Button(button_frame,text="OK",padx=5, command=self.on_ok)
            ok_button.pack(side="left", padx=5)
            cancel_button = Button(button_frame,text="Cancel",padx=5, command=self.on_cancel)
            cancel_button.pack(side="left", padx=5)

            self.grid_rowconfigure(1, weight=0)
            self.grid_columnconfigure(0, weight=1)

            #backup current state of account csv file so it can be reverted back if the user doesnt want to save changes
            with open("accounts.csv","r",newline="") as accounts:
                reader = csv.reader(accounts)
                optionspane.account_list_backup = list(reader)
            with open("geofences.csv","r",newline="") as accounts:
                reader = csv.reader(accounts)
                optionspane.geofences_backup = list(reader)

            self.mainloop

    def get_options():
        settings = []
        File = open("options.txt","r")
        File.seek(19)
        settings.append(File.readline())

        return settings

    def set_option(self,setting, new_val):
        with open("options.txt",'r') as file:
            lines = file.readlines()

        updated_options = []

        for line in lines:
            if line.startswith(setting):
                parts = line.split("=")
                if len(parts) == 2:
                    parts[1] = f' {new_val}'
                    line = '='.join(parts)
            updated_options.append(line)
        with open("options.txt",'w') as file:
            file.writelines(updated_options)

    # for updating contents inside the list of accounts
    def refresh_account_tree(self):
        with open("accounts.csv","r",newline="") as account:
                reader = csv.reader(account)
                optionspane.account_list_current = list(reader)
        accounts = []
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
        with open("accounts.csv","r") as file:
            # reader = csv.reader(file)
            # optionspane.account_list_current = list(reader)
            for line in file.readlines():
                parts = line.split(",")
                self.account_tree.insert('', 'end',parts[0],values=(parts[0], "*" * len(parts[1])))
                accounts.append(line)
        return accounts
    
    def refresh_geofence_tree(self):
        '''for updating contents inside the list of geofences'''
        with open("geofences.csv","r",newline="") as geofence:
            reader = csv.reader(geofence)
            optionspane.geofences_current = list(reader)
        geofences = []
        for item in self.geofences_tree.get_children():
            self.geofences_tree.delete(item)
        with open("geofences.csv","r") as file:
            file.readline()
            for line in file.readlines():
                parts = line.split(",")
                self.geofences_tree.insert('', 'end',parts[0],values=(parts[0],parts[2],parts[1],parts[4],parts[3],parts[5]))
                geofences.append(line)
        return geofences
    
    def on_cancel(self):
        '''exit without saving any options and revert options that were changed'''
        optionspane.options_open = False
        with open("accounts.csv","w",newline="") as file:
            writer = csv.writer(file)
            writer.writerows(optionspane.account_list_backup)
        with open("geofences.csv","w",newline="") as file:
            writer = csv.writer(file)
            writer.writerows(optionspane.geofences_backup)
        self.destroy()

    def on_ok(self):
        '''close the option pane and save settings that were changed'''

        optionspane.options_open = False
        if not self.refresh_time.get().strip() == self.settings[0]:
            self.set_option("refresh time",self.refresh_time.get().strip())
        tile_tracker.settings = optionspane.get_options()
        self.destroy()
    
    # account buttons functions
    def on_remove_account(self):
        '''remove account and password from the account file'''
        if self.account_tree.selection():
            account = self.account_tree.selection()[0]
            with open("accounts.csv","r",newline="") as accounts:
                reader = csv.reader(accounts)
                accounts = list(reader)

            rows_to_keep = [row for row in accounts if not row[0] == account]

            with open("accounts.csv","w",newline="") as file:
                writer = csv.writer(file)
                writer.writerows(rows_to_keep)
            self.refresh_account_tree()
        else:
            pass
    
    def on_add_account(self):
        '''add an new account to the program'''
        dialog = addAccountPane(self)
        self.wait_window(dialog)
        self.refresh_account_tree()
        self.grab_set()
    
    def on_edit_account(self):
        '''edit account details like email and password'''
        if self.account_tree.selection():
            account = self.account_tree.selection()
            dialog = editAccountPane(self, account)
            self.wait_window(dialog)
            self.grab_set()
            self.refresh_account_tree()
    #end of account button functions

    #geofence button functions

    def on_add_geofence(self):
        dialog = addGeofencePane(self)
        self.wait_window(dialog)
        self.grab_set()
        self.refresh_geofence_tree()
    
    def on_remove_geofence(self):
        if self.geofences_tree.selection():
            geofence = self.geofences_tree.selection()[0]
            with open("geofences.csv","r",newline="") as geofences:
                reader = csv.reader(geofences)
                geofences = list(reader)

            rows_to_keep = [row for row in geofences if not row[0] == geofence]

            with open("geofences.csv","w",newline="") as file:
                writer = csv.writer(file)
                writer.writerows(rows_to_keep)
            self.refresh_geofence_tree()
        else:
            pass
    
    def on_edit_geofence(self):
        if self.geofences_tree.selection():
            geofence = self.geofences_tree.selection()
            geofence = self.geofences_tree.item(geofence[0])['values']
            dialog = editGeofencePane(self, geofence)
            self.wait_window(dialog)
            self.grab_set()
            self.refresh_geofence_tree()
        else:
            pass


class addAccountPane(tk.Toplevel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        self.title("Add Account")
        self.geometry("300x150")
        self.resizable(False,False)

        tk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=10)
        
        self.username_entry = tk.Entry(self)
        self.password_entry = tk.Entry(self, show="*")

        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        button_frame = Frame(self)
        button_frame.grid(row=2, column=0,columnspan=2)

        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side="left",padx=5)
        tk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side="left",padx=5)

        # self.grid_rowconfigure(1, weight=0)
        # self.grid_columnconfigure(0, weight=1)
    
    def on_cancel(self):
        self.destroy()

    def on_ok(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username == "" and not password == "":
            if re.match(optionspane.email_regex,username):
                if all(username != account[0] for account in optionspane.account_list_current):
                    new_line = [self.username_entry.get().strip(), password]
                    with open("accounts.csv", mode="a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(new_line)
                    self.destroy()
                else:
                    messagebox.showerror("Account already exists!","The account \"" + self.username_entry.get().strip() + "\" already exists.")
            else:
                messagebox.showerror("Invalid email format","Please enter a valid email.")
        else:
            messagebox.showerror("No account info","Please enter both an email and password!")

class editAccountPane(tk.Toplevel):
    
    def __init__(self, parent, account):
        self.account = account
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        self.title("Edit Account")
        self.geometry("300x150")
        self.resizable(False,False)

        tk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self, text="Re-enter password").grid(row=1, column=0, padx=10, pady=10)
        
        self.username_entry = tk.Entry(self)
        self.password_entry = tk.Entry(self, show="*")
        self.username_entry.insert(0,self.account)

        self.username_entry.grid(row=0, column=1, padx=5, pady=5, )
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        button_frame = Frame(self)
        button_frame.grid(row=2, column=0,columnspan=2)

        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side="left",padx=5)
        tk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side="left",padx=5)
    

    def on_cancel(self):
        self.destroy()
    
    def on_ok(self):
        username = self.username_entry.get().strip()
        if not self.username_entry.get().strip() == "" and not self.password_entry.get() == "":
            if re.match(optionspane.email_regex,username):
                if all((username != account[0] or account[0] == self.account[0]) for account in optionspane.account_list_current):
                    edited_account = [self.username_entry.get().strip() ,self.password_entry.get()]
                    with open("accounts.csv","r",newline="") as file:
                        reader = csv.reader(file)
                        accounts = list(reader)
                    i = 0
                    for account in accounts:
                        if account[0] == self.account[0]:
                            accounts[i] = edited_account
                        i = i + 1

                    with open("accounts.csv","w", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerows(accounts)
                    self.destroy()
                else:
                    messagebox.showerror("Account already exists!","The account \"" + self.username_entry.get().strip() + "\" already exists.")
            else:
                messagebox.showerror("Invalid email format","Please enter a valid email.")
        else:
            messagebox.showerror("No account info","Please enter both an email and password!")

class addGeofencePane(tk.Toplevel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW",self.on_cancel)

        self.title("Add Geofence")
        self.geometry("450x225")
        self.resizable(False,False)

        tk.Label(self, text="Geofence Name:").grid(row=0, column=0, padx=5, pady=10)
        tk.Label(self, text="Latitude (top,bottom):").grid(row=1, column=0, padx=5, pady=10)
        tk.Label(self, text="Longitude (top,bottom):").grid(row=2, column=0, padx=5, pady=10)
        tk.Label(self, text="Email").grid(row=3, column=0, padx=5, pady=10)
        
        self.name = tk.Entry(self)
        self.top_latitude = tk.Entry(self)
        self.bot_latitude = tk.Entry(self)
        self.top_longitude = tk.Entry(self)
        self.bot_longitude = tk.Entry(self)
        self.email = tk.Entry(self)
        
        self.name.grid(row=0, column=1, padx=1, pady=5)
        self.top_latitude.grid(row=1, column=1, padx=1, pady=5)
        self.top_longitude.grid(row=2, column=1, padx=1, pady=5)
        self.bot_latitude.grid(row=1, column=2, padx=1, pady=5)
        self.bot_longitude.grid(row=2, column=2, padx=1, pady=5)
        self.email.grid(row=3,column=1,padx=1,pady=5)

        button_frame = Frame(self)
        button_frame.grid(row=4, column=0, columnspan=3)

        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side="left",padx=5)
        tk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side="left",padx=5)
    
    def on_cancel(self):
        self.destroy()
    
    def on_ok(self):
        name = self.name.get().strip()
        if not self.name.get().strip() == "" and not self.top_latitude.get().strip() == "" and not self.top_longitude.get().strip() == "" and not self.bot_latitude.get().strip() == "" and not self.bot_longitude.get().strip() == "":
            if all(name != account[0] for account in optionspane.geofences_current):
                if is_numeric(self.top_latitude.get().strip()) and is_numeric(self.top_longitude.get().strip()) and is_numeric(self.bot_latitude.get().strip()) and is_numeric(self.bot_longitude.get().strip()):
                    new_line = [self.name.get().strip(),self.top_longitude.get().strip(),self.top_latitude.get().strip(),self.bot_longitude.get().strip(),self.bot_latitude.get().strip(),self.email.get().strip()]
                    with open("geofences.csv",mode="a",newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(new_line)
                    self.destroy()
                else:
                    messagebox.showerror("Invalid Input", "Please enter only numerical values for Latitiude and Logitude!")
            else:
                messagebox.showerror("Geofence already exists!","The Geofence \"" + self.name.get().strip() + "\" already exists.")
        else:
            messagebox.showerror("Info Missing!","Please insure all fields are filled!")
    

class editGeofencePane(tk.Toplevel):
    
    def __init__(self, parent, geofence):
        self.name = geofence[0]
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW",self.on_cancel)
        self.geofence = geofence

        self.title("Add Geofence")
        self.geometry("450x225")
        self.resizable(False,False)

        tk.Label(self, text="Geofence Name:").grid(row=0, column=0, padx=5, pady=10)
        tk.Label(self, text="Latitude (top,bottom):").grid(row=1, column=0, padx=5, pady=10)
        tk.Label(self, text="Longitude (top,bottom):").grid(row=2, column=0, padx=5, pady=10)
        tk.Label(self, text="Email").grid(row=3, column=0, padx=5, pady=10)
        
        self.geofence_name = tk.Entry(self)
        self.top_latitude = tk.Entry(self)
        self.bot_latitude = tk.Entry(self)
        self.top_longitude = tk.Entry(self)
        self.bot_longitude = tk.Entry(self)
        self.email = tk.Entry(self)

        self.geofence_name.insert(0,self.geofence[0])
        self.top_latitude.insert(0,self.geofence[1])
        self.top_longitude.insert(0,self.geofence[2])
        self.bot_latitude.insert(0,self.geofence[3])
        self.bot_longitude.insert(0,self.geofence[4])
        self.email.insert(0,self.geofence[5])
        
        
        self.geofence_name.grid(row=0, column=1, padx=1, pady=5)
        self.top_latitude.grid(row=1, column=1, padx=1, pady=5)
        self.top_longitude.grid(row=2, column=1, padx=1, pady=5)
        self.bot_latitude.grid(row=1, column=2, padx=1, pady=5)
        self.bot_longitude.grid(row=2, column=2, padx=1, pady=5)
        self.email.grid(row=3,column=1,padx=1,pady=5)

        button_frame = Frame(self)
        button_frame.grid(row=4, column=0, columnspan=3)

        tk.Button(button_frame, text="OK", command=self.on_ok).pack(side="left",padx=5)
        tk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side="left",padx=5)
        
    def on_cancel(self):
        self.destroy()

    def on_ok(self):
        name = self.geofence_name.get().strip()
        if not self.geofence_name.get().strip() == "" and not self.top_latitude.get().strip() == "" and not self.top_longitude.get().strip() == "" and not self.bot_latitude.get().strip() == "" and not self.bot_longitude.get().strip() == "":
            if all((name != account[0] or account[0] == self.name) for account in optionspane.geofences_current):
                if is_numeric(self.top_latitude.get().strip()) and is_numeric(self.top_longitude.get().strip()) and is_numeric(self.bot_latitude.get().strip()) and is_numeric(self.bot_longitude.get().strip()):

                    edited_geofence = [self.geofence_name.get().strip(),self.top_longitude.get().strip(),self.top_latitude.get().strip(),self.bot_longitude.get().strip(),self.bot_latitude.get().strip(),self.email.get().strip()]
                    with open("geofences.csv","r",newline="") as file:
                        reader = csv.reader(file)
                        geofences = list(reader)
                    i = 0
                    for geofence in geofences:
                        if geofence[0] == self.name:
                            geofences[i] = edited_geofence
                        i = i + 1

                    with open("geofences.csv","w", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerows(geofences)
                    self.destroy()
                else:
                    messagebox.showerror("Invalid Input", "Please enter only numerical values for Latitiude and Logitude!")
            else:
                messagebox.showerror("Geofence already exists!","The Geofence \"" + self.geofence_name.get().strip() + "\" already exists.")
        else:
            messagebox.showerror("Info Missing!","Please insure all fields are filled!")

def is_numeric(input_str):
    return bool(re.match(r'^-?\d+(\.\d+)?$', input_str))