from gi.repository import Adw, Gio, GLib, Gtk

Gtk.init_check()
print("Hei hei!")

@Gtk.Template(resource_path='/no/brunhenriksen/Ord/window.ui')
class OrdWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'OrdWindow'

    main_text_view = Gtk.Template.Child()
    open_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # åpne fil knapp funksjonalitet
        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self.open_file_dialog)
        self.add_action(open_action)

        # lagre fil knapp funksjonalitet
        save_action = Gio.SimpleAction(name="save-as")
        save_action.connect("activate", self.save_file_dialog)
        self.add_action(save_action)

        self.settings = Gio.Settings(schema_id="no.brunhenriksen.Ord")
        self.settings.bind("window-width", self, "default-width",
                       Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height",
                       Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized",
                       Gio.SettingsBindFlags.DEFAULT)

    # open file dialog actionen
    def open_file_dialog(self, action, _):
        self._native = Gtk.FileChooserNative( # Gtk.FileChooserNative betyr at den bruker den native file manageren til operativsystemet ditt. på windows er det file explorer og på linux er det det du har satt som default (sikkert nautilu eller dolphin)
            title="Open File",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            accept_label="_Open", # understreken foran "Open" betyr at det er det tastatur snarveien (haha norsk er gøy) er for den actionen | keyboard shortcut = ctrl + O
            cancel_label="_Cancel" # samme som forrige | keyboard shortcut = ctrl + C
        )

        self._native.connect("response", self.on_open_response)
        self._native.show()

    # open file dialog vindu greien (hvordan skal jeg forklare dette)
    def on_open_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.open_file(dialog.get_file())
        else:
            print("Ingen fil åpnet")
        self._native = None

    # å faktisk åpne filen
    def open_file(self, file):
        file.load_contents_async(None, self.open_file_complete)

    def open_file_complete(self, file, result):
        contents = file.load_contents_finish(result)
        if not contents[0]: # hvis den ikke klarte å åpne filen
            path = file.peek_path()
            print(f"Kunne ikke åpne {path}: {contents[1]} :(")
        else: # hvis den klarte å åpne filen
            path = file.peek_path()
            print(f"Åpnet {path} :D ")

        try:
            text = contents[1].decode('utf-8')
        except UnicodeError as err:
            path = file.peek_path()
            print(f"Kunne ikke åpne {path}: the file is not encoded properly")
            return

        buffer = self.main_text_view.get_buffer()
        buffer.set_text(text)
        start = buffer.get_start_iter()
        buffer.place_cursor(start)

    def save_file_dialog(self, action, _):
        self._native = Gtk.FileChooserNative(
            title="Save file As",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            accept_label="_Save",
            cancel_label="_Cancel",
            )
        self._native.connect("response", self.on_save_response)
        self._native.show()

    def on_save_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.save_file(dialog.get_file())
        self._native = None

    def save_file(self, file):
        buffer = self.main_text_view.get_buffer()
        start = buffer.get_start_iter() # fin starten av filen
        end = buffer.get_end_iter() # fin slutten av filen
        text = buffer.get_text(start, end, False)

        if not text:
            print("Bufferet er tomt, bror")
            return

        bytes = GLib.Bytes.new(text.encode('utf-8'))
        file.replace_contents_bytes_async(bytes, None, False, Gio.FileCreateFlags.NONE, None, self.save_file_complete)

    def save_file_complete(self, file, result):
        res = file.replace_contents_finish(result)
        info = file.query_info("standard::display-name", Gio.FileQueryInfoFlags.NONE)

        if info:
            display_name = info.get_attribute_string("standard::display-name")
        else:
            display_name = file.get_basename()

        if not res:
            print(f"Kunne ikke lagre {display_name} :(")
