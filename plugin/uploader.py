import logging

import os, sys, json, socket, select, hashlib
from textwrap import wrap
from flask import abort, render_template_string
from flask import jsonify

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


IP = "10.0.0.1"
PORT = 12345


SITE_STRING = """
{% extends "base.html" %}
{% set active_page = "plugins" %}
{% block title %}
    Uploader
{% endblock %}

{% block styles %}
{{ super() }}
{% endblock %}

{% block content %}
<div class="ui-grid-b">
    <button class="ui-block-a" onclick="sendPost('uploader/srv-hello')">Check Connection</button>
    <button class="ui-block-b" onclick="sendPost('uploader/test-cmd', 'ssid')">Get Cracked SSIDs</button>
    <button class="ui-block-c" onclick="sendPost('uploader/test')">Test</button>
</div>
<div>
    Handshake path: {{hs_path}}
</div>
<div>
    Total Handshake count: {{hs_cnt}}
</div>
<div>
    Unsent Handshake count: {{new_hs_cnt}}
</div>
<div>
    APs on list: {{ap_cnt}}
</div>
<div>
    {% for path in hs_strings %}
    <p>{{path}}</p>
    {% endfor %}
</div>
<div>
    {% for bssid,ssid in ap_list.items() %}
    <p>{{bssid}} : {{ssid}}</p>
    {% endfor %}
</div>
{% endblock %}

{% block script %}
function sendPost(url, msg="") {
    var xobj = new XMLHttpRequest()
    var csrf = "{{ csrf_token() }}"
    xobj.open("POST", url)
    xobj.setRequestHeader("x-csrf-token", csrf)
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4) {
            console.log(xobj.status)
            try {
                console.log(JSON.parse(xobj.response))
            }
            catch (error) {
                console.error(error)
                console.log(xobj.response)
            }
            console.log("TODO: Dodać refresh")
        }
    }
    xobj.send(msg)
}

function jsonToTable(obj) {
    
}
{% endblock %}
"""


class Uploader(plugins.Plugin):
    __author__ = 'Ta trójka z labów'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Does it matter if it does not work anyway?'

    def __init__(self):
        logging.debug("example plugin created")
        self.ap_index = {"96:0a:c6:3a:97:60": "LBK_AP"}
        self.ready = False
        self.hs_paths = []
        self.ex_paths = []
        self.new_paths = []

    def on_config_changed(self, config):
        self.config = config
        self.ready = True
        logging.warning("CONFIG CHANGED")
        logging.info(self.config["bettercap"]["handshakes"])

    # called when http://<host>:<port>/plugins/<plugin>/ is called
    # must return a html page
    # IMPORTANT: If you use "POST"s, add a csrf-token (via csrf_token() and render_template_string)
    def on_webhook(self, path, request):
        if request.method == "GET":
            hs_dir = self.config["bettercap"]["handshakes"]
            # handshake filenames
            hs_fns = os.listdir(hs_dir)
            self.hs_paths = [os.path.join(hs_dir, filename) for
                    filename in hs_fns if filename.endswith(".pcap")]
            with open(os.path.join(
                    self.config["main"]["custom_plugins"],
                    "uploader_exclude"
                    )) as f:
                self.ex_paths = f.readlines()
            self.ex_paths = [x.rstrip() for x in self.ex_paths]

            hs_cnt = len(self.hs_paths)
            self.new_paths = list(
                set(self.hs_paths) - set(self.ex_paths)
                )
            new_hs_cnt = len(self.new_paths)

            return render_template_string(
                    SITE_STRING,
                    hs_path=self.config["bettercap"]["handshakes"],
                    hs_cnt=hs_cnt,
                    hs_strings=self.new_paths,
                    new_hs_cnt=new_hs_cnt,
                    ap_list=self.ap_index,
                    ap_cnt=len(self.ap_index.items())
                    )

        elif request.method == "POST":
            if path == "srv-hello":
                ret_str = "DEFAULT"
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((IP, PORT))
                    sock.send("yoo".encode())
                    rs, _, _ = select.select([sock], [], [])

                    for cs in rs:
                        reply = cs.recv(1024).decode().strip()
                        logging.info(reply)
                        cs.close()
                        ret_str = reply
                except Exception as e:
                    logging.error(e)
                    ret_str = e

                return ret_str

            elif path == "test-cmd":
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((IP, PORT))
                    sock.send(request.data)
                    rs, _, _ = select.select([sock], [], [])

                    for cs in rs:
                        reply = cs.recv(1024).decode().replace("\0", "\n").strip()
                        logging.info(reply)
                        cs.close()
                        kvp = [x.split("\t") for x in reply.split("\n")]
                        dct = {y[0]: y[1] for y in kvp}
                        ret_str = jsonify(dct)

                except Exception as e:
                    logging.error(e)
                    ret_str = e

                return ret_str


            elif path == "test":
                try:
                    for path in self.new_paths:
                        cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        cli_socket.connect((IP, PORT))
                        cli_socket.setblocking(False)

                        hsmac = ":".join(wrap(path.split("_")[1].split(".")[0], 2))
                        logging.info(f"hsmac= {hsmac}")

                        if hsmac not in self.ap_index.keys():
                            logging.error(f"{hsmac} not in ap_index")
                            continue

                        cli_socket.send("hs".encode())

                        sha256 = hashlib.sha256()

                        read_sockets, _, _ = select.select([cli_socket], [], [])

                        for socks in read_sockets:
                            test = socks.recv(1024).decode().strip()
                            logging.info(repr(test))

                            f = open(path, "rb")

                            for byte_block in iter(lambda: f.read(1024), b""):
                                sha256.update(byte_block)

                            f.close()
                            f = open(path, "rb")
                                    
                            cli_socket.send(f"{hsmac}#{self.ap_index[hsmac]}#{sha256.hexdigest()}".encode())

                            read_sockets, _, _ = select.select([cli_socket], [], [])

                            for socks in read_sockets:
                                test = socks.recv(1024).decode().strip()
                                logging.info(repr(test))

                                bs = f.read(1024)
                                while (bs):
                                    socks.send(bs)
                                    bs = f.read(1024)
                                socks.close()

                        logging.info(f"Uploaded {path}")
                except Exception as e:
                    logging.error(e)

                f = open(os.path.join(
                    self.config["main"]["custom_plugins"],
                    "uploader_exclude"
                    ),
                    "w"
                )
                for path in self.hs_paths:
                    f.write(path)
                    f.write('\n')
                f.close()

                return "zapisane"


            logging.info(str(request))
            logging.info(json.dumps(request))
            return "test"
        
        return "bad request"

    # called when the plugin is loaded
    def on_loaded(self):
        logging.warning("WARNING: this plugin is very bad!")

    # called when there's internet connectivity
    def on_internet_available(self, agent):
        pass

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        # add custom UI elements
        ui.add_element('upls', LabeledValue(color=BLACK, label='UPStat: ', value='INIT', position=(ui.width() / 2 - 30, 0),
                                           label_font=fonts.Bold, text_font=fonts.Medium))

    # called when the ui is updated
    def on_ui_update(self, ui):
        # update those elements
        #ui.set('uploader_status', "DEAD")
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        logging.info("unit is ready")
        # you can run custom bettercap commands if you want
        #   agent.run('ble.recon on')
        # or set a custom state
        #   agent.set_bored()

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        logging.info(filename)
        logging.info(json.dumps(access_point))
        self.ap_index[str(access_point.mac)] = str(access_point.hostname)
        logging.info(len(self.ap_index.items()))
        pass
