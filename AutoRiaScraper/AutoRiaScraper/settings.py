import time
from os import environ
from pathlib import Path

from dotenv import dotenv_values


BOT_NAME = 'AutoRiaScraper'
SPIDER_MODULES = ['AutoRiaScraper.spiders']
NEWSPIDER_MODULE = 'AutoRiaScraper.spiders'

# Root path to the project
ROOT_PATH = (Path(__file__) / "../../").resolve()

# Config filename and its absolute path
ENV_CONFIG_FILENAME = ".env.config"
ENV_CONFIG_PATH = ROOT_PATH / ENV_CONFIG_FILENAME

# Uploading all available environment variables and ones from the config file
ENV_CONFIG = {**environ, **dotenv_values(dotenv_path=ENV_CONFIG_PATH)}

# Splash configuration
SPLASH_URL = ENV_CONFIG.get("SPLASH_URL", "http://127.0.0.1:8050")
DOWNLOADER_MIDDLEWARES = {
    "scrapy_splash.SplashCookiesMiddleware": 723,
    "scrapy_splash.SplashMiddleware": 725,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
}
SPIDER_MIDDLEWARES = {
    "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
}
DUPEFILTER_CLASS = "scrapy_splash.SplashAwareDupeFilter"
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
SPLASH_LOG_400 = True

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2.5

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Default Spider headers to be sent to the target website:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,uk-UA;q=0.8,uk;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
}

# Identifying spider with a custom UA until random ones are provided
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"
