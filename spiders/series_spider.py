import scrapy
from ..items import *
from scrapy.http import FormRequest, Request
from scrapy.http import Response
from scrapy.utils.response import open_in_browser
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re

headers = {
    'User-Agent': '',
    'Accept': '',
    'Accept-Language': '',
    'Content-Type': '',
    'X-CSRF-TOKEN': '',
    'X-Requested-With': '',
    'Origin': '',
    'Connection': '',
    'Referer': '',
    'TE': '',
}

cookies = {
    '__cfduid': '',
    'PHPSESSID': '',
    'XSRF-TOKEN': '',
    'cakephp_session': '',
    'megadede-sess': '',
    'popshown2': '',
    '__cf_bm': '',
}


data = {
  '_token': '',
  'email': '',
  'password': '',
  'captcha': '',
  'popup': ''
}


class SeriesSpider(scrapy.Spider):
    name = 'series'
    login_url = 'https://www.megadede.com/login'
    series_url = 'https://www.megadede.com/series/all/'
    allowed_domains = ["megadede.com"] 
    start_urls = [
        'https://www.megadede.com/serie/',
        'https://www.megadede.com/series/all/',
        'https://www.megadede.com/'
        ]
    series_index = 0
    max_depth = 3
    use_max_depth = False
    
    def start_requests(self):
        yield FormRequest(
            url=self.login_url, 
            headers=headers, 
            cookies=cookies, 
            formdata=data,
            callback=self.parse)

    def parse(self, response):
        #open_in_browser(response)
        absoulute_url = response.urljoin(self.series_url)
        yield Request(absoulute_url , callback=self.parse_series)
        

    def parse_series(self, response):
        # Define elements
        series = SerieItem()

        #Search data
        media_container = response.css('div.media-container')
        for container in media_container:
            year = container.css('.year::text').extract()
            serie_url = container.css('a::attr(href)').extract()

            series['year'] = year[0]
            yield Request(serie_url[0], callback=self.parse_serieURL, meta={'series': series})
        
        self.series_index += 1
        next_url = self.series_url + str(self.series_index)
        if (len(media_container) == 0) or (self.series_index >= self.max_depth and self.use_max_depth):
            print('Series finished')
        else:
            yield response.follow(next_url, callback=self.parse_series)

    def parse_serieURL(self, response):
        series = response.meta.get('series')
        series['title'] = response.css('.big-title::text').extract()[0]
        series['url'] = response.request.url

        temporadas = {}
        temporadas_container = response.css('a.season-link')
        #esta parte solo contiene el nombre de la temporada
        for temp in temporadas_container:
            temporada_OBJECT = TemporadaItem()
            num_temporada = temp.css('::attr(data-season)').extract_first()
            temporada_OBJECT['nombre']= temp.css('::text').extract_first()
            temporadas[num_temporada] = temporada_OBJECT

        #Aqui ya se contiene los capitulos con enlace y mas, pero estan 
        #agrupados por temporada
        capTemp_container = response.css('ul.episode-container')
        for temp in capTemp_container:
            capitulos_container = temp.css('a.episode')
            season_number = temp.css('::attr(data-season)').extract_first()
            capitulos = {}
            for cap in capitulos_container:
                capitulo_OBJECT = CapituloItem()
                
                #find
                cap_id = cap.css('::attr(data-id)').extract_first()
                num_cap = cap.css('span.num::text').extract_first()
                titulo_cap = cap.css('div.name::text').extract()[1]
                fecha_cap = cap.css('div.date::text').extract_first()
                num_enlaces = cap.css('div.episode-stat::text').extract_first()
                enlaces_url = cap.css('::attr(data-href)').extract_first()

                #clean
                fecha_cap = re.sub('\s+', '', fecha_cap)
                titulo_cap = re.sub('\n+\t+', '', titulo_cap)
                num_enlaces = int(num_enlaces)
                
                #store
                capitulo_OBJECT['cap_id'] = cap_id
                capitulo_OBJECT['numero'] = int(num_cap)
                capitulo_OBJECT['titulo'] = titulo_cap
                capitulo_OBJECT['fecha'] = fecha_cap
                capitulo_OBJECT['numero_enlaces'] = num_enlaces
                capitulo_OBJECT['url_enlaces'] =  'www.megadede.com' + enlaces_url
                cap_name = season_number + 'x' + num_cap 
                capitulos[cap_name] = capitulo_OBJECT
                
                if num_enlaces > 0:
                    yield Request(( 'https://www.megadede.com' + enlaces_url), 
                        callback=self.parse_link, 
                        meta={'capitulo': capitulo_OBJECT})
                
            temporadas[season_number]['capitulos'] = capitulos

        series['temporadas'] = temporadas
        yield series

    def parse_link(self, response):
        capitulo = response.meta.get('capitulo')
        link_container = response.css('#online a.aporte')
        links = {}
        for lnk in link_container:
            link_OBJECT = LinkItem()

            #find
            id_link = lnk.css('::attr(data-id)').extract_first()
            host_link = lnk.css('.host img::attr(src)').extract_first()
            langs_img = lnk.css('.language img::attr(src)').extract()
            quality = lnk.css('div.videoquality::text').extract()[1]
            user_uploader = lnk.css('.uploader span::text').extract_first()
            
            #clean
            user_uploader = re.sub('\s+', '', user_uploader)
            quality = re.sub('\s+', '', quality)
            
            #store
            link_OBJECT['cap_id'] = capitulo['cap_id']
            link_OBJECT['link_id'] = id_link
            link_OBJECT['host'] = self.getHost(host_link)
            link_OBJECT['langs'] = self.getLangs(langs_img)
            link_OBJECT['quality'] = quality
            link_OBJECT['uploader'] = user_uploader
            links[id_link] = link_OBJECT
            
            #--------

            temp_link = lnk.css('::attr(href)').extract_first()
            yield response.follow((temp_link), 
                    callback=self.parse_referenceLink, 
                    meta={'link': link_OBJECT})

        capitulo['enlaces'] = links
        yield capitulo

    def getHost(self, host):
        splitted = host.split('/')
        clean_url =splitted[len(splitted)-1]
        return str(clean_url[:-4])

    def getLangs(self, langs):
        lang_array = []
        for lan in langs:
            splitted = lan.split('/')
            clean_url =splitted[len(splitted)-1]
            lang_array.append(clean_url[:-4])
        return lang_array

    def parse_referenceLink(self, response):
        ext_link = ExternalLinkItem()
        link = response.meta.get('link')
        visit_url = response.css('div.visit-buttons a::attr(href)').extract_first()
        ext_link['link_id'] = link['link_id']
        ext_link['reference_link'] = visit_url
        yield response.follow((visit_url), 
                    callback=self.parse_externalLink,
                    errback=self.errback_httpbin, 
                    meta={'link': ext_link})

    def parse_externalLink(self, response):
        link = response.meta.get('link')
        link['external_link'] = response.url
        yield link
    
    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))
