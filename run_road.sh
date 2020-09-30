#!/bin/bash

docker run -it -v $PWD/.config:/root/.config scl3/task_hii_road python hii_road.py -r 'Afrotropic'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_road python hii_road.py -r 'Australasia'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_road python hii_road.py -r 'Indomalayan'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_road python hii_road.py -r 'Nearctic'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_road python hii_road.py -r 'Neotropic'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_road python hii_road.py -r 'Oceania'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_road python hii_road.py -r 'Palearctic'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_road python hii_road.py -r 'HighArctic'
