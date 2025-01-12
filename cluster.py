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


knn = NearestNeighbors(n_neighbors=15, metric="precomputed")


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
            # throws this error when there aren't enough sites left in stacked

            print(
                f"""
            {len(stacked_copy)} remaining sites (not full {target_work_hours} hours):
            {addresses_copy}
            """
            )
            break

        for i in neighbors_mat:
            # neighbors_mat is new every iteration, so indexes row 0
            job_time = float(orig_data.iloc[i]["projected_hours"].rstrip(".").strip())
            neighbors_time_dict[i] = job_time
            # creates dict for site index and job_time

        for hours in neighbors_time_dict.values():
            hours_sum += hours
            # get total hours in neighbors_mat
        nbt_time_lst = list(neighbors_time_dict.values())

        amount_over_target = hours_sum - target_work_hours

        while True:
            val_to_remove = nbt_time_lst[0]
            # min(
            # range(len(nbt_time_lst)),
            # key=lambda i: abs(nbt_time_lst[i] - amount_over_target),
            # )
            # ]
            # finds the hours values in neighbors_time_dict that is closest to the amount over target

            if val_to_remove > amount_over_target and amount_over_target > 2.5:
                # makes sure no will not overestimate by more than 2.5 hours
                for x in range(len(nbt_time_lst)):
                    val = nbt_time_lst[x]
                    if val < amount_over_target:
                        val_to_remove = val
                        break

            if val_to_remove > amount_over_target:
                break

            amount_over_target = amount_over_target - val_to_remove
            site_to_remove = list(get_key(val_to_remove, neighbors_time_dict))
            nbt_time_lst.remove(val_to_remove)
            for i in site_to_remove:
                # because multiple sites have same hour value, this loop keeps an error from being raised and tries again with another site
                try:
                    neighbors_mat.remove(i)
                    break

                except ValueError:
                    pass

        one_site_group = []
        for idx in range(len(addresses_copy)):
            if idx in neighbors_mat:
                to_add = orig_data.iloc[idx].tolist()
                if to_add[4]:
                    to_add[4] = "Yes"
                if not to_add[4]:
                    to_add[4] = ""

                if to_add[5]:
                    to_add[5] = "Yes"
                if not to_add[5]:
                    to_add[5] = ""

                if to_add[7]:
                    to_add[7] = "Yes"
                if not to_add[7]:
                    to_add[7] = ""

                if to_add[8]:
                    to_add[8] = "Yes"
                if not to_add[8]:
                    to_add[8] = ""

                if to_add[9]:
                    to_add[9] = "Yes"
                if not to_add[9]:
                    to_add[9] = ""

                del to_add[12]

                one_site_group.append(to_add)

        addresses_copy = [
            ele for idx, ele in enumerate(addresses_copy) if idx not in neighbors_mat
        ]
        orig_data = orig_data.reset_index(drop=True)
        orig_data = orig_data.drop(neighbors_mat)

        stacked_copy = [
            ele for idx, ele in enumerate(stacked_copy) if idx not in neighbors_mat
        ]

        site_groups.append(one_site_group)

    # return clean(site_groups)
    return site_groups


def get_key(val, neighbors_time_dict):
    for key, value in neighbors_time_dict.items():
        if val == value:
            yield key


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
    # coords = [(lat, lng) for street, lat, lng in stacked]
    distance_matrix = precompute_distance_matrix(stacked, street_change_penalty)
    knn.fit(distance_matrix)
    _, neighbors_mat = knn.kneighbors(distance_matrix)

    neighbors_mat = list(
        reversed(neighbors_mat[0])
    )  # reversed so closest pt comes last
    return neighbors_mat
