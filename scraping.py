from bs4 import BeautifulSoup
import requests

temp_dict = {}
city_dict = {
            "sydney": 2147714,
            "melbourne": 2158177,
            "brisbane": 2174003,
            "perth": 2063523,
            "adelaide": 2078025,
            "canberra": 2172517,
            "hobart": 2163355,
            "darwin": 2073124
            }

for key in city_dict.keys():
    req = requests.get('https://www.bbc.com/weather/'+str(city_dict[key]))
    soup = BeautifulSoup(req.text, features="lxml")
    weather = soup.find_all("span", {"class":"wr-value--temperature--c"})
    weather_list = []
    for i in range(2):
        temp = weather[i].__dict__['contents'][0]
        weather_list.append(temp)
    temp_dict[key] = weather_list

print(temp_dict)


