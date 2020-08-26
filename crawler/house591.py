import json
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup


class House591Crawler(object):
    def __init__(self):
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537'
                              '.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Sa'
                              'fari/537.36',
                'accept-language': 'en-US;q=0.8,en;q=0.7',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0'
                          '.9,image/webp,image/apng,*/*;q=0.8,application/sign'
                          'ed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br'
        }
        self.base_url = 'https://rent.591.com.tw/?kind=0'
        self.json_url = 'https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=4'
        with open(Path(__file__).parent.absolute()/Path('house591', 'MRT.json'), 'r', encoding='big5') as f:
            mrt_data = json.load(f)
            # mrt_line: sid(mrt), name
            self.mrt_line = {}
            # station_name: sid(mrtline), name, lat, lng, zoom, nid(mrtcoods)
            self.mrt_station = {}
            for mrt_region in mrt_data['mrts']:
                for mrtline in mrt_region['mrtline']:
                    self.mrt_line[mrtline['name']] = {
                        'sid': mrtline['sid'], 'name': mrtline['name']}
                    for station in mrtline['station']:
                        self.mrt_station[station['name']] = station
        with open(Path(__file__).parent.absolute()/Path('house591', 'Region.json'), 'r', encoding='big5') as f:
            region_data = json.load(f)
            # section: id(region), txt
            self.section = {}
            # city: id(region), txt
            self.city = {}
            for region in region_data['region']:
                self.city[region['txt']] = {'id': region['id'], 'txt': region['txt']}
                for section in region['section']:
                    self.section[region['txt']+'.'+section['name']] = section

    def search_by_arguments(self, city='新北市', section='板橋區', mrt_line='板南線', mrt_station='板橋',
                            rentprice=[15000, 25000], order='nearby', max_iter=100):
        url = self.base_url
        params = ''
        if mrt_line is not None:
            mrtline = self.mrt_line[mrt_line]['sid']
            params += '&mrtline=' + str(mrtline)
        if city is not None:
            region = self.city[city]['id']
            params += '&region=' + str(region)
        # if mrt is not None:
        #     params += '&mrt=' + str(mrt)
        if mrt_station is not None:
            mrtcoods = self.mrt_station[mrt_station]['nid']
            params += '&mrtcoods=' + str(mrtcoods)
        if rentprice is not None:
            params += '&rentprice=' + str(rentprice[0]) + ',' + str(rentprice[1])
        if order is not None:
            if order == 'nearby':
                params += '&order=nearby&orderType=desc'
            elif order == 'posttime':
                params += '&order=posttime&orderType=desc'
            elif order == 'area':
                params += '&order=area&orderType=desc'
        url += params

        # start requests session
        with requests.Session() as s:
            search_req = s.get(url, headers=self.headers)
            search_soup = BeautifulSoup(search_req.text, features='html.parser')

            # set header
            csrf_token = search_soup.select_one('meta[name="csrf-token"]')['content']
            s.headers['X-CSRF-Token'] = csrf_token
            s.headers['X-Requested-With'] = 'XMLHttpRequest'
            s.headers['Host'] = 'rent.591.com.tw'
            s.headers['Referer'] = url
            # get first json
            json_url = self.json_url + params
            json_req = s.get(json_url, headers=s.headers)
            json_res = json.loads(json_req.text)
            firstRow = 0
            totalRows = int(json_res['records'])
            print('total:', totalRows)
            print('index 1')
            print(json_res['data']['data'][0]['address_img_title'])
            time.sleep(0.5)

            if totalRows > firstRow + 30:
                for i in range(firstRow+30, max_iter, 30):
                    json_url = self.json_url + params + '&firstRow=' + str(i) + '&totalRow=' + str(totalRows)
                    json_req = s.get(json_url, headers=s.headers)
                    json_res = json.loads(json_req.text)
                    print('index', i+1)
                    print(json_res['data']['data'][0]['address_img_title'])
                    time.sleep(0.1)


if __name__ == "__main__":
    House591 = House591Crawler()
    House591.search_by_arguments()
    print('finish')
