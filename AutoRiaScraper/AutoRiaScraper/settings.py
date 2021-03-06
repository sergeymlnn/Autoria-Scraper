from datetime import datetime
from os import getenv
from pathlib import Path

# from dotenv import dotenv_values


# Custom Spider Settings
DT = datetime.now()
CURRENT_YEAR = DT.year
MIN_YEAR = CURRENT_YEAR - 50
MIN_PRICE = 0.0
CAR_TYPES = ("Всі", "Вживані", "Нові", "Під пригон")
CAR_CATEGORIES = (
    "Будь-який", "Легкові", "Мото", "Вантажівки", "Причепи", "Спецтехніка",
    "Сільгосптехніка", "Автобуси", "Водний транспорт", "Повітряний транспорт",
    "Автобудинки"
)

# Paths to the dirs & files of the project
ROOT_PATH = (Path(__file__) / "../../").resolve()
LUA_SCRIPTS_PATH = Path(__file__).parent.absolute() / "lua"
LUA_CATEGORY_PAGE_SCRIPT = LUA_SCRIPTS_PATH / "category_page.lua"
LUA_CAR_PAGE_SCRIPT = LUA_SCRIPTS_PATH / "car_page.lua"
LUA_MAIN_PAGE_HANDLE_FORM = LUA_SCRIPTS_PATH / "main_page_handle_form.lua"
CARS_EXCEL_PATH = ROOT_PATH / f"{DT:%Y-%m-%d}-scraped_cars.xlsx"

# Scrapy's Spider Settings
BOT_NAME = 'AutoRiaScraper'
SPIDER_MODULES = ['AutoRiaScraper.spiders']
NEWSPIDER_MODULE = 'AutoRiaScraper.spiders'

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
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

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
    "Accept": "*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
}

# Excel pipeline
ITEM_PIPELINES = {
    'AutoRiaScraper.pipelines.ItemsToExcelPipeline': 300,
}