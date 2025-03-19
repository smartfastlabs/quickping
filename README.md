# [PRE-ALPHA] Quickping 
_THIS IS VERSION 0.0.) AND WILL CONTINUE TO CHANGE AND EVOLVE._

A modern, type-safe Python library for creating Home Assistant automations using native async Python and decorators. Quickping allows you to structure your automations similar to a modern web app. 

#### Features

- Modern python development environment, with native async/await support.
- Full type hints for enhanced development experience, linting, and error catching
- Intuitive API: defered execution, dependency injection, decorators, helpers, etc.  
- Seamless integration with Home Assistant's event system
- Zero configuration needed - works directly with AppDaemon

# Table of Contents

## Core Features
* [Installation](#installation)
* [Quick Start](#quick-start): Quickping's version of Hello World!
* [Things](#things): lights, fans, sensors, houses, etc. 
* [Collections](#collections): rooms, sensor cluster, light groups, etc.
* [Comparers](#comparers): REALLY REALLY REALLY fancy filtering
* [Changes](#changes): Our model representing state changes
* [Events](#events): Our model representing H.A. Events
* [Attributes](#attributes): state, brightness, temperature, etc. 
* [Handlers](#handlers): Let's write some Automations with vanilla python. 


## Nice To Haves
* [Dependency Injection](#dependecy-injection): Inject `Things` and `Collections` directly into your handlers

## Included Helpers
* [Time](#time): time of day constraints, scheduling, day of week, day of month, etc. 
* [Weather](#weather): temp, wind, clouds, etc [TODO]
* [Sun](#sun): sunset, sunrise, dusk, dawn, etc. [TODO]
* [wait](#wait): Wait for a state to be live. 

## Extending Quickping [TODO]
* [Custom Thing Types](#custom-things): You can get really fancy
* [Faux Things](#faux-things): A lot like a Thing, but its not a real Thing.

## Other Stuff
* [License](#license)
* [Contributing](#contributing)


# Installation

Install through the appdaemon addon in homeassistant.

# Quick Start

```python
import quickping as qp

# Define your rooms and devices
class LivingRoom(qp.Collection):
    # All of these ways work the same 
    lights: Annotated[qp.Device, "light.living_room_table_lamp"]
    shades: Shade = qp.Shade("cover.living_room")
    fan = qp.Fan("fan.living_room")


# Use dependency injection to access devices
@qp.when(LivingRoom.lights.is_on)
async def handle_living_room_lights(
    shades: LivingRoom.shades, 
    room: LivingRoom
):
    """Automatically manage shades based on light state"""
    if room.shades.is_closed:
        await qp.serial(
            shades.open(),
            qp.wait(
                qp.two_minutes, 
                shades.state == "open",
            ),
            print("Shades are open!")
        )
    else:
        await shades.close()

```

# Things
Things are the core building blocks of Quickping; they are similar to Devices in Home Assistan.  The class hierarchy is as follows:

* Thing
    * Collection
        * Room
        * House
        * Region
    * Device
        * Light
            * FancyLight
        * Fan
        * Sensor
            * BinarySensor
        * Switch
    * FauxThing
        * Clock
        * Weather
        * Sun

## Thing.state
All `Things` have a state attr, this is an [Attribute](#attributes)

# Collections

Collections are groups of Things; they're largely a nice to have. 

## Defining Collections and Things

```python
from quickping import Collection, Device

class MasterBedRoom(Collection):
    main_light = Device("light.bedroom_main")
    temperature = Device("sensor.bedroom_temperature")

class LivingRoom(Collection):
    light = Device("light.living_room_main")


class House(Collection):
    # Nested collections
    master_bedroom: MasterBedRoom
    living_room = LivingRoom

    # House-wide devices
    doorbell = Device("binary_sensor.doorbell")
```

# Thing.properties
All thing all things have a `properties` attr that is a `dict[str, Any]` this is where attributes from Home Assistant are stored.  These can be accessed just like a traditional dictionary. 

# Attributes
Attrubutes are QP primitives that track a value in realtime and can be used in [Comparers](#comparers).  `Things` can have an arbitrary number of attributes, see below:

```python
class MyLight(qp.light):
    my_custom_property: Annotated[Attribute, "brightness"] # this will take the value from `entity.attributes.brighness`
    
    async def special_command(self):
        asyncio.gather(
            self.quickping.call_service("do-something-special"),
            self.turn_on(),
        )
    
    
# Now you can use `my_custom_property` to create `Comparers`

@qp.when(MyLight.my_custom_property == 212)
async def doit(light: MyLight):
    """Run whenever MyLight has brightness set to 212"""
    await light.special_command()
```
Using this type of customization you can create custom types of `Things` for any Device in your home.

# Handlers

Handlers are where you write your code!  Handlers are defined and registered by using one of 5 decorators; they are all defined the same way but can all be used in different ways.
* [@when](#when): Runs on state changes
* [@event](#event): React to HASS events (link)
* [@route](#route): HTTP Handlers 
* [@on_idle](#on_idle): Run when a certain set of conditions is not met for a set period of time **(EXPERIMENTAL)**
* [@scene](#scene): Registers a scene with H.A.


## @when

**Heavily influenced by SQL Alchemy's Query Builder and Fast API's router, allowing you to use standard python syntax to write *custom* matching logic.** 

```python
from quickping.conditions import when
from quickping.entities import Sun

@when(
    Sun.is_setting, # is_sunset is a property on Clock
    LivingRoom.lights.state == "on", # state is a property on Light
    LivingRoom.shades.is_open, # is open is a property on Shade
)
async def handle_sundown():
    """Runs ONCE anytime the living room lights are on, shades are open, and sun sets"""


@when(
    BedRoom.motion,
    BedRoom.lights.is_off,
    Sun.is_down,
    BedRoom.temperature <= 65 # temperature is a property on Bedroom that returns a Comparer.
)
async def handle_bedroom_motion(bedroom: BedRoom):
    """Runs only at night when lights are off and room isn't too hot"""
```

## @on_idle [EXPERIMENTAL -- MAY BE ROLLED INTO WHEN]

**Just like `@when`...but the oposite; these handlers will be run once when the conditions have NOT been met for the specified amount of time**

```python
@quickping.on_idle(
    qp.five_minutes, 
    Office.door_motion, 
    UtilityRoom.door_motion,
)
async def no_motion(lights=UtilityRoom.lights):
    """Run if there is no motion for 5 minutes"""
```


## @on_event

**Listen for Home Assistant events with powerful filtering capabilities.  If you want access to the `Event` just ask for it in the function signature of your handler**

```python
# Filter by event type and entity
@qp("sun_set", entity_id="sun.sun")
async def handle_sun_change(
    event: qp.Event, # get the Event 
    living_room: LivingRoom,
):
    """Handle sun state changes"""


# Complex event filtering
@app.on_event(
    "call_service",
    domain="light",
    service="turn_on",
    entity_id=LivingRoom.lights.id
)
async def handle_light_service(
    living_room: LivingRoom,
):
    """Handle specific service calls to living room lights"""

```

## @route [EXPERIMENTAL: I MAY CHANGE THIS UP ENTIRELY]

**Turns any handler into an HTTP endpoint, your handler should return a `dict` or a `tuple[dict, int]`.**

```python
@1p("rooms/lights")
async def toggle_lights(
    request: dict,
    living_room: LivingRoom,
    office: Office,
    bedroom: BedRoom
):
    """Toggle lights in specified room"""
    room_id = request.get("room")
    brightness = request.get("brightness", 100)

    rooms = {
        "living": living_room,
        "office": office,
        "bedroom": bedroom
    }
    
    if room_id not in rooms:
        return {"ok": False}, 404
        

    await rooms[room_id].lights.turn_on(brightness=brightness)

    return {
        "status": "success",
        "room": room_id,
        "brightness": brightness
    }
```
# Comparers
Comparers are heavily influenced by SQLAlchemy's query builder; it allows you to use native python to define very complex filters.  Comparers **use** (or abuse, depending on who you ask...)  python's ["dunder methods"](https://www.geeksforgeeks.org/dunder-magic-methods-python/)...this allows:

```python
@qp.when(
    qp.seven_am < qp.Time < qp.nine_am,
    Weather.temperature >= 80
)
```

Quickping evaluates the equality of your `Comparables` on every statechange; any handler with a **NEWLY** satisfied constraint is run.

By default in `@when` all criteria are combine via a logical and; you can also be more explicit:

```python
@qp.when(
    qp.any(qp.seven_am > qp.Time, qp.Time > qp.nine_am),
    Weather.temperature >= 80,
)
```
# Dependency Injection

Quickping automatically injects requested devices and collections into your functions based on type annotations. This was influenced by fastapi; it's super handy if you want access to a Device or Collection just ask for it in your function signature:

```python
@quickping.on_change(DogRoom.water_level)
async def monitor_water(qp, door: DogRoom.door, room: DogRoom):
    """Handle low water level"""
    if room.water_level.state < 20:
        await door.close()
        await app.notify("Dog water level is low!")

@quickping.route("bedroom/night")
async def night_mode(
    hass,
    request: dict,
    bedroom: BedRoom
):
    """Set bedroom to night mode"""
    await bedroom.main_light.turn_off()
    await bedroom.reading_lamp.set_brightness(20)
    await bedroom.ceiling_fan.set_speed("low")
    return {"status": "success"}
```

# Helpers

## wait
If you need to pause your automation until a state has been satisified it is easy with `wait`:

```python

@qp.when(Light.is_on)
async def doit(light: Light):
    if await qp.wait(10, Light.britghness == 255):
        print("LIGHT IS FULLY ON")
    else:
        print("TIMED OUT WAITING FOR THE LIGHT TO BRIGHTEN UP")
``` 
## Time

### Time Constraints
```python
@when(
    Kitch.light.is_on, 
    qp.seven_am <= qp.Time qp.five_pm
)
def async doit():
    """run when the kitchen light turns on between 7am and 5pm"""
```

### Recurring Tasks
```python
@when(qp.Time.at(qp.seven_am, qp.five_pm))
def async doit():
    """run at 7am and 5pm"""
```

### Repeating Tasks
```python
@when(qp.Time.tick(qp.5_minutes)
def async doit():
    """run every 5 minutes"""
```

# Development Experience

Quickping is designed to provide a professional Python development experience. The library is fully typed and integrated with modern Python tooling:

- **IDE Integration**: Get full autocomplete, type checking, and inline documentation in editors like VS Code, PyCharm, or any other LSP-compatible editor
- **Type Checking**: Catch errors before runtime with `mypy` type checking
- **Code Navigation**: Jump to definitions, find references, and refactor with confidence
- **Rich Documentation**: Get inline documentation for all devices, collections, and system entities
- **Intelligent Autocomplete**:
  - Automatically suggest available devices in collections
  - Show valid states for devices
  - Display parameter hints for service calls
  - Provide autocomplete for event types and properties

For example, when writing:

```python
@app.on_change(LivingRoom.lights)
async def handle_lights(room: LivingRoom):
    # Your IDE will suggest all available properties and methods
    await room.shades.open()  # Type-checked and autocompleted
```

Your editor will:

- Show all available devices in `LivingRoom`
- Provide documentation for each device's capabilities
- Warn about invalid state checks or service calls
- Ensure type safety for all dependencies

This creates a robust development environment that catches errors early and makes working with Home Assistant automations more efficient and reliable.

## Async Requirements

Quickping is built on async Python, and all automation functions must be async. This is enforced by the framework to ensure optimal performance and responsiveness.

```python
# Correct ✅
@app.on_change(LivingRoom.lights)
async def handle_lights(room: LivingRoom):
    await room.shades.open()

# Wrong ❌
@app.on_change(LivingRoom.lights)
def handle_lights(room: LivingRoom):  # Missing async
    room.shades.open()  # Missing await
```

### Important Async Considerations

1. **Never use blocking operations**:

   ```python
   # Wrong ❌ - Will block the event loop
   @app.on_event("motion")
   async def handle_motion():
       time.sleep(5)  # Blocks all automations!
       await lights.turn_off()

   # Correct ✅ - Uses async sleep
   @app.on_event("motion")
   async def handle_motion():
       await asyncio.sleep(5)  # Other automations continue running
       await lights.turn_off()
   ```

2. **All device operations are async**:
   ```python
   # Correct ✅
   async def bedroom_routine(bedroom: BedRoom):
       await bedroom.lights.turn_off()
       await bedroom.shades.close()
       await bedroom.fan.set_speed("low")
   ```

Using synchronous operations like `time.sleep()` will block the entire event loop, preventing other automations from running. Always use `asyncio.sleep()` for delays and ensure all operations that interact with Home Assistant are properly awaited.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
