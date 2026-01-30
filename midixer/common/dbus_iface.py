"""D-Bus interface definitions for midixer daemon"""

# D-Bus service configuration
DBUS_SERVICE_NAME = "org.midixer.Daemon"
DBUS_OBJECT_PATH = "/org/midixer/Daemon"
DBUS_INTERFACE_NAME = "org.midixer.Daemon"

# D-Bus interface XML definition
DBUS_INTERFACE_XML = """
<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node>
  <interface name="org.midixer.Daemon">
    <method name="GetMappings">
      <arg direction="out" type="s" name="mappings_json"/>
    </method>
    <method name="AddMapping">
      <arg direction="in" type="s" name="mapping_json"/>
      <arg direction="out" type="b" name="success"/>
    </method>
    <method name="RemoveMapping">
      <arg direction="in" type="i" name="index"/>
      <arg direction="out" type="b" name="success"/>
    </method>
    <method name="GetMidiDevices">
      <arg direction="out" type="s" name="devices_json"/>
    </method>
    <method name="GetPipewireNodes">
      <arg direction="out" type="s" name="nodes_json"/>
    </method>
    <method name="Reload">
      <arg direction="out" type="b" name="success"/>
    </method>
    <method name="Quit">
    </method>
    <signal name="MappingChanged">
      <arg type="s" name="action"/>
    </signal>
  </interface>
</node>
"""
