import geofence
import csv, tile_tracker
import tkinter as tk

from tkinter import W, Frame, Scrollbar, messagebox
from tkinter import Button, Entry, LabelFrame
from tkinter.ttk import Treeview, Notebook

# 0 - refresh time


# def add_account(self):

class optionspane(tk.Tk):
    
    options_open = False
    account_list_backup = []

    def __init__(self):
        if optionspane.options_open == False:
            super().__init__()
            optionspane.options_open = True
            self.geometry("400x300")
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0,weight=1)
            self.title("Options")
            self.resizable(False,False)
            self.protocol("WM_DELETE_WINDOW",self.on_cancel)


            tab_control = Notebook(self)
            general_tab = Frame(tab_control)
            accounts_tab = Frame(tab_control)
            geofences_tabe = Frame(tab_control)
            tab_control.add(general_tab,text="General")
            tab_control.add(accounts_tab,text="Accounts")
            tab_control.add(geofences_tabe,text="Geofences")
            tab_control.grid(row=0, column=0, sticky="nsew",columnspan=2)

            
            group1 = LabelFrame(general_tab,text="Refresh Time (seconds)", padx=30,pady=15)
            group1.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="new")
            
            scrollbar = Scrollbar(accounts_tab,orient='vertical')
            accounts_group = LabelFrame(accounts_tab,text="Accounts")
            accounts_group.grid(sticky="new")

            accounts_tab.grid_rowconfigure(0, weight=1)
            accounts_tab.grid_columnconfigure(0, weight=1)
            accounts_group.grid_rowconfigure(0, weight=1)
            accounts_group.grid_columnconfigure(0, weight=1)

            # account management buttons
            acc_button_frame = Frame(accounts_tab)
            acc_button_frame.grid(row=1,column=0,pady=10)

            add_button = Button(acc_button_frame,text="Add...",command=self.on_add_account)
            remove_button = Button(acc_button_frame,text="Remove",command=self.on_remove)
            edit_button = Button(acc_button_frame,text="Edit...",command=self.on_edit)
            edit_button.grid(column=1,row=0,padx=5)
            add_button.grid(column=0,row=0,padx=5)
            remove_button.grid(column=2,row=0,padx=5)
            
            self.account_tree = Treeview(accounts_group, columns=('account','password'),show="headings")
            self.account_tree['columns'] = ('account','password')
            self.account_tree.column('account',width=60)
            self.account_tree.heading('account',text="Account")
            self.account_tree.column('password',width=60)
            self.account_tree.heading('password',text="Password")
            self.account_tree.grid(row=0,column=0,sticky="new")
            self.account_tree.config(yscroll=scrollbar.set)

            self.refresh_account_tree()

            scrollbar.grid(column=1,row=0,sticky='ns')
            scrollbar.config(command = self.account_tree.yview)
            
            self.settings = optionspane.get_options()
            # print(self.settings[0])

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

            with open("accounts.csv","r",newline="") as accounts:
                reader = csv.reader(accounts)
                optionspane.account_list_backup = list(reader)

            self.mainloop

    def get_options():
        settings = []
        File = open("options.txt","r")
        File.seek(19)
        settings.append(File.readline())

        return settings

    def set_option(setting, new_val):
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
        accounts = []
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
        with open("accounts.csv","r") as file:
            for line in file.readlines():
                parts = line.split(",")
                self.account_tree.insert('', 'end',parts[0],values=(parts[0], "*" * len(parts[1])))
                accounts.append(line)
        return accounts
    
    # exit without saving any options and revert options that were changed
    def on_cancel(self):
        optionspane.options_open = False
        with open("accounts.csv","w",newline="") as file:
            writer = csv.writer(file)
            writer.writerows(optionspane.account_list_backup)
        self.destroy()

    def on_ok(self):
        '''close the option pane and save settings that were changed'''

        optionspane.options_open = False
        if not self.refresh_time.get() == self.settings[0]:
            self.set_option("refresh time",self.refresh_time.get())
        tile_tracker.settings = optionspane.get_options()
        self.destroy()
    
    # remove account button
    def on_remove(self):
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
    
    # add an new account to the program
    def on_add_account(self):
        dialog = addAccountPane(self)
        self.wait_window(dialog)
        self.refresh_account_tree()
    
    # edit account button
    def on_edit(self):
        account = self.account_tree.selection()
        dialog = editAccountPane(self, account)
        self.wait_window(dialog)
        self.refresh_account_tree()


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
        if not self.username_entry.get() == "" and not self.password_entry.get() == "":
            new_line = [self.username_entry.get(), self.password_entry.get()]
            with open("accounts.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(new_line)
            self.destroy()
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
        if not self.username_entry.get() == "" and not self.password_entry.get() == "":
            new_account = [self.username_entry.get() ,self.password_entry.get()]
            with open("accounts.csv","r",newline="") as file:
                reader = csv.reader(file)
                accounts = list(reader)
            i = 0
            for account in accounts:
                if account[0] == self.account[0]:
                    accounts[i] = new_account
                i = i + 1
            
            with open("accounts.csv","w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(accounts)
            self.destroy()
        else:
            messagebox.showerror("No account info","Please enter both an email and password!")