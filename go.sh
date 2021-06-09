#!/bin/bash

cp -ruv artifacts/count_people/* ~/GreengrassCore/artifacts/com.example.count_people/1.0.0/
cp -ruv recipes/* ~/GreengrassCore/recipes/

sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir ~/GreengrassCore/recipes --artifactDir ~/GreengrassCore/artifacts --merge "com.example.count_people=1.0.0"

sleep 30
sudo /greengrass/v2/bin/greengrass-cli component restart --names=com.example.count_people
