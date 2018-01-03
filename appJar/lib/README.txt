## tkinter-png ##

# Overview #

Through use of just standard python modules and pypng this adds support for pngs
to tkinter which can be used through the standard PhotoImage? object to be
placed onto buttons, labels or a canvas.

This project was started in part due to no official build of PIL for python 3.x
and also to allow the use of png images in a standard python distribution
without the user needing to install anything else, which may prove problematic
without root/admin access.

# Current Features #

- Supports any .png image, regardless of bit depth or presence of an alpha channel.
- Has boolean transparency support: fully transparent or opaque, no partial transparency.
- Modified tkinter.PhotoImage class supports tcl/tk's transGet, transSet, copy, redither and data methods

# Advantages and Disadvantages #

The advantages to using this implementation over a more complete library are
simple:

- No installation needed: everything (including pypng) are just .py files that
can be dropped into your working directory
- Pure python: doesn't need any bindings to C libraries, relying only on python
and python-tk. As such it is highly portable and should work on any system that
tkinter runs on.
- Simple: codebase is small enough for others to understand and expand on.
- Extends existing tkinter functionality: several tcl/tk functions regarding the
PhotoImage class are not usable in tkinter (such as transGet and transSet) and
others which are present have been stripped down (e.g. copy). These functions
can be used with non-png PhotoImages too! 

That being said, there are reasons not to use this module:

- Lack of functionality: Compared to a more complete library such as the
Python Imaging Library, tkinter-png is very lacking, not even able to rotate
images (yet).
- Speed: Although it has been optimised several times and is now about 250%
faster than it once was, there is no denying that processing images is slow.
Even on modern machines, multiple large images can have a huge impact on how
long a program takes to load.
- Quality: No sense denying it, tkinter-png was hacked together by a complete
novice programmer as work to hand in during the 9th week of a 1st-year
university course. While this code shouldn't explode your machine or eat your
hamster, it's not exactly seen a wide testing grounds yet. 

# Installation #
1. Download the tkinter-png .zip archive or checkout the source from svn on google code.
2. Copy the tkinter_png.py and png.py files to whatever directory your code will be in.
3. ???
4. Profit!

# Usage #
Simply import tkinter_png after tkinter.
Initialise your image with "var_name = PngImageTk(filename)"
This will also create a blank PhotoImage associated with the image at "var_name.image"
Use "var_name.covert()" to convert the png so tkinter can use it. The associated PhotoImage will now contain the png.
Now you can use your png image in the "var_name.image" PhotoImage like any other image!

# Changelog #
0.75 - Added various optimisations (aprox 20% faster) and fixed a bug in PngImageTk.convert with images larger than 550x400
0.7 - Module and example program seperated for clarity and proper usage.
0.6 - Added a moving, bouncing box between two image layers to demonstrate transparency.
0.5 - Boolean transparency added. tcl/tk PhotoImage methods hacked onto tkinter.
0.4 - Optimisation: uses single .put() to place all pixels at once
0.3 - Structure rearranged to use classes and functions for later code re-use. General cleanup.
0.2 - Optimisation: .put() places entire rows instead of pixel by pixel. Huge speed boost.
0.1 - Working concept, extremely slow, uses .put() to place each pixel in the image. Strips alpha channel.
0.01 - No support for images with alpha channel, uses small rectangles to place each pixel. Not released.