import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.ops import unary_union

filename = "export.geojson"
gdf = gpd.read_file(filename)

print("Loaded GeoJSON:")
print(f"  - Number of features: {len(gdf)}")
print(f"  - Geometry type: {gdf.geometry.iloc[0].geom_type}")

geom = unary_union(gdf.geometry)
print(f"  - Unified type: {geom.geom_type}")


def extract_coords(geometry):
    """Extract coordinates from any geometry type"""
    coords_list = []

    if geometry.geom_type == "LineString":
        coords_list.append(np.array(geometry.coords))

    elif geometry.geom_type == "MultiLineString":
        for line in geometry.geoms:
            coords_list.append(np.array(line.coords))

    elif geometry.geom_type == "Polygon":
        #get exterior boundary
        coords_list.append(np.array(geometry.exterior.coords))
        #optionally include holes/interiors
        for interior in geometry.interiors:
            coords_list.append(np.array(interior.coords))

    elif geometry.geom_type == "MultiPolygon":
        for poly in geometry.geoms:
            coords_list.append(np.array(poly.exterior.coords))
            for interior in poly.interiors:
                coords_list.append(np.array(interior.coords))

    elif geometry.geom_type == "GeometryCollection":
        for geom_part in geometry.geoms:
            coords_list.extend(extract_coords(geom_part))
        return coords_list

    else:
        raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")

    return coords_list


coords_list = extract_coords(geom)
coords = np.vstack(coords_list)

print(f"  - Total coordinate points: {len(coords)}")

x = coords[:, 0]
y = coords[:, 1]

#normalize
x = (x - x.min()) / (x.max() - x.min())
y = (y - y.min()) / (y.max() - y.min())

points = np.column_stack([x, y])

N = 2048
grid = np.zeros((N, N), dtype=int)

ix = (points[:, 0] * (N - 1)).astype(int)
iy = (points[:, 1] * (N - 1)).astype(int)

#thicken lines to ensure connectivity
offsets = np.array([[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 0], [0, 1], [1, -1], [1, 0], [1, 1]])
for dx, dy in offsets:
    ix2 = np.clip(ix + dx, 0, N - 1)
    iy2 = np.clip(iy + dy, 0, N - 1)
    grid[iy2, ix2] = 1

filled_pixels = np.sum(grid)
print(f"  - Filled pixels: {filled_pixels} ({100 * filled_pixels / (N * N):.2f}% of grid)")

def boxcount(Z, k):
    S = np.add.reduceat(
        np.add.reduceat(Z, np.arange(0, Z.shape[0], k), axis=0),
        np.arange(0, Z.shape[1], k), axis=1
    )
    return np.count_nonzero(S)

sizes = 2 ** np.arange(1, int(np.log2(N / 4)) + 1)
counts = np.array([boxcount(grid, k) for k in sizes])

#debugging
print("\nBox-counting results:")
print("Box Size | Box Count")
print("-" * 25)
for s, c in zip(sizes, counts):
    print(f"{s:8d} | {c:8d}")

mask = counts > 0
sizes_f = sizes[mask]
counts_f = counts[mask]

logsizes = np.log(sizes_f)
logcounts = np.log(counts_f)

#debugging
print("\nLog-space data:")
print("log(ε)   | log(N)")
print("-" * 25)
for ls, lc in zip(logsizes, logcounts):
    print(f"{ls:8.4f} | {lc:8.4f}")

coeffs = np.polyfit(logsizes, logcounts, 1)
fractal_dim = abs(coeffs[0])

#plot the coastline with the dimension
plt.figure(figsize=(10, 10))
plt.imshow(grid, origin="lower", cmap='binary', interpolation='nearest')
plt.title(f"Rasterized Boundary (D = {fractal_dim:.4f})", fontsize=14, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.show()

#debugging
print("\n" + "=" * 40)
print(f"Fractal Dimension = {fractal_dim:.4f}")
print("=" * 40)


