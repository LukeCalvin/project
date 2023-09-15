import pandas as pd
import numpy as np
import googlemaps
from sklearn.neighbors import NearestNeighbors
from clean_sheet import clean_data

knn = NearestNeighbors(n_neighbors=15)

site_groups = []

TARGET_WORK_HOURS = 12


def cluster_sites(TARGET_WORK_HOURS):
    data = clean_data()
    addresses, lats, lngs = get_address_coords(data)
    stacked = stack_coords(lats, lngs)
    stacked_copy = stacked.copy()
    addresses_copy = addresses.copy()

    for i in stacked_copy:
        hours_sum = 0

        neighbors_time_dict = {}

        try:
            knn.fit(stacked_copy)
            distance_mat, neighbors_mat = knn.kneighbors(stacked_copy)
            neighbors_mat = list(
                reversed(neighbors_mat[0])
            )  # reversed so closest pt comes last

        except ValueError:
            # throws this error when there aren't enough sites left in stacked

            print(
                f"""
            {len(stacked_copy)} remaining sites:
            {addresses_copy}
            """
            )
            break

        for i in neighbors_mat:
            # neighbors_mat is new every iteration, so indexes row 0
            job_time = float(data.iloc[i]["projected_hours"])
            neighbors_time_dict[i] = job_time
            # creates dict for site index and job_time

        for hours in neighbors_time_dict.values():
            hours_sum += hours
            # get total hours in neighbors_mat
        nbt_time_lst = list(neighbors_time_dict.values())

        amount_over_target = hours_sum - TARGET_WORK_HOURS

        while True:
            val_to_remove = nbt_time_lst[
                min(
                    range(len(nbt_time_lst)),
                    key=lambda i: abs(nbt_time_lst[i] - amount_over_target),
                )
            ]
            # finds the hours values in neighbors_time_dict that is closest to the amount over target

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

        one_site_group = [
            ele for idx, ele in enumerate(addresses_copy) if idx in neighbors_mat
        ]
        addresses_copy = [
            ele for idx, ele in enumerate(addresses_copy) if idx not in neighbors_mat
        ]
        stacked_copy = [
            ele for idx, ele in enumerate(stacked_copy) if idx not in neighbors_mat
        ]

        site_groups.append(one_site_group)

    return clean(site_groups)


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

    for x in addresses:
        geocode = gmaps.geocode(x)
        geocode_pt = geocode[0].get("geometry").get("location")
        lat = geocode_pt.get("lat")
        lng = geocode_pt.get("lng")
        lats.append(lat)
        lngs.append(lng)
    return addresses, lats, lngs


def stack_coords(lats, lngs):
    x = np.array(lngs)
    y = np.array(lats)
    stacked = np.dstack((x, y))
    stacked = stacked[0]
    return stacked
