# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import csv
import cStringIO
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from aroundhunter.items import DianpingItem
from django.contrib.gis.geos import Point
import ujson
  
class PopulateDataFixturePipeline(object):
    """
        把抓取到的RecommendItem存入数据库
    """
    def __init__(self, *arg, **kwargs):
        self.jlfile = "./output/dianping_board_yueyang.jl"
        self.target = os.path.join(os.path.dirname(self.jlfile),
                      os.path.basename(self.jlfile).split('.')[0] + '.json')
        print self.target
        self.file = open('dianping_board_yueyang.fixture', "wb")
        self.file.write('[\n')
        super(PopulateDataFixturePipeline, self).__init__(*arg, **kwargs)
    
    
    def process_item(self, item, spider):
       if isinstance(item, DianpingItem):
           obj = {'model':'mile.MileItem',
                    'fields':{
                        'title':item['title'],
                        'summary': item['reason'],
                        'picOne': item['img_url'],
                        'coordinate': 'POINT(%s %s)' % tuple(item['coord'])
                     }
                  }
           line = ujson.dumps(obj) + ",\n"
           self.file.write(line)
       return item  # pass to next pipeline
    
    def close_spider(self, spider):
        self.file.write(']\n')
        self.file.close()
             