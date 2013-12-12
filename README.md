Module GearTick
===============


A circular Slider.


Usage::

 Python::

    from kivy.garden.geartick import GearTick
    parent.add_widget(GearTick(range=(0, 100)))

 kv::
 
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

![ScreenShot](https://raw.github.com/kivy-garden/garden.geartick/master/snapshot.jpeg)
