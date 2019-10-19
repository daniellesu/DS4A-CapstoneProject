from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely import wkt
import shapely.vectorized
from itertools import compress

def create_polygons(geo_df):
    poly_dict = {}
    for i in range(geo_df.shape[0]):
        poly_dict[geo_df.NTACode[i]] = wkt.loads(geo_df.the_geom[i])
    return poly_dict

def assign_nta_general(df, col_lat, col_long, col_NTA, poly_dict):
    tmp = df.sort_values(by=[col_lat, col_long])
    arr = tmp.values
    known = np.empty((0, df.shape[1]))
    nta_list = []
    unk = arr
    lat_idx = df.columns.get_loc(col_lat)
    long_idx = df.columns.get_loc(col_long)
    for i, key in enumerate(poly_dict.keys()):
        print(i, key)
        vals = shapely.vectorized.contains(poly_dict[key], unk[:, long_idx], unk[:, lat_idx])
        idx = list(compress(range(len(vals)), vals))
        nta_list.extend([key] * len(idx))
        known = np.append(known, arr[idx], axis=0)
        unk = np.delete(unk, idx, axis=0)
    nta_list.extend([np.nan] * unk.shape[0])
    new_df = pd.DataFrame(np.append(known, unk, axis=0), columns=df.columns)
    new_df[col_NTA] = nta_list
    return new_df

geo = pd.read_csv("nynta.csv")
poly_dict = create_polygons(geo)

file = pd.read_csv("FILENAME.csv")
new_df = assign_nta_general(file, col_lat, col_long, col_NTA, poly_dict)
new_df.to_csv("FILENAME.csv", index=False)
