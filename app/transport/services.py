from datetime import datetime
from django.db.models.aggregates import Count
from rest_framework.exceptions import AuthenticationFailed

from rest_framework.authtoken.models import Token
from helpers.global_helper.exceptions import api_exc
from helpers.global_helper.object_generator import *
from transport.selectors import get_company_details
from transport.utils import send_change_signal
from .models import *
import requests
import json
from .models import *
from .constants import *
from .serializers import *
from django.db import connection, transaction
from .helpers import *
import urllib
from django.core.exceptions import ObjectDoesNotExist
from .validators import validate_company_documents, validate_stock_images
from mailer.confirm_company_mailer import send_company_confirmation_email
from accounts.models import Account
from django.shortcuts import get_object_or_404

from push_notifications.push_transport import *

COUNTRIES_TO_ADD = ['DE', 'HR', 'BA', 'AT']



def insert_countries():
    r = requests.get("https://restcountries.eu/rest/v2/region/europe")
    data = json.loads(r.text)
    arr = []
    for i in data:
        if i['alpha2Code'] in COUNTRIES_TO_ADD:
            arr.append(Country(name=i['name'], alpha2Code=i['alpha2Code']))
    Country.objects.bulk_create(arr)
    # City.objects.create(country_id=1, name="Testni grad 1")
    # ZipCode.objects.create(city_id=1, code="111222")
    return True


@transaction.atomic
def insert_cities_zip_codes():
    countries = COUNTRIES_TO_ADD
    #Nema gradova: RS, SE, 'UA', 'GB', CH, 'LU', LI
    # countries = ['HR']
    for c in countries:
        url = f'https://parseapi.back4app.com/classes/{c}?limit=1000000'
        headers = {
            'X-Parse-Application-Id': 'zS2XAEVEZAkD081UmEECFq22mAjIvX2IlTYaQfai',
            # This is the fake app's application id
            'X-Parse-Master-Key': 't6EjVCUOwutr1ruorlXNsH3Rz65g0jiVtbILtAYU'
            # This is the fake app's readonly master key
        }
        data = json.loads(
            requests.get(url, headers=headers).content.decode('utf-8'))  # Here you have the data that you need
        # print(json.dumps(data, indent=2))
        data = data['results']
        # print(data)
        unique_cities_names = []
        unique_cities = []
        zip_codes_city = []
        zip_codes_names = []
        country_id = Country.objects.get(alpha2Code=c).id
        for i in data:
            if not i['adminName3'] in unique_cities_names:
                unique_cities_names.append(i['adminName3'])
                unique_cities.append(City(name=i['adminName3'], country_id=country_id))
                zip_codes_city.append({
                    'city': i['adminName3'],
                    'zip_codes': []
                })
        City.objects.bulk_create(unique_cities)

        for i in data:
            if not i['postalCode'] in zip_codes_names:
                zip_codes_names.append(i['postalCode'])
                for k in zip_codes_city:
                    if k['city'] == i['adminName3']:
                        k['zip_codes'].append(i['postalCode'])
                        break
        for i in zip_codes_city:
            city_id = City.objects.get(name=i['city'], country_id=country_id).id
            zip_codes_arr = []
            for z in i['zip_codes']:
                zip_codes_arr.append(ZipCode(code=z, city_id=city_id))
            ZipCode.objects.bulk_create(zip_codes_arr)

    return True

def insert_bih_cities_and_zip_codes():
    data = [
        {
            "zip": "78255",
            "city": "Aleksandrovac "
        },
        {
            "zip": "77246",
            "city": "Arapuša "
        },
        {
            "zip": "76219",
            "city": "Arizona "
        },
        {
            "zip": "89245",
            "city": "Avtovac "
        },
        {
            "zip": "72286",
            "city": "Babanovac "
        },
        {
            "zip": "75290",
            "city": "Banovići "
        },
        {
            "zip": "78000",
            "city": "Banja Luka "
        },
        {
            "zip": "74273",
            "city": "Banja Vrućica "
        },
        {
            "zip": "70267",
            "city": "Baraći "
        },
        {
            "zip": "76312",
            "city": "Batković "
        },
        {
            "zip": "72233",
            "city": "Begov Han "
        },
        {
            "zip": "73207",
            "city": "Berič "
        },
        {
            "zip": "88363",
            "city": "Berkovići "
        },
        {
            "zip": "77000",
            "city": "Bihać "
        },
        {
            "zip": "76204",
            "city": "Bijela "
        },
        {
            "zip": "73263",
            "city": "Bijelo Brdo "
        },
        {
            "zip": "76300",
            "city": "Bijeljina "
        },
        {
            "zip": "76321",
            "city": "Bijeljinsko Suho Polje "
        },
        {
            "zip": "72256",
            "city": "Bila "
        },
        {
            "zip": "71253",
            "city": "Bilalovac "
        },
        {
            "zip": "89230",
            "city": "Bileća "
        },
        {
            "zip": "88268",
            "city": "Biletić Polje "
        },
        {
            "zip": "72248",
            "city": "Bilješevo "
        },
        {
            "zip": "70262",
            "city": "Bjelajci "
        },
        {
            "zip": "88407",
            "city": "Bjelimići "
        },
        {
            "zip": "88201",
            "city": "Blagaj "
        },
        {
            "zip": "70259",
            "city": "Blagaj Kod Kupresa "
        },
        {
            "zip": "74275",
            "city": "Blatnica "
        },
        {
            "zip": "88263",
            "city": "Blatnica "
        },
        {
            "zip": "71215",
            "city": "Blažuj "
        },
        {
            "zip": "76210",
            "city": "Boće "
        },
        {
            "zip": "76277",
            "city": "Bok "
        },
        {
            "zip": "74322",
            "city": "Boljanić "
        },
        {
            "zip": "88405",
            "city": "Boračko Jezero "
        },
        {
            "zip": "73225",
            "city": "Borike "
        },
        {
            "zip": "88365",
            "city": "Borojevići "
        },
        {
            "zip": "77240",
            "city": "Bosanska Krupa "
        },
        {
            "zip": "74414",
            "city": "Bosanski Dubočac "
        },
        {
            "zip": "77250",
            "city": "Bosanski Petrovac "
        },
        {
            "zip": "80270",
            "city": "Bosansko Grahovo "
        },
        {
            "zip": "74221",
            "city": "Bosansko Suho Polje "
        },
        {
            "zip": "88408",
            "city": "Bradina "
        },
        {
            "zip": "75420",
            "city": "Bratunac "
        },
        {
            "zip": "76000",
            "city": "Brčko "
        },
        {
            "zip": "77205",
            "city": "Brekovica "
        },
        {
            "zip": "74210",
            "city": "Brestovo "
        },
        {
            "zip": "71255",
            "city": "Brestovsko "
        },
        {
            "zip": "71370",
            "city": "Breza "
        },
        {
            "zip": "79208",
            "city": "Brezičani "
        },
        {
            "zip": "76216",
            "city": "Brezovo Polje "
        },
        {
            "zip": "74206",
            "city": "Brijesnica Kod Doboja "
        },
        {
            "zip": "76206",
            "city": "Brka "
        },
        {
            "zip": "72243",
            "city": "Brnjic "
        },
        {
            "zip": "88243",
            "city": "Broćanac "
        },
        {
            "zip": "73309",
            "city": "Brod "
        },
        {
            "zip": "76313",
            "city": "Brodac "
        },
        {
            "zip": "78204",
            "city": "Bronzani Majdan "
        },
        {
            "zip": "74459",
            "city": "Brusnica Velika "
        },
        {
            "zip": "72295",
            "city": "Bučići "
        },
        {
            "zip": "79269",
            "city": "Budimlić Japra "
        },
        {
            "zip": "70230",
            "city": "Bugojno "
        },
        {
            "zip": "75203",
            "city": "Bukinje "
        },
        {
            "zip": "74277",
            "city": "Buletić "
        },
        {
            "zip": "88202",
            "city": "Buna "
        },
        {
            "zip": "74416",
            "city": "Bunar "
        },
        {
            "zip": "88366",
            "city": "Burmazi "
        },
        {
            "zip": "72260",
            "city": "Busovača "
        },
        {
            "zip": "88409",
            "city": "Buturović Polje "
        },
        {
            "zip": "77245",
            "city": "Bužim "
        },
        {
            "zip": "75405",
            "city": "Caparde "
        },
        {
            "zip": "71347",
            "city": "Careva Ćuprija "
        },
        {
            "zip": "77220",
            "city": "Cazin "
        },
        {
            "zip": "74211",
            "city": "Cerovica "
        },
        {
            "zip": "78403",
            "city": "Cerovljani "
        },
        {
            "zip": "76239",
            "city": "Crkvina "
        },
        {
            "zip": "88367",
            "city": "Crnići "
        },
        {
            "zip": "76328",
            "city": "Crnjelovo "
        },
        {
            "zip": "73280",
            "city": "Čajniče "
        },
        {
            "zip": "88300",
            "city": "Čapljina "
        },
        {
            "zip": "72224",
            "city": "Čardak "
        },
        {
            "zip": "72246",
            "city": "Čatići "
        },
        {
            "zip": "74274",
            "city": "Čečava "
        },
        {
            "zip": "80211",
            "city": "Čelebić "
        },
        {
            "zip": "88404",
            "city": "Čelebići "
        },
        {
            "zip": "73307",
            "city": "Čelebići "
        },
        {
            "zip": "75246",
            "city": "Čelić "
        },
        {
            "zip": "78240",
            "city": "Čelinac "
        },
        {
            "zip": "89243",
            "city": "Čemerno "
        },
        {
            "zip": "88265",
            "city": "Čerin "
        },
        {
            "zip": "88260",
            "city": "Čitluk "
        },
        {
            "zip": "77226",
            "city": "Ćoralići "
        },
        {
            "zip": "78427",
            "city": "Ćukali "
        },
        {
            "zip": "71221",
            "city": "Dejčići "
        },
        {
            "zip": "71223",
            "city": "Delijaš "
        },
        {
            "zip": "79243",
            "city": "Demirovac "
        },
        {
            "zip": "74400",
            "city": "Derventa "
        },
        {
            "zip": "75444",
            "city": "Derventa "
        },
        {
            "zip": "70204",
            "city": "Divičani "
        },
        {
            "zip": "89233",
            "city": "Divin "
        },
        {
            "zip": "74000",
            "city": "Doboj "
        },
        {
            "zip": "75328",
            "city": "Doborovci "
        },
        {
            "zip": "70210",
            "city": "Dobretići "
        },
        {
            "zip": "71124",
            "city": "Dobrinja "
        },
        {
            "zip": "79223",
            "city": "Dobrljin "
        },
        {
            "zip": "71232",
            "city": "Dobro Polje "
        },
        {
            "zip": "77242",
            "city": "Dobro Selo "
        },
        {
            "zip": "73247",
            "city": "Dobrun "
        },
        {
            "zip": "75206",
            "city": "Dokanj "
        },
        {
            "zip": "72278",
            "city": "Dolac Na Lašvi "
        },
        {
            "zip": "88446",
            "city": "Doljani "
        },
        {
            "zip": "76233",
            "city": "Domaljevac "
        },
        {
            "zip": "88305",
            "city": "Domanovići "
        },
        {
            "zip": "76293",
            "city": "Donja Dubica "
        },
        {
            "zip": "76274",
            "city": "Donja Mahala "
        },
        {
            "zip": "76237",
            "city": "Donja Slatina "
        },
        {
            "zip": "71305",
            "city": "Donje Moštre "
        },
        {
            "zip": "79228",
            "city": "Donji Agići "
        },
        {
            "zip": "76109",
            "city": "Donji Brezik "
        },
        {
            "zip": "79266",
            "city": "Donji Kamengrad "
        },
        {
            "zip": "88343",
            "city": "Donji Mamići "
        },
        {
            "zip": "76297",
            "city": "Donji Svilaj "
        },
        {
            "zip": "70220",
            "city": "Donji Vakuf "
        },
        {
            "zip": "78432",
            "city": "Donji Vijačani "
        },
        {
            "zip": "79289",
            "city": "Donji Vrbljani "
        },
        {
            "zip": "74209",
            "city": "Dragalovci "
        },
        {
            "zip": "76323",
            "city": "Dragaljevac "
        },
        {
            "zip": "78215",
            "city": "Dragočaj "
        },
        {
            "zip": "88215",
            "city": "Drežnica "
        },
        {
            "zip": "79290",
            "city": "Drinić "
        },
        {
            "zip": "88344",
            "city": "Drinovci "
        },
        {
            "zip": "73244",
            "city": "Drinsko "
        },
        {
            "zip": "75410",
            "city": "Drinjača "
        },
        {
            "zip": "80260",
            "city": "Drvar "
        },
        {
            "zip": "70237",
            "city": "Drvetine "
        },
        {
            "zip": "75358",
            "city": "Duboki Potok "
        },
        {
            "zip": "75308",
            "city": "Duboštica "
        },
        {
            "zip": "79227",
            "city": "Dubovik "
        },
        {
            "zip": "78411",
            "city": "Dubrave "
        },
        {
            "zip": "75274",
            "city": "Dubrave Donje "
        },
        {
            "zip": "75273",
            "city": "Dubrave Gornje "
        },
        {
            "zip": "74483",
            "city": "Dugo Polje "
        },
        {
            "zip": "75445",
            "city": "Dušanovo "
        },
        {
            "zip": "89202",
            "city": "Duži "
        },
        {
            "zip": "88342",
            "city": "Dužice "
        },
        {
            "zip": "76311",
            "city": "Dvorovi "
        },
        {
            "zip": "75272",
            "city": "Đurđevik "
        },
        {
            "zip": "79264",
            "city": "Fajtovci "
        },
        {
            "zip": "75423",
            "city": "Fakovići "
        },
        {
            "zip": "74218",
            "city": "Foča Kod Doboja "
        },
        {
            "zip": "71270",
            "city": "Fojnica "
        },
        {
            "zip": "89247",
            "city": "Fojnica "
        },
        {
            "zip": "88306",
            "city": "Gabela "
        },
        {
            "zip": "89240",
            "city": "Gacko "
        },
        {
            "zip": "74484",
            "city": "Garevac "
        },
        {
            "zip": "80230",
            "city": "Glamoč "
        },
        {
            "zip": "88406",
            "city": "Glavatičevo "
        },
        {
            "zip": "76318",
            "city": "Glavičice "
        },
        {
            "zip": "74258",
            "city": "Globarica "
        },
        {
            "zip": "88422",
            "city": "Glogošnica "
        },
        {
            "zip": "88207",
            "city": "Gnojnice "
        },
        {
            "zip": "73303",
            "city": "Godijeno "
        },
        {
            "zip": "71275",
            "city": "Gojevići "
        },
        {
            "zip": "72285",
            "city": "Goleš "
        },
        {
            "zip": "78203",
            "city": "Goleši "
        },
        {
            "zip": "73000",
            "city": "Goražde "
        },
        {
            "zip": "76296",
            "city": "Gornja Dubica "
        },
        {
            "zip": "77222",
            "city": "Gornja Koprivna "
        },
        {
            "zip": "76238",
            "city": "Gornja Slatina "
        },
        {
            "zip": "75208",
            "city": "Gornja Tuzla "
        },
        {
            "zip": "78405",
            "city": "Gornji Podgradci "
        },
        {
            "zip": "76207",
            "city": "Gornji Rahić "
        },
        {
            "zip": "79288",
            "city": "Gornji Ribnik "
        },
        {
            "zip": "78438",
            "city": "Gornji Smrtići "
        },
        {
            "zip": "78439",
            "city": "Gornji Štrpci "
        },
        {
            "zip": "74272",
            "city": "Gornji Teslić "
        },
        {
            "zip": "70240",
            "city": "Gornji Vakuf "
        },
        {
            "zip": "76214",
            "city": "Gornji Zovik "
        },
        {
            "zip": "89201",
            "city": "Grab "
        },
        {
            "zip": "78227",
            "city": "Grabovica "
        },
        {
            "zip": "74223",
            "city": "Grabska "
        },
        {
            "zip": "88443",
            "city": "Gračac Kod Prozora "
        },
        {
            "zip": "75320",
            "city": "Gračanica "
        },
        {
            "zip": "70233",
            "city": "Gračanica Kod Bugojna "
        },
        {
            "zip": "75276",
            "city": "Gračanica Selo "
        },
        {
            "zip": "88392",
            "city": "Gradac "
        },
        {
            "zip": "76250",
            "city": "Gradačac "
        },
        {
            "zip": "78400",
            "city": "Gradiška "
        },
        {
            "zip": "76234",
            "city": "Grebnice "
        },
        {
            "zip": "88340",
            "city": "Grude "
        },
        {
            "zip": "80205",
            "city": "Guber "
        },
        {
            "zip": "72277",
            "city": "Guča Gora "
        },
        {
            "zip": "75404",
            "city": "Gušteri "
        },
        {
            "zip": "71240",
            "city": "Hadžići "
        },
        {
            "zip": "72225",
            "city": "Hajdarevići "
        },
        {
            "zip": "72245",
            "city": "Haljinići "
        },
        {
            "zip": "72281",
            "city": "Han Bila "
        },
        {
            "zip": "71360",
            "city": "Han Pijesak "
        },
        {
            "zip": "88368",
            "city": "Hodovo "
        },
        {
            "zip": "71322",
            "city": "Hotonj "
        },
        {
            "zip": "71212",
            "city": "Hrasnica "
        },
        {
            "zip": "88395",
            "city": "Hrasno "
        },
        {
            "zip": "73295",
            "city": "Hrenovica "
        },
        {
            "zip": "71144",
            "city": "Hreša "
        },
        {
            "zip": "78436",
            "city": "Hrvaćani "
        },
        {
            "zip": "89203",
            "city": "Hum "
        },
        {
            "zip": "75216",
            "city": "Husino "
        },
        {
            "zip": "88394",
            "city": "Hutovo "
        },
        {
            "zip": "71210",
            "city": "Ilidža "
        },
        {
            "zip": "71380",
            "city": "Ilijaš "
        },
        {
            "zip": "73208",
            "city": "Ilovača "
        },
        {
            "zip": "78234",
            "city": "Imljani "
        },
        {
            "zip": "77208",
            "city": "Izačić "
        },
        {
            "zip": "88420",
            "city": "Jablanica "
        },
        {
            "zip": "74256",
            "city": "Jablanica Kod Maglaja "
        },
        {
            "zip": "73255",
            "city": "Jabuka Kod Foče "
        },
        {
            "zip": "71423",
            "city": "Jahorina "
        },
        {
            "zip": "70101",
            "city": "Jajce "
        },
        {
            "zip": "76316",
            "city": "Janja "
        },
        {
            "zip": "72215",
            "city": "Janjići "
        },
        {
            "zip": "88224",
            "city": "Jare "
        },
        {
            "zip": "78233",
            "city": "Javorani "
        },
        {
            "zip": "74264",
            "city": "Jelah "
        },
        {
            "zip": "70206",
            "city": "Jezero "
        },
        {
            "zip": "77241",
            "city": "Jezerski "
        },
        {
            "zip": "79244",
            "city": "Johova "
        },
        {
            "zip": "73319",
            "city": "Jošanica "
        },
        {
            "zip": "78244",
            "city": "Jošavka "
        },
        {
            "zip": "72264",
            "city": "Kaćuni "
        },
        {
            "zip": "72240",
            "city": "Kakanj "
        },
        {
            "zip": "74413",
            "city": "Kalenderovci "
        },
        {
            "zip": "75260",
            "city": "Kalesija "
        },
        {
            "zip": "71230",
            "city": "Kalinovik "
        },
        {
            "zip": "74268",
            "city": "Kalošević "
        },
        {
            "zip": "71355",
            "city": "Kaljina "
        },
        {
            "zip": "77204",
            "city": "Kamenica "
        },
        {
            "zip": "72265",
            "city": "Kaonik "
        },
        {
            "zip": "70235",
            "city": "Karadže "
        },
        {
            "zip": "72284",
            "city": "Karaula "
        },
        {
            "zip": "71213",
            "city": "Kasindo "
        },
        {
            "zip": "80246",
            "city": "Kazaginac "
        },
        {
            "zip": "88283",
            "city": "Kifino Selo "
        },
        {
            "zip": "71222",
            "city": "Kijevo Kod Sarajeva "
        },
        {
            "zip": "71250",
            "city": "Kiseljak "
        },
        {
            "zip": "75211",
            "city": "Kiseljak Kod Tuzle "
        },
        {
            "zip": "75280",
            "city": "Kladanj "
        },
        {
            "zip": "74452",
            "city": "Klakar Donji "
        },
        {
            "zip": "88324",
            "city": "Klobuk "
        },
        {
            "zip": "74207",
            "city": "Klokotnica "
        },
        {
            "zip": "79280",
            "city": "Ključ "
        },
        {
            "zip": "78230",
            "city": "Kneževo "
        },
        {
            "zip": "79246",
            "city": "Knežica "
        },
        {
            "zip": "71356",
            "city": "Knežina "
        },
        {
            "zip": "78423",
            "city": "Kobaš "
        },
        {
            "zip": "71323",
            "city": "Kobilja Glava "
        },
        {
            "zip": "88226",
            "city": "Kočerin "
        },
        {
            "zip": "78409",
            "city": "Kočićevo "
        },
        {
            "zip": "78207",
            "city": "Kola "
        },
        {
            "zip": "74454",
            "city": "Kolibe Gornje "
        },
        {
            "zip": "80244",
            "city": "Kongora "
        },
        {
            "zip": "88400",
            "city": "Konjic "
        },
        {
            "zip": "77249",
            "city": "Konjoder "
        },
        {
            "zip": "74489",
            "city": "Koprivna "
        },
        {
            "zip": "74456",
            "city": "Korače "
        },
        {
            "zip": "75247",
            "city": "Koraj "
        },
        {
            "zip": "74253",
            "city": "Kosova "
        },
        {
            "zip": "74222",
            "city": "Kostajnica "
        },
        {
            "zip": "76276",
            "city": "Kostrč "
        },
        {
            "zip": "78220",
            "city": "Kotor Varoš "
        },
        {
            "zip": "74215",
            "city": "Kotorsko "
        },
        {
            "zip": "72226",
            "city": "Kovači "
        },
        {
            "zip": "79202",
            "city": "Kozarac "
        },
        {
            "zip": "79240",
            "city": "Kozarska Dubica "
        },
        {
            "zip": "73314",
            "city": "Kozja Luka "
        },
        {
            "zip": "75413",
            "city": "Kozluk "
        },
        {
            "zip": "72244",
            "city": "Kraljeva Sutjeska "
        },
        {
            "zip": "79284",
            "city": "Krasulje "
        },
        {
            "zip": "75422",
            "city": "Kravica "
        },
        {
            "zip": "76212",
            "city": "Krepšić "
        },
        {
            "zip": "71260",
            "city": "Kreševo "
        },
        {
            "zip": "78256",
            "city": "Kriškovci "
        },
        {
            "zip": "77253",
            "city": "Krnjeuša "
        },
        {
            "zip": "78206",
            "city": "Krupa Na Vrbasu "
        },
        {
            "zip": "72253",
            "city": "Kruščica "
        },
        {
            "zip": "88203",
            "city": "Kruševo "
        },
        {
            "zip": "78226",
            "city": "Kruševo Brdo "
        },
        {
            "zip": "78424",
            "city": "Kukulje "
        },
        {
            "zip": "71216",
            "city": "Kula "
        },
        {
            "zip": "78443",
            "city": "Kulaši "
        },
        {
            "zip": "77206",
            "city": "Kulen Vakuf "
        },
        {
            "zip": "74415",
            "city": "Kulina "
        },
        {
            "zip": "80320",
            "city": "Kupres "
        },
        {
            "zip": "78250",
            "city": "Laktaši "
        },
        {
            "zip": "78407",
            "city": "Laminci – Sređani "
        },
        {
            "zip": "79204",
            "city": "Lamovita "
        },
        {
            "zip": "89208",
            "city": "Lastva "
        },
        {
            "zip": "72216",
            "city": "Lašva "
        },
        {
            "zip": "71254",
            "city": "Lepenica "
        },
        {
            "zip": "74453",
            "city": "Liješće "
        },
        {
            "zip": "78222",
            "city": "Liplje "
        },
        {
            "zip": "75213",
            "city": "Lipnica "
        },
        {
            "zip": "78434",
            "city": "Lišnja "
        },
        {
            "zip": "80204",
            "city": "Lištani "
        },
        {
            "zip": "80101",
            "city": "Livno "
        },
        {
            "zip": "76278",
            "city": "Lončari "
        },
        {
            "zip": "75240",
            "city": "Lopare "
        },
        {
            "zip": "75300",
            "city": "Lukavac "
        },
        {
            "zip": "75301",
            "city": "Lukavac Mjesto "
        },
        {
            "zip": "71126",
            "city": "Lukavica "
        },
        {
            "zip": "75327",
            "city": "Lukavica "
        },
        {
            "zip": "74411",
            "city": "Lupljanica "
        },
        {
            "zip": "80203",
            "city": "Lusnić "
        },
        {
            "zip": "79267",
            "city": "Lušci Palanka "
        },
        {
            "zip": "75214",
            "city": "Ljubače "
        },
        {
            "zip": "79206",
            "city": "Ljubija "
        },
        {
            "zip": "88380",
            "city": "Ljubinje "
        },
        {
            "zip": "89209",
            "city": "Ljubomir "
        },
        {
            "zip": "88320",
            "city": "Ljubuški "
        },
        {
            "zip": "88223",
            "city": "Ljuti Dolac "
        },
        {
            "zip": "74250",
            "city": "Maglaj "
        },
        {
            "zip": "74216",
            "city": "Majevac "
        },
        {
            "zip": "77235",
            "city": "Mala Kladuša "
        },
        {
            "zip": "74418",
            "city": "Mala Sočanica "
        },
        {
            "zip": "75326",
            "city": "Malešići "
        },
        {
            "zip": "76208",
            "city": "Maoča "
        },
        {
            "zip": "77265",
            "city": "Martin Brod "
        },
        {
            "zip": "78223",
            "city": "Maslovare "
        },
        {
            "zip": "78410",
            "city": "Mašići "
        },
        {
            "zip": "76271",
            "city": "Matići "
        },
        {
            "zip": "74203",
            "city": "Matuzići "
        },
        {
            "zip": "73242",
            "city": "Međeđa "
        },
        {
            "zip": "76257",
            "city": "Međiđa Donja "
        },
        {
            "zip": "88266",
            "city": "Međugorje "
        },
        {
            "zip": "73285",
            "city": "Međurječje "
        },
        {
            "zip": "79247",
            "city": "Međuvođe "
        },
        {
            "zip": "72282",
            "city": "Mehurići "
        },
        {
            "zip": "75267",
            "city": "Memići "
        },
        {
            "zip": "73228",
            "city": "Mesići "
        },
        {
            "zip": "80243",
            "city": "Mesihovina "
        },
        {
            "zip": "75446",
            "city": "Milići "
        },
        {
            "zip": "74485",
            "city": "Miloševac "
        },
        {
            "zip": "73283",
            "city": "Miljeno "
        },
        {
            "zip": "73313",
            "city": "Miljevina "
        },
        {
            "zip": "75329",
            "city": "Miričina "
        },
        {
            "zip": "74417",
            "city": "Mišinci "
        },
        {
            "zip": "74480",
            "city": "Modriča "
        },
        {
            "zip": "71428",
            "city": "Mokro "
        },
        {
            "zip": "89204",
            "city": "Mosko "
        },
        {
            "zip": "88000",
            "city": "Mostar "
        },
        {
            "zip": "75212",
            "city": "Mramor "
        },
        {
            "zip": "73206",
            "city": "Mravinjac "
        },
        {
            "zip": "70260",
            "city": "Mrkonjić Grad "
        },
        {
            "zip": "89249",
            "city": "Nadinići "
        },
        {
            "zip": "72212",
            "city": "Nemila "
        },
        {
            "zip": "88390",
            "city": "Neum "
        },
        {
            "zip": "88280",
            "city": "Nevesinje "
        },
        {
            "zip": "71383",
            "city": "Nišići "
        },
        {
            "zip": "72276",
            "city": "Nova Bila "
        },
        {
            "zip": "78418",
            "city": "Nova Topola "
        },
        {
            "zip": "76295",
            "city": "Novi Grad "
        },
        {
            "zip": "79220",
            "city": "Novi Grad "
        },
        {
            "zip": "74254",
            "city": "Novi Šeher "
        },
        {
            "zip": "72290",
            "city": "Novi Travnik "
        },
        {
            "zip": "74457",
            "city": "Novo Selo "
        },
        {
            "zip": "78428",
            "city": "Nožičko "
        },
        {
            "zip": "70225",
            "city": "Oborci "
        },
        {
            "zip": "76235",
            "city": "Obudovac "
        },
        {
            "zip": "76290",
            "city": "Odžak "
        },
        {
            "zip": "88285",
            "city": "Odžak "
        },
        {
            "zip": "71340",
            "city": "Olovo "
        },
        {
            "zip": "79203",
            "city": "Omarska "
        },
        {
            "zip": "72293",
            "city": "Opara "
        },
        {
            "zip": "78406",
            "city": "Orahova "
        },
        {
            "zip": "75323",
            "city": "Orahovica Donja "
        },
        {
            "zip": "76270",
            "city": "Orašje "
        },
        {
            "zip": "80206",
            "city": "Orguz "
        },
        {
            "zip": "75434",
            "city": "Osatica "
        },
        {
            "zip": "74412",
            "city": "Osinja "
        },
        {
            "zip": "74225",
            "city": "Osječani "
        },
        {
            "zip": "75406",
            "city": "Osmaci "
        },
        {
            "zip": "88423",
            "city": "Ostrožac "
        },
        {
            "zip": "77228",
            "city": "Ostrožac Kod Cazina "
        },
        {
            "zip": "76279",
            "city": "Oštra Luka "
        },
        {
            "zip": "79263",
            "city": "Oštra Luka "
        },
        {
            "zip": "77244",
            "city": "Otoka "
        },
        {
            "zip": "72238",
            "city": "Ozimica "
        },
        {
            "zip": "70243",
            "city": "Pajić Polje "
        },
        {
            "zip": "74255",
            "city": "Paklenica "
        },
        {
            "zip": "78437",
            "city": "Palačkovci "
        },
        {
            "zip": "71420",
            "city": "Pale "
        },
        {
            "zip": "75453",
            "city": "Paprača "
        },
        {
            "zip": "71243",
            "city": "Pazarić "
        },
        {
            "zip": "77227",
            "city": "Pećigrad "
        },
        {
            "zip": "76256",
            "city": "Pelagićevo "
        },
        {
            "zip": "74317",
            "city": "Petrovo "
        },
        {
            "zip": "75412",
            "city": "Pilica "
        },
        {
            "zip": "78217",
            "city": "Piskavica "
        },
        {
            "zip": "77248",
            "city": "Pištaline "
        },
        {
            "zip": "89235",
            "city": "Plana "
        },
        {
            "zip": "70275",
            "city": "Pljeva "
        },
        {
            "zip": "72252",
            "city": "Počulica "
        },
        {
            "zip": "71425",
            "city": "Podgrab "
        },
        {
            "zip": "80209",
            "city": "Podhum "
        },
        {
            "zip": "71387",
            "city": "Podlugovi "
        },
        {
            "zip": "74217",
            "city": "Podnovlje "
        },
        {
            "zip": "88403",
            "city": "Podorašac "
        },
        {
            "zip": "75355",
            "city": "Podorašje "
        },
        {
            "zip": "70266",
            "city": "Podrašnica "
        },
        {
            "zip": "88206",
            "city": "Podvelež "
        },
        {
            "zip": "77232",
            "city": "Podzvizd "
        },
        {
            "zip": "77209",
            "city": "Pokoj "
        },
        {
            "zip": "88204",
            "city": "Polog "
        },
        {
            "zip": "88402",
            "city": "Polje Bijela "
        },
        {
            "zip": "89206",
            "city": "Poljice "
        },
        {
            "zip": "75303",
            "city": "Poljice Kod Tuzle "
        },
        {
            "zip": "78242",
            "city": "Popovac "
        },
        {
            "zip": "88240",
            "city": "Posušje "
        },
        {
            "zip": "78216",
            "city": "Potkozarje "
        },
        {
            "zip": "88208",
            "city": "Potoci "
        },
        {
            "zip": "76298",
            "city": "Potočani "
        },
        {
            "zip": "78435",
            "city": "Potočani "
        },
        {
            "zip": "75433",
            "city": "Potočari "
        },
        {
            "zip": "73290",
            "city": "Prača "
        },
        {
            "zip": "73245",
            "city": "Prelovo "
        },
        {
            "zip": "72254",
            "city": "Preočica "
        },
        {
            "zip": "79287",
            "city": "Previja "
        },
        {
            "zip": "74276",
            "city": "Pribinić "
        },
        {
            "zip": "75249",
            "city": "Priboj Kod Lopara "
        },
        {
            "zip": "88288",
            "city": "Pridvorci "
        },
        {
            "zip": "79000",
            "city": "Prijedor "
        },
        {
            "zip": "80202",
            "city": "Priluka "
        },
        {
            "zip": "75248",
            "city": "Piperi "
        },
        {
            "zip": "80245",
            "city": "Prisoje "
        },
        {
            "zip": "78430",
            "city": "Prnjavor "
        },
        {
            "zip": "74214",
            "city": "Prnjavor Mali "
        },
        {
            "zip": "75304",
            "city": "Prokosovići "
        },
        {
            "zip": "88327",
            "city": "Prolog "
        },
        {
            "zip": "88440",
            "city": "Prozor "
        },
        {
            "zip": "76292",
            "city": "Prud "
        },
        {
            "zip": "70223",
            "city": "Prusac "
        },
        {
            "zip": "71335",
            "city": "Pržići "
        },
        {
            "zip": "72207",
            "city": "Puhovac "
        },
        {
            "zip": "75305",
            "city": "Puračić "
        },
        {
            "zip": "88325",
            "city": "Radišići "
        },
        {
            "zip": "75268",
            "city": "Rainci Gornji "
        },
        {
            "zip": "88245",
            "city": "Rakitno "
        },
        {
            "zip": "71217",
            "city": "Rakovica "
        },
        {
            "zip": "88370",
            "city": "Ravno "
        },
        {
            "zip": "78429",
            "city": "Razboj Lijevče "
        },
        {
            "zip": "76218",
            "city": "Ražljevo "
        },
        {
            "zip": "79288",
            "city": "Ribnik "
        },
        {
            "zip": "77215",
            "city": "Ripač "
        },
        {
            "zip": "73220",
            "city": "Rogatica "
        },
        {
            "zip": "80247",
            "city": "Roško Polje "
        },
        {
            "zip": "79226",
            "city": "Rudice "
        },
        {
            "zip": "73260",
            "city": "Rudo "
        },
        {
            "zip": "88347",
            "city": "Ružići "
        },
        {
            "zip": "79285",
            "city": "Sanica Gornja "
        },
        {
            "zip": "79260",
            "city": "Sanski Most "
        },
        {
            "zip": "75411",
            "city": "Sapna "
        },
        {
            "zip": "78202",
            "city": "Saračica "
        },
        {
            "zip": "71000",
            "city": "Sarajevo "
        },
        {
            "zip": "71321",
            "city": "Semizovac "
        },
        {
            "zip": "76205",
            "city": "Seonjaci "
        },
        {
            "zip": "74458",
            "city": "Sijekovac "
        },
        {
            "zip": "75207",
            "city": "Simin Han "
        },
        {
            "zip": "78422",
            "city": "Sitneši "
        },
        {
            "zip": "79283",
            "city": "Sitnica "
        },
        {
            "zip": "74212",
            "city": "Sjenina "
        },
        {
            "zip": "75436",
            "city": "Skelani "
        },
        {
            "zip": "74261",
            "city": "Skugrić "
        },
        {
            "zip": "75353",
            "city": "Sladna "
        },
        {
            "zip": "74271",
            "city": "Slatina "
        },
        {
            "zip": "78253",
            "city": "Slatina Ilidža "
        },
        {
            "zip": "74323",
            "city": "Sočkovac "
        },
        {
            "zip": "71350",
            "city": "Sokolac "
        },
        {
            "zip": "71218",
            "city": "Sokolović Kolonija "
        },
        {
            "zip": "71357",
            "city": "Sokolovići "
        },
        {
            "zip": "88345",
            "city": "Sovići "
        },
        {
            "zip": "78420",
            "city": "Srbac "
        },
        {
            "zip": "73300",
            "city": "Srbinje "
        },
        {
            "zip": "75430",
            "city": "Srebrenica "
        },
        {
            "zip": "75350",
            "city": "Srebrenik "
        },
        {
            "zip": "71385",
            "city": "Srednje "
        },
        {
            "zip": "79249",
            "city": "Sreflije "
        },
        {
            "zip": "76258",
            "city": "Srnice "
        },
        {
            "zip": "79224",
            "city": "Srpska Kostajnica "
        },
        {
            "zip": "74450",
            "city": "Srpski Brod "
        },
        {
            "zip": "73110",
            "city": "Srpsko Goražde "
        },
        {
            "zip": "71123",
            "city": "Srpsko Sarajevo "
        },
        {
            "zip": "74208",
            "city": "Stanari "
        },
        {
            "zip": "78243",
            "city": "Stara Dubrava "
        },
        {
            "zip": "79268",
            "city": "Stari Majdan "
        },
        {
            "zip": "72251",
            "city": "Stari Vitez "
        },
        {
            "zip": "77224",
            "city": "Stijena "
        },
        {
            "zip": "73223",
            "city": "Stjenice "
        },
        {
            "zip": "75324",
            "city": "Stjepan Polje "
        },
        {
            "zip": "88360",
            "city": "Stolac "
        },
        {
            "zip": "72209",
            "city": "Stranjani "
        },
        {
            "zip": "73267",
            "city": "Strgačina "
        },
        {
            "zip": "78208",
            "city": "Stričići "
        },
        {
            "zip": "70273",
            "city": "Strojice "
        },
        {
            "zip": "88323",
            "city": "Studenci "
        },
        {
            "zip": "75283",
            "city": "Stupari "
        },
        {
            "zip": "79229",
            "city": "Svodna "
        },
        {
            "zip": "76230",
            "city": "Šamac "
        },
        {
            "zip": "76209",
            "city": "Šatorovići "
        },
        {
            "zip": "88446",
            "city": "Šćipe "
        },
        {
            "zip": "88445",
            "city": "Šćit "
        },
        {
            "zip": "75450",
            "city": "Šekovići "
        },
        {
            "zip": "75275",
            "city": "Šerići "
        },
        {
            "zip": "75245",
            "city": "Šibošnica "
        },
        {
            "zip": "78433",
            "city": "Šibovska "
        },
        {
            "zip": "70270",
            "city": "Šipovo "
        },
        {
            "zip": "78224",
            "city": "Šiprage "
        },
        {
            "zip": "88220",
            "city": "Široki Brijeg "
        },
        {
            "zip": "74279",
            "city": "Šnjegotina Gornja "
        },
        {
            "zip": "75356",
            "city": "Špionica "
        },
        {
            "zip": "77223",
            "city": "Šturlić "
        },
        {
            "zip": "80249",
            "city": "Šujica "
        },
        {
            "zip": "77234",
            "city": "Šumatac "
        },
        {
            "zip": "71244",
            "city": "Tarčin "
        },
        {
            "zip": "75414",
            "city": "Teočak "
        },
        {
            "zip": "74270",
            "city": "Teslić "
        },
        {
            "zip": "74260",
            "city": "Tešanj "
        },
        {
            "zip": "74266",
            "city": "Tešanjka "
        },
        {
            "zip": "88348",
            "city": "Tihaljina "
        },
        {
            "zip": "75357",
            "city": "Tinja "
        },
        {
            "zip": "75455",
            "city": "Tišća "
        },
        {
            "zip": "73311",
            "city": "Tjentište "
        },
        {
            "zip": "77233",
            "city": "Todorovo "
        },
        {
            "zip": "75265",
            "city": "Tojšići "
        },
        {
            "zip": "76272",
            "city": "Tolisa "
        },
        {
            "zip": "79265",
            "city": "Tomina "
        },
        {
            "zip": "80240",
            "city": "Tomislavgrad "
        },
        {
            "zip": "72213",
            "city": "Topčić Polje "
        },
        {
            "zip": "70224",
            "city": "Torlakovac "
        },
        {
            "zip": "72270",
            "city": "Travnik "
        },
        {
            "zip": "88375",
            "city": "Trebinja "
        },
        {
            "zip": "89000",
            "city": "Trebinje "
        },
        {
            "zip": "78252",
            "city": "Trn "
        },
        {
            "zip": "76335",
            "city": "Trnova Donja "
        },
        {
            "zip": "71220",
            "city": "Trnovo "
        },
        {
            "zip": "76310",
            "city": "Trnjaci "
        },
        {
            "zip": "77225",
            "city": "Tržačka Raštela "
        },
        {
            "zip": "72283",
            "city": "Turbe "
        },
        {
            "zip": "75306",
            "city": "Turija "
        },
        {
            "zip": "78404",
            "city": "Turjak "
        },
        {
            "zip": "75000",
            "city": "Tuzla "
        },
        {
            "zip": "76330",
            "city": "Ugljenik "
        },
        {
            "zip": "74278",
            "city": "Ugodnovići "
        },
        {
            "zip": "71233",
            "city": "Ulog "
        },
        {
            "zip": "70280",
            "city": "Uskoplje "
        },
        {
            "zip": "74230",
            "city": "Usora "
        },
        {
            "zip": "73250",
            "city": "Ustikolina "
        },
        {
            "zip": "73202",
            "city": "Ustiprača "
        },
        {
            "zip": "73265",
            "city": "Uvac "
        },
        {
            "zip": "88444",
            "city": "Uzdol "
        },
        {
            "zip": "73249",
            "city": "Vardište "
        },
        {
            "zip": "71330",
            "city": "Vareš "
        },
        {
            "zip": "71333",
            "city": "Vareš Majdan "
        },
        {
            "zip": "77243",
            "city": "Varoška Rijeka "
        },
        {
            "zip": "74213",
            "city": "Velika Bukovica "
        },
        {
            "zip": "77207",
            "city": "Velika Gata "
        },
        {
            "zip": "77230",
            "city": "Velika Kladuša "
        },
        {
            "zip": "76329",
            "city": "Velika Obarska "
        },
        {
            "zip": "80208",
            "city": "Vidoši "
        },
        {
            "zip": "76275",
            "city": "Vidovice "
        },
        {
            "zip": "70202",
            "city": "Vinac "
        },
        {
            "zip": "74455",
            "city": "Vinska "
        },
        {
            "zip": "88247",
            "city": "Vir "
        },
        {
            "zip": "71300",
            "city": "Visoko "
        },
        {
            "zip": "73240",
            "city": "Višegrad "
        },
        {
            "zip": "88307",
            "city": "Višići "
        },
        {
            "zip": "72250",
            "city": "Vitez "
        },
        {
            "zip": "88326",
            "city": "Vitina "
        },
        {
            "zip": "74265",
            "city": "Vitkovci Donji "
        },
        {
            "zip": "73205",
            "city": "Vitkovići "
        },
        {
            "zip": "75440",
            "city": "Vlasenica "
        },
        {
            "zip": "71320",
            "city": "Vogošća "
        },
        {
            "zip": "71214",
            "city": "Vojkovići "
        },
        {
            "zip": "70246",
            "city": "Voljevac "
        },
        {
            "zip": "70247",
            "city": "Voljice "
        },
        {
            "zip": "72227",
            "city": "Vozuća "
        },
        {
            "zip": "74487",
            "city": "Vranjak "
        },
        {
            "zip": "88113",
            "city": "Vrapčići "
        },
        {
            "zip": "75248",
            "city": "Vražići "
        },
        {
            "zip": "78211",
            "city": "Vrbanja "
        },
        {
            "zip": "78225",
            "city": "Vrbanjci "
        },
        {
            "zip": "78408",
            "city": "Vrbaška "
        },
        {
            "zip": "77231",
            "city": "Vrnograč "
        },
        {
            "zip": "77203",
            "city": "Vrsta "
        },
        {
            "zip": "76325",
            "city": "Vršani "
        },
        {
            "zip": "77254",
            "city": "Vrtoče "
        },
        {
            "zip": "76254",
            "city": "Vučkovci "
        },
        {
            "zip": "74470",
            "city": "Vukosavlje "
        },
        {
            "zip": "73287",
            "city": "Zaborak "
        },
        {
            "zip": "76333",
            "city": "Zabrđe "
        },
        {
            "zip": "78221",
            "city": "Zabrđe "
        },
        {
            "zip": "78214",
            "city": "Zalužani "
        },
        {
            "zip": "73305",
            "city": "Zavajt "
        },
        {
            "zip": "72220",
            "city": "Zavidovići "
        },
        {
            "zip": "74451",
            "city": "Zborište "
        },
        {
            "zip": "77236",
            "city": "Zborište "
        },
        {
            "zip": "76259",
            "city": "Zelinja "
        },
        {
            "zip": "72000",
            "city": "Zenica "
        },
        {
            "zip": "88286",
            "city": "Zovi Do "
        },
        {
            "zip": "75400",
            "city": "Zvornik "
        },
        {
            "zip": "76273",
            "city": "Žabar Donji "
        },
        {
            "zip": "72236",
            "city": "Željezno Polje "
        },
        {
            "zip": "73226",
            "city": "Žepa "
        },
        {
            "zip": "72230",
            "city": "Žepče "
        },
        {
            "zip": "75270",
            "city": "Živinice "
        },
        {
            "zip": "75271",
            "city": "Živinice Gornje "
        },
        {
            "zip": "71373",
            "city": "Župča "
        }
    ]
    country_id = Country.objects.get(alpha2Code='BA').id
    for i in data:
        ci = City.objects.create(name=i['city'], country_id=country_id)
        ZipCode.objects.create(code=i['zip'], city=ci)
    return True

def insert_goods_types():
    data_hr = ['Komercijalna roba', 'Namještaj', 'Otpad', 'Prehrana', 'Selidba', 'Skupocjena roba / umjetnine',
               'Viseća roba', 'Vozila', 'Životinje', 'Ostalo']
    data_en = ['Type of Goods 1', 'Type of Goods 2']
    for i in range(len(data_hr)):
        obj = GoodsType.objects.create(name=[{"lang": HR, "name": data_hr[i]}], is_active=True)
        GoodsTypeTranslate.objects.create(lang=HR, goods_type=obj, name=data_hr[i])
        # GoodsTypeTranslate.objects.create(lang=EN, goods_type=obj, name=data_en[i])


def insert_vehicle_types():
    data_hr = ['Prikoličar', 'Tegljač sa poluprikolicom', 'Kamion do 12t', 'Kamion do 7.5t', 'Vozilo do 3.5t',
               'Mali kamion', 'Ostali kamioni']
    data_en = ['Type of Vehicle 1', 'Type of Vehicle 2']
    for i in range(len(data_hr)):
        obj = VehicleType.objects.create(name=[{"lang": HR, "name": data_hr[i]}], is_active=True)
        VehicleTypeTranslate.objects.create(lang=HR, vehicle_type=obj, name=data_hr[i])
        # VehicleTypeTranslate.objects.create(lang=EN, vehicle_type=obj, name=data_en[i])


def insert_vehicle_upgrades():
    data_hr = ['Autopodizač', 'Cerada', 'Cisterna', 'Coil korito', 'Furgon', 'Furgon (Kombi)', 'Hladnjača',
               'Izotermna prikolica', 'Jumbo', 'Kamion za prijevoz automobila', 'Specijalni kamion', 'Tautliner',
               'Tegljač', 'Teleskopska poluprikolica', 'Unutarnji utovarivač', 'Podvozje za kamione', 'Pokretni pod',
               'Pokretni pod (rasuti tereti)',
               'Sandučar', 'Silos prikolica', 'Kiper', 'Labudica', 'Mega', 'Utovarivač s kosinom', 'Korito',
               'Furgon za odjeću']
    # data_en = ['Upgrade of Vehicle 1', 'Upgrade of Vehicle 2']
    for i in range(len(data_hr)):
        obj = VehicleUpgrade.objects.create(name=[{"lang": HR, "name": data_hr[i]}], is_active=True)
        VehicleUpgradeTranslate.objects.create(lang=HR, vehicle_upgrade=obj, name=data_hr[i])
        # VehicleUpgradeTranslate.objects.create(lang=EN, vehicle_upgrade=obj, name=data_en[i])


def insert_vehicle_features():
    data_hr = ['Značajka Vozila 1', 'Značajka Vozila 2']
    # data_en = ['Feature of Vehicle 1', 'Feature of Vehicle 2']
    for i in range(2):
        obj = VehicleFeature.objects.create(name=[{"lang": HR, "name": data_hr[i]}], is_active=True)
        VehicleFeatureTranslate.objects.create(lang=HR, vehicle_feature=obj, name=data_hr[i])
        # VehicleFeatureTranslate.objects.create(lang=EN, vehicle_feature=obj, name=data_en[i])

def insert_vehicle_equipment():
    arr = ['ADR/Opasne tvari', 'Coil korito', 'Duboko zamrznuto', 'Hladno', 'Joloda tračnice', 'Prijenosni viličar', 'Prikolica na dvije razine',
           'Protuklizne podloge', 'Rastezljiva prikolica', 'Ručni viličar', 'Stupovi', 'Telefon', 'Zatezni pojasevi']
    arr2 = []
    for i in arr:
        arr2.append(VehicleEquipment(name=[{"lang": HR, "name": i}]))
    VehicleEquipment.objects.bulk_create(arr2)

def insert_languages():
    arr = ['Hrvatski', 'Engleski', 'Njemacki']
    _arr = []
    for i in arr:
        _arr.append(Language(name=i))
    Language.objects.bulk_create(_arr)


def insert_stock_types():
    arr = []
    for i in range(10):
        arr.append(StockType(name=[
            {
                "name": f"Testna vrsta skladista {i + 1}",
                "lang": HR
            },
            {
                "name": f'Test Stock Type {i + 1}',
                "lang": EN
            }
        ]))
    StockType.objects.bulk_create(arr)


def insert_stock_equipment():
    arr = []
    for i in range(10):
        arr.append(StockEquipment(name=[
            {
                "name": f"Testna oprema skladista {i + 1}",
                "lang": HR
            },
            {
                "name": f'Test Stock Equipment {i + 1}',
                "lang": EN
            }
        ]))
    StockEquipment.objects.bulk_create(arr)


def insert_transport_types():
    arr = ['Bočni utovar/istovar', 'Dotovar/djelomični utovar', 'Izvanredni prijevoz vremenski', 'Ekspresni prijevoz',
           'Prijevoz zbirne robe', 'Kompletni utovar',
           'Utovar i istovar dizalicom', 'Polazna i povratna tura', 'Bočni utovar/istovar']
    arr2 = []
    for i in arr:
        arr2.append(TransportType(name=[{"lang": HR, "name": i}]))
    TransportType.objects.bulk_create(arr2)


def insert_goods_forms():
    arr = ['Coil', 'Duboko smrznuta roba', 'Dugačka roba', 'Normalna roba', 'Opasne tvari', 'Punila', 'Rasuti teret',
           'Roba za hladnjaču', 'Roba za ispumpavanje', 'Težinski teret']
    arr2 = []
    for i in arr:
        arr2.append(GoodsForm(name=[{"lang": HR, "name": i}]))
    GoodsForm.objects.bulk_create(arr2)


def insert_loading_system():
    arr = ['Kran', 'Podizač rolo kontejnera', 'Podizna rampa', 'Pokretni pod', 'Stranični kiper', 'Stražnji kiper',
           'Teleskopski kiper']
    arr2 = []
    for i in arr:
        arr2.append(LoadingSystem(name=[{"lang": HR, "name": i}]))
    LoadingSystem.objects.bulk_create(arr2)

def fill_basic_data_in_db():
    # Contries
    print("Dodavanje drzava...")
    # insert_countries()
    print("Dodavanje Gradova i Postanskih brojeva...")
    # insert_cities_zip_codes()
    insert_bih_cities_and_zip_codes()

    print("Dodavanje ostalog...")
    insert_vehicle_types()
    insert_vehicle_upgrades()

    insert_transport_types()
    insert_goods_forms()
    insert_goods_types()

    insert_vehicle_equipment()
    insert_loading_system()

    insert_vehicle_features()
    insert_languages()
    insert_stock_types()
    insert_stock_equipment()


    pass


@transaction.atomic
def insert_cargo(data, token):
    # print(data)
    s = CheckInsertCargoSerializer(data=data)
    s.is_valid(raise_exception=True)
    json_data = data
    print(data)

    data = json.dumps(data)

    sql_data = call_sql_proc('insert_cargo', [data, token])
    # res = sql_data[0]
    # res = pretty_get_cargo_details(res)

    send_push_notification_by_user_filter.after_response(json_data, sql_data['id'], type='c', exclude_ids=[sql_data['contact_accounts'][0]['id']])

    return sql_data


@transaction.atomic
def insert_auction(data, token):
    s = CheckInsertAuctionSerializer(data=data)
    s.is_valid(raise_exception=True)
    sql_data = call_sql_proc('insert_auction', [token, data['cargo'], data['price']])
    if sql_data == 0:
        raise Http404()
    res = pretty_get_auctions(sql_data)
    send_push_insert_auction.after_response(data['cargo'], token)
    send_change_signal('list', None, 'cargo')
    send_change_signal('details', data['cargo'], 'cargo')
    return res

#CARGO START

@transaction.atomic
def update_cargo(data, token, cargo_id):
    data['cargo_id'] = cargo_id
    s = CheckUpdateCargoSerializer(data=data)
    s.is_valid(raise_exception=True)
    data = json.dumps(data)
    sql_data = call_sql_proc('update_cargo', [data, token])
    print(sql_data)
    return sql_data


@transaction.atomic
def close_cargo(pk, user):
    try:
        obj = Cargo.objects.get(id=pk)
    except ObjectDoesNotExist as o:
        raise Http404()
    except Exception as e:
        print(str(e))
        raise api_exc(str(e))
    if obj.created_by != user:
        raise PermissionDenied
    if obj.status == CLOSED:
        res, code = {"message": "LoadingSpace already Closed."}, 400
    else:
        obj.status = CLOSED
        obj.closed_at = datetime.now()
        obj.save()
        res, code = {"message": "Success"}, 200

    return res, code
#CARGO END

#LOADINGSPACE START
@transaction.atomic
def insert_loading_space(data, token):
    s = CheckInsertLoadingSpaceSerializer(data=data)
    s.is_valid(raise_exception=True)
    json_data = data
    data = json.dumps(data)
    sql_data = call_sql_proc('insert_loading_space', [data, token, False, 0])
    # res = pretty_get_loading_space_details(sql_data[0])

    send_push_notification_by_user_filter.after_response(json_data, sql_data['id'], type='l', exclude_ids=[sql_data['contact_accounts'][0]['id']])
    return sql_data


@transaction.atomic
def update_loading_space(data, token, id):
    data['loading_space_id'] = id
    s = CheckUpdateLoadingSpaceSerializer(data=data)
    s.is_valid(raise_exception=True)
    data = json.dumps(data)
    sql_data = call_sql_proc('insert_loading_space', [data, token, True, id])
    # res = pretty_get_loading_space_details(sql_data[0])
    return sql_data


@transaction.atomic
def close_loading_space(pk, user):
    try:
        obj = LoadingSpace.objects.get(id=pk)
    except ObjectDoesNotExist as o:
        raise Http404()
    except Exception as e:
        print(str(e))
        raise api_exc(str(e))
    if obj.created_by != user:
        raise PermissionDenied
    if obj.status == CLOSED:
        res, code = {"message": "LoadingSpace already Closed."}, 400
    else:
        obj.status = CLOSED
        obj.closed_at = datetime.now()
        obj.save()
        res, code = {"message": "Success"}, 200

    return res,code

#LOADINGSPACE END

def insert_stock_images(files, id):
    """
    Dodavanje fotografija za skladište
    """
    if not files: return True
    print("Dodavanje Fotografija skladista...")
    arr = []
    for file in files:
        print(file)
        arr.append(
            StockImage(image=file, stock_id=id)
        )
    StockImage.objects.bulk_create(arr)
    print("Dodane fotografije skladista!")
    return True


@transaction.atomic
def insert_stock(formdata, token, files=None):
    data = json.loads(formdata['data'])
    s = CheckInsertStockSerializer(data=data)
    s.is_valid(raise_exception=True)
    data['files'] = []

    if files:
        if not validate_stock_images(files):
            print("Nedozvoljene ekstenzije, vrati error.")
        for file in files:
            title = file.name
            file.name = generate_random_file_name(file.name)
            data['files'].append({
                'path': f'files/{file.name}',
                'title': title
            })

    data = json.dumps(data)
    sql_data = call_sql_proc('insert_update_stock', [data, token, False, 0])
    # print(sql_data)
    # res = pretty_get_stock_details(sql_data[0])
    res = sql_data
    if files:
        for file in files:
            with open(f'mediafiles/images/{file.name}', 'wb') as fp:
                fp.write(file.read())
        # insert_stock_images(files, res['id'])
    return res


@transaction.atomic
def update_stock(data, token, id):
    data['stock_id'] = id
    s = CheckUpdateStockSerializer(data=data)
    print("Prije validacije podataka")
    s.is_valid(raise_exception=True)
    data['files'] = []
    # if files:
    #     if not validate_stock_images(files):
    #         print("Nedozvoljene ekstenzije, vrati error.")
    #     for file in files:
    #         title = file.name
    #         file.name = generate_random_file_name(file.name)
    #         data['files'].append({
    #             'path': f'files/{file.name}',
    #             'title': title
    #         })
    data = json.dumps(data)
    sql_data = call_sql_proc('insert_update_stock', [data, token, True, id])
    print(sql_data)
    # if files:
    #     for file in files:
    #         with open(f'mediafiles/images/{file.name}', 'wb') as fp:
    #             fp.write(file.read())
    # res = pretty_get_stock_details(sql_data[0])
    return sql_data

@transaction.atomic
def close_stock(pk, user):
    try:
        obj = Stock.objects.get(id=pk)
    except ObjectDoesNotExist as o:
        raise Http404()
    except Exception as e:
        print(str(e))
        raise api_exc(str(e))
    if obj.created_by != user:
        raise PermissionDenied
    if obj.status == CLOSED:
        res, code = {"message": "LoadingSpace already Closed."}, 400
    else:
        obj.status = CLOSED
        obj.closed_at = datetime.now()
        obj.save()
        res, code = {"message": "Success"}, 200

    return res, code

def block_company(data, user):
    s = CheckBlockCompanySerializer(data=data)
    s.is_valid(raise_exception=True)
    if data['block']:
        obj, created = CompanyBlockList.objects.get_or_create(
            my_company=user.company,
            blocked_company_id=data['company'],
            blocked_by=user,
            unblocked_by=None
        )
        if not created:
            raise Http404()
    else:
        try:
            obj = CompanyBlockList.objects.get(unblocked_by=None, my_company=user.company,
                                               blocked_company_id=data['company'])
            obj.unblocked_at = datetime.now()
            obj.unblocked_by = user
            obj.save()
        except:
            raise Http404()
    return True


def upload_stock_images(stock_id, files, user):
    arr = []
    for file in files:
        print(file)
        arr.append(
            StockImage(title=file.name, path=file, stock_id=stock_id)
        )
    StockImage.objects.bulk_create(arr)
    objs = StockImage.objects.filter(is_active=True, stock_id=stock_id)
    ser = StockImagesSerializer(objs, many=True)
    res = {
        "images": ser.data
    }
    return res

def remove_stock_image(image_id, stock_id):
    obj = get_object_or_404(StockImage, is_active=True, id=image_id)
    obj.is_active = False
    obj.save()
    objs = StockImage.objects.filter(is_active=True, stock_id=stock_id)
    ser = StockImagesSerializer(objs, many=True)
    res = {
        "images": ser.data
    }
    return res


def upload_company_documents(company_id, files, user, is_update=False):
    if user.company_id != int(company_id):
        raise PermissionDenied()
    if is_update:
        CompanyDocument.objects.filter(company_id=company_id).delete()

    print("Dodavanje dokumenata od poduzeca...")
    arr = []
    for file in files:
        print(file)
        arr.append(
            CompanyDocument(path=file, title=file.name, company_id=company_id)
        )
    CompanyDocument.objects.bulk_create(arr)
    print("Dodani dokumenti poduzeca!")
    objs = CompanyDocument.objects.filter(is_active=True, company_id=company_id)
    ser = CompanyDocumentsSerializer(objs, many=True)
    res = {
        "company_documents": ser.data
    }
    return res

def remove_company_document(document_id, user):
    try:
        obj = CompanyDocument.objects.get(is_active=True, id=int(document_id))
        if obj.company_id != user.company_id:
            raise PermissionDenied()
        obj.is_active = False
        obj.save()
    except Exception as e:
        print(str(e))
        raise api_exc(str(e))

    objs = CompanyDocument.objects.filter(is_active=True, company_id=obj.company_id)
    ser = CompanyDocumentsSerializer(objs, many=True)
    res = {
        "company_documents": ser.data
    }
    return res

@transaction.atomic
def update_company(pk, formdata, files, token):
    try:
        data = json.loads(formdata['data'])
    except Exception as e:
        print(str(e))
        raise api_exc(str(e))
    s = CheckUpdateCompanySerializer(data=data)
    s.is_valid(raise_exception=True)
    data['company'] = pk
    data['files'] = []

    if files:
        if not validate_company_documents(files):
            print("Nedozvoljene ekstenzije, vrati error.")
        for file in files:
            title = file.name
            file.name = generate_random_file_name(file.name)
            data['files'].append({
                'path': f'files/{file.name}',
                'title': title
            })

    data = json.dumps(data)
    sql_data = call_sql_proc('insert_update_account_and_company', [True, data, token])
    print(sql_data)

    if files:
        for file in files:
            with open(f'mediafiles/files/{file.name}', 'wb') as fp:
                fp.write(file.read())
        # upload_company_documents(pk, files, is_update=True)

    # data = json.loads(formdata['data'])
    # data_for_update = update_company_format_data(data)
    # obj = Company.objects.get(id=pk)
    # ser = UpdateCompanySerializer(obj, data_for_update, partial=True)
    # ser.is_valid(raise_exception=True)
    # ser.save()
    # if 'company_numbers' in data:
    #     CompanyNumber.objects.filter(company_id=pk).delete()
    #     arr = []
    #     for i in data['company_numbers']:
    #         arr.append(CompanyNumber(company_id=pk, number=i['number'], type=i['type']))
    #     CompanyNumber.objects.bulk_create(arr)
    # if 'company_emails' in data:
    #     CompanyMail.objects.filter(company_id=pk).delete()
    #     arr = []
    #     for i in data['company_emails']:
    #         arr.append(CompanyMail(company_id=pk, email=i))
    #     CompanyMail.objects.bulk_create(arr)
    #
    # if files:
    #     upload_company_documents(pk, files, is_update=True)
    return get_company_details(pk)

def change_company_avatar(files, user):
    img = None
    if not files:
        print("Nema fotografije")
    else:
        img = files[0]
    user.company.avatar = img
    user.company.save()
    res = {
        'avatar': user.company.avatar.name
    }
    return res

@transaction.atomic
def confirm_company(data, user):
    mail_type = None
    s = CheckConfirmCompanySerializer(data=data)
    s.is_valid(raise_exception=True)
    try:
        obj = Company.objects.get(id=s.data['company_id'])
    except Exception as e:
        print(str(e))
        raise api_exc(str(e), 404)

    if s.data['confirm']:
        if obj.status == ACTIVE:
            raise api_exc("Already confirmed!")
        obj.status = ACTIVE
        print("Slati mail za AKTIVIRAN račun")
        mail_type = ACTIVE
    else:
        if obj.status == REJECTED:
            raise api_exc("Already rejected!")
        if obj.status == NEED_CONFIRM:
            print("Slati mail za NEODOBREN račun")
            mail_type = UNAUTHORIZED
        elif obj.status == ACTIVE:
            print("Slati mail za DEAKTIVIRAN račun")
            mail_type = DEACTIVATE
        obj.status = REJECTED

        Token.objects.filter(user__in=(Account.objects.filter(company=obj))).delete()

    obj.confirmed_by = user
    obj.confirmed_at = datetime.now()
    obj.save()

    #MAIL
    if obj.creator:
        print("Slanje maila")
        print(obj.creator.email)
        print(mail_type)
        print(s.data['company_id'])

        send_company_confirmation_email.after_response(obj.creator.email, mail_type, s.data['company_id'])
    else:
        print("NEMA CREATORA COMPANIJE")
    return True