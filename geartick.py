from kivy.uix.scatter import Scatter
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from math import atan2
import os
from kivy.properties import (NumericProperty, ReferenceListProperty,
    BoundedNumericProperty, AliasProperty, ListProperty, StringProperty)

from kivy.lang import Builder

Builder.load_string('''
#:import Animation kivy.animation.Animation

<GearTick>
    color: root.background_color
    source: self.background_image
    on_press:
        Animation.stop_all(sctr)
        Animation(scale=root.zoom_factor, d=.5).start(sctr)
    on_release:
        Animation.stop_all(sctr)
        Animation(scale=1, d=.5).start(sctr)
    Scatter:
        id: sctr
        do_scale: False
        do_translation: False
        do_rotation: False
        center: root.center
        size: root.size
        rotation: root.rotation
        Image:
            color: root.foreground_color
            size: root.size
            allow_stretch: True
            mipmap: True
            source: root.overlay_image
''')

_dir = os.path.dirname(os.path.realpath(__file__))

class GearTick(ButtonBehavior, Image):

    background_color = ListProperty((1, 1, 1, 1))
    ''' Color for the background image. Defaults to 1, 1, 1, 1
    '''

    foreground_color = ListProperty((.5, .5, .5, .5))
    ''' Color for the foreground image defaults to (.5, .5, .5, .5)
    '''

    zoom_factor = NumericProperty(4)
    '''Amount to zoom the wheel when scrolling
    '''

    value = NumericProperty(0.)
    '''Current value used for the GearTick.

    :data:`value` is a :class:`~kivy.properties.NumericProperty`, default to 0.
    '''

    min = NumericProperty(0.)
    '''Minimum value allowed for :data:`value`.

    :data:`min` is a :class:`~kivy.properties.NumericProperty`, default to 0.
    '''

    max = NumericProperty(360.)
    '''Maximum value allowed for :data:`value`.

    :data:`max` is a :class:`~kivy.properties.NumericProperty`, default to 100.
    '''

    range = ReferenceListProperty(min, max)
    '''Range of the geartick, in the format (minimum value, maximum value)::

        >>> geartick = Slider(min=10, max=80)
        >>> geartick.range
        [10, 80]
        >>> geartick.range = (20, 100)
        >>> geartick.min
        20
        >>> geartick.max
        100

    :data:`range` is a :class:`~kivy.properties.ReferenceListProperty` of
    (:data:`min`, :data:`max`)
    '''

    step = BoundedNumericProperty(1, min=0)
    '''Step size of the GearTick.

    Determines the size of each interval or step the geartick takes between
    min and max. If the value range can't be evenly divisible by step the
    last step will be capped by geartick.max

    :data:`step` is a :class:`~kivy.properties.NumericProperty`, default to 1.
    '''

    overlay_image = StringProperty(_dir + '/gear.png')
    '''  Image that rotates on top, defaults to gear.png
    '''

    background_image = StringProperty(_dir + '/background.png')
    ''' Image on the background. This image does not rotate.
    '''

    rotation = NumericProperty(0)
    ''' The rotation value of the overlay image.
    '''

    def get_norm_value(self):
        vmin = self.min
        d = self.max - vmin
        if d == 0:
            return 0
        return (self.value - vmin) / float(d)

    def set_norm_value(self, value):
        vmin = self.min
        step = self.step
        val = value * (self.max - vmin) + vmin
        if step == 0:
            self.value = val
        else:
            self.value = min(round((val - vmin) / step) * step + vmin, self.max)
    value_normalized = AliasProperty(get_norm_value, set_norm_value,
                                     bind=('value', 'min', 'max', 'step'))
    '''Normalized value inside the :data:`range` (min/max) to 0-1 range::

        >>> geartick = Slider(value=50, min=0, max=100)
        >>> geartick.value
        50
        >>> geartick.value_normalized
        0.5
        >>> geartick.value = 0
        >>> geartick.value_normalized
        0
        >>> geartick.value = 100
        >>> geartick.value_normalized
        1

    You can also use it for setting the real value without knowing the minimum
    and maximum::

        #>>> geartick = Slider(min=0, max=200)
        >>> geartick.value_normalized = .5
        >>> geartick.value
        100
        >>> geartick.value_normalized = 1.
        >>> geartick.value
        200

    :data:`value_normalized` is an :class:`~kivy.properties.AliasProperty`.
    '''

    def on_value(self, instance, value):
        self.rotation = 360*self.value_normalized

    def get_angle(self, x, y, center=None):
        # calculate touch.angle
        cx, cy = center if center else self.center
        delta_x = x - cx
        delta_y = y - cy
        return atan2(delta_y, delta_x) * 180 / (22/7)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_mouse_scrolling:
            self.on_touch_move(touch, scroll=True)

        touch.oangle = touch.pangle = self.get_angle(*touch.pos)

        return super(GearTick, self).on_touch_down(touch)

    def on_touch_move(self, touch, scroll=False):
        if not scroll and touch.grab_current != self:
            return

        if scroll:
            difference = -1 if touch.button in ('scrollup', 'scrollleft')\
                            else +1
        else:
            angle = self.get_angle(*touch.pos)
            #self.rotation = angle - touch.oangle
            if angle < 0:
                angle = abs(angle)
                difference = -(angle - touch.pangle)
            else:
                difference = angle - touch.pangle

        step = (350/self.max)*self.step
        if abs(difference) < step:
            return
        touch.pangle = angle
        self.value = min(self.max,
                         max(self.min, (self.value + (difference / step))))

if __name__ == '__main__':
    from kivy.app import runTouchApp
    runTouchApp(Builder.load_string('''
#:import Animation kivy.animation.Animation
GridLayout:
    cols: 2
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            size: self.size
            pos: self.pos
    BoxLayout:
        orientation: 'vertical'
        GearTick:
            id: gear_tick
            zoom_factor: 1.1
            # uncomment the following to use non default values
            #max: 100
            #background_image: 'background.png'
            #overlay_image: 'gear.png'
            on_release:
                Animation.stop_all(self)
                Animation(value=0).start(self)
        Label:
            size_hint: 1, None
            height: '22dp'
            color: 0, 1, 0, 1
            text: ('value: {}').format(gear_tick.value)
'''))
