import gpxpy
import pytz
import pyproj

from timezonefinder import TimezoneFinder
from statistics import median

def get_timezone_from_points(points):
    """Compute timezone from median latitude and longitude of points."""
    if not points:
        return "UTC"  # fallback if no points
    lats = [p.lat for p in points]  # use .lat
    lons = [p.lon for p in points]  # use .lon
    median_lat = median(lats)
    median_lon = median(lons)
    
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=median_lat, lng=median_lon)
    return tz or "UTC"

class Point:
	def __init__(
		self, 
		date,
		timestamp,
		lat,
		lon,
		az,
	):
		self.date = date
		self.timestamp = timestamp

		self.lat = float(lat)
		self.lon = float(lon)

		self.az = az

	def __str__(self):
		return f"date: '{self.date}', timestamp: {self.timestamp}, lat: {self.lat}, lon: {self.lon}, az: {self.az}"

	def to_dict(self):
		return {
			'date': self.date,
			'timestamp': self.timestamp,
			'lat': self.lat,
			'lon': self.lon,
			'az': self.az,
		}

class GPXData:
	def __init__(
		self,
		filename,
		timezone,
	):
		self.points = []

		with open(filename, 'r') as gpx_file:
			gpx = gpxpy.parse(gpx_file)
   
		gpx.simplify()
  
		for track in gpx.tracks:
			for segment in track.segments:
				for idx, point in enumerate(segment.points[1:]):
					previous_point = segment.points[
						idx - 1
      				]

					G = pyproj.Geod(ellps='WGS84')
					fwd_azimuth = G.inv(
						previous_point.longitude,
						previous_point.latitude,
						point.longitude,
						point.latitude
					)[0]
					if fwd_azimuth < 0:
						fwd_azimuth += 360
        
					dt = point.time.replace(
						tzinfo=pytz.UTC
					)
					local_time = dt.astimezone(
						pytz.timezone(timezone)
					)

					self.points.append(
						Point(
							local_time.strftime('%Y-%m-%dT%H:%M:%S'), 
							local_time.strftime('%s'), 
							point.latitude, 
							point.longitude,
							fwd_azimuth,
						)
					)

	def get_points(self):
		return self.points	