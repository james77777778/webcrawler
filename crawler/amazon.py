import requests
from bs4 import BeautifulSoup


class AmazonCrawler(object):
    def __init__(self):
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537'
                              '.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Sa'
                              'fari/537.36',
                'accept-language': 'en-US;q=0.8,en;q=0.7',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0'
                          '.9,image/webp,image/apng,*/*;q=0.8,application/sign'
                          'ed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
        }

    def get_price(self, price_string):
        price_char = ''
        for s in price_string:
            if s.isdigit() or s == '.':
                price_char += s
        return float(price_char)

    def get_review(self, review_string):
        res = review_string.split()[0]
        return float(res)

    def search_by_specific_url(self, url):
        '''Search products on Amazon by specific url and return the title and price
        Args:
            url (str): the desired url of product.
        Returns:
            list of the results [title, price]
        '''
        search_url = url
        search_req = requests.get(search_url, headers=self.headers)
        search_soup = BeautifulSoup(search_req.text, features="html.parser")

        title = search_soup.find(id='productTitle').get_text().strip()
        try:
            price = self.get_price(search_soup.find(id='priceblock_ourprice').get_text().strip())
        except ValueError or IndexError:
            price = None
        try:
            stock = search_soup.select('#availability .a-color-state')[0].get_text().strip()
        except IndexError:
            stock = 'Avaliable'
        review_star = self.get_review(search_soup.find(id='acrPopover').get_text().strip())
        return [title, price, stock, review_star, search_url]


if __name__ == "__main__":
    Amazon = AmazonCrawler()
    ipad_url = (
        'https://www.amazon.com/Apple-iPad-10-2-Inch-Wi-Fi-32GB/dp/B07XL7G4H'
        '6/ref=sr_1_3?dchild=1&keywords=ipad&qid=1598364570&s=electronics&sr'
        '=1-3')
    ipad_mini_url = (
        'https://www.amazon.com//Apple-iPad-Mini-Wi-Fi-64GB/dp/B07PRD2NQ7/re'
        'f=sr_1_3?dchild=1&keywords=ipad+mini&qid=1598367912&sr=8-3'
    )
    print(Amazon.search_by_specific_url(ipad_url))
    print(Amazon.search_by_specific_url(ipad_mini_url))
