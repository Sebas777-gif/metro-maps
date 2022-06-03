class Redirect:

    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert('end', text)
        self.widget.see('end') # autoscroll

    def flush(self):
        pass