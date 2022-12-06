#!/bin/bash
app="traversal_defense"
docker build . -t traversal_defense
docker run -p 5000:5000 -d traversal_defense