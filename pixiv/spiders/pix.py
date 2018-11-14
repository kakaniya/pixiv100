# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request,FormRequest
import json
from pyquery import PyQuery as pq
import requests
import logging


logging.captureWarnings(True)


class PixSpider(scrapy.Spider):
    name = 'pix'
    allowed_domains = ['pixiv.net']
    start_urls = ['http://pixiv.net/']

    login_url = 'https://accounts.pixiv.net/login'

    headers = {
                'accept': 'application/json',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN, zh;q=0.9',
                'upgrade-insecure-requests': 1,
                'content-type':'application/x-www-form-urlencoded',
                'user-agent': 'Mozilla/5.0(WindowsNT6.1;Win64;x64) AppleWebKit/537.36(KHTML,Gecko) Chrome/70.0.3538.77 Safari/537.36',
    }

    list_url = 'member_illust.php?id={user_id}&type=illust'
    user_id = 作者id
    all = 'ajax/user/{user_id}/profile/all'

    get_url = 'https://www.pixiv.net/ajax/user/{user_id}/illusts?'
    full_url = None

    def start_requests(self):
        yield Request(self.login_url,meta = {'cookiejar':1},callback=self.login_start)

    def login_start(self, response):
        print('start spider')
        post_key = response.xpath('//*[@id="old-login"]/form/input[1]/@value').extract_first()
        print(post_key)
        yield FormRequest.from_response(response,
                                         meta={'cookiejar':response.meta['cookiejar']},
                                         headers = self.headers,
                                         formdata = {
                                             'pixiv_id':'user_id',
                                             'captcha':'',
                                             'g_recaptcha_response':'',
                                             'password':'pass',
                                             'post_key':post_key,
                                             'source':'pc',
                                             'ref':'wwwtop_accounts_index',
                                             'return_to':'https://www.pixiv.net/'
                                         },
                                         callback = self.after_login,
                                         dont_filter = True)

    def after_login(self,response):
        lists_url = response.url + self.list_url.format(user_id = str(self.user_id))
        all_url = response.url+self.all.format(user_id = str(self.user_id))
        yield Request(all_url,meta = {'cookiejar':1},callback=self.full_urlget)


    def full_urlget(self,response):
        results = json.loads(response.text)
        #print(results)
        full_url = self.get_url.format(user_id=self.user_id)
        for result in results['body']['illusts']:
                full_url += 'ids%5B%5D=' + str(result) +'&'
        complite_url = full_url + 'is_manga_top=0'
        print(complite_url)
        yield Request(complite_url,meta = {'cookiejar':1},callback=self.parse_page)


    def parse_page(self,response):
        results = json.loads(response.text)
        print ('start')
        print(results)

