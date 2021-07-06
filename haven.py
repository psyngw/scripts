import requests
import scrapy
import os
import urllib3
import datetime

# STORE_PATH = os.path.join(BASE_PATH, 'wallpapers', 'wallhaven')


def main(url):
    page = requests.get(url)
    root = scrapy.Selector(page)
    pres = root.xpath("//a[@class='preview']/@href").extract()
    # ignore https warning
    urllib3.disable_warnings()
    for pre in pres:
        name = pre.split('/')[-1]
        pre_path = 'wallhaven-%s.jpg' % name
        print(f"now: {pre_path}")
        if not os.path.isfile(os.path.join(STORE_PATH, pre_path)):
            res = get_pic(name, pre_path)
            if not res:
                print(f"recheck: png")
                get_pic(name, pre_path.replace('.jpg', '.png'))
    print('done')


def get_pic(name, pre_path):
    img = requests.get("http://w.wallhaven.cc/full/%s/%s" %
                       (name[:2], pre_path),
                       verify=False)
    if img.status_code == 200:
        with open(os.path.join(STORE_PATH, pre_path), 'w+b') as f:
            f.write(img.content)
        return True
    return False


if __name__ == '__main__':
    bp = input(
        'please input the path you wanna save pics(or just Enter to save in the current folder):\n'
    )
    if bp and bp[0] == '~':
        _b = os.popen('echo $HOME')
        bp = bp.replace('~', _b.read()[:-1], 1)
    BASE_PATH = bp or os.path.dirname(os.path.abspath(__file__))
    STORE_PATH = os.path.join(BASE_PATH, 'wallpapers',
                              f'wallhaven-{datetime.datetime.now():%Y%m%d}')
    if not os.path.exists(STORE_PATH):
        os.makedirs(STORE_PATH)
    # url = "https://wallhaven.cc/search?categories=110&purity=100&resolutions=1920x1080&topRange=1M&sorting=toplist&order=desc&page=1"
    url = "https://wallhaven.cc/search?categories=110&purity=100&resolutions=1920x1080&sorting=random&order=desc&seed=lbCEj&page=1"
    m_url = input(
        'please input the pics\'url you wanna get(or just Enter to get random pics):\n'
    )
    if m_url: url = m_url
    main(url)
