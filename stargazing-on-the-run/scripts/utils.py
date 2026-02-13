from statistics import median
from dataclasses import dataclass
from typing import List

import gpxpy
import pyproj
import pytz
from timezonefinder import TimezoneFinder

VIEW_ANGLES = [0, 30, 70]


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
    alt: float


class GPXData:
    def __init__(
        self,
        filename,
        timezone,
        min_azimuth_change=30.0,  # Minimum heading change in degrees
        max_points=10,
    ):
        self.points = []
        self.min_azimuth_change = min_azimuth_change
        self.max_points = max_points

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
                                0.0,
                            )
                        )

        # Filter to only stargazing points
        self.min_azimuth_change = self._dynamic_azimuth_threshold()
        self.points = add_view_angles(self._select_stargazing_points())

    def _azimuth_difference(self, az1: float, az2: float) -> float:
        """Calculate the smallest angle difference between two azimuths."""
        diff = abs(az1 - az2)
        if diff > 180:
            diff = 360 - diff
        return diff

    def _dynamic_azimuth_threshold(self) -> float:
        if len(self.points) < 2:
            return self.min_azimuth_change

        diffs = []
        for previous_point, point in zip(self.points, self.points[1:]):
            diffs.append(self._azimuth_difference(previous_point.az, point.az))

        return median(diffs)

    def _is_point_unique(self, candidate: Point, selected: List[Point]) -> bool:
        """Check if a candidate point is sufficiently unique from already selected points."""
        if not selected:
            return True

        for existing in selected:
            azimuth_change = self._azimuth_difference(candidate.az, existing.az)

            if azimuth_change < self.min_azimuth_change:
                return False

        return True

    def _select_stargazing_points(self) -> List[Point]:
        """
        Select distinct points for stargazing that offer unique views.
        Points are chosen based on heading changes.
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

        return limit_points(stargazing_points, self.max_points)

    def get_points(self):
        """Get selected stargazing points with unique views."""
        return self.points


def add_view_angles(points, view_angles=VIEW_ANGLES):
    if not points:
        return []

    view_points = []
    for point in points:
        for idx, alt in enumerate(view_angles, start=1):
            view_points.append(
                Point(
                    point.time,
                    f"{point.timestamp}_v{idx}",
                    point.lat,
                    point.lon,
                    point.az,
                    alt,
                )
            )

    return view_points


def limit_points(points, max_points=10):
    if len(points) <= max_points:
        return points

    step = (len(points) - 1) / (max_points - 1)
    return [points[round(i * step)] for i in range(max_points)]


def load_points(gpx_file):
    points_for_timezone = GPXData(gpx_file, timezone="UTC").get_points()
    timezone = get_timezone_from_points(points_for_timezone)
    return GPXData(gpx_file, timezone).get_points()
