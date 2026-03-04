@echo off
echo Building and running

docker stop cont-markov-app 2>nul
docker rm cont-markov-app 2>nul

docker build -t image-marko-app .

docker run -d -p 8080:8000 --name cont-markov-app image-marko-app

echo App is RUNNING SUCCESSFULLY!
echo IN browser http://localhost:8080
echo API documentation: http://localhost:8080/docs
echo.
echo For log check: docker logs cont-markov-app
echo To stop container: docker stop cont-markov-app