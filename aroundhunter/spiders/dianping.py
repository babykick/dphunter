# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import urlparse
from aroundhunter.items import DianpingItem
import re

 
class SpiderUtilsMixin(object):
    def extract_first_or_None(self, selector):
        return selector.extract_first().strip() if selector else None
    
     
     
class DianpingSpider(scrapy.Spider, SpiderUtilsMixin):
    name = "dianping"
    allowed_domains = ["dianping.com"]
    categories = {
        '25': '电影院',
        '10': '美食',
    }
    # start_urls = (
    #     'http://www.dianping.com/mylist/yueyang',
    # )
    root_domain = "http://www.dianping.com/"
    
    def __init__(self, topage=None, *args, **kwargs):
        self.topage = topage
        super(DianpingSpiderSpider, self).__init__(*args, **kwargs) 
         
    def start_requests(self, city="yueyang"):
        self.city = city
        url = 'http://www.dianping.com/mylist/%s' % city
        r = Request(url=url,
                    # cookies={'JSESSIONID': '02752BCB5C11756EBEB6EB63BF95233E',
                    #                   'PHOENIX_ID': '0a03052a-1507fbe0a52-124ab',
                    #                  # '_hc.v', "\"9dc4f8fe-83aa-4ab2-a7e7-10d225cf471e.1437123244\"",
                    #                   },
                    callback=self.parse)
        yield r
    
    
    def parse(self, response):
        self.log("parse how many pages")
        if self.topage is None:
            last_page = response.xpath("//div/div[contains(@class, 'Pages')]/a[position()=(last()-1)]/text()").extract_first()
        else:
            last_page = self.topage
        for i in range(1, int(last_page) + 1, 1):
            self.log("process page %s" % i)
            url = 'http://www.dianping.com/mylist/%s?pg=%s' % (self.city, i)
            yield Request(url=url, callback=self.parse_board_list)
            
            
    def parse_board_list(self, response):
        self.log("parse board list from %s" % response.url)
        for dt in response.xpath("//div/dl[contains(@class, 'perList')]"):
           link = dt.xpath("./dt/span/a/@href").extract_first()
           title = dt.xpath("./dt/span/a/img/@title").extract_first()
           intro = dt.xpath("./dd/div/p/text()").extract_first()
           url = urlparse.urljoin(self.root_domain, link)
           yield Request(url=url, callback=self.parse_board, meta={'board':{'url':url,
                                                                            'title': title,
                                                                            'intro': intro
                                                                            }})

    def parse_board(self, response):
        self.log("parse board")
        board = response.meta['board']
        for li in response.xpath(".//div[@class='mc-list']/ul/li"):
            img = li.xpath("./div/div/a/img/@src").extract_first()
            img_data = li.xpath("./div/div/a/img/@data-src").extract_first()
            item = DianpingItem()
            item['img_url'] = img or img_data
            item['url'] = urlparse.urljoin(self.root_domain, li.xpath("./div/div/a/@href").extract_first())
            item['title'] = li.xpath("./div/div/a/img/@title").extract_first()
            item['board'] = board
            item['reason'] = self.extract_first_or_None(li.xpath('.//div[@class="txt-more"]/span/text()'))
            item['star'] = li.css('.item-rank-rst').xpath('@title').extract_first()
            yield Request(url=item['url'], callback=self.parse_detail, meta={'item': item})
        
        
        
    def parse_detail(self, response):
        self.log("parse item detail")
        item = response.meta['item']
        item['coord'] = response.xpath("//script").re("lng:(.*?),lat:(.*?)}")
        item['region'] = self.extract_first_or_None(response.xpath('//div[contains(@class, "address")]/a/span/text()'))
        item['address'] = self.extract_first_or_None(response.xpath('//div[contains(@class, "address")]/span[@class="item"]/text()'))
        # item['category'] = self.extract_first_or_None(response.css('.address').xpath('./a/@href'))
        # if item['category']: item['category'] = item['category'].split("category")[-1]
        item['phone']  = self.extract_first_or_None(response.xpath('//p[contains(@class, "tel")]/span[@class="item"]/text()')) 
        item['city'] = self.extract_first_or_None(response.css('.city').xpath('./text()'))
        # 从面包削获取类别
        a = response.css('.breadcrumb').xpath('.//a')[-1] #最后一个
        catecode = self.get_cate_code(a.xpath('@href').extract_first())
        catename = a.xpath('.//text()').extract_first().strip()
        item['category'] = self.infer_full_cate_name(catecode, catename)
        # 推荐项
        recommends = []
        text = re.search('<p class="recommend-name">.*?</p>', response.body_as_unicode(), re.DOTALL)
        if text:
            text = text.group()
            sel = scrapy.Selector(text=text, type="html")
            for a in sel.css('.item'):
                   dish = urlparse.urljoin(self.root_domain, a.xpath("@href").extract_first())
                   name = self.extract_first_or_None(a.xpath("text()"))
                   recommends.append({'url': dish, 'name':name, 'img':None})
        item['recommends'] = recommends
        # 查找对应的图片
        text = re.search('<ul class="recommend-photo clearfix">.*?</ul>', response.body_as_unicode(), re.DOTALL)
        if text:
            text = text.group()
            sel = scrapy.Selector(text=text, type="html")
            for li in sel.css('.item'):
                img = li.xpath('./img/@src').extract_first()
                name = li.css('.name').xpath('text()').extract_first().strip()
                for r in recommends:
                    if r['name'] == name:
                        r['img'] = img;
                        break
        item['comments'] = response.css('.comment-item').css('.content').css('p.desc::text').extract()           
        specials_url = response.xpath('//p[contains(@class, "nug-shop-ab-special_a")]/a[contains(@class, "J-service")]/@href')
        
        # if specials_url:
        #    specials_url = specials_url.extract_first()
        #    item['specials_url'] = specials_url
        #    yield Request(url=specials_url, callback=self.parse_specials, meta={'item': item})
        # else:
        #    item['specials_url'] = None
        
        # 翻页抓取其他评论
        # yield ...
        
        yield item
        
    def parse_specials(self, response):
        """ 团购
        """
        self.log("parse specials")
        
    
    
    def get_cate_code(self, url):
        """ return (主类别号, 子类别号)
        """
        category = url.split('category')[1].split('r')[0].split('/')[2:]
        return category        
        
    def infer_full_cate_name(self, catecode, catename):
         """ 大众点评网站'美食'大类别号为10, 但包含了酒吧, 我们用子类别号码排除酒吧
         """
         food_code_exclude = ('g133', )
         if catecode[0] == '10' and catecode[1] not in food_code_exclude:
              return u'美食'
         return catename
    