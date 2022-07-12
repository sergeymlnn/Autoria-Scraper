### Running Splash Container

```
docker run -d -p 8050:8050 \
    --memory=4.5G \
    --restart=always \
    scrapinghub/splash:3.5 \
    --maxrss 4000 \
    --max-timeout 3600
```


### Using Scrapyd + Scrapyd-Client

```
pip install scrapyd git+https://github.com/scrapy/scrapyd-client.git
```

Step 1: run scrapyd server
```
scrapyd
```
UI will be available here: http://127.0.0.1:6800/

Step 2: deploy spider to scrapyd
```
scrapyd-deploy default -p AutoRiaScraper
```

Step 3: scheduling spider
```
curl http://127.0.0.1:6800/schedule.json \
 -d project=AutoRiaScraper \
 -d spider=autoria_spider
```
Grab **jobid** from the response (6fc595c2eb5211eca0e82db6e1622406)

Step 4: Stop the spider

```
curl http://127.0.0.1:6800/cancel.json \
    -d project=AutoRiaScraper \
    -d job=6fc595c2eb5211eca0e82db6e1622406
```
