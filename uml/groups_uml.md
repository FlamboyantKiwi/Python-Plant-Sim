```mermaid
classDiagram
    Group <|-- CameraGroup
    Group <|-- MapTileGroup
    Group <|-- PlantGroup
    Group <|-- UIGroup
    class Group {
        <<EXTERNAL>>
    }
    class CameraGroup {
        +display_surface
        +offset
        -__init__()
        +custom_draw()
        +entities()
    }
    class MapTileGroup {
        +display_surface
        -__init__()
        +custom_draw()
    }
    class PlantGroup {
        -__init__()
        +add()
        +get_plant_at_grid()
        +grow_all()
        +plants()
    }
    class UIGroup {
        +draw()
        +elements()
        +handle_event()
        +update()
    }
```