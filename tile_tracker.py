import asyncio, time, Mail, csv, os
from turtle import settiltangle
import tkinter as tk
from options_pane import optionspane
from tkinter import *
from tkinter.ttk import Treeview
from tkinter import messagebox
from pyppeteer import launch
from app2 import USERNAME,PASSWORD,USERNAME2,PASSWORD2, EMAIL3,PASSWORD3

from aiohttp import ClientSession
from geofence import GeoFence
from pytile import async_login, tile

running = True
settings = optionspane.get_options()
geofences = []
emails = []

class tiletraker(tk.Tk):
    
    def __init__(self):
        self.updates_avalible = False
        self.accounts = self.init_tile_list()
        def refresh():
            
            try:
                for account in self.accounts:
                    account[2] = asyncio.run(self.update_tiles(account[0],account[1],account[2],1)).copy()
                    asyncio.run(self.main(1,account[2]))
                    self.start_time = time.time()
            except:
                print("Failed to refresh, Please check your internet connection and try again later")

        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.minsize(400,400)
        menubar = Menu(self)

        group1 = LabelFrame(self, text="Tracked Tiles", padx=5, pady=5)
        group2 = LabelFrame(self,text="Tracking Log", padx=5, pady=5)

        scrollbar = Scrollbar(group1,orient='vertical')
        self.tree = Treeview(group1, columns=('name','timestamp','location','account'),show="headings",yscrollcommand = scrollbar.set)
        self.mylist = Listbox(group2, width=50 )

        group1.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=S+E+W+N)
        group2.grid(row=1, column=0, padx=10, pady=10, sticky=N+E+W+S)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0,weight=1)
        
        group1.grid_rowconfigure(0, weight=1)
        group1.grid_columnconfigure(0, weight=1)

        group2.grid_rowconfigure(0, weight=1)
        group2.grid_columnconfigure(0, weight=1)

        self.tree['columns'] = ('name','timestamp', 'location','account')
        self.tree.column('name',width=60)
        self.tree.heading('name',text="Name")
        self.tree.column('timestamp',width=120)
        self.tree.heading('timestamp',text="Timestamp")
        self.tree.column('location',width=120)
        self.tree.heading('location',text="Location")
        self.tree.column('account',width=120)
        self.tree.heading('account',text="Account")
        self.tree.grid(row=0,column=0,sticky=E+W+N+S)
        
        scrollbar.grid(column=1,row=0,sticky='nse')
        scrollbar.config( command = self.tree.yview )
        
        self.mylist.grid(row=0,column=0,sticky=S+N+E+W)

        refreshButton = Button(group1,text="Refresh", command=refresh)
        refreshButton.grid(row=2,column=0)

        self.config(menu=menubar)
        
        filemenu = Menu(menubar,tearoff=0)
        filemenu.add_command(label="Options",command=lambda: self.options())
        filemenu.add_separator( )
        filemenu.add_command(label="Exit",command=self.on_exit)

        menubar.add_cascade(label="File", menu=filemenu)

        
    
    def init_tile_list(self):
        accounts = []
        initiziled = False
        start_time = time.time() - float(settings[0])
        with open("accounts.csv","r",newline="") as accounts_file:
            reader = csv.reader(accounts_file)
            accounts = list(reader)
        while not initiziled:
            if (start_time + float(settings[0])) < time.time():
                for account in accounts:
                    try:
                        tiles = asyncio.run(self.update_tiles(account[0],account[1],None,0)).copy()
                        account.append(tiles)
                        initiziled = True
                    except Exception as e:
                        if "getaddrinfo failed" in str(e):
                            # messagebox.showerror("Connection Error","Failed to connect to tile account " + USERNAME2 + ", please check internet connection. Attempting to reconnect again in "+ str(settings[0]) + " seconds.",)
                            print("Failed to connect to tile account " + account[0] + ", please check internet connection. Attempting to reconnect again in "+ str(settings[0]) + " seconds.")
                        else:
                            print("An unknown error has occured while attempting to update tiles, trying again in "+ settings[0] + " seconds.")
                            print(e)
                start_time = time.time()
            time.sleep(0.05)
        return accounts
                            
        



    def options(self):
        options = optionspane(self)
        self.wait_window(options)

    def on_exit(self):
        global running
        if messagebox.askokcancel("Quit","Are you sure you want to exit?"):
            self.destroy()
            running = False
    
    def initialize_files(self):
        with open('geofences.csv', mode = 'r')as file: #function appends all geofences list so program can compare to all geofences when checking location
        
            # reading the CSV file
            csvFile = csv.reader(file)
            i = 0

            # displaying the contents of the CSV file
            for lines in csvFile:
                    if i > 0:
                        geofences.append(GeoFence(lines[0],lines[1],lines[2],lines[3],lines[4],lines[5]))
                    i = i + 1
        with open('emails.csv', mode = 'r')as file: #this file houses a list of all the emails you want to send location updates to and the function appends the emails so the program knows what emails to send to
            csvFile = csv.reader(file) 
            i = 0
            for lines in csvFile:
                if i > 0:
                    emails.append(lines[0])
                i = i + 1
        
        
    async def update_tiles(self, email, password, tiles, runtype):
        '''Grabs updates from the tile by creating new tile objects from the api and carries over the last_location and last_time variables to the new tile objects created and then returns the updated
        tile objects in the new list.
        
        runtype: 0 for init 1 for update'''
        async with ClientSession() as session:
            if runtype == 1:
                tiles2 = tiles.copy()
                api = await async_login(email, password, session)
                tiles = await api.async_get_tiles()
                for tile_uuid, tile in tiles.items():
                    # if tiles.__contains__
                    tile.lasttime = tiles2[tile.uuid].lasttime
                    tile.lastlocation = tiles2[tile.uuid].lastlocation
                    tile.account = email
            else:
                api = await async_login(email, password, session)
    
                tiles = await api.async_get_tiles()

                for tile_uuid, tile in tiles.items():
                    tile.account = email
                
        
        return tiles
    
    #Checks the location of the tile given in the parameter
    #loops through the geofence list until the longitude and latitude of the tile fall 
    #into one of the geofences then location_found is set to true and then breaks the loop retuning the location
    #if a location is not found outside is returned
    def get_location(self,tile):
        for geofence in geofences: 
            if (tile.latitude > geofence.BotLat and tile.latitude < geofence.TopLat) and (tile.longitude < geofence.BotLong and tile.longitude > geofence.TopLong):
                return geofence
        return GeoFence("Outside",0,0,0,0,"")
    
    async def capture_map(self, latitude, longitude):
        
        clip = {
        'x': 900,    
        'y': 325,     
        'width': 400,
        'height': 400
        }
        path = os.path.join(os.getcwd(), 'map.png')
        executable_path = r'C:\Users\e-tyl\OneDrive - Rowan University\TileTracker\chrome-win\chrome.exe'
        browser = await launch(headless=True, executablePath=executable_path)
        url = 'https://www.google.com/maps/place/' + str(latitude) + ',' + str(longitude) + '/@' + str(latitude) + ',' + str(longitude - 0.003) + ',16z'
        
        print(f'navigating to {url}')
        
        page = await browser.newPage()

        await page.setViewport({'width': 1920, 'height': 1080})
        await page.goto(url)
        await page.screenshot({'path': path, 'clip': clip})
        await browser.close()

        print(f'Screenshot saved to {path}')
    
    async def main(self, runtype, tiles):
        '''updates the treeview and listview as well as finding location info and sending it out to the mailing list'''
        for tile_uuid, tile in tiles.items():
            
            # if tile.name == 'Keys': 
            #     await self.capture_map(tile.latitude, tile.longitude)
            #     for email in emails:
            #         address = email
            #         email = Mail.email(address,'Tile has left '+ tile.lastlocation, ('The tile \'' + tile.name + '\' has exited the geofence \'' + tile.lastlocation + '\' its last location was at ' + str(tile.latitude) + ' ' + str(tile.longitude)))
            #         email.send()
            #         print(f'location email sent for {tile.name} to {address}')
            # else:
            #     print("false")

            if not (tile.last_timestamp == tile.get_lasttime()):
                self.updates_avalible = True
                geofence = self.get_location(tile)
                location = geofence.name
                self.mylist.insert(END, str(tile.name) + " " + str(tile.last_timestamp) + " Location: " + location)
                if runtype == 0: #runtype determines whether you're updating the information(1) in the TKinter tree view or initializing it(0)
                    self.tree.insert('', 'end', str(tile.name), values=(tile.name,tile.last_timestamp, location,tile.account))
                else:
                    self.tree.delete(str(tile.name))
                    self.tree.insert('', 'end', str(tile.name), values=(tile.name,tile.last_timestamp, location,tile.account))
                    print("Last Location: ",tile.get_lastlocation())
                    
                    if(location == "Outside" and not tile.lastlocation == "Outside") or (not location ==  tile.lastlocation):
                        await self.capture_map(tile.latitude, tile.longitude)
                    if(location == "Outside" and not tile.lastlocation == "Outside"):
                        for email in emails:
                            address = email
                            email = Mail.email(address,'Tile has left '+ tile.lastlocation, ('The tile \'' + tile.name + '\' has exited the geofence \'' + tile.lastlocation + '\' its last location was at ' + str(tile.latitude) + ' ' + str(tile.longitude)))
                            email.send()
                            print(f'location email sent for {tile.name} to {address}')
                    elif(not location == tile.lastlocation):
                        for email in emails:
                            address = email
                            email = Mail.email(address,'Tile has entered '+ location, ('The tile \'' + tile.name + '\' has entered the geofence \'' + location + '\' from \'' + tile.lastlocation +'\'its last location was at ' + str(tile.latitude) + ' ' + str(tile.longitude)))
                            email.send()
                            print('location email sent for\'', tile.name, '\'to ', address)
                tile.set_lastlocation(location)
                tile.set_lasttime(tile.last_timestamp)
                # print(tile_uuid)
                
                print(tile.name,tile.get_lastlocation(), str(tile.last_timestamp))
                print(str(tile.latitude) + " " + str(tile.longitude))
    
    
    
    def run(self):
        # accounts = self.init_tile_list()
        self.start_time = time.time()
        self.title("Tile Tracker")
        self.initialize_files()
        initilized = False
        current_time = (time.time() + float(settings[0]) + 1)
        while not initilized:
            if current_time > (self.start_time + float(settings[0])):
                for account in self.accounts:
                    try:
                         account[2] = asyncio.run(self.update_tiles(account[0],account[1],account[2],0)).copy()
                         asyncio.run(self.main(0,account[2]))
                         self.start_time = time.time()
                         initilized = True
                    except Exception as e:
                        if "getaddrinfo failed" in str(e):
                            # messagebox.showerror("Connection Error","Failed to connect to tile account " + USERNAME2 + ", please check internet connection. Attempting to reconnect again in "+ str(settings[0]) + " seconds.",)
                            print("Failed to connect to tile account " + account[0] + ", please check internet connection. Attempting to reconnect again in "+ str(settings[0]) + " seconds.")
                        else:
                            print("An unknown error has occured while attempting to update tiles, trying again in "+ settings[0] + " seconds.")
                            print(e)
                self.start_time = time.time()
            time.sleep(0.05)
            current_time = time.time()
        
        

        self.start_time = time.time()
        offline = False
        while running:
            current_time = time.time()
            time.sleep(0.05)
            if current_time > (self.start_time + float(settings[0])):
                print("Checking for updates...")
                for account in self.accounts:
                    try:
                        account[2] = asyncio.run(self.update_tiles(account[0],account[1],account[2],1)).copy()
                        if offline:
                            offline = False
                            self.mylist.insert(END,"Connection Restored")
                        asyncio.run(self.main(1,account[2]))
                        self.start_time = time.time()
                    except Exception as e:
                        if "getaddrinfo failed" in str(e):
                            print("Failed to connect to tile account " + account[0] + ", please check internet connection. Attempting to reconnect again in "+ str(settings[0]) + " seconds.")
                            if not offline:
                                self.mylist.insert(END,"Failed to connect to tile servers. Attempting to reconnect again in "+ str(settings[0]) + " seconds.")
                            offline = True
                        else:
                            print("An unkown error has occured while attempting to update tiles, trying again in "+ settings[0] + " seconds.")
                            print(e)
                if not self.updates_avalible:
                    print("No new information availible, cheking again in " + settings[0] + " seconds.")
                else:
                    self.updates_avalible = False

                self.start_time = time.time()
            self.update_idletasks()
            self.update()
            
