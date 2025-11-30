Thanks for taking a look at this project!

To use a different coastline, go to `overpass-turbo.eu` and zoom into the coastline you want to export. 

Use this query: 
[out:json][timeout:90];
(
  // Get coastline ways
  way["natural"="coastline"]({{bbox}});
  
  // Also get any relations containing coastlines (for complex coastlines)
  relation["natural"="coastline"]({{bbox}});
);
out geom;

Click `Run`. If it is siccessful, go to `Export` and click the `download` button next to GeoJSON. To use this in the code. Switch out my `export.geoson` file for the one you have acquired. 

You can now run `simulation.py` with your own coastline. 
