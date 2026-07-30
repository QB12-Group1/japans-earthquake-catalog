import pandas as pd

from src.collectors import (
    emsc_collector as ec,
)
from src.collectors import (
    geofon_collector as gc,
)
from src.collectors import (
    usgs_collector as uc,
)
from src.transform import (
    geofon_transform as gt,
)
from src.transform import (
    side_dataset_transform as sdt,
)
from src.transform import (
    usgs_transform as ut,
)


def get_side_dataset_df(collect: bool) -> pd.DataFrame:
    if collect:
        sdt.export_transformed()
    return sdt.load_transformed()


def get_geofon_df(collect: bool) -> pd.DataFrame:
    if collect:
        gc.export_raw()
        gt.export_transformed()
    return gt.load_transformed()


def get_usgs_df(collect: bool) -> pd.DataFrame:
    if collect:
        uc.export_raw()
        ut.export_transformed()
    return ut.load_transformed()


def get_emsc_df(collect: bool) -> pd.DataFrame:
    if collect:
        ec.export_raw()  # TODO: this should be transformed
    return ec.load_raw()


def get_merged_sources_df(collect: bool) -> pd.DataFrame:
    loaders = [get_usgs_df, get_side_dataset_df, get_geofon_df, get_emsc_df]
    return pd.concat([loader(collect) for loader in loaders])
