docker build -f Dockerfile.mapgen -t harbor-registry.atlantishq.de/atlantishq/neroxis-mapgen .
docker build -f Dockerfile.mapgen-worker -t harbor-registry.atlantishq.de/atlantishq/neroxis-mapgen-worker .
docker build -f Dockerfile.server -t harbor-registry.atlantishq.de/atlantishq/mapgen-as-a-service-server

docker push harbor-registry.atlantishq.de/atlantishq/neroxis-mapgen
docker push harbor-registry.atlantishq.de/atlantishq/neroxis-mapgen-worker
docker push harbor-registry.atlantishq.de/atlantishq/mapgen-as-a-service-server
