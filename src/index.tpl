<!DOCTYPE html>
<html>
    <head>
        <title>Network report</title>
        <meta http-equiv="refresh" content="{{refresh}}">
    </head>
    <body>
        <table>
            <tr>
                <th>NAME</th>
                <th>IP</th>
                <th>MAC</th>
                <th>Linkek</th>
            </tr>
            % for device in device_list:
                <tr>
                    <td>{{device.name}}</td>
                    <td>{{device.ip}}</td>
                    <td>{{device.mac}}</td>
                    <td>
                        <table>
                            <tr>
                                <th>Switch neve</th>
                                <th>Port leírás</th>
                                <th>Port</th>
                                <th>VLAN</th>
                                <th>Status</th>
                            </tr>
                        % for link in device.port_links:
                            <tr>
                                <td>{{link.sw_name}}</td>
                                <td>{{link.port_description}}</td>
                                <td>{{link.port_id}}</td>
                                <td>{{link.vlan}}</td>
                                <td>{{link.status}}</td>
                            </tr>
                        % end
                        </table></td>
                </tr>
            % end
        </table>
    </body>
</html>
