"""Named bright stars used for offline FOV labeling (J2000, no catalog download)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrightStar:
    name: str
    ra_hours: float
    dec_degrees: float
    magnitude: float
    constellation: str


# Magnitudes and positions: standard IAU/common navigational values (J2000).
BRIGHT_STARS: tuple[BrightStar, ...] = (
    BrightStar("Sirius", 6.7525, -16.7161, -1.46, "CMa"),
    BrightStar("Canopus", 6.3992, -52.6957, -0.74, "Car"),
    BrightStar("Arcturus", 14.2610, 19.1824, -0.05, "Boo"),
    BrightStar("Vega", 18.6156, 38.7837, 0.03, "Lyr"),
    BrightStar("Capella", 5.2782, 45.9980, 0.08, "Aur"),
    BrightStar("Rigel", 5.2423, -8.2016, 0.13, "Ori"),
    BrightStar("Procyon", 7.6550, 5.2250, 0.34, "CMi"),
    BrightStar("Betelgeuse", 5.9195, 7.4071, 0.42, "Ori"),
    BrightStar("Altair", 19.8464, 8.8683, 0.76, "Aql"),
    BrightStar("Aldebaran", 4.5987, 16.5093, 0.85, "Tau"),
    BrightStar("Antares", 16.4901, -26.4319, 0.96, "Sco"),
    BrightStar("Spica", 13.4199, -11.1613, 0.97, "Vir"),
    BrightStar("Pollux", 7.7553, 28.0262, 1.14, "Gem"),
    BrightStar("Fomalhaut", 22.9608, -29.6222, 1.16, "PsA"),
    BrightStar("Deneb", 20.6905, 45.2803, 1.25, "Cyg"),
    BrightStar("Regulus", 10.1395, 11.9672, 1.35, "Leo"),
    BrightStar("Adhara", 6.9771, -28.9721, 1.50, "CMa"),
    BrightStar("Castor", 7.5766, 31.8883, 1.58, "Gem"),
    BrightStar("Bellatrix", 5.4189, 6.3497, 1.64, "Ori"),
    BrightStar("Elnath", 5.4382, 28.6075, 1.65, "Tau"),
    BrightStar("Alnilam", 5.6036, -1.2019, 1.69, "Ori"),
    BrightStar("Alioth", 12.9004, 55.9598, 1.76, "UMa"),
    BrightStar("Mirfak", 3.4054, 49.8612, 1.79, "Per"),
    BrightStar("Dubhe", 11.0621, 61.7510, 1.79, "UMa"),
    BrightStar("Alkaid", 13.7923, 49.3133, 1.85, "UMa"),
    BrightStar("Alhena", 6.6285, 16.3993, 1.93, "Gem"),
    BrightStar("Polaris", 2.5303, 89.2641, 1.98, "UMi"),
    BrightStar("Mirach", 1.1622, 35.6206, 2.05, "And"),
    BrightStar("Alpheratz", 0.1398, 29.0904, 2.06, "And"),
    BrightStar("Hamal", 2.1195, 23.4628, 2.00, "Ari"),
    BrightStar("Denebola", 11.8177, 14.5721, 2.14, "Leo"),
    BrightStar("Algol", 3.1361, 40.9556, 2.12, "Per"),
    BrightStar("Alphard", 9.4598, -8.6586, 1.98, "Hya"),
    BrightStar("Schedar", 0.6751, 56.5373, 2.23, "Cas"),
    BrightStar("Caph", 0.1529, 59.1498, 2.27, "Cas"),
    BrightStar("Mira", 2.3224, -2.9776, 3.04, "Cet"),
    BrightStar("Enif", 21.7364, 9.8750, 2.39, "Peg"),
    BrightStar("Markab", 23.0793, 15.2053, 2.49, "Peg"),
    BrightStar("Scheat", 23.0629, 28.0828, 2.42, "Peg"),
    BrightStar("Ruchbah", 1.4302, 60.2353, 2.68, "Cas"),
)
