#!/bin/bash
app="traversal_defense"
docker build . -t traversal_defense
docker run -p 5000:5000 -v $(pwd):/user_images -d traversal_defense