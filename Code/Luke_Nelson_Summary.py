#code to pull from module, save API Keys, Print summary, create google map

import sqlite3
import park_and_climb
from sys import argv
import os

#Change cd to Output folder so that database table is saved there instead of in the code folder
new_p = os.path.normpath(os.getcwd() + os.sep + os.pardir)  # The parent Directory LUKE_NELSON_homework5
new_p_out = os.path.join(new_p, 'Output')  # The folder "Output"
os.chdir(new_p_out)  # Change cd to be the Output folder so that we can save the database table there


#Create a database to store your API keys so you don't have to manually re-enter them every time you run the program
conn = sqlite3.connect('park_and_climb')
c = conn.cursor()

#get the count of tables with the name to see if there are already API keys
c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='api_keys' ''')

#if the count is 1, then table exists
#Allow for the user to enter new api keys if they want otherwise they dont have to go through the hassle of doing so each time
if c.fetchone()[0]==1 :
    re_create=input('It looks like there is already a table of API keys. Would you like to update your keys? [Yes/No]')
    if re_create=='Yes':
        c.execute('''DROP TABLE api_keys''')
        c.execute('''CREATE TABLE api_keys (key_type TEXT, key TEXT)''')
        nps_api_key=input('Please enter your NPS API Key:\n')
        mp_api_key=input('Please enter your Mountain Project API Key:\n')
        goog_api_key=input('Please enter your Google API Key:\n')
        c.execute('INSERT INTO api_keys VALUES(?, ?)', ('nps_api_key', nps_api_key))
        c.execute('INSERT INTO api_keys VALUES(?, ?)', ('mp_api_key', mp_api_key))
        c.execute('INSERT INTO api_keys VALUES(?, ?)', ('goog_api_key', goog_api_key))
        conn.commit()
    else:
        c.execute('SELECT key FROM api_keys WHERE key_type = "nps_api_key"')
        nps_api_key=c.fetchall()
        nps_api_key=nps_api_key[0][0]

        c.execute('SELECT key FROM api_keys WHERE key_type = "mp_api_key"')
        mp_api_key=c.fetchall()
        mp_api_key=mp_api_key[0][0]
        
        c.execute('SELECT key FROM api_keys WHERE key_type = "goog_api_key"')
        goog_api_key=c.fetchall()
        goog_api_key=goog_api_key[0][0]
        

else:
    c.execute('''CREATE TABLE api_keys (key_type TEXT, key TEXT)''')
    nps_api_key=input('Please enter your NPS API Key:\n')
    mp_api_key=input('Please enter your Mountain Project API Key:\n')
    goog_api_key=input('Please enter your Google API Key:\n')
    c.execute('INSERT INTO api_keys VALUES(?, ?)', ('nps_api_key', nps_api_key))
    c.execute('INSERT INTO api_keys VALUES(?, ?)', ('mp_api_key', mp_api_key))
    c.execute('INSERT INTO api_keys VALUES(?, ?)', ('goog_api_key', goog_api_key))
    conn.commit()


#Change the cd back so that we can access the park_and_climb module
new_p_code = os.path.join(new_p, 'Code')  # The folder "Output"
os.chdir(new_p_code)  # Change cd to be the Output folder so that we can save the database table there

#Request the user for the inputs required for the functions to return the data


#The name of the park they would like to visit
park_name=input('Please enter the name of a U.S. National Park Service maintained park.\nEx. Rocky Mountain National Park, Dinosaur National Monument, Lincoln Memorial, etc.\n')

#The easiest difficulty of climb the person is willing to climb
easiest=input('Please enter the easiest difficulty you are willing to climb.\nEx. 5.8 (Climbing difficulties range from 5.6 - 5.14 and always include the decimal point)\n')

#The hardest difficulty of climb the person is willing to climb
hardest=input('Please enter the hardest difficulty you are willing to climb.\nEx. 5.10 (Climbing difficulties range from 5.6 - 5.14 and always include the decimal point)\n')

#The distance in miles from the park the person is willing to consider for a climbing route
radius=input('Please enter the distance (in miles) from the park you are willing to consider a climbing route. You do not need to enter units.\nEx. 30\n')

#The climbers preferred climbing route type
preferred_type=input('Please enter the type of climb you are looking for. Enter [Sport/Trad/TR/Alpine]:\n')

#Dictionary of data for the park chosen by the user
park_info=park_and_climb.national_park_info(park_name, nps_api_key)

if park_info is None:
    print('Please re-run the program and try typing in new conditions!')

else:
    #List of dictionaries where each dictionary is one of the highest rated climbs returned
    climb_info=park_and_climb.get_climbs(park_info, mp_api_key, easiest, hardest, radius, preferred_type)


    #String Recommendation from Inside Hook for what to do at the park if it is a National Park
    recommendation=park_and_climb.get_recommendations(park_info)


    #Dictionary of Weather forecast data at the location of the park, including forecast for tomorrow and data on extended temp forecast
    weather_forecast=park_and_climb.get_weather(park_info)

####SUMMARY INFORMATION######


    #National Park Summary Information
    print('\nSUMMARY:\n')
    print(park_info['name'],'is a',park_info['designation'],'within the state of',park_info['state']+'.')
    print(park_info['description'])
    print('Park URL:', park_info['url'])
    print('\nTypical weather as provided by the park is as follows. An accurate forecast for tomorrow and the extended forecast will be provided later on below:\n',park_info['weather'])
    print()
    if park_info['number_of_alerts']=='0':
        print(park_info['alert_details'])
    else:
        count=1
        print('There are currently '+park_info['number_of_alerts']+' alerts for this park given by the US National Park Service. Details are as follows:')
        for a,b in park_info['alert_details'].items():
            print(count)
            count=count+1
            print(a)
            print(b[0])
            print(b[1])
            print()

    if park_info['number_of_events']=='0':
        print(park_info['event_details'])
    else:
        count2=1
        print('\nThere are currently '+park_info['number_of_events']+' events happening over the next 4 weeks. Details are as follows:')
        for a,b in park_info['event_details'].items():
            print(count2)
            count2=count2+1
            print(a)
            print('This event is happening:',b)
            print()

    print('\nThere are',park_info['other_parks'], 'other US National Park Service maintained parks within',park_info['state']+'. Please see a list of the other types of parks below:')
    for a,b in park_info['other_parks_details'].items():
        print(a,':',b)
    print('URL for other parks in the state:',park_info['other_parks_url'])
    print()

    #Inside Hook Recommendation
    print(recommendation)

    #Real-time Weather Forecast
    print("\nTomorrow's weather forecast at",park_info['name']+':')
    print(weather_forecast['tomorrows_forecast'][1])
    print(weather_forecast['tomorrows_forecast'][2])
    print('The average High temperature over the next',weather_forecast['high_count'],'periods is',weather_forecast['high_mean'], 'degrees Fahrenheit')
    print('The average Low temperature over the next',weather_forecast['low_count'],'periods is',weather_forecast['low_mean'], 'degrees Fahrenheit')

    #Information on returned climbing routes
    if climb_info is None:
        print('\nUnfortunately there are no climbs within your specified constraints. Please try broadening them. As a result, a map will not be printed at this time.')
    else:
        print('\nBelow you will find information on the highest rated climbs returned from your query:')
        for i in climb_info:
            for a,b in i.items():
                print(a+':',b)
            print()

        #See Google Map
        print('A new window should have been opened in your internet browser. Please navigate there to view where the park is relative to the climbing routes. Otherwise, an html has been saved in the Output folder - please open it to see the map. Hover over and click on the markers to get useful information.\nHave a wonderful adventure!')
        park_and_climb.park_and_climbs_visual(park_info,climb_info,goog_api_key)