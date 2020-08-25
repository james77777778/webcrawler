import json

from crawler import amazon
from notify.line_notify import line_notify


def construct_msg(res):
    msg = '\n'
    msg += 'Product Name: ' + res[0] + '\n'
    msg += 'Price: ' + str(res[1]) + '\n'
    msg += 'Stock: ' + res[2] + '\n'
    msg += 'Star: ' + str(res[3]) + '\n'
    msg += 'URL: ' + res[4] + '\n'
    return msg


if __name__ == "__main__":
    with open('token.json', 'r') as f:
        token = json.load(f)['Amazon Crawler']
    amazon_crawler = amazon.AmazonCrawler()

    urls = [
        ('https://www.amazon.com/Apple-iPad-10-2-Inch-Wi-Fi-32GB/dp/B07XL7G4H'
         '6/ref=sr_1_3?dchild=1&keywords=ipad&qid=1598364570&s=electronics&sr'
         '=1-3'),
        ('https://www.amazon.com//Apple-iPad-Mini-Wi-Fi-64GB/dp/B07PRD2NQ7/re'
         'f=sr_1_3?dchild=1&keywords=ipad+mini&qid=1598367912&sr=8-3')
    ]
    target_prices = [
        280,
        350,
    ]

    print('start')
    res = []
    for url in urls:
        res.append(amazon_crawler.search_by_specific_url(url))
    for r, t in zip(res, target_prices):
        if r[1] < t:
            line_notify(token, construct_msg(r))
    print('finish.')
