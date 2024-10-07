#!/usr/bin/python3
"""
OpenGear boilerplate
"""
import requests
import urllib3
import json

# Class definition
class Opengear:
    """
    Opengear Class
    """

    # Class constructor
    def __init__(self, host:str, username:str , password:str , verify:bool=False, port:int=443, api:str="/api/v1.8"):
        """
        Args:
            host (str): IP or hostname (without https://)
            username (str): Username
            password (str): Password
            verify (bool): enable / disable certificate check
            port (int): TCP port number (defaults to 443)
        """
        # Base properties
        self.base_url = 'https://' + host + ":" + str(port) + api
        self.session = requests.Session()
        # SSL verify
        self.verify = verify
        if not verify:
            urllib3.disable_warnings()
        # Login
        self.connected = self.__login(username,password)

    # Login method
    def __login(self, username:str, password:str):
        """
        Authenticates to Opengear and update session
        """
        # Submit login form
        headers = { "Content-Type": "application/json" }
        data = { "username": f"{username}", "password": f"{password}" }
        try:
            response = self.session.post(f"{self.base_url}/sessions", data=json.dumps(data), headers=headers, verify=self.verify)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'ConnectionError: {e}')
        # Login OK when response code is 200
        if response.status_code == 200:
            # Get session
            data = json.loads(response.text)
            token = data["session"]
            # Set headers
            self.headers = {
                "Content-Type": "application/json",
                "Authorization" : f"Token {token}"
            }
            self.kwargs = {"verify": self.verify, "headers": self.headers}
            return True
        # Fail by default
        return False

    # Private method
    def __get(self,path:str,params:dict={}):
        """
        Generic GET request
        Returns:
            str: response body
        """
        if not self.connected:
            return None
        try:
            response = self.session.get(f"{self.base_url}{path}", **self.kwargs, params=params)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'ConnectionError: {e}')
        return response.text if response.status_code == 200 else None

    def __post(self,path:str,params:dict={},data:dict={}):
        """
        Generic POST request
        Returns:
            str: response body
        """
        if not self.connected:
            return None
        try:
            response = self.session.post(f"{self.base_url}{path}", **self.kwargs, params=params, data=data)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f'ConnectionError: {e}')
        return response.text if response.status_code == 200 else None

    # Public method
    def getVersion(self):
        """
        Get version
        Returns:
            dict: Device version
        """
        data = self.__get('/system/version')
        return json.loads(data)["system_version"] if data else None
    
    def getDevice(self):
        """
        Get device
        Returns:
            dict: Device details
        """
        data = self.__get('/nodeDescription')
        return json.loads(data) if data else None

    def getSerialPorts(self):
        """
        Get serial ports
        Returns:
            dict: Serial ports configuration
        """
        data = self.__get('/serialPorts')
        return json.loads(data)["serialports"] if data else None

    def getModemStatus(self):
        """
        Get cellular modem status
        Returns:
            dict: Modem status
        """
        data = self.__get('/interfaces/cellmodem/status')
        return json.loads(data) if data else None

# Run
if __name__ == "__main__":
    # Instantiate class
    host     = "hostname"
    username = "username"
    password = "password"
    session = Opengear(host, username, password)
    # Get device version
    version = session.getVersion()
    if version:
        print(version["firmware_version"])
    # Get device data
    device = session.getDevice()
    if device:
        print(f'model={device["model_number"]},serial={device["serial_number"]},version={device["firmware_version"]}')
    # List ports
    ports = session.getSerialPorts()
    if ports:
        [ print(port["label"])  for port in ports if port["hardwareType"] == "builtInUART"]
    # Get modem status
    modem = session.getModemStatus()
    if modem:
        print(f'active={modem["up"]},signal_strength={modem["links"][0]["wwan"]["signalStrength"]},carrier={modem["links"][0]["wwan"]["carrier"]},tech={modem["links"][0]["wwan"]["technology"]}')
