import gpxpy
import pyproj
import pytz
from dataclasses import dataclass
from typing import List

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

@dataclass
class Point:
    time: str
    timestamp: str
    lat: float
    lon: float
    az: float


class GPXData:
    def __init__(
        self,
        filename,
        timezone,
        min_distance_km=5.0,  # Minimum distance between stargazing points
        min_azimuth_change=30.0,  # Minimum heading change in degrees
    ):
        self.points = []
        self.min_distance_km = min_distance_km
        self.min_azimuth_change = min_azimuth_change
        
        with open(filename, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            gpx.simplify()
            for track in gpx.tracks:
                for segment in track.segments:
                    for idx, point in enumerate(segment.points[1:]):
                        previous_point = segment.points[idx - 1]
                        G = pyproj.Geod(ellps="WGS84")
                        fwd_azimuth = G.inv(
                            previous_point.longitude,
                            previous_point.latitude,
                            point.longitude,
                            point.latitude,
                        )[0]
                        if fwd_azimuth < 0:
                            fwd_azimuth += 360
                        dt = point.time.replace(tzinfo=pytz.UTC)
                        local_time = dt.astimezone(pytz.timezone(timezone))
                        self.points.append(
                            Point(
                                local_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                local_time.strftime("%s"),
                                point.latitude,
                                point.longitude,
                                fwd_azimuth,
                            )
                        )
        
        # Filter to only stargazing points
        self.points = self._select_stargazing_points()

    def _calculate_distance(self, p1: Point, p2: Point) -> float:
        """Calculate distance between two points in kilometers."""
        G = pyproj.Geod(ellps="WGS84")
        _, _, distance = G.inv(p1.lon, p1.lat, p2.lon, p2.lat)
        return distance / 1000  # Convert to km

    def _azimuth_difference(self, az1: float, az2: float) -> float:
        """Calculate the smallest angle difference between two azimuths."""
        diff = abs(az1 - az2)
        if diff > 180:
            diff = 360 - diff
        return diff

    def _is_point_unique(self, candidate: Point, selected: List[Point]) -> bool:
        """Check if a candidate point is sufficiently unique from already selected points."""
        if not selected:
            return True
        
        for existing in selected:
            distance = self._calculate_distance(candidate, existing)
            azimuth_change = self._azimuth_difference(candidate.az, existing.az)
            
            # Point must be either far enough OR have significantly different heading
            if distance < self.min_distance_km and azimuth_change < self.min_azimuth_change:
                return False
        
        return True

    def _select_stargazing_points(self) -> List[Point]:
        """
        Select distinct points for stargazing that offer unique views.
        Points are chosen based on spatial separation and heading changes.
        """
        if not self.points:
            return []
        
        stargazing_points = []
        
        # Always include the first point
        stargazing_points.append(self.points[0])
        
        # Sample points throughout the track
        for point in self.points[1:]:
            if self._is_point_unique(point, stargazing_points):
                stargazing_points.append(point)
        
        # Always include the last point if it's not already included
        if self.points[-1] not in stargazing_points:
            if self._is_point_unique(self.points[-1], stargazing_points):
                stargazing_points.append(self.points[-1])
        
        return stargazing_points

    def get_points(self):
        """Get selected stargazing points with unique views."""
        return self.points