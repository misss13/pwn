import logging

import os, sys, json
from flask import abort, render_template_string

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


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
<button onclick="sendPost('uploader/test')">TEST</button>
<button onclick="sendPost('http://10.0.0.1:12345')">TESTURL</button>
<div>
    Got new handshake: {{handshake_flag}}
</div>
<div>
    Handshake path: {{hs_path}}
</div>
<div>
    Handshake count: {{hs_cnt}}
</div>
<div>
    {% for path in hs_strings %}
    <p>{{path}}</p>
    {% endfor %}
</div>
{% endblock %}

{% block script %}
function sendPost(url) {
    var xobj = new XMLHttpRequest()
    var csrf = "{{ csrf_token() }}"
    xobj.open("POST", url)
    xobj.setRequestHeader("x-csrf-token", csrf)
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4) {
            console.log(xobj.status)
            console.log("TODO: Dodać refresh")
        }
    }
    xobj.send("test")
}
{% endblock %}
"""


class Uploader(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'An example plugin for pwnagotchi that implements all the available callbacks.'

    def __init__(self):
        logging.debug("example plugin created")
        self.ready = False
        self.new_hsh = False
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

            return render_template_string(
                    SITE_STRING,
                    handshake_flag=self.new_hsh,
                    hs_path=self.config["bettercap"]["handshakes"],
                    hs_cnt=hs_cnt,
                    hs_strings=self.new_paths
                    )

        elif request.method == "POST":
            if path == "test":
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
                return "x"
            logging.info(str(request))
            logging.info(json.dumps(request))
            return "test"
        
        return "bad request"

    # called when the plugin is loaded
    def on_loaded(self):
        logging.warning("WARNING: this plugin should be disabled! options = " % self.options)

    # called before the plugin is unloaded
    def on_unload(self, ui):
        pass

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

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        logging.info("unit is ready")
        # you can run custom bettercap commands if you want
        #   agent.run('ble.recon on')
        # or set a custom state
        #   agent.set_bored()

    # called when a non overlapping wifi channel is found to be free
    def on_free_channel(self, agent, channel):
        pass

    # called when the agent refreshed its access points list
    def on_wifi_update(self, agent, access_points):
        pass

    # called when the agent refreshed an unfiltered access point list
    # this list contains all access points that were detected BEFORE filtering
    def on_unfiltered_ap_list(self, agent, access_points):
        pass

    # called when the agent is sending an association frame
    def on_association(self, agent, access_point):
        pass

    # called when the agent is deauthenticating a client station from an AP
    def on_deauthentication(self, agent, access_point, client_station):
        pass

    # callend when the agent is tuning on a specific channel
    def on_channel_hop(self, agent, channel):
        pass

    # called when a new handshake is captured, access_point and client_station are json objects
    # if the agent could match the BSSIDs to the current list, otherwise they are just the strings of the BSSIDs
    def on_handshake(self, agent, filename, access_point, client_station):
        self.new_hsh = True
        logging.info(filename)
        logging.info(json.dumps(access_point))
        logging.info(json.dumps(client_station))
        pass

    # called when an epoch is over (where an epoch is a single loop of the main algorithm)
    def on_epoch(self, agent, epoch, epoch_data):
        pass

    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        pass

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        pass
