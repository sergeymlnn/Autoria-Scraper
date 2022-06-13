### Running Splash Container

```
docker run -d -p 8050:8050 \
    --memory=4.5G \
    --restart=always \
    scrapinghub/splash:3.5 \
    --maxrss 4000 \
    --max-timeout 3600
```
