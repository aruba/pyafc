# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from typing import Literal

from pyafc.common import exceptions
from pyafc.route_policies import (
    as_path_lists,
    community_lists,
    prefix_lists,
    route_maps,
)


class RoutePolicy(
    route_maps.RouteMap,
    prefix_lists.PrefixList,
    community_lists.CommunityList,
    as_path_lists.ASPathList,
):
    def __init__(
        self,
        client,
        name: str,
        policy_type: Literal[
            "route_map", "prefix_list", "community_list", "aspath_list"
        ] = "unset",
        **kwargs: dict,
    ) -> None:
        self.client = client
        self.name = name
        if policy_type == "route_map":
            route_maps.RouteMap.__init__(self, **kwargs)
        elif policy_type == "prefix_list":
            prefix_lists.PrefixList.__init__(self, **kwargs)
        elif policy_type == "community_list":
            community_lists.CommunityList.__init__(self, **kwargs)
        elif policy_type == "aspath_list":
            as_path_lists.ASPathList.__init__(self, **kwargs)
        else:
            raise exceptions.PolicyTypeNotValid(
                "Policy Type has not been specified or is not a valid one"
            )
