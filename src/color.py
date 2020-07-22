import src.helpers as helpers
from sys import exit as sysexit

if __name__ == "__main__":
    sysexit("This is a helper module for 'colorlist.py'. Please avoid running it as a script.")


class Color:
    def __init__(self, string, value_dict):
        # Store the matched string
        self.string = string

        # Collect values from the dict
        for key, value in value_dict.items():
            general_key = key.lower()

            if general_key == "r":
                self.r = value

            if general_key == "g":
                self.g = value

            if general_key == "b":
                self.b = value

            if general_key == "a":
                self.a = value
            else:
                self.a = 255

        # Store luminance
        self.luminance = round((self.r*0.299 + self.g*0.587 + self.b*0.114) / 256, 2)

        # Store hex
        self.hex = self.get_hex()

        # Store hsv
        self.h, self.s, self.v = self.get_hsv()

    def __hash__(self):
        return hash((self.string, self.r, self.g, self.b, self.a))

    def __eq__(self, other):
        return self.string == other.string

    def __str__(self):
        return f"{self.string}\trgba:{self.r},{self.g},{self.b},{self.a}\thex:{self.hex}\thsv:{self.h},{self.s},{self.v}\tlum:{self.luminance}"

    def get_hex(self):
        hex_val = hex((1 << 24) + (self.r << 16) + (self.g << 8) + self.b)

        return hex_val.replace("0x1", "#").upper()

    def get_hsv(self):
        r_abs = self.r / 255
        g_abs = self.g / 255
        b_abs = self.b / 255

        v = max(r_abs, g_abs, b_abs)

        diff = v - min(r_abs, g_abs, b_abs)

        def diff_c(c):
            return (v - c) / 6 / diff + 1 / 2

        def percent_round(n):
            return round(n * 100) / 100

        if diff == 0:
            h = 0
            s = 0
        else:
            s = diff / v
            rr = diff_c(r_abs)
            gg = diff_c(g_abs)
            bb = diff_c(b_abs)

            if r_abs == v:
                h = bb - gg
            elif g_abs == v:
                h = (1 / 3) + rr - bb
            elif b_abs == v:
                h = (2 / 3) + gg - rr

            if h < 0:
                h += 1
            elif h > 1:
                h -= 1

        return (
            round(h * 360),
            percent_round(s * 100),
            percent_round(v * 100))

    def as_html(self, template):
        replacements = {
            r"(?<!\[)\[string\](?!\])": self.string,
            r"(?<!\[)\[r\](?!\])":      str(self.r),
            r"(?<!\[)\[g\](?!\])":      str(self.g),
            r"(?<!\[)\[b\](?!\])":      str(self.b),
            r"(?<!\[)\[a\](?!\])":      str(self.a),
            r"(?<!\[)\[h\](?!\])":      str(self.h),
            r"(?<!\[)\[s\](?!\])":      str(self.s),
            r"(?<!\[)\[v\](?!\])":      str(self.v),
            r"(?<!\[)\[lum\](?!\])":    str(self.luminance),
            r"(?<!\[)\[fgcol\](?!\])":  "white" if self.luminance <= 0.5 else "black",
            r"(?<!\[)\[bgcol\](?!\])":  "black" if self.luminance <= 0.5 else "white"}

        return helpers.multi_replace(template, replacements)
