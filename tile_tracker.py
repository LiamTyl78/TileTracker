import asyncio, time, Mail, csv, os

from tkinter import *
from tkinter.ttk import Treeview
from pyppeteer import launch
from app2 import USERNAME,PASSWORD,USERNAME2,PASSWORD2, EMAIL3,PASSWORD3

from aiohttp import ClientSession
from geofence import GeoFence
from pytile import async_login

root = Tk()
group1 = LabelFrame(root, text="Tracked Tiles", padx=5, pady=5)
group2 = LabelFrame(root,text="Tracking Log", padx=5, pady=5)

scrollbar = Scrollbar(group1,orient='vertical')
tree = Treeview(group1, columns=('name','timestamp','location'),show="headings",yscrollcommand = scrollbar.set)
mylist = Listbox(group2, width=50 )
geofences = []
emails = []
update_time = 120


class tiletraker:
    async def initialize_tiles(self, email, password):
        async with ClientSession() as session:
        
            api = await async_login(email, password, session)
    
            tiles = await api.async_get_tiles()

            for tile_uuid, tile in tiles.items():
                tile.account = email

        return tiles
    
    def initialize_files(self):
        with open('Geofences.csv', mode = 'r')as file: #function appends all geofences list so program can compare to all geofences when checking location
        
            # reading the CSV file
            csvFile = csv.reader(file)
            i = 0

            # displaying the contents of the CSV file
            for lines in csvFile:
                    if i > 0:
                        geofences.append(GeoFence(lines[0],lines[1],lines[2],lines[3],lines[4]))
                    i = i + 1
        with open('emails.csv', mode = 'r')as file: #this file houses a list of all the emails you want to send location updates to and the function appends the emails so the program knows what emails to send to
            csvFile = csv.reader(file) 
            i = 0
            for lines in csvFile:
                if i > 0:
                    emails.append(lines[0])
                i = i + 1
        
        
    #Grabs updates from the tile by creating new tile objects from the api and carries over the last_location and last_time variables to the new tile objects created and then returns the updated
    #tile objects in the new list
    async def update(self, email, password, tiles):
        async with ClientSession() as session:

            self.tiles2 = tiles.copy()
            api = await async_login(email, password, session)
            tiles = await api.async_get_tiles()
            for tile_uuid, tile in tiles.items():
                # if tiles.__contains__
                tile.lasttime = self.tiles2[tile.uuid].lasttime
                tile.lastlocation = self.tiles2[tile.uuid].lastlocation
                tile.account = email
                
        
        return tiles
    
    #Checks the location of the tile given in the parameter
    #loops through the geofence list until the longitude and latitude of the tile fall 
    #into one of the geofences then location_found is set to true and then breaks the loop retuning the location
    #if a location is not found outside is returned
    def check_location(self,tile):
        location_found = False
        for geofence in geofences: 
            if (tile.latitude > geofence.BotLat and tile.latitude < geofence.TopLat) and (tile.longitude < geofence.BotLong and tile.longitude > geofence.TopLong):
                location = geofence.name
                location_found = True
            else:
                if location_found:
                    break
                location = "Outside"
        return location
    
    async def capture_map(self, latitude, longitude):
        
        clip = {
        'x': 900,    
        'y': 325,     
        'width': 400,
        'height': 400
        }
        path = os.path.join(os.getcwd(), 'map.png')
        executable_path = r'C:\Users\e-tyl\OneDrive - Rowan University\TileTraker\chrome-win\chrome.exe'
        browser = await launch(headless=True, executablePath=executable_path)
        url = 'https://www.google.com/maps/place/' + str(latitude) + ',' + str(longitude) + '/@' + str(latitude) + ',' + str(longitude - 0.003) + ',16z'
        
        print(f'navigating to {url}')
        
        page = await browser.newPage()

        await page.setViewport({'width': 1920, 'height': 1080})
        await page.goto(url)
        await page.screenshot({'path': path, 'clip': clip})
        await browser.close()

        print(f'Screenshot saved to {path}')
    
    async def main(self, runtype, tiles) -> None:
        for tile_uuid, tile in tiles.items():
            
            if tile.name == 'Wallet': 
                await self.capture_map(tile.latitude, tile.longitude)
                for email in emails:
                    address = email
                    email = Mail.email(address,'Tile has left '+ tile.lastlocation, ('The tile \'' + tile.name + '\' has exited the geofence \'' + tile.lastlocation + '\' its last location was at ' + str(tile.latitude) + ' ' + str(tile.longitude)))
                    email.send()
                    print(f'location email sent for {tile.name} to {address}')
            else:
                print("false")

            if not (tile.last_timestamp == tile.get_lasttime()):
                location = self.check_location(tile)
                mylist.insert(END, str(tile.name) + " " + str(tile.last_timestamp) + " Location: " + location)
                if runtype == 0: #runtype determines whether you're updating the information(1) in the TKinter tree view or initializing it(0)
                    tree.insert('', 'end', str(tile.name), values=(tile.name,tile.last_timestamp, location,tile.account))
                else:
                    tree.delete(str(tile.name))
                    tree.insert('', 'end', str(tile.name), values=(tile.name,tile.last_timestamp, location,tile.account))
                    print("Last Location: ",tile.get_lastlocation())
                    
                    if(location == "Outside" and not tile.lastlocation == "Outside") or (not location == "Outside" and tile.lastlocation == "Outside"):
                        await self.capture_map(tile.latitude, tile.longitude)
                    if(location == "Outside" and not tile.lastlocation == "Outside"):
                        # await self.capture_map(tile.latitude, tile.longitude)
                        for email in emails:
                            address = email
                            email = Mail.email(address,'Tile has left '+ tile.lastlocation, ('The tile \'' + tile.name + '\' has exited the geofence \'' + tile.lastlocation + '\' its last location was at ' + str(tile.latitude) + ' ' + str(tile.longitude)))
                            email.send()
                            print(f'location email sent for {tile.name} to {address}')
                    elif(not location == "Outside" and tile.lastlocation == "Outside"):
                        for email in emails:
                            address = email
                            email = Mail.email(address,'Tile has entered '+ location, ('The tile \'' + tile.name + '\' has entered the geofence \'' + location + '\' its last location was at ' + str(tile.latitude) + ' ' + str(tile.longitude)))
                            email.send()
                            print('location email sent for\'', tile.name, '\'to ', address)
                tile.set_lastlocation(location)
                tile.set_lasttime(tile.last_timestamp)
                # print(tile_uuid)
                
                print(tile.name,tile.get_lastlocation(), str(tile.last_timestamp))
                print(str(tile.latitude) + " " + str(tile.longitude))
    
    
    def run(self):
        def refresh():
            try:
                self.tiles2=asyncio.run(self.update(USERNAME2,PASSWORD2,self.tiles2))
                asyncio.run(self.main(1,self.tiles2))
                self.start_time = time.time()
            except:
                print("Failed to connect, attempting to reconnect again in", update_time, "seconds.")

        self.start_time = time.time()
        root.title("Tile Tracker")
        self.initialize_files()
        initilized = False
        current_time = (time.time() + update_time + 1)
        while not initilized:
            
            if current_time > (self.start_time + update_time):
                try:
                    self.tiles2=asyncio.run(self.initialize_tiles(USERNAME2,PASSWORD2))
                    asyncio.run(self.main(0,self.tiles2))
                    initilized = True
                except ConnectionAbortedError:
                    print("Failed to connect, attempting to reconnect again in", update_time, " seconds.")
                except Exception as e:
                    print("An error has occured while attempting to update tiles, trying again in", update_time , " seconds.")
                    print(e)
                self.start_time = time.time()
            current_time = time.time()
        
        group1.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=S+E+W+N)
        group2.grid(row=1, column=0, padx=10, pady=10, sticky=N+E+W+S)
        
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(0,weight=1)
        
        group1.grid_rowconfigure(0, weight=1)
        group1.grid_columnconfigure(0, weight=1)

        group2.grid_rowconfigure(0, weight=1)
        group2.grid_columnconfigure(0, weight=1)

        tree['columns'] = ('name','timestamp', 'location','account')
        tree.column('name',width=60)
        tree.heading('name',text="Name")
        tree.column('timestamp',width=120)
        tree.heading('timestamp',text="Timestamp")
        tree.column('location',width=120)
        tree.heading('location',text="Location")
        tree.column('account',width=120)
        tree.heading('account',text="Account")
        tree.grid(row=0,column=0,sticky=E+W+N+S)
        
        scrollbar.grid(column=1,row=0,sticky='nse')
        scrollbar.config( command = tree.yview )
        
        mylist.grid(row=1,column=0,sticky=S+N+E+W)

        refreshButton = Button(text="refresh", command=refresh)
        refreshButton.grid(row=2,column=0)

        self.start_time = time.time()
        while True:
            current_time = time.time()
            time.sleep(0.1)
            if current_time > (self.start_time + update_time):
                try:
                    self.tiles2 = asyncio.run(self.update(USERNAME2,PASSWORD2,self.tiles2))
                    asyncio.run(self.main(1,self.tiles2))
                except ConnectionAbortedError:
                    print("Failed to connect, attempting to reconnect again in"+ str(update_time) + "seconds.")
                except Exception as e:
                    print("An error has occured while attempting to update tiles, trying again in" + str(update_time) + "seconds.")
                    print(e)
                
                self.start_time = time.time()
            root.update_idletasks()
            root.update()
