from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ActuatorRequest(_message.Message):
    __slots__ = ["active", "deviceId", "name", "value"]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DEVICEID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    active: bool
    deviceId: int
    name: str
    value: float
    def __init__(self, name: _Optional[str] = ..., deviceId: _Optional[int] = ..., value: _Optional[float] = ..., active: bool = ...) -> None: ...

class ActuatorResponse(_message.Message):
    __slots__ = ["success"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DeviceStatus(_message.Message):
    __slots__ = ["active", "deviceId", "name", "unit", "value"]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DEVICEID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    active: bool
    deviceId: int
    name: str
    unit: str
    value: float
    def __init__(self, deviceId: _Optional[int] = ..., name: _Optional[str] = ..., active: bool = ..., value: _Optional[float] = ..., unit: _Optional[str] = ...) -> None: ...
