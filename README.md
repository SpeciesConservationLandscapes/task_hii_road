HII ROAD DRIVER
-----------

## What does this task do?

1. Imports rasterized OSM and gROADS data stored as EarthEngine assets
2. Utilized most recent OSM data, based on the task date
3. Uses gROADS data before OSM data is available (2012-09-12), or to fill in OSM data when OSM data is available
4. Weights OSM road types by relative importance (https://wiki.openstreetmap.org/wiki/Key:highway)
5. Direct impact (full weights) are set for 0.5 km either side of a road
6. Indirect weights are calculated using and exponential decay function for up to 15 km either side of a road
  • The indirect maximum weight is 1/2 of the direct weight for a given road type.
  • Motorized roads and non-motorized roads have distinct decay functions.
  • The decay function is defined as:
    indirect_influence = e^(Distance * decay_constant) * indirect_weight
7. For any pixel, the end result is the maximum weight (cumulative affects are not accounted for)
8. Values are multiplied by 100 and set to integers
9. Outputs are exported to the HII Road Driver image collection

## Key Variables and Defaults

```
SERVICE_ACCOUNT_KEY=<GOOGLE SERVICE ACCOUNT KEY>
SCALE=300
OSM_START=(2012-09-09)
NOMINAL_ROAD_WIDTH=300
DIRECT_INFLUENCE_WIDTH=1000
INDIRECT_INFLUENCE_RADIUS=15000
DECAY_CONSTANT_MOTORIZED=-0.0003
DECAY_CONSTANT_NON_MOTORIZED=-0.0004
DIRECT_INDIRECT_INFLUENCE_RATIO=0.5
```

## Usage

```
/app # python hii_road.py --help
usage: task.py [-h] [-d TASKDATE]

optional arguments:
  -h, --help            show this help message and exit
  -d TASKDATE, --taskdate TASKDATE
```
