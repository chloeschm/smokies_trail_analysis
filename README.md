# Smokies Trail Analysis

Estimating elevation gain for different trail segmens in GSMNP and presenting the results as 
gain per mile and an interactive map :)

## Question

How much elevation gain do Smokies trail segments have, and how can the
segments be grouped into useful difficulty bands?

(The analysis is intended for comparison and visualization. This is not a
replacement for an official trail information or an on trail measurements)

## Data sources

The repository includes:

- `data/trails.geojson`: trail geometries and source attributes
  (attributes include trail names, access information, and source metadata)
- `data/smokies_dem.tif`: the digital elevation model used to sample
  elevations along each trail geometry

The trail data is reprojected to EPSG:5070 before lengths and elevation profiles 
are calculated. The final metrics are exported to `outputs/trail_metrics.geojson` 
in EPSG:4326 so they can be used by Folium.

The validation script compares estimates for two named trails with published
figures from third-party web sources:

- Ramsey Cascades Trail: 2,200–2,375 ft published range
- Abrams Falls Trail: 610–679 ft published range

These references are used just as plausibility checks.

## Method

The analysis follows these steps:

1. Load the trail geometries and reproject them to EPSG:5070.
2. Derive trail length from the projected geometry in meters, then convert it
   to miles.
3. Segmentize each line at approximately 8.82 m, which matches the DEM cell
   size.
4. Interpolate DEM elevations at those sample points.
5. Smooth the elevation profile with a centered rolling median over a 150 m
   span.
6. Calculate total gain by summing only positive changes between consecutive
   smoothed elevations, then convert the result from meters to feet.
7. Calculate `gain_per_mi` as total gain in feet divided by the derived
   length in miles.
8. Export the segment metrics and use them to create the interactive map.

Multipart geometries are handled part by part. Their gains are summed so the
metric represents the complete feature rather than only one component.

### Why a 150 m span?

The 150 m smoothing span was selected by running the validation workflow
against the published reference ranges for Ramsey Cascades Trail and Abrams
Falls Trail. The span reduces small-scale DEM noise while retaining broader
climbs. The validation script reports whether each computed gain falls within
its published range.

Validation rests on only two trails, and the published references themselves
conflict across sources. The selected span should therefore be treated as a
practical, project-specific choice rather than a universally optimal
parameter.

## Difficulty cutoffs

The map assigns each segment a difficulty label from `gain_per_mi`:

| Classification | Elevation gain per mile |
| --- | ---: |
| Easy | 0–250 ft/mi |
| Moderate | 251–500 ft/mi |
| Difficult | 501–800 ft/mi |
| Very Challenging | 801 ft/mi and up |

Segments shorter than 0.1 mile are excluded from the map because their
gain-per-mile values are especially sensitive to small elevation errors. The
map reports how many segments were removed before classification.

## Outputs

- `outputs/trail_metrics.geojson`: calculated metrics for all trail features
- `outputs/trail_map.html`: interactive Folium map with colored trail lines,
  popups, and a difficulty legend
- `outputs/gain_map.png`: static gain visualization
- `outputs/trails_map.png`: static trail visualization

## Running the analysis

Run commands from the repository root:

```text
python src/analysis.py
python src/validate_gain.py
python src/make_map.py
```

The scripts expect the input files in `data/` and write generated files to
`outputs/`.

## Limitations

- **DEM noise on flat ground:** Flat or nearly flat ground can still show
  some calculated gain because small elevation fluctuations in the DEM become
  positive differences after sampling. The 150 m rolling median reduces this
  effect but does not eliminate it.
- **Limited and conflicting validation:** Validation uses only Ramsey Cascades
  Trail and Abrams Falls Trail. Their published elevation figures differ
  between sources, so agreement with these ranges does not establish accuracy
  for every trail.
- **Length-field mismatch:** The source dataset's length attributes do not
  match the lengths implied by its geometries. This project derives
  `length_mi` from the projected geometry for consistency with the spatial
  analysis; results should not be compared casually with the source length
  fields.
- **Resolution and interpolation:** Elevation estimates depend on the DEM's
  resolution, interpolation, and alignment with the trail geometry.
- **No descent or trail-condition information:** Gain per mile captures
  cumulative ascent only. It does not account for descent, surface,
  exposure, switchbacks, weather, or current trail conditions.
- **Classification is project-specific:** The difficulty bands are simple
  gain-per-mile thresholds and should not be interpreted as official National
  Park Service difficulty ratings.
