HII ROAD DRIVER
---------------

## What does this task do?

This task calculates the (unitless) anthropogenic "influence" of roads on the terrestrical surface as one of the key 
drivers for a combined [Human Influence Index](https://github.com/SpeciesConservationLandscapes/task_hii_weightedsum)
. "Influence" is a combination of `direct` and `indirect` influence 
relative to each cell with at least one road. These source road cells are a combination of:

1. The most recent OSM data relative to `taskdate`, as rasterized by the 
   [task_hii_osm_csv](https://github.com/SpeciesConservationLandscapes/task_hii_osm_csv) and 
   [task_hii_osm_ingest](https://github.com/SpeciesConservationLandscapes/task_hii_osm_ingest) tasks. This image, 
   stored in Earth Engine at `projects/HII/v1/osm/osm_image`, contains up to 24 
   bands for OSM features with motorized-road tags, and up to 5 non-motorized road tags. A cell in each band has a 
   value of 1 in every 300m pixel if there are any OSM features with that tag in the cell, and NoData otherwise. 
   This data is available since 2012-09-12, in steadily increasing quantity and quality.
2. Static gROADS data (https://sedac.ciesin.columbia.edu/data/set/groads-global-roads-open-access-v1) representing 
   1980-2010 are used to fill cells not marked by OSM. (Implicitly, we do not capture roads that actually disappear 
   over time.) In the future, once gROADS' contribution is marginal enough, we will discontinue its use. Conversely, 
   prior to 2012-09-12, it is the only source. 

We are able to use the different OSM road types to weight road influence by type, a key advance over previous Human 
Footprint efforts. These weights are based on the OSM Wiki descriptions: https://wiki.openstreetmap.org/wiki/Key:highway

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

Direct influence is calculated as the per-road-type full weight (above) for 0.5 km to either side of a road.

Indirect influence is calculated using an exponential decay function for 0.5 km to 15 km to either side of a road:

- The indirect maximum weight (at 0.5 km) is 1/2 of the direct weight for a given road type. (This is 
  directly comparable to the logic followed by  
  [Venter et al. 2016](https://trello-attachments.s3.amazonaws.com/5da8bc0a329f3c4dd3089c3f/5eeb7ee36f4bd0693c98125f/b4f64f9bd6270db46ee2e4c4321fb246/Venter_et_al_2016_HFP_update_Data_Scientific_Data.pdf))
- Motorized roads and non-motorized roads have distinct decay functions, reflecting the relative degree of access from 
  the road itself by different modes of travel.
- The decay function is defined as:
```
indirect_influence = e^(distance * decay_constant) * indirect_weight
```

For any given output cell, the end result is the maximum (**not** the cumulative addition) of each direct and indirect 
influence calculated for each type of road. Values are multiplied by 100 and converted to integer for efficient 
exporting to and storage in the Earth Engine HII Road Driver image collection (`projects/HII/v1/driver/roads`).

## Variables and Defaults

### Environment variables
```
SERVICE_ACCOUNT_KEY=<GOOGLE SERVICE ACCOUNT KEY>
```

### Class constants

```
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
