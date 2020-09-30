# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class SerieItem(scrapy.Item):
    title = scrapy.Field()
    year = scrapy.Field()
    url = scrapy.Field()
    temporadas = scrapy.Field()

class TemporadaItem(scrapy.Item):
    nombre = scrapy.Field()
    capitulos = scrapy.Field()

class CapituloItem(scrapy.Item):
    cap_id = scrapy.Field()
    titulo = scrapy.Field()
    numero = scrapy.Field()
    fecha = scrapy.Field()
    url_enlaces = scrapy.Field()
    numero_enlaces = scrapy.Field()
    enlaces = scrapy.Field()

class LinkItem(scrapy.Item):
    link_id = scrapy.Field()
    cap_id = scrapy.Field()
    host = scrapy.Field()
    link = scrapy.Field()
    langs = scrapy.Field()
    quality = scrapy.Field()
    uploader = scrapy.Field()

class ExternalLinkItem(scrapy.Item):
    link_id = scrapy.Field()
    reference_link = scrapy.Field()
    external_link = scrapy.Field()


