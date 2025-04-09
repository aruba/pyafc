# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0


class NoBGPonRemoteBorderException(Exception):
    pass


class InterfaceNotFound(Exception):
    pass


class RouterAreaNotFound(Exception):
    pass


class NotIPv4Address(Exception):
    pass


class TimeframeNotValid(Exception):
    pass


class PolicyTypeNotValid(Exception):
    pass


class PolicyTypeNotSpecified(Exception):
    pass


class AuthenticationIssue(Exception):
    pass


class EndpointGroupUnknown(Exception):
    pass


class ServiceQualifierUnknown(Exception):
    pass


class ApplicationUnknown(Exception):
    pass


class RuleUnknown(Exception):
    pass


class EnforcerUnknown(Exception):
    pass


class VrfNotFound(Exception):
    pass


class FabricNotFound(Exception):
    pass


class NetworkNotFound(Exception):
    pass


class VMNotFound(Exception):
    pass


class NICNotFound(Exception):
    pass


class VMKNotFound(Exception):
    pass


class HostNotFound(Exception):
    pass


class PortGroupNotFound(Exception):
    pass


class vSwitchNotFound(Exception):
    pass


class NoDeviceFound(Exception):
    pass


class UpdateFailed(Exception):
    pass


class NotGoodVar(Exception):
    pass
