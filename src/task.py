import argparse
import ee
from datetime import datetime, timezone
from task_base import HIITask


class HIIRoad(HIITask):
    scale = 300
    OSM_START = datetime(2012, 9, 12).date()
    NOMINAL_ROAD_WIDTH = 300  # width of roads in inputs
    DIRECT_INFLUENCE_WIDTH = 1000  # total width of direct influence (meters)
    INDIRECT_INFLUENCE_RADIUS = (
        15000  # distance from road indirect influence limit (meters)
    )
    DECAY_CONSTANT_MOTORIZED = -0.0003
    DECAY_CONSTANT_NON_MOTORIZED = -0.0004
    DIRECT_INDIRECT_INFLUENCE_RATIO = 0.5

    inputs = {
        "osm": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": "projects/HII/v1/osm/osm_image",
            "maxage": 1,
        },
        # TODO: refactor source dir structure
        "groads": {
            "ee_type": HIITask.IMAGE,
            "ee_path": "projects/HII/v1/source/infra/gROADS-v1-global",
            "static": True,
        },
        "water": {
            "ee_type": HIITask.IMAGE,
            "ee_path": "projects/HII/v1/source/phys/watermask_jrc70_cciocean",
            "static": True,
        },
    }
    # road keys and relative importance: https://wiki.openstreetmap.org/wiki/Key:highway
    road_weights = {
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
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sumatra AOI for testing
        # self.set_aoi_from_ee(
        #     "projects/SCL/v1/Panthera_tigris/geographies/Sumatra/Sumatra_woody_cover"
        # )
        self.osm, _ = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["osm"]["ee_path"])
        )
        self.groads = ee.Image(self.inputs["groads"]["ee_path"])
        self.water = ee.Image(self.inputs["water"]["ee_path"])
        self.road_direct_cost = None
        self.road_indirect_cost = None
        self.kernel = {
            "DIRECT": ee.Kernel.euclidean(
                radius=self.DIRECT_INFLUENCE_WIDTH / 2, units="meters"
            ),
            "INDIRECT": ee.Kernel.euclidean(
                radius=self.INDIRECT_INFLUENCE_RADIUS, units="meters"
            ),
        }

    def osm_groads_combined_influence(self):
        osm_band_names = self.osm.bandNames()
        motorized_weights = ee.Dictionary(self.road_weights["motorized"])
        non_motorized_weights = ee.Dictionary(self.road_weights["non_motorized"])
        road_weights = motorized_weights.combine(non_motorized_weights)
        band_names = ee.Dictionary(
            {
                "all": road_weights.keys(),
                "osm": osm_band_names.filter(
                    ee.Filter.inList("item", road_weights.keys())
                ),
                "motorized": motorized_weights.keys().filter(
                    ee.Filter.Or(
                        ee.Filter.inList("item", osm_band_names),
                        ee.Filter.eq("item", "groad"),
                    )
                ),
                "non_motorized": non_motorized_weights.keys(),
                "groad": ["groad"],
            }
        )

        direct_weights = road_weights.toImage()
        indirect_weights = direct_weights.multiply(self.DIRECT_INDIRECT_INFLUENCE_RATIO)

        osm_roads = self.osm.select(band_names.get("osm"))

        osm_direct = (
            osm_roads.distance(kernel=self.kernel["DIRECT"], skipMasked=False)
            .lte((self.DIRECT_INFLUENCE_WIDTH - self.NOMINAL_ROAD_WIDTH) / 2)
            .multiply(direct_weights.select(band_names.get("osm")))
        )

        groad_direct = (
            self.groads.distance(kernel=self.kernel["DIRECT"], skipMasked=False)
            .lte((self.DIRECT_INFLUENCE_WIDTH - self.NOMINAL_ROAD_WIDTH) / 2)
            .multiply(direct_weights.select(band_names.get("groad")))
        )

        non_osm = osm_direct.reduce(ee.Reducer.max()).unmask(0).eq(0).selfMask()

        groad_fill = groad_direct.updateMask(non_osm)

        road_direct_bands = osm_direct.addBands(groad_fill)
        self.road_direct_cost = road_direct_bands.reduce(ee.Reducer.max()).rename(
            "road_direct"
        )

        road_indirect_cost_distance = road_direct_bands.distance(
            kernel=self.kernel["INDIRECT"], skipMasked=False
        )
        motorized_indirect_cost = road_indirect_cost_distance.select(
            band_names.get("motorized")
        )
        non_motorized_indirect_cost = road_indirect_cost_distance.select(
            band_names.get("non_motorized")
        )

        motorized_decay = (
            motorized_indirect_cost.multiply(self.DECAY_CONSTANT_MOTORIZED)
            .exp()
            .multiply(indirect_weights.select(band_names.get("motorized")))
            .updateMask(
                motorized_indirect_cost.lte(
                    self.INDIRECT_INFLUENCE_RADIUS - (self.DIRECT_INFLUENCE_WIDTH / 2)
                )
            )
            .reduce(ee.Reducer.max())
            .rename("road_indirect_motorized")
        )

        non_motorized_decay = (
            non_motorized_indirect_cost.multiply(self.DECAY_CONSTANT_NON_MOTORIZED)
            .exp()
            .multiply(indirect_weights.select(band_names.get("non_motorized")))
            .updateMask(
                non_motorized_indirect_cost.lte(
                    self.INDIRECT_INFLUENCE_RADIUS - (self.DIRECT_INFLUENCE_WIDTH / 2)
                )
            )
            .reduce(ee.Reducer.max())
            .rename("road_indirect_non_motorized")
        )
        self.road_indirect_cost = motorized_decay.addBands(non_motorized_decay)

    def groads_influence(self):
        groad_direct_weight = self.road_weights["motorized"]["groad"]
        groad_indirect_weight = groad_direct_weight * (
            self.DIRECT_INDIRECT_INFLUENCE_RATIO
        )

        self.road_direct_cost = (
            self.groads.distance(kernel=self.kernel["DIRECT"], skipMasked=False)
            .lte((self.DIRECT_INFLUENCE_WIDTH - self.NOMINAL_ROAD_WIDTH) / 2)
            .multiply(groad_direct_weight)
            .rename("road_direct")
        )
        groad_indirect_cost_distance = self.road_direct_cost.distance(
            kernel=self.kernel["INDIRECT"], skipMasked=False
        )
        self.road_indirect_cost = (
            groad_indirect_cost_distance.multiply(self.DECAY_CONSTANT_MOTORIZED)
            .exp()
            .multiply(groad_indirect_weight)
            .updateMask(
                groad_indirect_cost_distance.lte(
                    self.INDIRECT_INFLUENCE_RADIUS - (self.DIRECT_INFLUENCE_WIDTH / 2)
                )
            )
            .rename("road_indirect_motorized")
        )

    def calc(self):
        if self.osm:
            self.osm_groads_combined_influence()
        else:
            self.groads_influence()

        road_driver = (
            self.road_direct_cost.addBands(self.road_indirect_cost)
            .reduce(ee.Reducer.max())
            .unmask(0)
            .updateMask(self.water)
            .multiply(100)
            .int()
            .rename("hii_road_driver")
        )

        # TODO: implement normalization options
        self.export_image_ee(
            road_driver,
            f"driver/roads",
        )

    def check_inputs(self):
        if self.taskdate >= self.OSM_START:
            super().check_inputs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing outputs instead of incrementing",
    )
    options = parser.parse_args()
    road_task = HIIRoad(**vars(options))
    road_task.run()
