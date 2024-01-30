import pandas as pd
import numpy as np
import googlemaps
from sklearn.neighbors import NearestNeighbors
from clean_sheet import clean_data

site_groups = []

street_change_penalty = 0.0001  # Adjust this value as needed


def precompute_distance_matrix(points, penalty):
    num_points = len(points)
    distance_matrix = np.zeros((num_points, num_points))

    for i in range(num_points):
        for j in range(num_points):
            if i != j:
                street_i = points[i][0]
                street_j = points[j][0]
                coords_i = points[i][1:]
                coords_j = points[j][1:]
                distance = np.linalg.norm(np.array(coords_i) - np.array(coords_j))
                if street_i != street_j:
                    distance += penalty
                distance_matrix[i, j] = distance

    return distance_matrix


def cluster_sites(target_work_hours: int, circuit: str) -> list[str]:
    data, orig_data = clean_data(circuit)
    addresses, lats, lngs = get_address_coords(data)
    stacked = stack_coords(addresses, lats, lngs)
    stacked_copy = stacked.copy()
    addresses_copy = addresses.copy()

    for i in stacked_copy:
        hours_sum = 0

        neighbors_time_dict = {}

        try:
            neighbors_mat = get_neighbors(stacked_copy)

        except ValueError:
            err_msg = f"""
            {len(stacked_copy)} remaining sites (not full {target_work_hours} hours):
            {addresses_copy}
            """
            raise ValueError(err_msg)

        job_time = (
            orig_data.iloc[neighbors_mat, :].loc["projected_hours"].apply(lambda val: float(val.rstrip(".").strip()))
        )
        neighbors_time_dict = {row: job_time for row, job_time in zip(range(len(neighbors_mat)), job_time.values)}

        hours_sum = job_time.sum()
        # get total hours in neighbors_mat
        nbt_time_lst = list(job_time)

        amount_over_target = hours_sum - target_work_hours
        amount_over_target_without_element = amount_over_target - nbt_time_lst
        error = amount_over_target_without_element - target_work_hours
        # get the index the results in the smallest error without going 2.5 hours over
        error_minimizing_idx = error.index(min([x if x < 2.5 else np.inf for x in error]))
        job_time_to_remove = nbt_time_lst[error_minimizing_idx]
        amount_over_target -= job_time_to_remove
        del nbt_time_lst[error_minimizing_idx]
        # reverse the dict, then use the value as the key
        site_to_remove = {v: k for k, v in neighbors_time_dict.items()}[job_time_to_remove]
        neighbors_mat.remove(site_to_remove)

        one_site_group = []
        for idx in range(len(addresses_copy)):
            if idx in neighbors_mat:
                to_add = ["Yes" if item else "" for item in orig_data.iloc[idx]]
            del to_add[12]

            one_site_group.append(to_add)

        addresses_copy = [ele for idx, ele in enumerate(addresses_copy) if idx not in neighbors_mat]
        orig_data = orig_data.reset_index(drop=True)
        orig_data = orig_data.drop(neighbors_mat)

        stacked_copy = [ele for idx, ele in enumerate(stacked_copy) if idx not in neighbors_mat]

        site_groups.append(one_site_group)

    return site_groups


def clean(site_groups):
    clean_site_groups = []

    for i in site_groups:
        groups = [x[0] for x in i]
        clean_site_groups.append(groups)
    return clean_site_groups


def get_address_coords(data):
    gmaps = googlemaps.Client(key="AIzaSyCe-hRSpX1tm2kND1AhL5ueIPd-rduvcaE")
    df = data.loc[:, "full_address"]
    df = pd.DataFrame(df)
    addresses = df.values.tolist()

    lats = []
    lngs = []

    addresses = [x for x in addresses if x != [""]]

    for x in addresses[0:120]:
        geocode = gmaps.geocode(x)
        geocode_pt = geocode[0].get("geometry").get("location")
        lat = geocode_pt.get("lat")
        lng = geocode_pt.get("lng")
        lats.append(lat)
        lngs.append(lng)
    return addresses, lats, lngs


def stack_coords(addresses, lats, lngs):
    split = [x[0].split() for x in addresses]
    streets = [x[1:4] for x in split]
    streets = ["".join(x).lower() for x in streets]
    stacked = [(street, lat, lng) for street, lat, lng in zip(streets, lats, lngs)]
    return stacked


def get_neighbors(stacked):
    knn = NearestNeighbors(n_neighbors=15, metric="precomputed")
    # coords = [(lat, lng) for street, lat, lng in stacked]
    distance_matrix = precompute_distance_matrix(stacked, street_change_penalty)
    knn.fit(distance_matrix)
    _, neighbors_mat = knn.kneighbors(distance_matrix)

    neighbors_mat = list(reversed(neighbors_mat[0]))  # reversed so closest pt comes last
    return neighbors_mat
