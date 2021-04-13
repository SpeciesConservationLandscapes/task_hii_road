import argparse
import ee
from datetime import datetime, timezone, timedelta
from task_base import HIITask


class HIIRoad(HIITask):
    scale = 100
    OSM_START = datetime(2012, 9, 12).date()
    KERNEL_DISTANCE = 500
    DIRECT_INFLUENCE_RADIUS = 350
    INDIRECT_INFLUENCE_RADIUS = 15000
    DECAY_CONSTANT = -0.0002
    INDIRECT_INFLUENCE = 4

    inputs = {
        "osm": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": "projects/HII/v1/osm/osm_image",
            "maxage": 1,
        },
        "groads": {
            "ee_type": HIITask.IMAGE,
            "ee_path": "projects/HII/v1/source/infra/gROADS-v1-global-v2",
            "static": True,
        },
        "water": {
            "ee_type": HIITask.IMAGE,
            "ee_path": "projects/HII/v1/source/phys/watermask_jrc70_cciocean",
            "static": True,
        },
    }
    weights = {
        "osm": {
            "highway_residential": 10,
            "highway_bridleway": 10,
            "highway_bus_guideway": 10,
            "highway_cycleway": 10,
            "highway_elevator": 10,
            "highway_escape": 4,
            "highway_footway": 4,
            "highway_living_street": 10,
            "highway_mini_roundabout": 10,
            "highway_motorway": 10,
            "highway_motorway_link": 10,
            "highway_path": 4,
            "highway_pedestrian": 4,
            "highway_primary": 10,
            "highway_primary_link": 10,
            "highway_raceway": 10,
            "highway_rest_area": 10,
            "highway_road": 10,
            "highway_secondary": 10,
            "highway_secondary_link": 10,
            "highway_service": 10,
            "highway_steps": 4,
            "highway_tertiary": 10,
            "highway_tertiary_link": 10,
            "highway_track": 4,
            "highway_trunk": 10,
            "highway_trunk_link": 10,
            "highway_turning_circle": 10,
            "highway_unclassified": 10,
        },
        "groad": 10,
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
        self.road_direct = None

    def kernel(self):
        return ee.Kernel.euclidean(radius=self.KERNEL_DISTANCE, units="meters")

    def osm_groads_combined_influence(self):
        osm_band_names = self.osm.bandNames()
        road_band_names = list(self.weights["osm"].keys())
        road_bands = osm_band_names.filter(ee.Filter.inList("item", road_band_names))
        osm_roads = self.osm.select(road_bands)
        weights_image = ee.Dictionary(self.weights["osm"]).toImage().select(road_bands)

        # creates 1km wide images with direct influence values
        osm_direct = (
            osm_roads.distance(kernel=self.kernel(), skipMasked=False)
            .lte(self.DIRECT_INFLUENCE_RADIUS)
            .selfMask()
            .multiply(weights_image)
        )
        groads_direct = (
            self.groads.distance(kernel=self.kernel(), skipMasked=False)
            .lte(self.DIRECT_INFLUENCE_RADIUS)
            .selfMask()
            .multiply(self.weights["groad"])
        )

        # masks groads that overlap (< 500m) from an OSM road
        non_osm_binary = osm_direct.reduce(ee.Reducer.anyNonZero()).unmask(0).eq(0)
        groads_fill = groads_direct.updateMask(non_osm_binary)

        self.road_direct = (
            osm_direct.addBands(groads_fill)
            .reduce(ee.Reducer.sum())
            .multiply(2)
            .unmask(0)
            .rename("road_direct_influence")
        )

    def groads_influence(self):
        self.road_direct = (
            (
                self.groads.distance(kernel=self.kernel(), skipMasked=False)
                .lte(self.DIRECT_INFLUENCE_RADIUS)
                .selfMask()
                .multiply(self.weights["groad"])
            )
            .multiply(2)
            .unmask(0)
            .rename("road_direct_influence")
        )

    def calc(self):
        if self.osm:
            self.osm_groads_combined_influence()
        else:
            self.groads_influence()
        road_binary = self.road_direct.gt(0).unmask(0)
        road_indirect = (
            road_binary.eq(0)
            .cumulativeCost(road_binary, self.INDIRECT_INFLUENCE_RADIUS)
            .multiply(self.DECAY_CONSTANT)
            .exp()
            .multiply(self.INDIRECT_INFLUENCE)
            .reproject(crs=self.crs, scale=self.scale)
            .unmask(0)
            .rename("roads_indirect_influence")
        )
        # TODO: determine if drivers are to be normalized or not.
        # TODO: values beyond indirect range (15km) - do we set to 0 or mask?
        road_driver = (
            self.road_direct.where(self.road_direct.eq(0), road_indirect)
            .rename("road_driver")
            .updateMask(self.water)  # Mask water
            .multiply(100)  # Scales outputs and sets data to integer
            .int()
        )

        self.export_image_ee(
            road_driver,
            f"driver/roads",
        )

    # Check inputs is not called if date is before OSM_START
    def check_inputs(self):
        if self.taskdate >= self.OSM_START:
            super().check_inputs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate", default=datetime.now(timezone.utc).date())
    options = parser.parse_args()
    road_task = HIIRoad(**vars(options))
    road_task.run()
