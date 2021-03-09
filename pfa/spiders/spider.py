import re
import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from ..items import PfaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

import requests

url = "https://pfabank.dk/api/sitecore/NewsArchive/AjaxNewsArchive/?page=999&pagesize=16&prefilters=&filters=&year=undefined&breaking="

payload="page=6&pagesize=16&prefilters=&filters=&year=undefined&breaking="
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'Accept': '*/*',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://pfabank.dk',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://pfabank.dk/news-archive/',
  'Accept-Language': 'en-US,en;q=0.9',
  'Cookie': '_fbp=fb.1.1615211712348.814160810; CookieInformationConsent=%7B%22website_uuid%22%3A%22212c162e-60e7-491c-a502-1260497a48a7%22%2C%22timestamp%22%3A%222021-03-08T13%3A55%3A16.496Z%22%2C%22consent_url%22%3A%22https%3A%2F%2Fpfabank.dk%2Fprivat%2F%22%2C%22consent_website%22%3A%22pfabank.dk%22%2C%22consent_domain%22%3A%22pfabank.dk%22%2C%22user_uid%22%3A%220dbd14ad-7977-4747-9ddf-d6d6ce97fbb9%22%2C%22consents_approved%22%3A%5B%22cookie_cat_necessary%22%2C%22cookie_cat_functional%22%2C%22cookie_cat_statistic%22%2C%22cookie_cat_marketing%22%2C%22cookie_cat_unclassified%22%5D%2C%22consents_denied%22%3A%5B%5D%2C%22user_agent%22%3A%22Mozilla%2F5.0%20%28Windows%20NT%206.1%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F88.0.4324.190%20Safari%2F537.36%22%7D; _gcl_au=1.1.432395538.1615211718; SC_ANALYTICS_GLOBAL_COOKIE=79b1d618942340e9893e3a138105a85f|True; _ga=GA1.2.953580481.1615211718; _gid=GA1.2.890836124.1615211718; ASP.NET_SessionId=rz1s2euh2zxdf0r0dkqvdmxn; at_check=true; AMCVS_920C025E5B89DDA70A495E2E%40AdobeOrg=1; AMCV_920C025E5B89DDA70A495E2E%40AdobeOrg=-1124106680%7CMCIDTS%7C18695%7CMCMID%7C54553108742194914442528684559795664099%7CMCAAMLH-1615877833%7C6%7CMCAAMB-1615877833%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1615280233s%7CNONE%7CvVersion%7C5.2.0; s_cc=true; mbox=session#872e6b815e024303b908a556405a0a9b#1615274893|PC#872e6b815e024303b908a556405a0a9b.37_0#1678517848; s_sq=pfapensionpfabankproduction%252Cpfapensionglobal%3D%2526c.%2526a.%2526activitymap.%2526page%253Dnews-archive%2526link%253DSe%252520flere%252520nyheder%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dnews-archive%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fpfabank.dk%25252Fnews-archive%25252F%252523%2526ot%253DA'
}


class PfaSpider(scrapy.Spider):
	name = 'pfa'
	start_urls = ['https://pfabank.dk/news-archive/']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		links = Selector(text=data.text).xpath('//div[@class="col-sm-6 col-md-3"]/a/@href').getall()
		yield from response.follow_all(links, self.parse_post)
	def parse_post(self, response):
		date = response.xpath('//dl[@class="news-article__info"]/dd/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//article[@class="news-article__content"]//text()[not (ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PfaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
