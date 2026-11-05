import spatial_analysis as sa
from data_cleaning import load_trails

# (low, high) in feet, from published sources
REFERENCES = {
    'Ramsey Cascades Trail': (2200, 2375),
    'Abrams Falls Trail': (610, 679),
}


def trail_gain(trails, dem, name):
    # sum segment gains for every segment carrying this trail name
    sub = trails[trails.TRAILNAME == name]
    return sum(sa.segment_gain(dem, geom) for geom in sub.geometry)


def main():
    trails = load_trails()
    dem = sa.load_dem()
    print(f'SMOOTH_SPAN_M={sa.SMOOTH_SPAN_M}  window={sa.SMOOTH_WINDOW} points')
    for name, (low, high) in REFERENCES.items():
        gain = trail_gain(trails, dem, name)
        status = 'within' if low <= gain <= high else 'outside'
        print(f'{name}: {gain:.0f} ft (published {low}-{high} ft, {status})')


if __name__ == '__main__':
    main()
