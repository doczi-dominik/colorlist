# Colorlist
Extract and display colors conveniently!

## Contents

#### 1. [Features](#features)
#### 2. [Installation](#installation)
#### 3. [Usage](#usage)
#### 4. [Customization](#customization)

## Features

&#x2714; **Portable** - The only dependencies are *Python 3*, and a \*nix based system!

&#x1f527; **Customizable** - Specify multiple color formats, customize the output with *templates*, and more!

&#x1f91d; **Versatile** - The use of standard streams, file and tab-delimited text output makes it pleasing to manipulate `colorlist` in a terminal.

## Installation

1. Clone this repository to a convenient place:
```bash
$ git clone https://github.com/doczi-dominik/colorlist
```

2. (Optional) Alias `colorlist.py` for even easier access!
```bash
# In ~/.bashrc
alias colorlist='/path/to/colorlist/colorlist.py'
```
You can also make some options *'default'* this way.

## Usage

##### `colorlist` parses colors in a provided format *(#RRGGBB by default)*, creates a HTML document out of them, and opens the file in a program. *(`$BROWSER` by default)*

### Basic usage

#### Passing plaintext

```bash
$ colorlist.py "#ff00ff anything can be written between the colors #C0FFEE"
```

#### Passing a file path - the best application for Colorlist!
```bash
$ colorlist.py ~/.config/rofi/colors.rasi
```

#### Passing `-` (or nothing) for reading `STDIN` - useful for file manipulation beforehand!
```bash
$ head -n 5 ~/.cache/wal/colors | colorlist.py

# same as: head -n 5 ~/.cache/wal/colors | colorlist.py -
```

### Formats

You can specify alternate color formats using the `-f` / `--format` flags. Formats use placeholder letters which are used to identify the corresponding part, the rest are only used for matching:
- `R, G, B, A`: A single hexadecimal **digit**
- `r, g, b, a`: A single decimal **number**

Notes:
- Using `a` and `A` is optional. 
- A format must contain at least one of `R, G, B` or `r, g, b`. 
- Hex and decimal placeholders cannot be mixed.
- Placeholders can be used as regular characters by escaping them.

Examples:
- `#RRGGBB`: Hexadecimal numbers (default)
- `r, g, b`: Comma-separated RGB values
- `\r\g\b\a(r,g,b,a)`: Matches the CSS `rgba()` function
- `#RGB`: Short hexadecimal notation
- `#GGAARRBB`: Whatever abomination this is - but it's still valid!

### Alternate output modes

#### Program output
By default, `colorlist` will open a generated HTML doc in the program defined in the `$BROWSER` environment variable by passing it to `$1`. The program can be specified manually by using the `-p` / `--program` flag. Additional arguments to the program can also be specified with `-ab` / `--args-before` and `-aa` / `--args-after`, which are relative to `$1`.

```bash
$ colorlist.py -p firefox -aa "~/colors.txt" -ab "--new-window" ~/colors.txt

# Assembled command: firefox --new-window /tmp/colorlist_colors.txt_XxxXXx ~/colors.txt
#                    [ -p  ] [ -ab      ] [ generated HTML               ] [ -aa      ]
```

#### File output
If you want, you can save the generated HTML file instead of opening it by using `-o` / `--out` and passing a filename. Passing `"-"` as the filename will print the contents to `STDOUT`.

```bash
$ colorlist.py ~/.cache/wal/colors -o asd.html
$ colorlist.py ~/.cache/wal/colors -o - | head -n 2
<!DOCTYPE html>
<html>
```

#### Text output
`colorlist` can also provide output in the terminal by passing the `-s` / `--stdout` flag. The output is tab-delimited for easy use with tools like `cut`, and is categorised by the formats provided.

```bash
$ colorlist.py -s "#c0ffee #556677 #FF00aa"
#RRGGBB
-------
#556677	rgba:85,102,119,255	hex:#556677	hsv:210,28.57,46.67	lum:0.39
#FF00aa	rgba:255,0,170,255	hex:#FF00AA	hsv:320,100.0,100.0	lum:0.37
#c0ffee	rgba:192,255,238,255	hex:#C0FFEE	hsv:164,24.71,100.0	lum:0.91
```

## Customization

### HTML templates
You can customize the way the HTML output looks by customizing the default template, or by creating a new one!

Templates can be found inside the template directory. Each template has two files in it: `page.html` and `color.html`. Templates work like formats, using placeholder values to search and replace with information.

`page.html` placeholders:
- `[list]`: The point where the colors will be inserted into the file.

`color.html` placeholders:
- `[string]`: The color as it was found in the source
- `[hex]`: Hex representation of the color
- `[lum]`: The luminance of the color
- `[fgcol]`: White for darker colors, black for brighter ones
- `[bgcol]`: Black for darker colors, white for brighter ones
- `[r]`: Decimal representation of R
- `[g]`: Decimal representation of G
- `[b]`: Decimal representation of B
- `[a]`: Decimal representation of A
- `[h]`: Decimal representation of H (hue)
- `[s]`: Decimal representation of S (saturation)
- `[v]`: Decimal representation of V (value)

The template to be used can be specified with `-t [TEMPLATE-NAME]` / `--template [TEMPLATE-NAME]` when running `colorlist`.

### Take a look at the default template for examples!

# Pull requests and suggestions welcome! &#x1f642;
