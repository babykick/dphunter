#coding=utf-8
import ujson

for line in open("./output/dianping_board_yueyang.jsonl"):
    item = ujson.loads(line)
    