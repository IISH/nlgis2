Batch process scripts to convert and upload polygons in json in the database.
<br>
Usage for batch processing:
batch_loader.py ../json
<br>Directory topojon with all topographic polygons will be automatically created
<br>Usage to get polygons in topojson for specific year, for example, 1812:
<br>topojson.py 1812
<br>Ouput:
{'file_name': '../json/1812.json', 'json': '{"type":"FeatureCollection","features":[{"type":"Feature","id":"gemeenten.108655","geometry":{"type":"MultiPolygon","coordinates":[[[[3.5378534987727446,
51.5541452800982],[3.5419386180420016,51.542342274725364]...
}}

