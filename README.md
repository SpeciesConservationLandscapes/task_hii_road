HII ROAD DRIVER
---------------

## What does this task do?

This task calculates the anthropogenic impact of roads on the terrestrial surface as one of the key
drivers for a combined [Human Impact Index](https://github.com/SpeciesConservationLandscapes/task_hii_weightedsum). 
"Impact" is a combination of `direct` and `indirect` impact relative to each cell with at least one road. 
The output HII driver calculated by this task is, like all other HII drivers, unitless; it refers to an absolute 0-10
scale but is not normalized to it, so the actual range of values may be smaller than 0-10.

Source road cells are a combination of:

1. The most recent OSM data relative to `taskdate`, as rasterized by the
   [task_hii_osm_csv](https://github.com/SpeciesConservationLandscapes/task_hii_osm_csv) and
   [task_hii_osm_ingest](https://github.com/SpeciesConservationLandscapes/task_hii_osm_ingest) tasks. This image,
   stored in Earth Engine at `projects/HII/v1/osm/osm_image`, contains up to 24
   bands for OSM features with motorized-road tags, and up to 5 non-motorized road tags. A cell in each band has a
   value of 1 in every 300m pixel if there are any OSM features with that tag in the cell, and NoData otherwise.
   This data is available since 2012-09-12, in steadily increasing quantity and quality; for HII calculations we 
   use OSM data starting in June 2014.
2. Static gROADS data (https://sedac.ciesin.columbia.edu/data/set/groads-global-roads-open-access-v1) representing
   1980-2010 are used to fill cells not marked by OSM. (Implicitly, we do not capture roads that actually disappear
   over time.) In the future, once gROADS' contribution is marginal enough, we will discontinue its use. Conversely,
   prior to 2014-06-04, it is the only source.

We are able to use the different OSM road types to weight road impact by type, a key advance over previous Human
Footprint efforts. These weights are based on the 
[OSM Wiki descriptions](https://wiki.openstreetmap.org/wiki/Key:highway).

```
"motorized": {
    # roads
    "highway_motorway": 10,
    "highway_trunk": 10,
    "highway_primary": 9,
    "highway_secondary": 9,
    "highway_tertiary": 8,
    "highway_unclassified": 7,
    "highway_residential": 7,
    # link roads
    "highway_motorway_link": 10,
    "highway_trunk_link": 10,
    "highway_primary_link": 9,
    "highway_secondary_link": 9,
    "highway_tertiary_link": 8,
    # special road types
    "highway_living_street": 7,
    "highway_service": 8,
    "highway_pedestrian": 6,
    "highway_track": 5,
    "highway_bus_guideway": 8,
    "highway_escape": 8,
    "highway_raceway": 8,
    "highway_road": 10,
    # other highway features
    "highway_elevator": 8,
    "highway_mini_roundabout": 8,
    "highway_rest_area": 7,
    "highway_turning_circle": 8,
    # groad
    "groad": 10,
},
"non_motorized": {
    "highway_footway": 2,
    "highway_bridleway": 3,
    "highway_steps": 4,
    "highway_path": 2,
    "highway_cycleway": 4,
},
```

Direct impact is calculated as the per-road-type full weight (above) for 0.5 km to either side of a road.

Indirect impact is calculated using an exponential decay function for 0.5 km to 15 km to either side of a road:

- The indirect maximum weight (at 0.5 km) is 1/2 of the direct weight for a given road type. (This is
  directly comparable to the logic followed by  
  [Venter et al. 2016](https://www.nature.com/articles/sdata201667))
- Motorized roads and non-motorized roads have distinct decay functions, reflecting the relative degree of access from
  the road itself by different modes of travel.
- The decay function is defined as:
```
indirect_influence = e^(distance * decay_constant) * indirect_weight
```

For any given output cell, the end result is the maximum (**not** the cumulative addition) of each direct and indirect
impact calculated for each type of road. Values are multiplied by 100 and converted to integer for efficient
exporting to and storage in the Earth Engine HII Road Driver image collection (`projects/HII/v1/driver/roads`).

## Variables and Defaults

### Environment variables
```
SERVICE_ACCOUNT_KEY=<GOOGLE SERVICE ACCOUNT KEY>
```

### Class constants

```
scale=300
OSM_START = datetime(2014, 6, 4).date()
NOMINAL_ROAD_WIDTH=300
DIRECT_INFLUENCE_WIDTH=1000
INDIRECT_INFLUENCE_RADIUS=15000
DECAY_CONSTANT_MOTORIZED=-0.0003
DECAY_CONSTANT_NON_MOTORIZED=-0.0004
DIRECT_INDIRECT_INFLUENCE_RATIO=0.5
```

## Usage

*All parameters may be specified in the environment as well as the command line.*

```
/app # python task.py --help
usage: task.py [-h] [-d TASKDATE] [--overwrite]

optional arguments:
  -h, --help            show this help message and exit
  -d TASKDATE, --taskdate TASKDATE
  --overwrite           overwrite existing outputs instead of incrementing

```

### License
Copyright (C) 2022 Wildlife Conservation Society
The files in this repository  are part of the task framework for calculating 
Human Impact Index and Species Conservation Landscapes (https://github.com/SpeciesConservationLandscapes) 
and are released under the GPL license:
https://www.gnu.org/licenses/#GPL
See [LICENSE](./LICENSE) for details.
