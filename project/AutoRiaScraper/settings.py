from os import getenv
from pathlib import Path
from time import time


# Paths to the dirs & files of the project
SETTINGS_PATH = Path(__file__)
PROJECT_PATH = SETTINGS_PATH.parents[1]
LUA_SCRIPTS_PATH = SETTINGS_PATH.parent / "lua"
LUA_CATEGORY_PAGE_SCRIPT = LUA_SCRIPTS_PATH / "category_page.lua"
LUA_CAR_PAGE_SCRIPT = LUA_SCRIPTS_PATH / "car_page.lua"
LUA_MAIN_PAGE_HANDLE_FORM = LUA_SCRIPTS_PATH / "main_page_handle_form.lua"
OUTPUT_FILEPATH = PROJECT_PATH / f"{int(time())}_scraped_cars.xlsx"

# Default spider settings generated by Scrapy
BOT_NAME = "AutoRiaScraper"
SPIDER_MODULES = [f"{BOT_NAME}.spiders"]
NEWSPIDER_MODULE = f"{BOT_NAME}.spiders"

# Splash configuration
SPLASH_URL = getenv("SPLASH_URL", "http://127.0.0.1:8050")
DOWNLOADER_MIDDLEWARES = {
  "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
  "AutoRiaScraper.middlewares.RandomUserAgentMiddleware": 540,
  "scrapy_splash.SplashCookiesMiddleware": 723,
  "scrapy_splash.SplashMiddleware": 725,
  "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
}
SPIDER_MIDDLEWARES = {
  "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
}
DUPEFILTER_CLASS = "scrapy_splash.SplashAwareDupeFilter"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Default Spider headers to be sent to the target website:
DEFAULT_REQUEST_HEADERS = {
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",  # noqa
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7",
}

# Excel pipeline
ITEM_PIPELINES = {
  "AutoRiaScraper.pipelines.ItemsToExcelPipeline": 300,
}
