import glob
import sys
import os
import shutil

from utils import GPXData

class StellariumScript:
	SCRIPT = """
points = [
$POINTS$
];

core.clear("natural");
core.setGuiVisible(false);

StelMovementMgr.moveViewport(-45, -45, 0)

LandscapeMgr.setFlagAtmosphere(false);

SolarSystem.setFlagLabels(true);
SolarSystem.setLabelsAmount(10);

SolarSystem.setMoonScale(20);
SolarSystem.setFlagMoonScale(false);

SolarSystem.setFlagMinorBodyScale(false);
SolarSystem.setMinorBodyScale(20);

SolarSystem.setFlagPlanetScale(false);
SolarSystem.setPlanetScale(20);

StarMgr.setFlagStars(true);
StarMgr.setFlagLabels(true);

MilkyWay.setFlagShow(true);

ConstellationMgr.setFlagLabels(true);
ConstellationMgr.setFlagLines(true);

points.forEach(
	function(point) { 
		core.moveToAltAzi(0, point.az)
		core.wait(0.01);

		core.setObserverLocation(
			point.lon, 
			point.lat, 
			0
		);

		core.setDate(point.date, "local");
		core.wait(1);

		core.screenshot(
			point.timestamp, 
			false,
			"$SCREENSHOT_DIR$",
			true,
			"jpeg"
		);
	}
);

core.quitStellarium();
	"""

	def __init__(
		self, 
		points,
		screenshot_dir
	):
		self.points = points
		self.screenshot_dir = screenshot_dir

	def create_script(self, filename):
		script = self.SCRIPT

		script = script.replace(
			"$POINTS$", 
			",\n".join('{ ' + str(point) + ' }' for point in self.points)
		)
		script = script.replace(
			"$SCREENSHOT_DIR$", 
			self.screenshot_dir
		)

		file = open(filename, "w")
		file.write(script)
		file.close()

def main(
    gpx_dir, 
    timezone,
    stellarium_dir,
    screenshot_dir,
):
	if os.path.exists(screenshot_dir):
		shutil.rmtree(screenshot_dir)
    
	gpx_files = glob.glob(
		os.path.join(gpx_dir, '*.gpx'),
    )
	for gpx_file in gpx_files:
		filename = os.path.splitext(os.path.basename(gpx_file))[0]

		gpx_data = GPXData(gpx_file, timezone)
		points = gpx_data.get_points()

		screenshot_path = f"{screenshot_dir}/{filename}"
		os.makedirs(screenshot_path)

		script = StellariumScript(
			points,
			screenshot_path,
		)
		script.create_script(
			f"{stellarium_dir}/{filename}.ssc"
		)
	
if __name__ == "__main__":
    main(*sys.argv[1:])