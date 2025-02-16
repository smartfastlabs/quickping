## WIP

_THIS IS VERSION 0.0.0 AND WILL CONTINUE TO CHANGE AND EVOLVE._

# Quickping

A modern, type-safe Python library for creating Home Assistant automations using native async Python and decorators. Heavily influenced by AppDaemon and pyscript, Quickping combines the best of both worlds: AppDaemon's reliable runtime model with pyscript's decorator paradigm, while adding types, dependency injection, and other python niceties.

## Features

- Modern python development environment, with native async/await support.
- Full type hints for enhanced development experience, linting, and error catching
- Decorator-based API with dependency injection for intuitive and clean automation scripts
- Seamless integration with Home Assistant's event system
- Zero configuration needed - works directly with AppDaemon

## Installation

Install through the appdaemon addon in homeassistant.

## Quick Start

```python
from quickping import AppDaemonApp, Collection, Device


# Define your rooms and devices
class LivingRoom(Collection):
    lights = Device("light.living_room_table_lamp")
    shades = Device("cover.living_room")
    fan = Device("fan.living_room")

class Office(Collection):
    desk_lamp = Device("light.office_desk")
    computer = Device("switch.computer")
    ac = Device("climate.office")

app = HomeAssistant()

# Use dependency injection to access devices
@app.on_change(LivingRoom.lights)
async def handle_living_room_lights(shades: LivingRoom.shades, room: LivingRoom):
    """Automatically manage shades based on light state"""
    if room.lights.state == "on" and room.shades.state == "closed":
        await shades.open()
    elif room.lights.state == "off" and room.shades.state == "open":
        await shades.close()

# Access multiple collections
@app.on_event("sunset")
async def evening_routine(living_room: LivingRoom, office: Office):
    """Evening routine across multiple rooms"""
    await living_room.lights.turn_on()
    await office.desk_lamp.turn_on(brightness=50)
```

## Collections and Devices

Collections and Devices are the core building blocks of Quickping. They provide a type-safe way to organize and interact with your home automation entities. Collections can contain both devices and other collections, allowing you to create intuitive hierarchical structures.

### Defining Collections and Devices

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

@quickping.on_change(House.doorbell)
async def handle_doorbell(
    living_room: LivingRoom,
):
    await living_room.light.turn_on()
```

### Dependency Injection

Quickping automatically injects requested devices and collections into your functions based on type annotations. This was influenced by fastapi; it's super handy if you want access to a Device or Collection just ask for it in your function signature:

```python
@quickping.on_change(DogRoom.water_level)
async def monitor_water(door: DogRoom.door, room: DogRoom):
    """Handle low water level"""
    if room.water_level.state < 20:
        await door.close()
        await app.notify("Dog water level is low!")

@quickping.route("bedroom/night")
async def night_mode(
    request: dict,
    bedroom: BedRoom
):
    """Set bedroom to night mode"""
    await bedroom.main_light.turn_off()
    await bedroom.reading_lamp.set_brightness(20)
    await bedroom.ceiling_fan.set_speed("low")
    return {"status": "success"}
```

## Core Decorators

### @on_event

Listen for Home Assistant events with powerful filtering capabilities.

```python
# Filter by event type and entity
@quickping.on_event("sun_set", entity_id="sun.sun")
async def handle_sun_change(event: Change, living_room: LivingRoom):
    """Handle sun state changes"""
    if event.new == "below_horizon":
        await living_room.lights.turn_on()


# Complex event filtering
@app.on_event(
    "call_service",
    domain="light",
    service="turn_on",
    entity_id=LivingRoom.lights.id
)
async def handle_light_service(event: Change, living_room: LivingRoom):
    """Handle specific service calls to living room lights"""
    await living_room.shades.open()
```

### @on_change

Monitor specific entity state changes with strongly-typed state values.

```python
@app.on_change(Office.computer)
async def handle_computer(ac: Office.ac, desk_lamp: Office.desk_lamp):
    """React to computer state changes"""
    if computer.state == "on":
        await ac.turn_on()
        await desk_lamp.turn_on()
```

### @route

Create HTTP endpoints to interact with your automations. The route decorator handles error cases and status codes automatically.

```python
@app.route("rooms/lights")
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

    room = rooms[room_id]  # Decorator handles KeyError
    await room.lights.turn_on(brightness=brightness)

    return {
        "status": "success",
        "room": room_id,
        "brightness": brightness
    }

@app.route("temperature")
async def get_temperature(
    request: dict,
    clock: Clock,
    weather: Weather,
    temp_sensor: LivingRoom.temperature
):
    units = request.get("units", "celsius")
    include_forecast = request.get("forecast", False)

    response = {
        "room_temperature": temp_sensor.state,
        "outdoor_temperature": weather.temperature,
        "humidity": weather.humidity,
        "timestamp": clock.now,
        "is_daytime": clock.is_daytime,
        "units": units
    }

    if include_forecast:
        response["forecast"] = weather.get_forecast()

    return response
```

## State Conditions

```python
from quickping.conditions import when
from quickping.entities import Sun

@app.on_event("sunset")
@when(
    LivingRoom.lights.is_("on"),
    LivingRoom.shades.is_("open"),
)
async def handle_sundown():
    """Runs only when living room lights are on, shades are open, and sun sets"""
    await LivingRoom.shades.close()

@app.on_change(BedRoom.motion)
@when(
    BedRoom.lights.is_("off"),
    Sun.is_("down"),
    BedRoom.temperature.less_than(65)
)
async def handle_bedroom_motion(bedroom: BedRoom):
    """Runs only at night when lights are off and room isn't too hot"""
    await bedroom.lights.turn_on(brightness=30)
```

## Development Experience

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
