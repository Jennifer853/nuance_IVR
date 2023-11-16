


## Build Azure App Service

1. login Azure Container Registry
```bash
docker login 2waysms.azurecr.io
```

2. local test

build your image
```bash
docker build . -t 2waysms.azurecr.io/2waysms:0.2
```

test your image locally

```bash
docker run --rm -it -p 8001:80 2waysms.azurecr.io/2waysms:0.2
```

2. Build and push
```bash
docker push 2waysms.azurecr.io/2waysms:0.1
```

3. 