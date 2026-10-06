#docker build -f Dockerfile.mapgen -t registry.services.atlantishq.de/atlantishq/neroxis-mapgen .
#docker build -f Dockerfile.mapgen-worker -t registry.services.atlantishq.de/atlantishq/neroxis-mapgen-worker .
docker build -f ./server/Dockerfile.server -t registry.services.atlantishq.de/atlantishq/mapgen-as-a-service-server ./server
docker build ./frontend -t harbor-registry.atlantishq.de/atlantishq/mapgen-as-a-service-server-frontend

#docker push registry.services.atlantishq.de/atlantishq/neroxis-mapgen
#docker push registry.services.atlantishq.de/atlantishq/neroxis-mapgen-worker
docker push registry.services.atlantishq.de/atlantishq/mapgen-as-a-service-server
docker push registry.services.atlantishq.de/atlantishq/mapgen-as-a-service-server-frontend
