import logging

import os, sys, json, socket, select, hashlib, time
from textwrap import wrap
from flask import abort, render_template_string, jsonify

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

<style>
    .ui-box {
        padding: 0.5rem;
        background-color: rgb(233, 233, 233);
        border: 1px solid rgb(221, 221, 221);
        text-align: center;
        box-sizing: border-box;
    }
    .no-margin {
        margin-bottom: 0 !important;
    }
    table {
        border-collapse: collapse;
        border: 1px solid rgb(221, 221, 221);
    }
    table td,th {
        padding: 0.5rem;
        text-align: center;
        border-collapse: collapse;
        border: 1px solid rgb(221, 221, 221);
        background-color: rgb(246, 246, 246);
    }
    .banner {
        width: 100%;
        padding: 0.2rem;
    }
    #success {
        background-color: green;
        text-align: center;
        color: white;
    }
    #fail {
        background-color: red;
        text-align: center;
        color: white;
    }
</style>
{% endblock %}

{% block content %}
<div class="ui-grid ui-grid-b">
    <div class="ui-block-a">
        <button class="ui-btn ui-icon-search  ui-btn-icon-left no-margin" onclick="sendPost('uploader/srv-hello')">Check Connection</button>
    </div>
    <div class="ui-block-b">
        <button class="ui-btn ui-icon-arrow-d ui-btn-icon-left no-margin" onclick="sendPost('uploader/ssid-pass')">Get Cracked SSIDs</button>
    </div>
    <div class="ui-block-c">
        <button class="ui-btn ui-icon-arrow-u ui-btn-icon-left no-margin" onclick="sendPost('uploader/upload-hs')">Upload Handshakes</button>
    </div>
</div>
<div id="success" style="display:none" class="banner">
    Command succeeded
</div>
<div id="fail" style="display:none" class="banner">
    Command failed
</div>
<div class="ui-grid ui-grid-b marg-me">
    <div class="ui-block-a ui-box">
        Unsent Handshakes: <b>{{new_hs_cnt}}</b>
    </div>
    <div class="ui-block-b ui-box">
        Fully Captured Handshakes: <b>{{ap_cnt}}</b>
    </div>
    <div class="ui-block-c ui-box">
        Total Handshakes: <b>{{hs_cnt}}</b>
    </div>
</div>
<div class="ui-grid ui-grid-a">
    <table class="ui-block-a ui-box">
        <tr>
            <th>Path to handshake file</th>
        </tr>
        {% if hs_strings|length %}
            {% for path in hs_strings %}
            <tr>
                <td>{{path}}</td>
            </tr>
            {% endfor %}
        {% else %}
            <tr>
                <td style="color: gray"> -- no entries -- </td>
            </tr>
        {% endif %}
    </table>
    <table class="ui-block-b ui-box">
        <tr>
            <th>BSSID</th>
            <th>SSID</th>
        </tr>
        {% if ap_list.items()|length %}
            {% for bssid,ssid in ap_list.items() %}
            <tr>
                <td>{{bssid}}</td>
                <td>{{ssid}}</td>
            </tr>
            {% endfor %}
        {% else %}
            <tr>
                <td colspan=2 style="color: gray"> -- no entries -- </td>
            </tr>
        {% endif %}
    </table>
</div>
<div class="ui-grid ui-grid-solo marg-me">
    <div class="ui-block-a ui-box">
        Cracked SSIDs
    </div>
</div>
<div class="ui-grid ui-grid-solo">
    <table class="ui-block-a ui-box">
        <tr>
            <th>SSID</th>
            <th>PASSWORD</th>
        </tr>
        <tbody id="crack">
            <tr>
                <td colspan=2 style="color: gray"> -- no entries -- </td>
            </tr>
        </tbody>
    </table>
</div>
{% endblock %}

{% block script %}
var timeout = null;

function sendPost(url) {
    var xobj = new XMLHttpRequest()
    var csrf = "{{ csrf_token() }}"
    xobj.open("POST", url)
    xobj.setRequestHeader("x-csrf-token", csrf)
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4) {
            $("#success").css("display", "none")
            $("#fail").css("display", "none")
            
            if (xobj.status == 200) {
                $("#success").css("display", "block")
                $("#fail").css("display", "none")
            } else {
                $("#success").css("display", "none")
                $("#fail").css("display", "block")
            }

            if (url == "uploader/srv-hello") {
                console.log("Hello? Well... not much else to do")
            }
            else if (url == "uploader/ssid-pass") {
                if (xobj.status == 200) {

                    try {
                        ssid_json = JSON.parse(xobj.response)
                        $("#crack").empty()

                        for (let key in ssid_json) {
                            $("#crack").append("<tr><td>" + key + "</td><td>" + ssid_json[key] + "</td></tr>")
                        }
                    }
                    catch (e) {
                        console.error(e)
                    }
                }
            }
            else if (url == "uploader/upload-hs") {
                
            }
            
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                $("#success").css("display", "none")
                $("#fail").css("display", "none")
            }, 3000)

            console.log(xobj.status)
            try {
                console.log(JSON.parse(xobj.response))
            }
            catch (error) {
                console.log(xobj.response)
            }
        }
    }
    xobj.send()
}

function ssidPassTable(obj) {
    
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
        # Wstawić ten z RainbowTable na koniec btw
        self.ap_index = {"96:0a:c6:3a:97:60": "LBK_AP", "7c:03:d8:2d:e0:a9": "Caffe_late"}
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
                    hs_cnt=hs_cnt,
                    hs_strings=self.new_paths,
                    new_hs_cnt=new_hs_cnt,
                    ap_list=self.ap_index,
                    ap_cnt=len(self.ap_index.items())
                    )

        elif request.method == "POST":
            if path == "srv-hello":
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((IP, PORT))
                    sock.send("yoo".encode())
                    rs, _, _ = select.select([sock], [], [])

                    for cs in rs:
                        reply = cs.recv(1024).decode().strip()
                        logging.info(reply)
                        cs.close()
                        return reply, 200
                except Exception as e:
                    logging.error(e)
                    return str(e), 500

            elif path == "ssid-pass":
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((IP, PORT))
                    logging.info("connected")
                    sock.send("ssid".encode())
                    logging.info("sent")
                    rs, _, _ = select.select([sock], [], [])
                    logging.info("read ready")

                    for cs in rs:
                        reply = cs.recv(1024).decode().replace("\0", "\n").rstrip()
                        logging.info(reply)
                        cs.close()
                        logging.info("sock closed")
                        kvp = [x.split("\t") for x in reply.split("\n")]
                        dct = {y[0]: y[1] for y in kvp}
                        return jsonify(dct), 200
                except Exception as e:
                    logging.error(e)
                    return str(e), 500


            elif path == "upload-hs":
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

                        rs, _, _ = select.select([cli_socket], [], [])

                        for cs in rs:
                            reply = cs.recv(1024).decode().strip()
                            logging.info(repr(reply))

                            with open(path, "rb") as f:
                                for byte_block in iter(lambda: f.read(1024), b""):
                                    sha256.update(byte_block)
                                    
                            cs.send(f"{self.ap_index[hsmac]}\t{hsmac}\t{sha256.hexdigest()}".encode())

                            rs, _, _ = select.select([cli_socket], [], [])

                            for cs in rs:
                                reply = cs.recv(1024).decode().strip()
                                logging.info(repr(reply))

                                with open(path, "rb") as f:
                                    bs = f.read(1024)
                                    while (bs):
                                        cs.send(bs)
                                        bs = f.read(1024)
                                    cs.close()

                        # WAŻNY TEN SLEEP
                        time.sleep(1)
                        

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

                return "zapisane", 200


            logging.info(str(request))
            logging.info(json.dumps(request))
            return "test", 418
        
        return "bad request", 400

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

