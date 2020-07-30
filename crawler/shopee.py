import re
import requests
import urllib
from bs4 import BeautifulSoup


def string2float(s):
    mul = 1
    s = s.replace(',', '')
    if '萬' in s:
        mul *= 10000
        s = s.replace('萬', '')
    res = float(s)
    res *= mul
    return res


class ShopeeCrawler(object):
    def __init__(self):
        self.base_url = "https://shopee.tw/"
        self.search_url = "search/"
        self.headers = {
                'User-Agent': 'Googlebot',
        }

    def search_by_keyword(self, keyword, search_type="relevancy", used=None, price=(-1, -1)):
        '''Search products on shopee by keyword and can be sorted by search_type
        Args:
            keyword (str): the desired keyword for searching.
            search_type (str): "relevancy", "ctime", "sales".
            used (bool): whether to find used item.
                         Toggle to None for default search.
                         Toggle to False for new item only.
            price (tuple of int): set the min and max price.
        Returns:
            list of the results
        '''
        keyword = urllib.parse.quote(keyword)
        search_params = {
            "keyword": keyword,
            "page": 0,
            "sortBy": search_type,
        }
        if used is not None:
            if used:
                search_params["usedItem"] = 'true'
            else:
                search_params["newItem"] = 'true'
        if price is not None:
            if price[0] != -1:
                search_params["minPrice"] = int(price[0])
            if price[1] != -1:
                search_params["maxPrice"] = int(price[1])
        search_url = self.base_url + self.search_url
        search_req = requests.get(
            search_url, headers=self.headers, params=search_params)
        search_soup = BeautifulSoup(search_req.text, features="html.parser")

        # find sale number
        def is_sale_number(s):
            return '已售出' in s.text

        res_list = []
        for item in search_soup.find_all(attrs={'data-sqe': 'link'}):
            # find link
            item_link = self.base_url + item['href'][1:]

            # find name
            item_name = item.find(attrs={'data-cy': 'product_name_product_card'}).string

            # find price
            item_price = item.find(attrs={'data-cy': 'product_actual_price_product_card'}).find_all('span')
            # only one price
            if len(item_price) == 2:
                item_min_price = item_max_price = string2float(item_price[-1].string)
            # got price range
            elif len(item_price) == 4:
                item_min_price = string2float(item_price[1].string)
                item_max_price = string2float(item_price[-1].string)

            # find sale number
            try:
                item_sale_number = int(string2float(item.find(text=re.compile('已售出 ')).string[4:]))
            except AttributeError:
                item_sale_number = 0
            except ValueError:
                item_sale_number = 0
            res_list.append(
                (item_name, item_link, item_sale_number, item_min_price, item_max_price))
        return res_list


if __name__ == "__main__":
    Shopee = ShopeeCrawler()
    res = Shopee.search_by_keyword('switch', used=True, price=(5000, 10000))
    for item in res:
        print(item)
