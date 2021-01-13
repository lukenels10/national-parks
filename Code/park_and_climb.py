#LIBRARIES WE NEED:


import json    #NPS; MP
from datetime import date, timedelta   #NPS
from math import sin, cos, sqrt, atan2, radians    #DISTANCE FUNCTION
from bs4 import BeautifulSoup    #WEATHER, INSIDE HOOK
import urllib    #WEATHER, INSIDE HOOK
import requests    #WEATHER, INSIDE HOOK, NPS, MP
from statistics import mean    #WEATHER
import gmaps #GOOGLE MAPS
from ipywidgets.embed import embed_minimal_html    #GOOGLE MAPS
import webbrowser    #GOOGLE MAPS
import os    #GOOGLE MAPS


#NPS FUNCTION
#Function to print all the summary info about the park

def national_park_info(park_name, nps_api_key):
    park_info=dict()
    
    try:
        #Access the NPS API with park name
        error1=park_name[0]    #This protects against the user entering '' for the park_name
        error2=len(park_name)/(len(park_name)-1)    #Park name has to be more than 1 character, otherwise yields random match
        resp=requests.get('https://developer.nps.gov/api/v1/parks?q='+park_name+'&api_key='+nps_api_key)
        js=resp.json()
        error3=js['data'][0] #this protects against the user entering a park name that does not exist
    
    except:
        print('Please enter a valid park name and valid API keys!')
        return
    
    #Check to see if the park returned by the JSON is the park intended by the user
    park_checker=input('Did you intend to search for '+js['data'][0]['fullName']+'? Please respond [Yes/No] to continue:\n')
    if park_checker != 'Yes':
        print('That is Okay!')
        return
    else:
    
        #Add park name to dict
        park_info['name']=js['data'][0]['fullName']

        #The state the park is in
        state=js['data'][0]['states']
        park_info['state']=state

        #ParkCode
        parkCode=js['data'][0]['parkCode']
        park_info['parkCode']=parkCode
        
        #ParkDesignation
        parkDesignation=js['data'][0]['designation']
        park_info['designation']=parkDesignation

        #The coordinates for the park
        coordinates=js['data'][0]['latLong']
        coordinates=coordinates.split(',')
        lat_colon=coordinates[0].find(':')
        latitude=float(coordinates[0][lat_colon+1:])
        lon_colon=coordinates[1].find(':')
        longitude=float(coordinates[1][lon_colon+1:])
        new_coordinates=(latitude,longitude)
        park_info['coordinates']=new_coordinates

        #Park Description
        description=js['data'][0]['description']
        park_info['description']=description

        #General Weather
        weather=js['data'][0]['weatherInfo']
        park_info['weather']=weather

        #URL.
        url=js['data'][0]['url']
        park_info['url']=url

        #Get information about the other parks within the state
        resp2=requests.get('https://developer.nps.gov/api/v1/parks?stateCode='+state+'&api_key='+nps_api_key)
        js2=resp2.json()

        sites=dict()
        total_parks=js2['total']
        site_info=js2['data']
        for item in site_info:
            x=item['designation']
            sites[x]=sites.get(x,0)+1
        park_info['other_parks']=total_parks
        park_info['other_parks_details']=sites

        #URL for all parks in the state
        park_info['other_parks_url']='https://www.nps.gov/state/'+state+'/index.htm'

        #Get information on Live-real time alerts within the park
        resp3=requests.get('https://developer.nps.gov/api/v1/alerts?parkCode='+parkCode+'&api_key='+nps_api_key)
        js3=resp3.json()
        number_of_alerts=js3['total']
        park_info['number_of_alerts']=number_of_alerts
        if number_of_alerts != '0':
            alerts=dict()
            alert_info=js3['data']
            for item in alert_info:
                x=item['title']
                y=item['description']
                z=item['url']
                alerts[x]=[y,z]
            park_info['alert_details']=alerts
        else:
            park_info['alert_details']='There are no alerts at this time.'

        #Get data on Live Events happening tomorrow or within 4 weeks 
        startDate=str(date.today()+timedelta(days=1))
        endDate=str(date.today()+timedelta(days=28))
        resp4=requests.get('https://developer.nps.gov/api/v1/events?parkCode='+parkCode+'&api_key='+nps_api_key+'&dateStart='+startDate+'&dateEnd='+endDate)
        js4=resp4.json()
        number_of_events=js4['total']
        park_info['number_of_events']=number_of_events
        if number_of_events != '0':
            events=dict()
            event_info=js4['data']
            for item in event_info:
                try:
                    x=item['description']
                    x=x.replace('<p>','')
                    x=x.replace('</p>','')
                    z=item['datestart']
                    events[x]=z
                except:
                    events[item['description']]='Unfortunately there is no datestart'
            park_info['event_details']=events
        else:
            park_info['event_details']='There are no events within the next 4 weeks at this time.'

        #return dictionary
        return park_info



#DISTANCE FUNCTION
#This formula takes the distance (in miles) bewteen two points of the form parameters tuple - (lat1, long1), tuple - (lat2, long2) and returns distance in kms between both (lat, long) tuples.

def dist(point1, point2):
    # approximate radius of earth in km
    R = 6373.0
    lat1 = radians(point1[0])
    lon1 = radians(point1[1])
    lat2 = radians(point2[0])
    lon2 = radians(point2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c #in km
    distance=distance * 0.62137 #converted to miles
    distance=round(distance,2)
    return distance




#MOUNTAIN PROJECT FUNCTION
def get_climbs(park_info, mp_api_key, easiest, hardest, radius, preferred_type):
    
    
    latitude=str(park_info['coordinates'][0])
    longitude=str(park_info['coordinates'][1])
    park_coords=park_info['coordinates']
    
    try:
        resp=requests.get('https://www.mountainproject.com/data/get-routes-for-lat-lon?lat='+latitude+'&lon='+longitude+'&maxDistance='+radius+'&minDiff='+easiest+'&maxDiff='+hardest+'&key='+mp_api_key)
        js=resp.json()
        data=js['routes']
    except:
        print('Please enter valid inputs!')
        return
    
    #Create a dictionary for all climbs of the specified type
    all_climbs=dict()
    for item in data:
        if preferred_type in item['type']:
            all_climbs[item['name']]=[item['stars'],item['url'],item['rating'],item['pitches'],(item['latitude'],item['longitude']),item['type']]
        else:
            continue

    #Sort dictionary by Star Rating. tmp stands for temporary since this is a temporary list for sorting
    tmp=[]
    for a,b in all_climbs.items():
        newtup=(b,a)
        tmp.append(newtup)
    tmp.sort(reverse=True)

    #If there are zero climbs or fewer than 5 climbs, let the user know:
    if len(tmp)== 0:
        #print('Unfortunately there are no climbs within your specified constraints. Please try broadening them.')
        return
    
    #Turn the list into the top 5 rated climbs
    climbs=tmp[:5]


    #Turn back into a dictionary with name as the key and star rating back as a value
    climbs_dct=dict()
    for a,b in climbs:
        climbs_dct[b]=a

    #Calculate distance between the 5 climbs and the national park
    #Then feed the lat lon and the park_coords into the distance function and append the distance to climbs_dct 
    for a,b in climbs_dct.items():
        distance_from_park=dist(park_coords,b[4])
        climbs_dct[a].append(distance_from_park)
        
    #Make each climb into a dictionary and make a list of dictionaries so making the google map will be easier. Top5 refers to our Top5 climbs
    Top5=list()
    for a,b in climbs_dct.items():
        d=dict()
        d['name']=a
        d['stars']=b[0]
        d['distance']=b[6]
        d['type']=b[5]
        d['rating']=b[2]
        d['pitches']=b[3]
        d['coordinates']=b[4]
        d['url']=b[1]
        Top5.append(d)
    
    #return list
    return Top5  



#RECOMMENDATION FROM INSIDE HOOK IF NATIONAL PARK
#If the user entered a national park, give inside hook's recommendation as to what to do there

def get_recommendations(park_info):
    if park_info['designation']=='National Park':
        park_name=park_info['name']
        html=urllib.request.urlopen("https://www.insidehook.com/feature/travel/best-activity-all-59-us-national-parks").read()
        soup=BeautifulSoup(html,'html.parser')
        switch=True
        for link in soup.find_all('p'):
            title=link.get_text()
            title=title.rstrip()
            if switch==False:
                return 'At this park, the online lifestyle publication, Inside Hook, recommends you: '+title.replace('\xa0',' ')
            elif park_name in title:
                switch=False
                continue 
    else:
        return('The online lifestyle publication, Inside Hook, does not have any recommendations for this park. Try a National Park and they very well might!')





#WEATHER FORECAST
#Return tomorrow's forecast at the park and then the mean of the High and Low extended forecast
#Note, I know weather.gov has an API but decided to scrape to validate one of the requirements of the project rubric. I ran this by Yigal and he is okay with it

def get_weather(park_info):
    
    lat=str(park_info['coordinates'][0])
    lon=str(park_info['coordinates'][1])

    #Connect to website and retrieve html
    html=urllib.request.urlopen("http://forecast.weather.gov/MapClick.php?lat="+lat+"&lon="+lon).read()
    soup=BeautifulSoup(html,'html.parser')
    forecast=soup.find(id="seven-day-forecast")
    forecast_info = forecast.find_all(class_="tombstone-container")

    weather_forecast=dict()
    weather_forecast['temps_high']=[]
    weather_forecast['temps_low']=[]
    switch=False
    count=0

    #Get the forecast for tomorrow. Since there is no period "tomorrow" in the html, we have to create a switch, because tomorrow could be any day of the week.
    #the html has "Today, This Afternoon, Tonight, etc." but no "Tomorrow"
    for item in forecast_info:
        period=item.find(class_="period-name").get_text()
        description=item.find("img")
        description2=description['title']
        temperature=item.find(class_="temp").get_text()

        if switch==True:
            weather_forecast['tomorrows_forecast']=[period,description2,temperature]
            break
        elif period=='Tonight':
            switch=True
            continue
        else:
            continue

    #Get the high and low temps in the extended forecast so we can return and average
    for item in forecast_info:
        temperature=item.find(class_="temp").get_text()    
        temperature=temperature.split(': ')
        temperature[1]=temperature[1][:-3]
        temperature[1]=float(temperature[1])
        if temperature[0]=='High':
            weather_forecast['temps_high'].append(temperature[1])
        elif temperature[0]=='Low':
            weather_forecast['temps_low'].append(temperature[1])
    
    #Get the average and count of forecasted high and low temps
    #This way we can return the mean high and low temperatures for the following number of periods given in the extended forecast (Ex. The 5 period average high is 45 degrees F)
    weather_forecast['high_count']=len(weather_forecast['temps_high'])
    weather_forecast['high_mean']=mean(weather_forecast['temps_high'])
    weather_forecast['low_count']=len(weather_forecast['temps_low'])
    weather_forecast['low_mean']=mean(weather_forecast['temps_low'])

    return weather_forecast


# GOOGLE MAPS
# mention that this required pip install gmaps

def park_and_climbs_visual(park_info, Top5, goog_api_key):
    if Top5 is None:
        print('There are no climbs to be shown. Please re-run the program with broader specifications')
        return
    else:
        gmaps.configure(api_key=goog_api_key)

        ntl_park_coords = []
        ntl_park_coords.append(park_info['coordinates'])

        # Create the map figure
        fig = gmaps.figure()

        # Create the National Park symbol that is blue so it stands out from the climbs
        park_dot = gmaps.symbol_layer(ntl_park_coords, fill_color='green', stroke_color='blue', scale=7)

        # Create Markers for the Top 5 climbing routes
        climb_locations = [climb['coordinates'] for climb in Top5]
        climb_names = [climb['name'] + '-' + climb['rating'] for climb in Top5]
        info_box_template = """
        <dl>
        <dt>Name</dt><dd>{name}</dd><br><br>
        <dt>Rating</dt><dd>{rating}</dd><br><br>
        <dt>Stars</dt><dd>{stars}</dd><br><br>
        <dt>Climb Type</dt><dd>{type}</dd><br><br>
        <dt>Pitches</dt><dd>{pitches}</dd><br><br>
        <dt>Distance From National Park (miles)</dt><dd>{distance}</dd><br><br>
        <a href={url}>Link to Climb Info</a>
        </dl>
        """
        climb_info = [info_box_template.format(**climb) for climb in Top5]

        # Create park and climb marker layers and add them to the GMAPS figure (fig for short)
        climb_marker_layer = gmaps.marker_layer(climb_locations, hover_text=climb_names, info_box_content=climb_info)
        park_marker_layer = gmaps.marker_layer(ntl_park_coords,
                                               hover_text=park_info['name'] + ', ' + park_info['state'],
                                               info_box_content=park_info['description'])
        fig = gmaps.figure()
        fig.add_layer(climb_marker_layer)
        fig.add_layer(park_marker_layer)
        fig.add_layer(park_dot)


        new_p=os.path.normpath(os.getcwd() + os.sep + os.pardir)    #The parent Directory LUKE_NELSON_homework5
        new_p_out=os.path.join(new_p,'Output')    #The folder "Output"
        os.chdir(new_p_out)    #Change cd to be the Output folder so that we can save html there
        embed_minimal_html('park_and_climbs_visual.html', views=[fig])    #Save the google map as html in Output folder
        url='file://'+os.path.join(new_p_out,'park_and_climbs_visual.html')    #Create url for Mac users
        try:
            webbrowser.open_new_tab('park_and_climbs_visual.html')    #For PC open the html in web browser
            webbrowser.open(url, new=2)  # For Mac open the html in web browser
        except:
            return






