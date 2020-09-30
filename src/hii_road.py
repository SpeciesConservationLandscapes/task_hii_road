import argparse
import ee
from datetime import datetime, timezone
from task_base import HIITask

class HIIRoad(HIITask):
    ee_rootdir = "projects/HII/v1/"
    ee_driverdir = "driver/road"
    ee_hiistatic_osm = "projects/HII/v1/source/osm_earth/"
    ee_hiistatic_infra = "projects/HII/v1/source/infra/"
    ee_hiistatic_physical = "projects/HII/v1/source/phys/"
    scale = 300
    DECAY_CONSTANT = -0.0002
    INDIRECT_INFLUENCE = 4

    highway_bridleway_weighting = 10
    highway_bus_guideway_weighting = 10
    highway_cycleway_weighting = 10
    highway_elevator_weighting = 10
    highway_escape_weighting = 4
    highway_footway_weighting = 4
    highway_living_street_weighting = 10
    highway_mini_roundabout_weighting = 10
    highway_motorway_weighting = 10
    highway_motorway_link_weighting = 10
    highway_path_weighting = 4
    highway_pedestrian_weighting = 4
    highway_primary_weighting = 10
    highway_primary_link_weighting = 10
    highway_raceway_weighting = 10
    highway_rest_area_weighting = 10
    highway_road_weighting = 10
    highway_secondary_weighting = 10
    highway_secondary_link_weighting = 10
    highway_service_weighting = 10
    highway_steps_weighting = 4
    highway_tertiary_weighting = 10
    highway_tertiary_link_weighting = 10
    highway_track_weighting = 4
    highway_trunk_weighting = 10
    highway_trunk_link_weighting = 10
    highway_turning_circle_weighting = 10
    highway_unclassified_weighting = 10

    highway_groads_weighting = 10




    inputs = {
        "highway_bridleway": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/bridleway",
        },
        "highway_bus_guideway": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/bus_guideway",
        },
        "highway_cycleway": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/cycleway",
        },
        "highway_elevator": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/elevator",
        },
        "highway_escape": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/escape",
        },
        "highway_footway": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/footway",
        },
        "highway_living_street": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/living_street",
        },
        "highway_mini_roundabout": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/mini_roundabout",
        },
        "highway_motorway": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/motorway",
        },
        "highway_motorway_link": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/motorway_link",
        },
        "highway_path": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/path",
        },
        "highway_pedestrian": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/pedestrian",
        },
        "highway_primary": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/primary",
        },
        "highway_primary_link": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/primary_link",
        },
        "highway_raceway": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/raceway",
        },
        "highway_rest_area": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/rest_area",
        },
        "highway_road": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/road",
        },
        "highway_secondary": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/secondary",
        },
        "highway_secondary_link": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/secondary_link",
        },
        "highway_service": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/service",
        },
        "highway_steps": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/steps",
        },
        "highway_tertiary": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/tertiary",
        },
        "highway_tertiary_link": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/tertiary_link",
        },
        "highway_track": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/track",
        },
        "highway_trunk": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/trunk",
        },
        "highway_trunk_link": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/trunk_link",
        },
        "highway_turning_circle": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/turning_circle",
        },
        "highway_unclassified": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{ee_hiistatic_osm}highway/unclassified",
        },
        "groads_additions": {
            "ee_type": HIITask.IMAGE,
            "ee_path": f"{ee_hiistatic_infra}groads_additions",
        },
        "watermask": {
            "ee_type": HIITask.IMAGE,
            "ee_path": f"{ee_hiistatic_physical}watermask_jrc70_cciocean",
            "static": True,
        },
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.realm = kwargs.pop("realm", None)

        self.set_aoi_from_ee('projects/HII/v1/source/realms/' + self.realm)  


    def calc(self):
        watermask = ee.Image(self.inputs["watermask"]["ee_path"])

        highway_bridleway, highway_bridleway_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_bridleway"]["ee_path"])
        )
        
        highway_bus_guideway, highway_bus_guideway_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_bus_guideway"]["ee_path"])
        )
        
        highway_cycleway, highway_cycleway_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_cycleway"]["ee_path"])
        )
        
        highway_elevator, highway_elevator_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_elevator"]["ee_path"])
        )
        
        highway_escape, highway_escape_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_escape"]["ee_path"])
        )
        
        highway_footway, highway_footway_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_footway"]["ee_path"])
        )
        
        highway_living_street, highway_living_street_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_living_street"]["ee_path"])
        )
        
        highway_mini_roundabout, highway_mini_roundabout_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_mini_roundabout"]["ee_path"])
        )

        highway_motorway, highway_motorway_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_motorway"]["ee_path"])
        )

        highway_motorway_link, highway_motorway_link_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_motorway_link"]["ee_path"])
        )
        
        highway_path, highway_path_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_path"]["ee_path"])
        )
        
        highway_pedestrian, highway_pedestrian_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_pedestrian"]["ee_path"])
        )
        
        highway_primary, highway_primary_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_primary"]["ee_path"])
        )
        
        highway_primary_link, highway_primary_link_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_primary_link"]["ee_path"])
        )
        
        highway_raceway, highway_raceway_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_raceway"]["ee_path"])
        )
        
        highway_rest_area, highway_rest_area_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_rest_area"]["ee_path"])
        )
        
        highway_road, highway_road_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_road"]["ee_path"])
        )

        highway_secondary, highway_secondary_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_secondary"]["ee_path"])
        )

        highway_secondary_link, highway_secondary_link_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_secondary_link"]["ee_path"])
        )
        
        highway_service, highway_service_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_service"]["ee_path"])
        )
        
        highway_steps, highway_steps_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_steps"]["ee_path"])
        )
        
        highway_tertiary, highway_tertiary_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_tertiary"]["ee_path"])
        )
        
        highway_tertiary_link, highway_tertiary_link_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_tertiary_link"]["ee_path"])
        )
        
        highway_track, highway_track_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_track"]["ee_path"])
        )
        
        highway_trunk, highway_trunk_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_trunk"]["ee_path"])
        )
        
        highway_trunk_link, highway_trunk_link_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_trunk_link"]["ee_path"])
        )

        highway_turning_circle, highway_turning_circle_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_turning_circle"]["ee_path"])
        )

        highway_unclassified, highway_unclassified_date = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["highway_unclassified"]["ee_path"])
        )



        highway_total = (highway_bridleway.multiply(self.highway_bridleway_weighting)
            .add(highway_bus_guideway.multiply(self.highway_bus_guideway_weighting))
            .add(highway_cycleway.multiply(self.highway_cycleway_weighting))
            .add(highway_elevator.multiply(self.highway_elevator_weighting))
            .add(highway_escape.multiply(self.highway_escape_weighting))
            .add(highway_footway.multiply(self.highway_footway_weighting))
            .add(highway_living_street.multiply(self.highway_living_street_weighting))
            .add(highway_mini_roundabout.multiply(self.highway_mini_roundabout_weighting))
            .add(highway_motorway.multiply(self.highway_motorway_weighting))
            .add(highway_motorway_link.multiply(self.highway_motorway_link_weighting))
            .add(highway_path.multiply(self.highway_path_weighting))
            .add(highway_pedestrian.multiply(self.highway_pedestrian_weighting))
            .add(highway_primary.multiply(self.highway_primary_weighting))
            .add(highway_primary_link.multiply(self.highway_primary_link_weighting))
            .add(highway_raceway.multiply(self.highway_raceway_weighting))
            .add(highway_rest_area.multiply(self.highway_rest_area_weighting))
            .add(highway_road.multiply(self.highway_road_weighting))
            .add(highway_secondary.multiply(self.highway_secondary_weighting))
            .add(highway_secondary_link.multiply(self.highway_secondary_link_weighting))
            .add(highway_service.multiply(self.highway_service_weighting))
            .add(highway_steps.multiply(self.highway_steps_weighting))
            .add(highway_tertiary.multiply(self.highway_tertiary_weighting))
            .add(highway_tertiary_link.multiply(self.highway_tertiary_link_weighting))
            .add(highway_track.multiply(self.highway_track_weighting))
            .add(highway_trunk.multiply(self.highway_trunk_weighting))
            .add(highway_trunk_link.multiply(self.highway_trunk_link_weighting))
            .add(highway_turning_circle.multiply(self.highway_turning_circle_weighting))
            .add(highway_unclassified.multiply(self.highway_unclassified_weighting))
            .add(ee.Image(self.inputs["groads_additions"]["ee_path"]).multiply(self.highway_groads_weighting))
        ).multiply(2)


        roads_bool = highway_total.gt(0)

        roads_indirect = roads_bool.eq(0)\
            .cumulativeCost(roads_bool, 15000)\
            .reproject(crs=self.crs, scale=self.scale)\
            .multiply(self.DECAY_CONSTANT)\
            .exp()\
            .multiply(self.INDIRECT_INFLUENCE)\
            .unmask(0)

        roads_total = highway_total.add(roads_indirect).updateMask(watermask)

        self.export_image_ee(
            roads_total,
            "{}/{}".format(self.ee_driverdir, "aois/" + self.realm),
            
        )

    def check_inputs(self):
        super().check_inputs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--realm", default='Afrotropic')
    parser.add_argument("-d", "--taskdate", default=datetime.now(timezone.utc).date())
    options = parser.parse_args()
    road_task = HIIRoad(**vars(options))
    road_task.run()