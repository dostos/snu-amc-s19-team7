import numpy as np
import folium
from folium.plugins import HeatMap

from .group import Group
from .user import User, UserStatus

def data_to_html(user_dict : list, group_dict: list) -> str:

    # create map
    data = (np.random.normal(size=(100, 3)) *
            np.array([[1, 1, 1]]) +
            np.array([[48, 5, 1]])).tolist()
    folium_map = folium.Map([48., 5.], tiles='stamentoner', zoom_start=6)
    HeatMap(data).add_to(folium_map)
    
    return folium_map.get_root().render().encode('utf8')
