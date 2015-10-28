# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

 
class DianpingItem(scrapy.Item):
    """
       board -> {'board_title':xx, 'board_url':xx, 'board_intro':xx}    
    """
    board = scrapy.Field() 
    title = scrapy.Field()
    url = scrapy.Field()
    img_url = scrapy.Field()
    coord = scrapy.Field() # (lng, lat)
    region = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    specials_url = scrapy.Field()
    recommends = scrapy.Field()
    reason = scrapy.Field()
    star = scrapy.Field()
    comments = scrapy.Field()
    category = scrapy.Field()
    city = scrapy.Field()
    breadcrumb = scrapy.Field()
  

 