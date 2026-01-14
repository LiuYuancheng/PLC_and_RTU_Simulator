# -*- coding: utf-8 -*-
'''
Copyright Kevin Schlosser April 2019
GNU General Public License v3.0

https://github.com/kdschlosser/wxVolumeKnob

Amendments by RolfofSaxony 2023
    Enabling the volume knob to become an all-round circular gauge, which can have multiple uses
    e.g. as a speedometer, a meter for voltage, amperes, revolutions per minute,  psi, a thermometer etc

    It has become reversible, orientable and invertible

    Amended Version 2.2
        code optimisation? to dramatically reduce certain calls during OnPaint, mainly creating the tick_list
        also only bind mouse move when Hotspots are active, otherwise, the function is called needlessly.

        Change
         TickFrequency must be >= the increment
        Change
         when neon_colour is calculated, to avoid unnecessary function calls
        Change
         value is set after min_value and max_value on initial start up, to ensure that it is within those 2 values
          this prevents an illegal value being set at startup.
        Change
         Left double mouse click is treated the same as a right click i.e. jump to click position
        Change
            automatic reduction of the number of texts to be displayed, now uses slicing as is it's faster
        Change
            automatic reduction of the number of texts to be displayed, is now aware of whether you are displaying
             the text inside the gauge or outside. Outside there's a maximum of 30 texts allowed, inside only 12.
        Change
            Gauge text now takes account of the Font settings of the KnobCtrl, if set, the exception is the Odometer
            (The font size is still calculated based on the size of the control)
        Change
            An attempt has been made to limit the number of ticks to below what I consider to be excessive.
            The arbitrary limit I've set is 600 for the entire gauge and no more than 1.66 ticks per degree,
             when setting the StartEndDegrees. An over crowded gauge is not only slow but visually messy
            Additionally, the number of Large ticks attempts to stay below 30, again for visual clarity
        Addition
            DefinedScaleValues are user defined tick override values
            this is a list of values within the scope of the gauge and each divisible by the tick_frequency,
             where you want a large tick with a text value.
            It overrides the automatic calculation of ticks and tick values, replacing it with your predefined values
             e.g. self.ctrl.DefinedScaleValues = [1.0, 4.4, 9.0 11.0] will only display large ticks with those values.
            Small ticks are unaffected.
            Values that are deemed not within the gauge range or not divisible by the tick frequency, will be excluded.

    Amended Version 2.1
        Fixed bug in mouse drag.
        Attempting to prevent unnecessary events once the meter's minimum value was hit, I failed to process the fact
         that it had hit the minimum - Thanks go to RichardT for pointing it out.

        Addition of variable DisableMinMaxMouseDrag - True or False - Default False
            If set to True, disables the ability, when dragging, to accidently flip from Min to Max or Max to Min
            The maximum valid mouse drag, by default, is set to 50% of the difference in degrees between start and end degrees.
            This can be adjusted by setting the control's variable 'mouse_max_move' to a value of your choice e.g.
                self.ctrl.mouse_max_move = 50
            Any attempt to drag by more than that, is cancelled.
            Obviously, this also means that you can disable mouse dragging altogether, simply by setting mouse_max_move to zero.

    Amended Version 2.0

        Addition of variable UseHotSpots, which notes the dial thumb position and the Odometer position
        If the mouse is hovered over those positions whilst UseHotSpots is True, a ToolTip
            is displayed of the current value of the control for the dial thumb and the elapsed running time for the Odometer.
            The Odometer may also have Text set in addition, see below

        Addition of variable OdometerToolTip
            If given a string value this will be display when hovering over the Odometer, if SetHotSpot is active,
             in addition to the running time.

        Addition of function SetHotSpots()
            SetHotSpots toggles UseHotSpots between True and False
             additionally it turns off standard ToolTip if it is Set

        Addition of function GetHotSpots()
            returns current value of UseHotSpots

        Addition of function SetDefaultTickColour(colour)
            overrides the default tick colour, the colour used beyond the current value (normally Dark Grey)
            or the foreground colour of the parent panel.

        Addition of function GetDefaultTickColour(colour)
            returns the current default tick colour

        Addition of function SetTickRangePercentage(True/False) - Default True
            By default the tick range values given are converted to percentages to colour the gauge
            If this is set to False the values are used as discrete values
            This reinstates the original method as written by Kevin Schlosser

        Addition of variable Caption.
            If given a string value, this text is shown centred, at the foot of the meter.
            If positioned at the foot, there is only room for a single line
            The Caption gets it's colour from the DefaultTickColour.

        Addition CaptionPos = int Default 0
            The Caption by default is positioned centrally at the bottom of the gauge
            If you set this variable the caption will be positioned:
                1 - Top Left
                2 - Top Right
                3 - Bottom Left
                4 - Bottom Right
            In these positions there is more room for text, which may include newlines.

        Addition of coping with numeric keypad input of digits, as well as ordinary digits, to jump by a percentage
            0 = min value, 1 = 10% ...... 9 = 90%

        Addition of SetStartEndDegrees(start=n, end=n) - Permitting you to orient the gauge and decide how much of the circle to use
            Defaults 135.0 (7:30) and 405.0 (4:30) respectively
            Positions are specified in degrees with 0 degree angle corresponding to the positive horizontal axis (3 o’clock) direction
                following the convention in drawing wx.DC arcs.
            i.e. to set the minimum position at 9 o'clock the start angle would be 180.0
                 to set the maximum position at 3 o'clock the end angle would be 360.0
            Each hourly position is +30°, so 7:30 would be 4.5 * 30 i.e. 7:30 minus 3:00 = 4.5 hours * 30 = 135.0
                                          with an end position of 4:30 = (1.5 + 12) * 30 = 405.0

            Both the Start and the End positions must both be Positive or both be Negative and the Range cannot exceed 360°

            Negative values are permitted but remember they are inverse:
                so -135° is 10:30 and -405° is 1:30

            Reversed Start and End positions are allowed, to make the gauge appear to run from positive to negative
             e.g. start 405.0 end 135.0 or -405.0 to -135.0

            i.e.
                Start   End        Min position   Max Position        Where is Midway
                135     405         7:30            4:30                Top
                405     135         4:30            7:30                Top
               -135    -405        10:30            1:30                Bottom
               -405    -135         1:30           10:30                Bottom

        Addition  GetStartEndDegrees() - returns a tuple

        Addition  SetAlwaysTickColours(True or False)
            Normally the ticks are only coloured based on the current value.
            If this is set to True, the ticks permanently have the colours assigned by the TickColourRanges and
                the current position is denoted by the current value tick, being the default tick colour.

        Addition ShowScale True or False
            ShowScale now makes a best effort to show text scale values on the gauge, without overcrowding the image
            By default the values are displayed on the exterior of the gauge

        Addition InsideScale True or False
            If set in combination with either ShowScale or ShowMinMax, the scale is displayed on the interior
             of the gauge.
            Given the restricted space available, this can be slightly hit and miss, best results are achieved
             by adjusting the tick frequency.

        Addition GaugeImage = a wx.Image
            This, much like GaugeText displays the input centrally in the gauge.
            The image should be a wx.Image and is expected to be transparent.
            The image is resized, based on the control's size, although it makes sense to ensure
             that the image is as small as is appropriate, beforehand, just for efficiency.
            If you are displaying text too, you may wish to display that further up the gauge,
             include 1 or 2 linefeeds in the text, to separate it from the image.

        Addition GaugeImagePos = int Default 0
            The image by default is positioned centrally
            If you set this variable the image will be positioned:
                1 - Top Left
                2 - Top Right
                3 - Bottom Left
                4 - Bottom Right

        Addition of EVT_SCROLL_CHANGED, activated if the value changes via SetValue()
            This caters for events to be monitored if you feed value changes into the gauge, rather than treating it
             purely as an input control.
            Events available for Binding are:
                wx.EVT_SCROLL_TOP, the gauge has hit maximum value;
                wx.EVT_SCROLL_BOTTOM, the gauge has hit minimum value;
                wx.EVT_SCROLL_LINEUP, gauge moved up one increment:;
                wx.EVT_SCROLL_LINEDOWN', gauge moved down one increment
                wx.EVT_SCROLL_PAGEUP, the user hit page up;
                wx.EVT_SCROLL_PAGEDOWN, the user hit page down;
                wx.EVT_SCROLL_THUMBRELEASE, the mouse has been released;
                wx.EVT_SCROLL_CHANGED, the gauge value has changed;
            and the catch all, wx.EVT_SCROLL, an event occurred.

        Addition of variable OdometerBackgroundColour - Default None

        Bug fixes:
        The knobStyle values have been corrected.
         Default: KNOB_GLOW | KNOB_DEPRESSION | KNOB_HANDLE_GLOW | KNOB_TICKS | KNOB_SHADOW
         Originally the knobStyle values always seemed to produce True, so everything was always turn On, as the values
          assigned were incorrect.
         The knobStyle is one of the initial parameters but can be  overridden with SetKnobStyle(...)
            e.g. self.ctrl.SetKnobStyle(knob.KNOB_TICKS | knob.KNOB_SHADOW | knob.KNOB_DEPRESSION)
          valid style values are:
            KNOB_GLOW = 1                   # Adds a neon glow around the gauge
            KNOB_DEPRESSION = 2             # Adds the central depression
            KNOB_HANDLE_GLOW = 4            # Adds a neon glow to the thumb
            KNOB_TICKS = 8                  # Adds ticks to the gauge
            KNOB_SHADOW = 16                # Adds a shadow to the gauge
            KNOB_RIM = 32                   # Adds a coloured rim to indicate the position of the gauge

            KNOB_RIM is a new style, as an alternative to KNOB_GLOW, (although they can be used together)
            Whereas KNOB_GLOW lights up the gauge rim with the relevant diffused colour range, KNOB_RIM lights up
             the gauge rim with the relevant solid colour range, only up to the current value.
             In essence it acts as a separate value indicator.

            If you are a fan of bitwise operations, I find them confusing, you can manipulate the existing flags,
             using GetKnobStyle()
             e.g.
                knobstyle = self.ctrl.GetKnobStyle()
                self.ctrl.SetKnobStyle((knobstyle | knob.KNOB_RIM) &~ knob.KNOB_SHADOW)
             which adds the RIM style to the existing setting and removes the Shadow at the same time.

        Changes to the methods used to calculate the tick positions
            calculating tick positions for integer values was fine but trying to set the increments for fine values,
                such as a meter measuring from -1.0 to 1.0 with an increment of 0.01 and a tick frequency of 0.02,
                for example, runs into floating point Modulo issues ( a horror story in its own right)
            Either the tickfrequency could be refused or there would be missing ticks or too many ticks
            I've attempted to resolve those by importing Decimal and using round() and some other tweaks, including
             defining the required precision.
             The increment determines the precision that will be used e.g. 0.01 would set precision to 2, 0.005 to 3.
            Hopefully, I haven't broken anything. :)

        SetTickColours now handles the various ways of defining a colour e.g.
            (77, 77, 255)
            wx.Colour('#7777ff')
            '#7777ff'
            wx.BLUE
         The Bug was in setting the neon_colour for the ticks and body of the meter which expects a tuple.

        Changes:

        Change to existing function GetAverageSpeed()
         This now returns a tuple of Average value and the elapsed time period in seconds

        Change PageUp, PageDown to simple + or - 10%

        Event reporting can no longer issue double events e.g. SCROLL_PAGEUP and SCROLL_CHANGED
            Now the specific event is reported or SCROLL_CHANGED not both.

        Change TickColourRanges to cope with values < 1
            The tickcolourranges didn't handle ranges which strayed negative, they calculated a percentage of the maximum value.
            They now handle a range which goes from negative to positive e.g.
                SetTickColourRanges([10, 50, 75]) for a minimum value of -10.0 and max of 20.0,
                 would set the values at -7.0, 5.0 and 12.5 as the range is actually 30 ( -10 -> 20 )
            It should also handle purely negative ranges

        GaugeText replaces SpeedoText in a variable name change - sorry about that, just more appropriate

        GaugeText has also become more vertically centrally located.
            If you wish the text to display further up the gauge include 1 or 2 linefeeds in the text.
            This is especially true if including a centrally located image with GaugeImage()

    Amended Version 1.1
        Bug fix for incorrect Unbind of the odometer update timer
        Addition of a pointer spine
        Addition of variable ShowMinMax values
        Addition of variable OdometerColour

    Amended version 1.0

    Display optional Volume/Speed value as text
     To allow for very large values when using RPM for example, if the initial value is set as an integer
        only an integer is displayed, allowing for much larger numbers to be catered to.

    Enable Right Click to jump to a position

    Calculate tick colour as a percentage of the maximum value rather than fixed value

    Optional pointer with shadow for Speedometer feel

    Optional Speedo text, expected to be something like Mph, Kph, Rpm ft/s etc

    Optional Odometer - defaults calculation to distance covered per hour

    Optional odometer period unit - "H" per Hour, "M" per Minute, "S" per Second - Default "H"

    Optional Odometer update period - expects a millisecond value like wxTimer
        a timer that updates the odometer irrespective of the value being changed
         based on the current Speed/Velocity
        A value > than 0 turns the odometer on, <= 0 turns it off

    Plus minor adjustments

    Variables added:
        ShowToolTip = True          Shows a tooltip of the Volume/Speed value
        ShowValue = True            Shows the Volume/Speed value in the centre of the widget
        ShowPointer = True          Shows a pointer indicating the Volume/Speed
        PointerColour = None        Sets the Colour of the pointer, allows for transparency
                                     The default is to use the current tick colour.
        SpeedoText = ''             Sets a short text to be displayed indicating the measurement
                                     e.g. Mph, Kph, Rpm
        ShowOdometer = False        True/False
        OdometerUpdate = 0          Value in milliseconds - Sets automatic odometer update
                                     without this the odometer is only updated on an event
                                    Note:
                                        Showing the odometer with an auto update is expensive and the more
                                        frequent the update, the more expensive
                                        ***************************************
        OdometerPeriod = "H"        "H", "M" or "S"
                                     If you change this after setting it initially, the odometer readings
                                      will be nonsense, you will have a mixture of unit readings

    Additional functions:

        GetOdometerUpdate()         return Odometer update period

        SetOdometerUpdate(value)    Set odometer update period in milliseconds
                                    Sets or cancels the odometer depending on positive or negative value

        GetAverageSpeed()           Returns the average speed depending on the odometer period unit
                                     from program start to now (running time in secs, as of version 2.0)

        GetOdometerValue()          Returns current odometer value

        GetOdometerHistory()        Returns the history of speed changes as a list

'''

import wx
import math
from decimal import Decimal
import time

digits_numeric_pad = [wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, wx.WXK_NUMPAD4,
                      wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, wx.WXK_NUMPAD9]


def frange(start, stop=None, step=1.0, prec=1):
    """
    Range function that accepts floats
    """

    start = float(start)
    step = float(step)

    if stop is None:
        stop, start = start, 0.0

    count = int(abs(stop - start) / step) + 1
    return iter(round(start + (n * step), prec) for n in range(count))


def _remap(value, old_min, old_max, new_min, new_max):
    old_range = old_max - old_min
    new_range = new_max - new_min
    try:
       return (
            (((value - old_min) * new_range) / old_range) + new_min
        )
    except ZeroDivisionError as e:
        return new_min


class Handler(object):

    def __init__(self, parent=None):
        self._size = None
        self._tick_list = None
        self._value = None
        self._min_value = None
        self._max_value = None
        self._thumb_multiplier = 0.04
        self._thumb_position = None
        self._thumb_radius = None
        self._radius = None
        self._thumb_orbit = None
        self._neon_radius = None
        self._neon_colour = None
        self._foreground_colour = None
        self._background_colour = None
        self._tick_pens = []
        self._tick_ranges = []
        self._tick_range_percentage = True
        self._tick_range_colours = []
        self._default_tick_pen = None
        self._tick_frequency = 2.0
        self._increment = 1.0
        self._secondary_colour = wx.Colour(255, 255, 255)
        self._primary_colour = wx.Colour(33, 33, 33)
        self._page_size = None
        self._glow = False
        self._depression = False
        self._thumb_glow = False
        self._ticks = False
        self._always_tick_colours = False
        self._shadow = False
        self._precision = 0
        self._start_degree = 135.0
        self._end_degree = 405.0
        self._mid_point = 90.0
        self._mid_point_adj = 45.0
        self._negative_mid_point = 270.0
        self._parent = parent
        if parent:
            self._font = parent.GetFont()
        else:
            self._font = None


    @property
    def shadow(self):
        return self._shadow

    @shadow.setter
    def shadow(self, value):
        self._shadow = value

    @property
    def glow(self):
        return self._glow

    @glow.setter
    def glow(self, value):
        self._glow = value

    @property
    def depression(self):
        return self._depression

    @depression.setter
    def depression(self, value):
        self._depression = value

    @property
    def thumb_glow(self):
        return self._thumb_glow

    @thumb_glow.setter
    def thumb_glow(self, value):
        self._thumb_glow = value

    @property
    def primary_colour(self):
        return self._primary_colour

    @primary_colour.setter
    def primary_colour(self, value):
        self._primary_colour = value

    @property
    def secondary_colour(self):
        return self._secondary_colour

    @secondary_colour.setter
    def secondary_colour(self, value):
        self._secondary_colour = value

    @property
    def foreground_colour(self):
        return self._foreground_colour

    @foreground_colour.setter
    def foreground_colour(self, value):
        self._tick_list = None
        self._default_tick_pen = wx.Pen(value, 2)
        self._foreground_colour = value

    @property
    def background_colour(self):
        return self._background_colour

    @background_colour.setter
    def background_colour(self, value):
        self._background_colour = value

    @property
    def min_value(self):
        return self._min_value

    @min_value.setter
    def min_value(self, value):
        self._min_value = value

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        self._max_value = value

    @property
    def mid_point(self):
        return self._mid_point

    @mid_point.setter
    # used when the mouse is clicked or dragged
    def mid_point(self, value):
        start, end, = value
        if start > end:                             # find gap between start and end
            gap = start - end
        else:
            gap = end - start
        if gap < 0:                                 # find the reverse of that
            mod_diff = gap % -360.0
        else:
            mod_diff = gap % 360.0
        mod_diff = (360 - mod_diff) / 2             # find halfway point in difference
        self._mid_point_adj = mod_diff              # Note halfway point
        if start > end:
            mod_diff = end - self._mid_point_adj
        else:
            mod_diff = start - self._mid_point_adj
        if mod_diff < 0:
            mod_diff = abs(mod_diff + 360)
        self._mid_point = mod_diff                  # mid point opposite range e.g. 0 -> 180 = 270°

    @property
    def negative_mid_point(self):
        return self._negative_mid_point

    @negative_mid_point.setter
    # used when the mouse is clicked or dragged
    def negative_mid_point(self, value):
        start, end, = value
        if start > end:                             # find gap between start and end
            gap = start - end
        else:
            gap = end - start
        if gap < 0:                                 # find the reverse of that
            mod_diff = gap % 360.0
        else:
            mod_diff = gap % -360.0
        mod_diff = mod_diff / 2                     # find halfway point in difference
        self._mid_point_adj = abs(mod_diff)         # Note halfway point adjustment
        if start < end:
            mod_diff = end + self._mid_point_adj
        else:
            mod_diff = start + self._mid_point_adj

        mod_diff = mod_diff % 360
        self._negative_mid_point = mod_diff         # mid point opposite range e.g. 0 -> 180 = 270°

    @property
    def mid_point_adj(self):
        return self._mid_point_adj

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, value):
        self._precision = value

    @property
    def start_degree(self):
        return self._start_degree

    @start_degree.setter
    def start_degree(self, value):
        self._start_degree = value

    @property
    def end_degree(self):
        return self._end_degree

    @end_degree.setter
    def end_degree(self, value):
        self._tick_list = None
        self._end_degree = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._radius = None
        self._thumb_radius = None
        self._neon_radius = None
        self._thumb_orbit = None
        self._thumb_position = None
        self._tick_list = None
        self._size = value

    @property
    def center(self):
        width, height = self.size

        return int(width / 2), int(height / 2)

    @property
    def radius(self):
        if self._radius is None:
            width, height = self.size
            radius = (min(width, height) // 2) * 0.75
            self._radius = radius

        return self._radius

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._thumb_position = None
        self._tick_list = None
        if value < self.min_value:
            value = self.min_value
        if value > self.max_value:
            value = self.max_value
        self._value = value

    @property
    def neon_radius(self):
        if self._neon_radius is None:
            radius = self.radius
            self._neon_radius = radius - 1

        return self._neon_radius

    @property
    def thumb_multiplier(self):
        return self._thumb_multiplier

    @thumb_multiplier.setter
    def thumb_multiplier(self, value):
        self._thumb_radius = None
        self._thumb_orbit = None
        self._thumb_position = None
        self._thumb_multiplier = value

    @property
    def thumb_radius(self):
        if self._thumb_radius is None:
            radius = self.radius
            self._thumb_radius = radius * self.thumb_multiplier

        return self._thumb_radius

    @property
    def thumb_orbit(self):
        if self._thumb_orbit is None:
            radius = self.radius
            center_radius = self.center_radius
            self._thumb_orbit = int(round((radius - center_radius) / 2.0)) + center_radius

        return self._thumb_orbit

    @property
    def neon_colour(self):
        colour = self._neon_colour
        colours = self.tick_range_colors
        if colours:
            colour = self.tick_range_colors[0]
        for i, r_value in enumerate(self.tick_ranges):
            if r_value <= self.value:
                try:
                    colour = colours[i + 1]
                except IndexError:
                    break
        colour = wx.Colour(colour).Get(False)
        self._neon_colour = colour
        return colour

    @property
    def center_radius(self):
        thumb_radius = self.thumb_radius

        return self.radius - (thumb_radius * 2) - (self.radius * 0.1)

    @property
    def thumb_position(self):
        if self._thumb_position is None:
            width, height = self.size

            x_center = width // 2
            y_center = height // 2

            thumb_orbit = self.thumb_orbit
            thumb_degree = _remap(self.value, self.min_value, self.max_value, self.start_degree, self.end_degree)
            thumb_radian = math.radians(thumb_degree)

            cos = math.cos(thumb_radian)
            sin = math.sin(thumb_radian)

            thumb_x = x_center + int(round(thumb_orbit * cos))
            thumb_y = y_center + int(round(thumb_orbit * sin))

            self._thumb_position = (thumb_x, thumb_y)

        return self._thumb_position

    @property
    def tick_pens(self):
        return self._tick_pens

    @property
    def tick_range_colors(self):
        return self._tick_range_colours

    @tick_range_colors.setter
    def tick_range_colors(self, value):
        del self._tick_pens[:]

        for colour in value:
            self._tick_pens += [wx.Pen(colour, 1)]

        self._tick_list = None
        self._tick_range_colours = value

    @property
    def tick_ranges(self):
        return self._tick_ranges

    @tick_ranges.setter
    def tick_ranges(self, value):
        self._tick_list = None
        self._tick_ranges = value

    @property
    def tick_range_percentage(self):
        return self._tick_range_percentage

    @tick_range_percentage.setter
    def tick_range_percentage(self, value):
        self._tick_range_percentage = value

    @property
    def increment(self):
        return self._increment

    @increment.setter
    def increment(self, value):
        self._increment = value

    @property
    def tick_frequency(self):
        return self._tick_frequency

    @tick_frequency.setter
    def tick_frequency(self, value):
        self._tick_frequency = value

    @property
    def page_size(self):
        if self._page_size is None:
            return (self.max_value - self.min_value) / 10.0
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        self._page_size = value
        self._tick_list = None

    @property
    def ticks(self):
        return self._ticks

    @ticks.setter
    def ticks(self, value):
        self._ticks = value

    @property
    def always_tick_colours(self):
        return self._always_tick_colours

    @always_tick_colours.setter
    def always_tick_colours(self, value):
        self._always_tick_colours = value

    # testing for a quicker way to remap values to degrees
    def make_remapper(self, val_min, val_max, deg_min, deg_max):
        # Compute the scale factor between value range and degree range
        scaleFactor = float(deg_max - deg_min) / float(val_max - val_min)

        def remap_degree(value): #returns both value and degree equivalent
            return value, deg_min + (value - val_min) * scaleFactor

        return remap_degree

    @property
    def tick_list(self):
        if self._tick_list is None:

            width, height = self.size
            center = int(round(min(width, height) / 2.0))

            center_x = int(round(width / 2.0))
            center_y = int(round(height / 2.0))

            large_outside_radius = center - int(round(center * 0.05))
            inside_radius = int(round(large_outside_radius * 0.90))
            small_outside_radius = int(round(self.radius * 1.20))
            inside_values_radius = int(round(self.center_radius * 0.85))
            ticks = []
            _value_ticks = []        # note tick list cordinates for ShowScale/ShowMinMax outside the gauge
            _tick_values = []        # note value at each large tick as a string for display
            _inside_value_ticks = [] # note tick list cordinates for display inside the gauge

            _tick_ranges = self.tick_ranges
            _max_value = self.max_value
            _min_value = self.min_value
            _tick_frequency = self.tick_frequency
            _precision = self.precision

            gauge_range = list(frange(_min_value, _max_value, _tick_frequency, _precision))

            # if a set of predefined scale values exist weed out any illegal values
            if self._parent and self._parent.DefinedScaleValues:
                predefined = True
                _tick_values = [str(x) for x in self._parent.DefinedScaleValues \
                                    if not Decimal(str(x)) % Decimal(str(_tick_frequency)) and x in gauge_range]
            else:
                predefined = False

            base_fontsize = int(height/10)
            if self._font:
                font = self._font
                font.SetPointSize(int(base_fontsize/4))
            else:
                font = wx.Font(int(base_fontsize/4), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
            pix_x, pix_y = font.GetPixelSize()

            tick_pens = self.tick_pens
            always_tick_colours = self.always_tick_colours

            num_small_ticks = int(round((_max_value - _min_value) / _tick_frequency)) + 1
            num_large_ticks = int(round((_max_value - _min_value) / self.page_size)) + 1
            num_small_ticks -= num_large_ticks

            self._neon_colour = self.neon_colour
            large_tick_frequency = (num_large_ticks - 1) * self.increment

            #limit large ticks or it gets messy
            while (_max_value - _min_value) / large_tick_frequency > 30:
                large_tick_frequency *= 2.0
            pen_size = max(1.0, (center * 0.015) - (num_small_ticks / 100.0))
            half = round(((_max_value - _min_value) / 2) + _min_value, _precision)
            check_tick_frequency = _tick_frequency
            check_large_tick_frequency = Decimal(str(large_tick_frequency))

            scaler = self.make_remapper(_min_value, _max_value, self._start_degree, self._end_degree)
            remapped_degrees = map(scaler, gauge_range)

            for i, degree in remapped_degrees:
                if always_tick_colours or i <= self._value:
                    # coloured tick
                    for pen_num, tick_range in enumerate(_tick_ranges):
                        if i <= tick_range:
                            if pen_num < len(tick_pens):
                                pen = tick_pens[pen_num]
                            else:
                                pen = self._default_tick_pen
                            break
                    else:
                        pen = self._default_tick_pen
                else:
                    pen = self._default_tick_pen

                pen.SetWidth(int(pen_size))

                # Overrides - Pos 0 = Red, Pos halfway = Blue and always_tick_colours = Default colour for visibility
                if i == 0:
                    pen = wx.Pen((255, 0, 0), int(pen_size + 1))
                if i == half:
                    pen = wx.Pen((0, 0, 255), int(pen_size + 1))
                if always_tick_colours and i == self._value:
                    pen = self._default_tick_pen
                    pen.SetWidth(int(pen_size + 2))

                radian = math.radians(degree)
                cos = math.cos(radian)
                sin = math.sin(radian)

                x2 = center_x + int(round(inside_radius * cos))
                y2 = center_y + int(round(inside_radius * sin))

                if not i.is_integer():          # remove superfluous characters for display purposes
                    str_i = str(i)
                else:
                    str_i = str(int(i))

                if predefined: # if a set of predefined scale values exist use them for the tick entries
                    if str(i) in _tick_values: # Large tick with text
                        x1 = tvx1 = center_x + int(round(large_outside_radius * cos))
                        y1 = tvy1 = center_y + int(round(large_outside_radius * sin))

                        tvx2 = center_x + int(round(inside_values_radius * cos))
                        tvy2 = center_y + int(round(inside_values_radius * sin)) - int(pix_y / 2)
                        tvx2 = tvx2 - int((len(str(i)) / 3.0) * pix_x)

                        if x1 < (width/2):          # adjust text position if on left hand side
                            tvx1 = x1 - int(((len(str(i)) * 0.75) * pix_x))
                        elif x1 == (width/2):
                            tvx1 = x1 - int(((len(str(i)) * 0.25) * pix_x))
                        else:
                            tvx1 += pix_x

                        tvy1 = y1 - int(pix_y / 2)

                        _value_ticks += [[tvx1, tvy1]]
                        _inside_value_ticks += [[tvx2, tvy2]]
                    else: # Small tick
                        x1 = center_x + int(round(small_outside_radius * cos))
                        y1 = center_y + int(round(small_outside_radius * sin))

                else:        # No predefined scale values, calculate the tick values
                    if Decimal(str(i)) % check_large_tick_frequency: # Small tick
                        x1 = center_x + int(round(small_outside_radius * cos))
                        y1 = center_y + int(round(small_outside_radius * sin))
                    else:                                            # Large tick mark with text
                        x1 = tvx1 = center_x + int(round(large_outside_radius * cos))
                        y1 = tvy1 = center_y + int(round(large_outside_radius * sin))

                        tvx2 = center_x + int(round(inside_values_radius * cos))
                        tvy2 = center_y + int(round(inside_values_radius * sin)) - int(pix_y / 2)
                        tvx2 = tvx2 - int((len(str(i)) / 3.0) * pix_x)

                        if x1 < (width/2):          # adjust text position if on left hand side
                            tvx1 = x1 - int(((len(str(i)) * 0.75) * pix_x))
                        elif x1 == (width/2):
                            tvx1 = x1 - int(((len(str(i)) * 0.25) * pix_x))
                        else:
                            tvx1 += pix_x
                        tvy1 = y1 - int(pix_y / 2)

                        _value_ticks += [[tvx1, tvy1]]
                        _tick_values += [str_i]
                        _inside_value_ticks += [[tvx2, tvy2]]

                ticks += [[i, pen, [x1, y1, x2, y2]]]

            self._tick_list = ticks

            count = len(_value_ticks)
            last_tick = _tick_values[-1]
            last_value = _value_ticks[-1]
            last_inside_value = _inside_value_ticks[-1]

            if not self._parent or not self._parent.InsideScale:
                if count > 31: # reduce excessive text which will present as a jumble of numbers - outside up to 30 values
                    step, count = count, 0
                    while step > 30:
                        step = math.ceil(step/30)
                        count += step
                    step = count
                    _value_ticks = _value_ticks[::step]
                    _tick_values = _tick_values[::step]
                    _inside_value_ticks = _inside_value_ticks[::step]
            elif self._parent and self._parent.InsideScale:
                if count > 13: # inside up to 12 values
                    step, count = count, 0
                    while step > 12:
                        step = math.ceil(step/12)
                        count += step
                    step = count
                    _value_ticks = _value_ticks[::step]
                    _tick_values = _tick_values[::step]
                    _inside_value_ticks = _inside_value_ticks[::step]

            _value_ticks[-1] = last_value   #ensure last entry is the maximum
            _tick_values[-1] = last_tick
            _inside_value_ticks[-1] = last_inside_value

            self.value_ticks = _value_ticks
            self.tick_values = _tick_values
            self.inside_value_ticks = _inside_value_ticks

        return self._tick_list

    def _get_tick_number(self, value):
        value_range = self.max_value + self.increment - self.min_value
        num_ticks = value_range * self.tick_frequency

        tick_num = _remap(value, self.min_value, self._max_value, 0, num_ticks)
        return int(tick_num)

    def is_value_line_up(self, value):
        if value < self.value:
            return False

        ticks = self.tick_list

        for i, (v, pen, coords) in enumerate(ticks):
            if v == value:
                break
        else:
            return False

        if i == len(ticks) - 1:
            return False
        if ticks[i + 1][2] != coords:
            return True

        return False

    def is_value_line_down(self, value):
        if value > self.value:
            return False
        ticks = self.tick_list

        for i, (v, pen, coords) in enumerate(ticks):
            if v == value:
                break
        else:
            return False

        if i == 0:
            return False
        if ticks[i - 1][2] != coords:
            return True

        return False

    def is_page(self, value):
        if value % self.page_size:
            return False
        return True


class KnobEvent(wx.PyCommandEvent):
    """
    Wrapper around wx.ScrollEvent to allow the GetPosition and SetPosition
    to accept floats
    """

    def __init__(self, event_type, id=1):
        wx.PyCommandEvent.__init__(self, event_type, id)

        self.__orientation = None
        self.__position = 0

    def SetPosition(self, value):
        self.__position = value

    def GetPosition(self):
        return self.__position

    def SetOrientation(self, value):
        self.__orientation = value

    def GetOrientation(self):
        return self.__orientation

    def GetEventUserData(self):
        return None

    Position = property(fget=GetPosition, fset=SetPosition)
    Orientation = property(fget=GetOrientation, fset=SetOrientation)


KNOB_GLOW = 1 << 0          # 1
KNOB_DEPRESSION = 1 << 1    # 2
KNOB_HANDLE_GLOW = 1 << 2   # 4
KNOB_TICKS = 1 << 3         # 8
KNOB_SHADOW = 1 << 4        # 16
KNOB_RIM = 1 << 5           # 32

DefaultKnobStyle = KNOB_GLOW | KNOB_DEPRESSION | KNOB_HANDLE_GLOW | KNOB_TICKS | KNOB_SHADOW
KnobNameStr = 'Knob Control'
# noinspection PyPep8Naming
class KnobCtrl(wx.Control):

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        value=0.0,
        minValue=0.0,
        maxValue=100.0,
        increment=1.0,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=0,
        name=KnobNameStr,
        knobStyle=DefaultKnobStyle
    ):

        wx.Control.__init__(
            self,
            parent,
            id=id,
            pos=pos,
            size=size,
            style=style | wx.BORDER_NONE,
            name=name
        )

        self.SetBackgroundColour(parent.GetBackgroundColour())

        self.increment = increment
        self.ShowToolTip = False
        self.ShowValue = False
        self.ShowMinMax = False
        self.ShowScale = False
        self.InsideScale = False
        self.DefinedScaleValues = []
        self.ShowPointer = False
        self.PointerColour = None
        self.GaugeText = ''
        self.GaugeImage = None
        self.GaugeImagePos = 0
        self.ShowOdometer = False
        self.OdometerUpdate = 0
        self.distance_matrix = []
        self.OdometerPeriod = "H"
        self.OdometerColour = '#30303080'
        self.OdometerBackgroundColour = None
        self.UseHotSpots = False
        self.HotSpot = None
        self.OdometerHotSpot = None
        self.OdometerToolTip = ''
        self.Caption = ''
        self.CaptionPos = 0
        self.negative = False
        self.DisableMinMaxMouseDrag = False

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self._on_mouse_lost_capture)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_mouse_right_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_mouse_right_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_left_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self._handler = Handler(self)
        _prec = str(increment).split('.')
        if len(_prec) > 1:
            self.precision = len(_prec[-1])
        else:
            self.precision = 0
        self._handler.precision = self.precision
        if minValue >= maxValue:
            raise ValueError(f'Min value {minValue} is higher then the Max value {maxValue}')
        self._handler.min_value = minValue
        self._handler.max_value = maxValue
        self._handler.increment = increment
        self._handler.value = value
        self._handler.type = value
        self._handler.background_colour = parent.GetBackgroundColour()
        self._handler.foreground_colour = parent.GetForegroundColour()
        self._last_degrees = None

        # 50% in degrees of default end_degrees - start_degrees - used for restricting mouse movement See: DisableMinMaxMouseDrag
        self.mouse_max_move = abs(self._handler.end_degree - self._handler.start_degree) * 0.5

        self._handler.size = self.GetBestSize()

        self._handler.glow = bool(knobStyle & KNOB_GLOW)
        self._handler.depression = bool(knobStyle & KNOB_DEPRESSION)
        self._handler.thumb_glow = bool(knobStyle & KNOB_HANDLE_GLOW)
        self._handler.ticks = bool(knobStyle & KNOB_TICKS)
        self._handler.shadow = bool(knobStyle & KNOB_SHADOW)
        self._handler.highlight_rim = bool(knobStyle & KNOB_RIM)
        self._knob_style = knobStyle

        self.current_time = time.time()
        self.start_time = self.current_time
        self.current_speed = self._handler.value
        wx.ToolTip.Enable(True)
        wx.ToolTip.SetDelay(10)


    def HasGlow(self):
        return self._handler.glow

    def HasDepression(self):
        return self._handler.depression

    def HasHandleGlow(self):
        return self._handler.thumb_glow

    def HasTicks(self):
        return self._handler.ticks

    def HasShadow(self):
        return self._handler.shadow

    def GetKnobStyle(self):
        return self._knob_style

    def SetKnobStyle(self, knobStyle):
        self._handler.glow = bool(knobStyle & KNOB_GLOW)
        self._handler.depression = bool(knobStyle & KNOB_DEPRESSION)
        self._handler.thumb_glow = bool(knobStyle & KNOB_HANDLE_GLOW)
        self._handler.ticks = bool(knobStyle & KNOB_TICKS)
        self._handler.shadow = bool(knobStyle & KNOB_SHADOW)
        self._handler.highlight_rim = bool(knobStyle & KNOB_RIM)
        self._knob_style = knobStyle

        def _do():
            self.Refresh()
            self.Update()

        wx.CallAfter(_do)

    def GetPageSize(self):
        return self._handler.page_size

    def SetPageSize(self, value):
        if Decimal(str(self._handler.max_value - self._handler.min_value)) % Decimal(str(value)):
            raise RuntimeError(
                f'Page size needs to be a multiple of the value range {self._handler.max_value - self._handler.min_value}'
            )
        self._handler.page_size = value

        def _do():
            self.Refresh()
            self.Update()

        wx.CallAfter(_do)

    def GetValueRange(self):
        return self._handler.min_value, self._handler.max_value

    def SetValueRange(self, minValue, maxValue):
        self._handler.min_value = minValue
        self._handler.max_value = maxValue

        def _do():
            self.Refresh()
            self.Update()

        wx.CallAfter(_do)

    def _create_event(self, event, value):
        """
        Internal use, creates a new KnobEvent
        :param event: wx event.
        :return: None
        """
        event = KnobEvent(event, self.GetId())
        event.SetId(self.GetId())
        event.SetEventObject(self)
        event.SetPosition(value)
        event.SetOrientation(wx.HORIZONTAL)
        self.GetEventHandler().ProcessEvent(event)

    def _on_char_hook(self, evt):

        key_code = evt.GetKeyCode()
        if key_code in (wx.WXK_PAGEUP, wx.WXK_NUMPAD_PAGEUP): #jump 10% (or manually set page size)
            value = self._handler.value + self._handler.page_size
            #value -= value % self._handler.page_size
            event = wx.wxEVT_SCROLL_PAGEUP

        elif key_code in (wx.WXK_PAGEDOWN, wx.WXK_NUMPAD_PAGEDOWN): #jump 10%
            value = self._handler.value - self._handler.page_size

            #if value == self._handler.value:
            #   value -= self._handler.page_size
            event = wx.wxEVT_SCROLL_PAGEDOWN

        elif key_code in (
            wx.WXK_UP,
            wx.WXK_ADD,
            wx.WXK_NUMPAD_UP,
            wx.WXK_NUMPAD_ADD
        ):
            event = wx.wxEVT_SCROLL_LINEUP
            value = self._handler.value + self._handler.increment

        elif key_code in (
            wx.WXK_DOWN,
            wx.WXK_SUBTRACT,
            wx.WXK_NUMPAD_DOWN,
            wx.WXK_NUMPAD_SUBTRACT
        ):
            event = wx.wxEVT_SCROLL_LINEDOWN
            value = self._handler.value - self._handler.increment

        elif key_code in (wx.WXK_HOME, wx.WXK_NUMPAD_HOME):
            value = self._handler.min_value
            event = None

        elif key_code in (wx.WXK_END, wx.WXK_NUMPAD_END):
            value = self._handler.max_value
            event = None

        # numbers that represent 10% (or manually set page size) incremnts of the value range
        elif key_code - 48 in list(range(0, 10)):
            mult  = key_code - 48
            value = (mult * self._handler.page_size) + self._handler.min_value
            event = None
        elif key_code in digits_numeric_pad:
            idx = [index for (index , item) in enumerate(digits_numeric_pad) if item == key_code]
            if idx:
                mult = idx[0]
                value = (mult * self._handler.page_size) + self._handler.min_value
                event = None
        else:
            evt.Skip()
            return

        if self.precision:
            round2 = self.precision
        else:
            round2 = None
        value = round(value, round2)

        self._last_degrees = None
        self.__generate_events(event, value)

        evt.Skip()

    def _on_erase_background(self, _):
        pass

    def _on_mouse_lost_capture(self, evt):
        if self.HasCapture():
            pass
        else:
            #evt.Skip()
            return
        self._last_degrees = None
        self.ReleaseMouse()
        self.Unbind(wx.EVT_MOTION, handler=self._on_mouse_move)
        if self.UseHotSpots:
            self.Bind(wx.EVT_MOTION, handler=self._on_motion)
        self._create_event(wx.wxEVT_SCROLL_THUMBRELEASE, round(self.GetValue(), self.precision))
        self.Refresh()
        #self.Update()
        #evt.Skip()

    def __generate_events(self, event, value, degrees=None):
        if value >= self._handler.max_value:
            value = self._handler.max_value

        elif value <= self._handler.min_value:
            value = self._handler.min_value

        if value != self._handler.value:
            self._last_degrees = degrees
            handler_value = self._handler.value
            self._handler.value = value

            def _do():
                self.Refresh()
            #    self.Update()

            wx.CallAfter(_do)

            if event is not None:
                self._create_event(event, value)
                return
            if value == self._handler.max_value:
                self._create_event(wx.wxEVT_SCROLL_TOP, value)
                return
            elif value == self._handler.min_value:
                self._create_event(wx.wxEVT_SCROLL_BOTTOM, value)
                return
            if self._handler.is_page(value):
                if value > handler_value:
                    self._create_event(wx.wxEVT_SCROLL_PAGEUP, value)
                else:
                    self._create_event(wx.wxEVT_SCROLL_PAGEDOWN, value)
                return

            self._create_event(wx.wxEVT_SCROLL_CHANGED, value)
            return True

        return False

    def _on_mouse_wheel(self, evt):
        wheel_delta = evt.GetWheelRotation()
        value = self._handler.value

        if wheel_delta < 0:
            value -= self._handler.increment
            event = wx.wxEVT_SCROLL_LINEDOWN

        elif wheel_delta > 0:
            value += self._handler.increment
            event = wx.wxEVT_SCROLL_LINEUP

        else:
            evt.Skip()
            return

        if self.precision:
            round2 = self.precision
        else:
            round2 = None
        value = round(value, round2)
        self.__generate_events(event, value)

        evt.Skip()

    # define if mouse click is in the invalid range of the circle and if so is it nearer to the lower valid range
    # or the upper valid range
    # permits a decision to jump to nearest valid range if outside of valid range.
    # returns True/False if in invalid range and True if the nearest valid range is lower, else False
    def angle_in_range(self, hitpos, lower, upper):
        Inzone = (hitpos - lower) % 360 <= (upper - lower) % 360
        if Inzone:
            midpoint = ((upper - lower) % 360) / 2
            pos = (hitpos - lower) % 360
            if pos < midpoint:
                lower = True
            else:
                lower = False
        else:
            lower = False
        return Inzone, lower

    def _on_mouse_left_up(self, evt):
        if self.HasCapture():
            self.Unbind(wx.EVT_MOTION, handler=self._on_mouse_move)
            if self.UseHotSpots:
                self.Bind(wx.EVT_MOTION, handler=self._on_motion)
            self.ReleaseMouse()
            self._create_event(wx.wxEVT_SCROLL_THUMBRELEASE, round(self.GetValue(), self.precision))
            self.Refresh()
            self.Update()

        evt.Skip()

    def _on_mouse_left_down(self, evt):
        thumb_x, thumb_y = self._handler.thumb_position
        thumb_radius = self._handler.thumb_radius

        # Is the click near the thumb
        region = wx.Region(int(thumb_x - (thumb_radius * 2)), int(thumb_y - (thumb_radius * 2)),
                           int(thumb_radius * 4), int(thumb_radius * 4))

        pos = evt.GetPosition()
        if region.Contains(pos):
            self.CaptureMouse()
            self.Unbind(wx.EVT_MOTION, handler=self._on_motion)
            self.Bind(wx.EVT_MOTION, self._on_mouse_move)

        evt.Skip()

    def _on_mouse_right_down(self, evt):

        width, height = self.GetSize()
        center_x = width / 2.0
        center_y = height / 2.0
        x, y = evt.GetPosition()
        radians = math.atan2(y - center_y, x - center_x)
        cpd = radians * (180 / math.pi)
        if cpd < 0:
            cpd += 360
        degrees = cpd                               # degrees between 0 and 360 counting from 3 o,clock clockwise

        if not self.negative:
            up = int(self._handler.mid_point - self._handler.mid_point_adj)
            down = int(self._handler.mid_point + self._handler.mid_point_adj)

        else:
            up = int(self._handler.negative_mid_point - self._handler.mid_point_adj)
            down = int(self._handler.negative_mid_point + self._handler.mid_point_adj)

        outofrange, jumplower = self.angle_in_range(degrees, up, down)

        if outofrange and jumplower:
            if self._handler.end_degree > self._handler.start_degree:            # Is the gauge defined to travel positive
                degrees = self._handler.end_degree
            else:                                       # or negative
                degrees = self._handler.start_degree
        if outofrange and not jumplower:
            if self._handler.end_degree > self._handler.start_degree:            # Is the gauge defined to travel positive
                degrees = self._handler.start_degree
            else:                                       # or negative
                degrees = self._handler.end_degree

        if not self.negative:
            if self._handler.end_degree > 360 and degrees < self._handler.start_degree:
                degrees += 360
            if self._handler.start_degree > 360 and degrees < self._handler.end_degree: # gauge defined for negative travel
                degrees += 360
        else:
            degrees = degrees % -360
            if self._handler.end_degree < -360 and degrees > self._handler.start_degree:
                degrees -= 360
            if self._handler.start_degree < -360 and degrees > self._handler.end_degree: # gauge defined for negative travel
                degrees -= 360

        value = float(_remap(degrees, self._handler.start_degree, self._handler.end_degree, self._handler.min_value, self._handler.max_value))
        value = math.ceil(value / self.increment) * self.increment
        value = round(value, self.precision)
        self.__generate_events(wx.wxEVT_SCROLL_THUMBRELEASE, value)
        self.Refresh()
        self.Update()

        #evt.Skip()

    def _on_mouse_move(self, evt):
        if self.HasCapture():
            pass
        else:
            evt.Skip()
            return

        x, y = evt.GetPosition()
        width, height = self.GetSize()
        center_x = width / 2.0
        center_y = height / 2.0
        radians = math.atan2(y - center_y, x - center_x)
        degrees = math.degrees(radians)

        disabled_minmax_jump = self._last_degrees   # used to determine if a jump from min to max or max to min is allowed

        cpd = radians * (180 / math.pi)
        if cpd < 0:
            cpd += 360
        degrees = cpd                               # degrees between 0 and 360 counting from 3 o,clock clockwise

        if not self.negative:
            up = int(self._handler.mid_point - self._handler.mid_point_adj)
            down = int(self._handler.mid_point + self._handler.mid_point_adj)
        else:
            up = int(self._handler.negative_mid_point - self._handler.mid_point_adj)
            down = int(self._handler.negative_mid_point + self._handler.mid_point_adj)


        outofrange, jumplower = self.angle_in_range(degrees, up, down)

        if outofrange and jumplower:
            if self._handler.end_degree > self._handler.start_degree:               # Is the gauge defined to travel positive
                degrees = self._handler.end_degree
            else:                                                                   # or negative
                degrees = self._handler.start_degree
        if outofrange and not jumplower:
            if self._handler.end_degree > self._handler.start_degree:               # Is the gauge defined to travel positive
                degrees = self._handler.start_degree
            else:                                                                   # or negative
                degrees = self._handler.end_degree

        if not self.negative:
            if self._handler.end_degree > 360 and degrees < self._handler.start_degree:
                degrees += 360
            if self._handler.start_degree > 360 and degrees < self._handler.end_degree: # gauge defined for negative travel
                degrees += 360
        else:
            degrees = degrees % -360
            if self._handler.end_degree < -360 and degrees > self._handler.start_degree:
                degrees -= 360
            if self._handler.start_degree < -360 and degrees > self._handler.end_degree: # gauge defined for negative travel
                degrees -= 360

        value = _remap(degrees, self._handler.start_degree, self._handler.end_degree, self._handler.min_value, self._handler.max_value)
        if (value % self._handler.increment) * 2 >= self._handler.increment:
            if self._last_degrees < degrees:
                #value -= (value % self._handler.increment)
                #value = round(value, self.precision)
                value = math.ceil(value / self.increment) * self.increment
                event = wx.wxEVT_SCROLL_LINEUP
            elif self._last_degrees > degrees:
                #value -= (value % self._handler.increment)
                #value = round(value, self.precision)
                value = math.ceil(value / self.increment) * self.increment
                event = wx.wxEVT_SCROLL_LINEDOWN
            else:
                self._last_degrees = degrees
                evt.Skip()
                return
        else:
            self._last_degrees = degrees
            evt.Skip()
            event = None
           # return

        if self.DisableMinMaxMouseDrag:
            if abs(degrees - disabled_minmax_jump) > self.mouse_max_move:
                self._on_mouse_lost_capture(None)
                return

        #if self.DisableMinMaxMouseDrag:     # Prevent mouse move accidently flipping instantly from Min to Max or Max to Min
        #    if disabled_minmax_jump == self._handler.start_degree and degrees == self._handler.end_degree:
        #        value = self._handler.min_value
        #        self._on_mouse_lost_capture(None)
        #    if disabled_minmax_jump == self._handler.end_degree and degrees == self._handler.start_degree:
        #        value = self._handler.max_value
        #        self._on_mouse_lost_capture(None)

        value = round(value, self.precision)

        if self.UseHotSpots:
            self.SetToolTip(str(value))

        if self.__generate_events(event, value, degrees):
            self._create_event(wx.wxEVT_SCROLL_THUMBTRACK, value)

        evt.Skip()

    def _on_size(self, evt):
        width, height = evt.GetSize()
        self._handler.size = (width, height)

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)
        evt.Skip()

    def _on_motion(self, event):
        if self.UseHotSpots:
            if self.HotSpot:
                ClientPos = event.GetPosition()
                if self.HotSpot.Contains(ClientPos):
                    if self.precision:
                        show_val = f'{self._handler.value:3.{self.precision}f}'
                    else:
                        show_val = f'{int(self._handler.value):3}'
                    self.SetToolTip(show_val)
                elif self.OdometerHotSpot and self.OdometerHotSpot.Contains(ClientPos):
                    t = f'{time.time() - self.start_time:3.2f}'
                    if self.OdometerToolTip:
                        tip = self.OdometerToolTip  + "\nRunning Time in Secs: " + t
                    else:
                        tip = "Running Time: " + t
                    self.SetToolTip(tip)
                else:
                    self.SetToolTip('')
        event.Skip()


    def GetPrimaryColour(self):
        return self._handler.primary_colour

    def SetPrimaryColour(self, value):

        if isinstance(value, (list, tuple)):
            value = wx.Colour(*value)

        self._handler.primary_colour = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetSecondaryColour(self):
        return self._handler.secondary_colour

    def SetSecondaryColour(self, value):

        if isinstance(value, (list, tuple)):
            value = wx.Colour(*value)

        self._handler.secondary_colour = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetTickFrequency(self):
        return self._handler.tick_frequency

    def SetTickFrequency(self, value):
        value_range = self._handler.max_value - self._handler.min_value
        ticks = value_range / value
        if ticks > 600:
            raise RuntimeError(f'This tick frequency would produce excessive ticks: {ticks} - The limit is 600')

        inc = self._handler.increment

        # Issue with modulo e.g. 4 % 0.1 does NOT return zero so we use Decimal
        if Decimal(str(value_range)) % Decimal(str(value)):
            raise RuntimeError(f'The Value Range: {value_range} is Not divisible by the Tick Frequency: {value}')

        if value < inc:
            raise RuntimeError(f'The tick frequency: {value} is less than the increment: {inc}')

        self._handler.tick_frequency = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetThumbSize(self):
        return int(self._handler.thumb_multiplier * 100)

    def SetThumbSize(self, value):
        value /= 100.0
        self._handler.thumb_multiplier = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetTickColours(self):
        return self._handler.tick_range_colors

    def SetTickColours(self, values):

        colours = []

        for colour in values:
            if isinstance(colour, (list, tuple)):
                colour = wx.Colour(*colour)

            colours += [colour]

        self._handler.tick_range_colors = colours

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetTickColorRanges(self):
        return self._handler.tick_ranges

    def SetTickColourRanges(self, values):
        percs_to_values = []
        # calculate value as a percentage, allowing for negatives in the range of min/max values e.g. -10.0 -> +10.0
        if self._handler.tick_range_percentage:
            for r_value in values:
                percs_to_values.append(round(((r_value * (self._handler.max_value - self._handler.min_value) / 100) + self._handler.min_value), self.precision))
        else:
            # Use value as given
            for r_value in values:
                percs_to_values.append(r_value)
        self._handler.tick_ranges = percs_to_values

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def SetDefaultTickColour(self, value):
        self._handler._default_tick_pen.SetColour(value)

    def GetDefaultTickColour(self):
        return self._handler._default_tick_pen.GetColour()

    def SetTickRangePercentage(self, value):
        self._handler.tick_range_percentage = value

    def SetAlwaysTickColours(self, value=False):
        self._handler.always_tick_colours = value

    def SetSize(self, size):
        wx.Control.SetSize(self, size)
        width, height = self.GetSize()
        self._handler.size = (width, height)

    def GetValue(self):
        return self._handler.value

    def SetValue(self, value):
        self._last_degrees = None

        if self._handler.min_value > value:
            raise ValueError(f'new value {value} is lower then the set minimum {self._handler.min_value}')
            value = self._handler.min_value
        if self._handler.max_value < value:
            raise ValueError(f'new value {value} is higher then the set maximum {self._handler.max_value}')
            value = self._handler.max_value
        diff = round(value - self._handler.value, self.precision)
        self._handler.value = value

        if diff:
            event = wx.wxEVT_SCROLL_CHANGED
            self._create_event(event, value)

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetIncrement(self):
        return self._handler.increment

    def SetIncrement(self, increment):
        self._handler.increment = increment

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetMinValue(self):
        return self._handler.min_value

    def SetMinValue(self, value):
        self._handler.min_value = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetMaxValue(self):
        return self._handler.max_value

    def SetMaxValue(self, value):
        self._handler.max_value = value

        def do():
            self.Refresh()
            self.Update()

        wx.CallAfter(do)

    def GetOdometerUpdate(self):
        return self.OdometerUpdate

    def SetOdometerUpdate(self, value):
        self.OdometerUpdate = value
        if value > 0:
            self.ShowOdometer = True
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
            self.timer.Start(value)
        else:
            self.ShowOdometer = False
            self.Unbind(wx.EVT_TIMER, self.timer)
            self.timer.Stop()
            self.Refresh()
            self.Update()

    def SetHotSpots(self):
        self.UseHotSpots = not self.UseHotSpots
        if self.UseHotSpots:
            self.Unbind(wx.EVT_MOTION, handler=self._on_mouse_move)
            self.Bind(wx.EVT_MOTION, handler=self._on_motion)
            self.ShowToolTip = False    # Turn off standard tooltip if On
        else:
            self.Unbind(wx.EVT_MOTION, handler=self._on_motion)

    def GetHotSpots(self):
        return self.UseHotSpots

    def GetStartEndDegrees(self):
        return self._handler.start_degree, self._handler.end_degree

    def SetStartEndDegrees(self, start = 135.0, end = 405.0):
        start = float(start)
        end = float(end)
        if (start < 0 and end > 0) or (start > 0 and end < 0):
            raise RuntimeError(f'Choose a direction - Positive or Negative - Not Both - {start} | {end}')

        self._handler.start_degree = start
        self._handler.end_degree = end

        self.mouse_max_move = abs(end - start) * 0.5

        if start >= 0:
            self.negative = False
            if abs(start - end) > 360.0:
                raise RuntimeError(
                'Distance between Start and End points, cannot exceed 360° - Currently: ' + str(abs(start - end))
                )

            self._handler.mid_point = (start, end)
        else:
            self.negative = True
            if (start - end) < -360:
                raise RuntimeError(
                'Distance between Start and End points, cannot exceed 360° - Currently: ' + str(start - end)
                )
            self._handler.negative_mid_point = (start, end)

        ticks = (self._handler.max_value - self._handler.min_value) / self._handler.tick_frequency
        excess = ticks / abs(end - start)
        if excess > 1.666: # max limit 600 ticks or 1.66 per degree
                raise RuntimeError(
                f'Excessive ticks in this range ( {excess} per Degree) - adjust TickFrequency or StartEndDegrees'
                )

        def do():
            self.Refresh()
            self.Update()

        # Force a Repaint
        value = self.GetValue()
        #if value + self._handler.increment > self._handler.max_value:
        #    sval = value - self._handler.increment
        #else:
        #    sval = value + self._handler.increment
        #self.SetValue(sval)
        self.SetValue(value)
        wx.CallAfter(do)
        return

    def OnTimer(self, evt):
        #self.RefreshRect(self.OdometerHotSpot.GetBox())
        self.Refresh() # quickest x 1000!
        #self.Update()

    def GetAverageSpeed(self):
        t = time.time() - self.start_time
        d = sum(self.distance_matrix)
        if self.OdometerPeriod.upper() == "S":
            mult = 1
        elif self.OdometerPeriod.upper() == "M":
            mult = 60
        else:
            mult = 3600
        return (((d/t) * mult), t)

    def GetOdometerValue(self):
        return sum(self.distance_matrix)

    def GetOdometerHistory(self):
        return self.distance_matrix

    def OnPaint(self, _):
        width, height = self._handler.size

        if width <= 0 or height <= 0:
            bmp = wx.Bitmap.FromRGBA(
                1,
                1
            )
            pdc = wx.PaintDC(self)
            gcdc = wx.GCDC(pdc)
            gcdc.DrawBitmap(bmp, 0, 0)

            gcdc.Destroy()
            del gcdc

            return

        bmp = wx.Bitmap.FromRGBA(
            width,
            height
        )

        if self.ShowOdometer:
            # Distance travelled defaults to per hour
            update_time = time.time() - self.current_time
            if self.OdometerPeriod.upper() == "S":
                d = update_time * self.current_speed
            elif self.OdometerPeriod.upper() == "M":
                d = ((update_time * self.current_speed) / 60)
            else:
                d = (((update_time * self.current_speed) / 60) / 60)
            if d:
                self.distance_matrix.append(d)
            distance_travelled = sum(self.distance_matrix)
            self.current_time  = time.time()
            self.current_speed = self._handler.value

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(dc)
        gcdc = wx.GCDC(gc)

        gcdc.SetBrush(wx.Brush(self.GetBackgroundColour()))
        gcdc.SetPen(wx.TRANSPARENT_PEN)

        gcdc.DrawRectangle(0, 0, width, height)

        def draw_circle(x, y, r, _gcdc):
            _gcdc.DrawEllipse(
                int(round(float(x) - r)),
                int(round(float(y) - r)),
                int(round(r * 2.0)),
                int(round(r * 2.0))
            )

        def draw_circle_rim(x, y, r, _gcdc):
            x_center, y_center = self._handler.center
            thumb_x, thumb_y = self._handler.thumb_position
            if not self.negative:
                start = abs(self._handler.start_degree % -360)
                end = abs(self._handler.end_degree % -360)
            else:
                start = self._handler.start_degree % 360
                end = self._handler.end_degree % 360
            radians = math.atan2(thumb_y - y_center, thumb_x - x_center)
            if not self.negative:
                degrees = abs(radians * (180 / math.pi) % -360)
            else:
                degrees = abs(radians * (180 / math.pi) % 360)
                start, degrees = -start, -degrees
            if self._handler.start_degree > self._handler.end_degree:
                degrees = degrees % -360
                start = start % 360
                start, degrees = degrees, start
            _gcdc.SetBrush(wx.Brush(self._handler.neon_colour))

            # Only draw arc if it indicates a value of > minimum value - also test for a reversed start and end value
            #  without these tests, a minimum value will highlight the entire rim
            rim_reverse_start = round(degrees % -360)
            start = round(start)
            if round(degrees) != start and start != rim_reverse_start:
                _gcdc.DrawEllipticArc(
                    int(round(float(x) - r)),
                    int(round(float(y) - r)),
                    int(round(r * 2.0)),
                    int(round(r * 2.0)),
                    degrees, start
                    )

        gcdc.SetBrush(wx.TRANSPARENT_BRUSH)
        x_center, y_center = self._handler.center

        gcdc.SetPen(wx.TRANSPARENT_PEN)
        radius = self._handler.radius

        if self._handler.shadow:
            # shadow
            stops = wx.GraphicsGradientStops()
            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.45))
            stops.Add(wx.GraphicsGradientStop(wx.Colour(0, 0, 0, 255), 0.25))

            stops.SetStartColour(wx.Colour(0, 0, 0, 255))
            stops.SetEndColour(wx.TransparentColour)

            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    x_center + (radius * 0.10),
                    y_center + (radius * 0.10),
                    x_center + (radius * 0.30),
                    y_center + (radius * 0.30),
                    radius * 2.3,
                    stops
                )
            )

            draw_circle(x_center + (radius * 0.10), y_center + (radius * 0.10), radius * 2, gcdc)

            # eliminate any shadow under the knob just in case there is a color
            # used in the gradient of the knob that does not have an alpha level of 255

            gc.SetBrush(wx.Brush(self.GetBackgroundColour()))
            draw_circle(x_center, y_center, radius - 2, gcdc)

        if self._handler.glow or self._handler.highlight_rim: # glow 100% of rim or highlight to the rim value
            neon_colour = self._handler.neon_colour

            stops = wx.GraphicsGradientStops()

            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.295)) # 0.265
            stops.Add(wx.GraphicsGradientStop(wx.Colour(*neon_colour + (200,)), 0.25))
            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.248))

            stops.SetStartColour(wx.TransparentColour)
            stops.SetEndColour(wx.TransparentColour)

            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    x_center,
                    y_center,
                    x_center,
                    y_center,
                    radius * 4,
                    stops
                )
            )

            if self._handler.glow:
                draw_circle(x_center, y_center, radius * 2, gcdc)
            if self._handler.highlight_rim:
                draw_circle_rim(x_center, y_center, radius+(radius*0.05), gcdc)

        # outside ring of volume knob

        gc.SetBrush(
            gc.CreateRadialGradientBrush(
                x_center - radius,
                y_center - radius,
                x_center,
                y_center - radius,
                radius * 2,
                self._handler.secondary_colour,
                self._handler.primary_colour

            )
        )

        draw_circle(x_center, y_center, radius, gcdc)

        thumb_x, thumb_y = self._handler.thumb_position
        thumb_radius = self._handler.thumb_radius

        # inside of volume knob
        if self._handler.depression:
            center_radius = self._handler.center_radius
            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    x_center + center_radius,
                    y_center + center_radius,
                    x_center,
                    y_center + center_radius,
                    center_radius * 2,
                    self._handler.secondary_colour,
                    self._handler.primary_colour
                )
            )

            draw_circle(x_center, y_center, center_radius, gcdc)

        if self._last_degrees is None:
            self._last_degrees = _remap(
                self._handler.value,
                self._handler.min_value,
                self._handler.max_value,
                self._handler.start_degree,
                self._handler.end_degree
            )

        # handle of the volume knob
        gc.SetBrush(
            gc.CreateRadialGradientBrush(
                thumb_x + thumb_radius,
                thumb_y + thumb_radius,
                thumb_x,
                thumb_y + thumb_radius,
                thumb_radius * 2,
                self._handler.secondary_colour,
                self._handler.primary_colour
            )
        )

        draw_circle(thumb_x, thumb_y, thumb_radius, gcdc)

        base_fontsize = int(height/10)

        if self._handler.thumb_glow:
            neon_colour = self._handler.neon_colour

            stops = wx.GraphicsGradientStops()

            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.355))
            stops.Add(wx.GraphicsGradientStop(wx.Colour(*neon_colour + (255,)), 0.28))
            stops.Add(wx.GraphicsGradientStop(wx.TransparentColour, 0.258))

            stops.SetStartColour(wx.TransparentColour)
            stops.SetEndColour(wx.TransparentColour)

            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    thumb_x,
                    thumb_y,
                    thumb_x,
                    thumb_y,
                    thumb_radius * 4,
                    stops
                )
            )

            draw_circle(thumb_x, thumb_y, thumb_radius * 2, gcdc)

        # Note position of volume/speed knob for hotspot tooltip, this noted if even off, in case it's turned on later
        # The size of the hotspot is adjusted to a minimum of 20x20 if the control is so small,
        # that hitting the hotspot with the mouse pointer would be difficult
        if thumb_radius < 10:
            hs_adj = 10
        else:
            hs_adj = thumb_radius
        self.HotSpot = wx.Region(int(thumb_x - hs_adj), int(thumb_y - hs_adj), \
                        int(hs_adj * 2), int(hs_adj * 2))

        gcdc.SetBrush(wx.TRANSPARENT_BRUSH)

        # draw the tick marks
        # first ensure handler is aware of whether the text for ticks is for inside or outside the gauge
        if self._handler.ticks:
            ticks = []
            pens = []
            for _, pen, coords in self._handler.tick_list:
                ticks += [coords]
                pens += [pen]

            gcdc.DrawLineList(ticks, pens)

        if self.ShowScale:
            if not self._handler.tick_list:
                _ = self._handler.tick_list # declared here to ensure tick_list has been created even without TICKS style
            #font = wx.Font(int(base_fontsize/4), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
            font = self.Font
            font.SetPointSize(int(base_fontsize/4))
            gcdc.SetFont(font)
            gcdc.SetTextForeground(self.GetDefaultTickColour())
            if not self.InsideScale:                                                # draw scale on the gauge exterior
                gcdc.DrawTextList(self._handler.tick_values, self._handler.value_ticks)
            else:                                                                   # draw scale on the gauge interior
                gcdc.DrawTextList(self._handler.tick_values, self._handler.inside_value_ticks)

        if self.ShowMinMax:
            if not self._handler.tick_list:
                _ = self._handler.tick_list # declared here to ensure tick_list has been created even without TICKS style
            font = self.Font
            font.SetPointSize(int(base_fontsize/4))
            gcdc.SetFont(font)
            gcdc.SetTextForeground(self.GetDefaultTickColour())
            minmax_values = [self._handler.tick_values[0],self._handler.tick_values[-1]]
            if not self.InsideScale:                                                # draw minmax on the gauge exterior
                minmax_ticks = [self._handler.value_ticks[0],self._handler.value_ticks[-1]]
            else:                                                                   # draw minmax on the gauge interior
                minmax_ticks = [self._handler.inside_value_ticks[0],self._handler.inside_value_ticks[-1]]
            gcdc.DrawTextList(minmax_values, minmax_ticks)

        # For very high values like rpm, allow the initial value to be an int and only display an integer value
        if self.precision:
            show_val = f'{self._handler.value:3.{self.precision}f}'
        else:
            show_val = f'{int(self._handler.value):3}'

        # Draw gauge image
        if self.GaugeImage:
            gcdc.SetTextBackground(wx.TransparentColour)
            image = self.GaugeImage
            iw, ih = image.GetSize()
            adj = base_fontsize / ih
            iw = int(adj * iw)
            gaugebmp = wx.Bitmap(image.Scale(iw, base_fontsize))
            bw, bh = gaugebmp.GetSize()
            adjx = x_center - int(bw/2)
            adjy = y_center - int((bh) + (bh/4))
            if self.GaugeImagePos == 1:
                adjx = adjy = 0
            elif self.GaugeImagePos == 2:
                adjx = width - bw
                adjy = 0
            elif self.GaugeImagePos == 3:
                adjx = 0
                adjy = height - bh
            elif self.GaugeImagePos == 4:
                adjx = width - bw
                adjy = height - bh
            gcdc.DrawBitmap(gaugebmp, adjx, adjy)

        # Draw central gauge text
        if self.GaugeText:
            #font = wx.Font(int(base_fontsize/2), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
            font = self.Font
            font.SetPointSize(int(base_fontsize/2))
            gcdc.SetFont(font)
            gcdc.SetTextForeground(self._handler.neon_colour)
            tw, th = gcdc.GetTextExtent(self.GaugeText)
            adj = x_center - int(tw/2)
            gcdc.DrawText(self.GaugeText, adj, y_center - int(th))

        # draw text value
        if self.ShowValue:
            #font = wx.Font(base_fontsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.BOLD)
            font = self.Font.Bold()
            font.SetPointSize(int(base_fontsize))
            gcdc.SetFont(font)
            gcdc.SetTextForeground(self._handler.neon_colour)
            tw, th = gcdc.GetTextExtent(show_val)
            adj = x_center - int(tw/2)
            gcdc.DrawText(show_val, adj, y_center)

        # Show ToolTip
        if self.ShowToolTip:
            self.SetToolTip(show_val)

        # Draw pointer with shadow
        if self.ShowPointer:
            center_radius = self._handler.center_radius
            radians = math.atan2(thumb_y - y_center, thumb_x - x_center)
            PxEnd = x_center + (center_radius - base_fontsize/4.5) * math.cos(radians)
            PyEnd = y_center + (center_radius - base_fontsize/4.5) * math.sin(radians)

            spine_size = int(base_fontsize/10)
            if spine_size < 1:
                spine_size = 1
            p_pen_size =  spine_size * 2
            if spine_size % 2 != 0: # pen size odd if spine size odd
                p_pen_size += 1

            shadow_adj = 0.075
            #halfway point flip shadow - assumes page size is the default 10%
            if self._handler.value >= (5 * self._handler.page_size) + self._handler.min_value:
                shadow_adj = -0.075

            # Draw shadow if outside of range from light source (1/3 and 1/2 of max_value) or not near max_value
            if self._handler.value < self._handler.max_value * 0.9 \
                and int(self._handler.value * 10) not in \
                    range(int((self._handler.max_value / 3) * 10), int((self._handler.max_value / 2) * 10)):
                if int(self._handler.value * 10) > int((self._handler.max_value / 2) * 10):     # Short shadow
                    PxEndShadow = x_center + (center_radius - base_fontsize/3.5) * math.cos(radians + shadow_adj)
                    PyEndShadow = y_center + (center_radius - base_fontsize/3.5) * math.sin(radians + shadow_adj)
                else:                                                                           # Long shadow
                    PxEndShadow = x_center + (center_radius - base_fontsize/5) * math.cos(radians + shadow_adj)
                    PyEndShadow = y_center + (center_radius - base_fontsize/5) * math.sin(radians + shadow_adj)
                spen = wx.Pen('#30303080', p_pen_size)
                #spen.SetCap(wx.CAP_PROJECTING)
                gcdc.SetPen(spen)
                gcdc.DrawLine(x_center, y_center, int(PxEndShadow), int(PyEndShadow))

            # Pointer Spine
            if not self.PointerColour:
                pointer_colour = wx.Colour(self._handler.neon_colour)
            else:
                pointer_colour = self.PointerColour


            ppen = wx.Pen(pointer_colour, spine_size)
            gcdc.SetPen(ppen)
            gcdc.DrawLine(x_center, y_center, int(PxEnd), int(PyEnd))

            if not self.PointerColour:
                pointer_colour = wx.Colour(*self._handler.neon_colour + (160,))
            else:
                pointer_colour = self.PointerColour

            ppen = wx.Pen(pointer_colour, p_pen_size)#base_fontsize/4))
            #ppen.SetCap(wx.CAP_PROJECTING)
            gcdc.SetPen(ppen)
            gcdc.DrawLine(x_center, y_center, int(PxEnd), int(PyEnd))

        if self.ShowOdometer:
            font = wx.Font(int(base_fontsize/2), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
            #font = self.Font
            #font.SetPointSize(int(base_fontsize/2))
            gcdc.SetFont(font)
            gcdc.SetTextForeground(self.OdometerColour)
            dist = f'{round(distance_travelled, 2):07.2f}'
            if len(dist) > 7:
                dist = f'{round(distance_travelled, 1):07.1f}'
                if len(dist) > 7:
                    dist = str(int(distance_travelled))
            tw, th = gcdc.GetTextExtent(dist)
            adjx = x_center - int(tw/2)
            adjy = int(y_center + (th * 1.75))
            dpen = wx.Pen(self.OdometerColour, 1)
            gcdc.SetPen(dpen)
            if self.OdometerBackgroundColour:
                gcdc.SetBrush(wx.Brush(self.OdometerBackgroundColour))
            else:
                gcdc.SetBrush(wx.TRANSPARENT_BRUSH)
            gcdc.DrawRectangle(adjx, adjy, tw, th)
            gcdc.DrawText(dist, adjx, adjy)
            self.OdometerHotSpot = wx.Region(adjx, adjy, tw, th)

        if self.Caption:
            #font = wx.Font(int(base_fontsize/4), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
            font = self.Font
            font.SetPointSize(int(base_fontsize/4))
            gcdc.SetFont(font)
            gcdc.SetTextForeground(self.GetDefaultTickColour())
            tw, th = gcdc.GetTextExtent(self.Caption)
            adjx = x_center - int(tw/2)
            adjy = int(height - th)
            if self.CaptionPos == 1:
                adjx = adjy = 0
            elif self.CaptionPos == 2:
                adjx = width - tw
                adjy = 0
            elif self.CaptionPos == 3:
                adjx = 0
                adjy = height - th
            elif self.CaptionPos == 4:
                adjx = width - tw
                adjy = height - th
            dpen = wx.Pen(self.GetDefaultTickColour(), 1)
            gcdc.SetPen(dpen)
            gcdc.DrawText(self.Caption, adjx, adjy)

        dc.SelectObject(wx.Bitmap(1, 1))
        gcdc.Destroy()
        del gcdc

        dc.Destroy()
        del dc

        # create a buffered paint dc to draw the bmp to the client area
        pdc = wx.PaintDC(self)
        gcdc = wx.GCDC(pdc)
        gcdc.DrawBitmap(bmp, 0, 0)

        gcdc.Destroy()
        del gcdc


if __name__ == '__main__':
    EVENT_MAPPING = {
        wx.EVT_SCROLL_TOP.typeId: 'EVT_SCROLL_TOP',
        wx.EVT_SCROLL_BOTTOM.typeId: 'EVT_SCROLL_BOTTOM',
        wx.EVT_SCROLL_LINEUP.typeId: 'EVT_SCROLL_LINEUP',
        wx.EVT_SCROLL_LINEDOWN.typeId: 'EVT_SCROLL_LINEDOWN',
        wx.EVT_SCROLL_PAGEUP.typeId: 'EVT_SCROLL_PAGEUP',
        wx.EVT_SCROLL_PAGEDOWN.typeId: 'EVT_SCROLL_PAGEDOWN',
        wx.EVT_SCROLL_THUMBTRACK.typeId: 'EVT_SCROLL_THUMBTRACK',
        wx.EVT_SCROLL_THUMBRELEASE.typeId: 'EVT_SCROLL_THUMBRELEASE',
        wx.EVT_SCROLL_CHANGED.typeId: 'EVT_SCROLL_CHANGED'
    }


    class Frame(wx.Frame):

        def __init__(self):

            wx.Frame.__init__(self, None, -1, "Volume Knob Demo", size=(400, 500))

            sizer = wx.BoxSizer(wx.VERTICAL)
            self.ctrl = KnobCtrl(self, value=0.0, minValue=0.0, maxValue=11.0, increment=0.1, size=(150, 150))
            self.ctrl.ShowToolTip = False
            self.ctrl.ShowPointer = False
            self.ctrl.ShowValue = True
            #self.ctrl.PointerColour = "#ffffff80"
            self.ctrl.SetThumbSize(7)
            self.ctrl.SetTickFrequency(0.1)
            self.ctrl.SetTickColours([(0, 255, 0, 255), (255, 187, 0, 255), (255, 61, 0, 255)])
            #self.ctrl.SetTickRangePercentage(False)
            self.ctrl.SetTickColourRanges([80, 90, 100])
            self.ctrl.SetBackgroundColour(wx.Colour(120, 120, 120))
            #self.ctrl.SetPrimaryColour((33, 36, 112, 255))
            self.ctrl.SetSecondaryColour((225, 225, 225, 255))
            #self.ctrl.SetOdometerUpdate(1000)
            self.ctrl.ShowScale = True

            self.ctrl.UseHotSpots = True
            self.ctrl.DisableMinMaxMouseDrag = True   # because this is a volume knob demonstration
            self.ctrl.InsideScale = False
            self.ctrl.SetDefaultTickColour('#ffffff') # White

            self.ctrl.SetStartEndDegrees(135.0, 405.0)
            help = wx.TextCtrl(self, -1, value="\nQuick Demonstration - Please wait!", size=(-1, 110),
                               style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_CENTRE)
            self.ctrl.Bind(wx.EVT_SCROLL, self.on_event)
            help.Bind(wx.EVT_SET_FOCUS, self.on_focus_event)
            self.Bind(wx.EVT_CLOSE, self.OnQuit)
            sizer.Add(self.ctrl, 1, wx.EXPAND, 0)
            sizer.Add(help, 0, wx.EXPAND)
            self.SetSizer(sizer)
            self.Show()
            self.Refresh()
            self.Update()

            help.SetValue("Adjust Speedometer with Mouse or Keyboard\nLeft Click & Drag - Right Click\nMouse Scroll Up / Down\nKeyboard Up / Down / Page Up / Page Down\nKeyboard Home / End / Plus & Minus\nKeyboard numbers as a %")

        def on_event(self, event):
            print (EVENT_MAPPING[event.GetEventType()], event.Position)
            #print ("Avge speed \ time:", self.ctrl.GetAverageSpeed(), "Distance:", self.ctrl.GetOdometerValue())

        # Prevent keyboard event taking focus from ctrl
        def on_focus_event(self, event):
            self.ctrl.SetFocus()
            event.Skip()

        def OnQuit(self, event):
            self.Destroy()

    app = wx.App()

    frame = Frame()
    #frame.Show()
    app.MainLoop()
