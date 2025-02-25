"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import builtins
import google.protobuf.descriptor
import google.protobuf.message
import typing

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class ActuatorRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    NAME_FIELD_NUMBER: builtins.int
    DEVICEID_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    ACTIVE_FIELD_NUMBER: builtins.int
    name: builtins.str
    deviceId: builtins.int
    value: builtins.float
    active: builtins.bool
    def __init__(
        self,
        *,
        name: builtins.str = ...,
        deviceId: builtins.int = ...,
        value: builtins.float = ...,
        active: builtins.bool = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["active", b"active", "deviceId", b"deviceId", "name", b"name", "value", b"value"]) -> None: ...

global___ActuatorRequest = ActuatorRequest

@typing.final
class ActuatorResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    SUCCESS_FIELD_NUMBER: builtins.int
    success: builtins.str
    def __init__(
        self,
        *,
        success: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["success", b"success"]) -> None: ...

global___ActuatorResponse = ActuatorResponse

@typing.final
class DeviceStatus(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    DEVICEID_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    VALUE_FIELD_NUMBER: builtins.int
    UNIT_FIELD_NUMBER: builtins.int
    deviceId: builtins.int
    name: builtins.str
    value: builtins.float
    unit: builtins.str
    def __init__(
        self,
        *,
        deviceId: builtins.int = ...,
        name: builtins.str = ...,
        value: builtins.float = ...,
        unit: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["deviceId", b"deviceId", "name", b"name", "unit", b"unit", "value", b"value"]) -> None: ...

global___DeviceStatus = DeviceStatus
