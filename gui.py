import os
import json
import requests
import gi
import subprocess
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib

class SicOSUpdater(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("SicOS Updater")
        self.set_default_size(400, 200)

        # Create a vertical box layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_child(self.box)

        # Get the username
        self.username = os.getlogin()

        # Create a header bar
        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_show_title_buttons(True)
        self.set_titlebar(self.header_bar)
        self.header_bar.set_title_widget(Gtk.Label(label="SicOS Updater"))

        # Create a label to display the update status
        self.label = Gtk.Label(label="Checking for updates...", wrap=True, justify=Gtk.Justification.CENTER)
        self.label.set_margin_top(24)
        self.box.append(self.label)

        # Create a button to execute the check.py file
        self.button = Gtk.Button(label="Update Now")
        self.button.set_margin_top(24)
        self.button.set_margin_bottom(24)
        self.button.connect("clicked", self.on_button_clicked)
        self.box.append(self.button)

        # Create a button to refresh the update status
        self.refresh_button = Gtk.Button(label="Refresh")
        self.refresh_button.set_margin_top(24)
        self.refresh_button.set_margin_bottom(24)
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        self.box.append(self.refresh_button)

        # Call the check_for_updates method after initialization
        self.check_for_updates()

        # Schedule a timeout every 1 hour to check for updates
        GLib.timeout_add(3600 * 1000, self.check_for_updates)  # 3600 seconds = 1 hour

    def check_for_updates(self):
        # Get the POINTRELEASE value from the local file
        local_file_path = f"/home/{self.username}/.update/POINTRELEASE.json"
        with open(local_file_path, "r") as f:
            local_point_release = json.load(f)["pointRelease"]

        # Get the POINTRELEASE value from the remote server
        remote_url = "http://cliente.tomadahost.cloud:10060/update"
        response = requests.get(remote_url)
        remote_point_release = response.json()["pointRelease"]

        # Compare the POINTRELEASE values
        if local_point_release == remote_point_release:
            self.label.set_text("Your SicOS is updated")
            self.button.set_visible(False)
        else:
            self.label.set_text("You're not updated")
            self.button.set_visible(True)

        # Return True to reschedule the timeout
        return True

    def on_button_clicked(self, button):
        # Execute the check.py file and wait for it to finish
        subprocess.run(["python3", "check.py"])

        # Refresh the update status after check.py execution
        self.check_for_updates()

    def on_refresh_clicked(self, button):
        # Refresh the update status
        self.check_for_updates()

    def on_destroy(self, window):
        self.get_application().quit()

class Application(Gtk.Application):
    def __init__(self, application_id, flags):
        super().__init__(application_id=application_id, flags=flags)

    def do_activate(self):
        win = SicOSUpdater(application=self)
        win.connect("destroy", win.on_destroy)
        win.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.quit_cb)
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<primary>q"])

    def quit_cb(self, action, param):
        self.quit()

if __name__ == '__main__':
    app = Application('org.example.SicOSUpdater', 0)
    app.run()
