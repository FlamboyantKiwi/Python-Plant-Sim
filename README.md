# Python Plant Sim 🌱

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)

A robust, data-driven 2D farming and exploration game built entirely from scratch in Python using the Pygame library. 

Rather than relying on hardcoded game loops, this project was developed as a technical sandbox to implement advanced software engineering concepts, including procedural map generation, SQLite database integration, custom UI component factories, and a strict State Machine architecture.

## 🎮 Gameplay Features
* **Dynamic Farming:** Till soil, plant seeds, water crops, and harvest produce based on real-time database growth stages.
* **Interactive Hotbar:** fully functional drag-and-drop inventory system that supports item stacking, splitting, and swapping.
* **In-Game Economy:** Buy and sell items through a dynamic shop interface synchronized with the player's wallet.
* **Procedural Environments:** Explore uniquely generated maps on every load.

## 🚀 Core Systems & Architecture

### 🗄️ Data-Driven Item & Plant System (SQLite)
Game data is entirely decoupled from the codebase. Items, plants, and shops are stored in a relational `gamedata.db` SQLite database.
* **Smart Proxying:** Python `dataclasses` (e.g., `ItemData`, `PlantData`) act as proxies, fetching attributes like `buy_price`, `max_stack`, and `energy_gain` dynamically.
* **Auto-Generated Enums:** Includes a custom build tool (`tools/generate_enums.py`) that reads the database tables and asset folders to automatically generate strict Python `Enums`, ensuring complete type safety across the codebase and preventing missing-key crashes.

### 🗺️ Procedural Terrain (Marching Squares)
The environment uses a dynamic Node Map that calculates terrain borders on the fly.
* Utilizes a **9-node neighborhood check** (Marching Squares algorithm) to perfectly blend grass, tilled soil, and water textures (`world.level` and `world.tile`).
* Automatically resolves corner cases, diagonals, and inner corners for seamless organic environments.

### 📦 Robust Asset Pipeline & Caching
Assets are managed by a centralized `AssetLoader` to optimize memory and prevent disk-read bottlenecks.
* **Smart Caching:** Sprite sheets, fonts, and individual images are loaded into memory exactly once.
* **Dynamic Fallbacks:** If a texture or file is missing, the engine catches the error and generates a visible "fallback" texture (e.g., a colored bounding box or a "Glitch Item") at runtime, preventing hard crashes.

### 🖼️ Advanced UI Framework & Wrappers
A custom, modular UI generation system built from the ground up (`ui.ui_factory`).
* **Composition over Inheritance:** UI elements use dynamic Wrappers (`BorderWrapper`, `ShadowWrapper`, `Tooltip`, `FlashWrapper`) to add behaviors to standard buttons and slots without duplicating classes.
* **Stateful Drag-and-Drop:** A fully realized `InventoryManager` handles logic, item stacking, and data-layer synchronization completely independently of visual rendering.

### ⚙️ State Machine & Entity Components
* **State Stack Pattern:** The game loop is governed by a `StateStack` (`core/states/base.py`) which allows for seamless layering. Menus, HUD, Shops, and Gameplay can pause, suppress, or draw over one another flawlessly.
* **Component-Based Entities:** Entity logic is split into modular components (`AnimationController`, `InteractionController`, `InventoryController`) to avoid deep, messy inheritance trees.
* **Decoupled Physics:** Custom collision detection uses axis-separated resolution and dedicated hitboxes that are independent of the sprite's visual bounds.

## 📂 Project Structure
```text
Python-Plant-Sim/
├── main.py                 # Main entry point and game loop
├── settings.py             # Global configurations and constants
├── Assets/                 # Spritesheets, fonts, and SQLite database
├── core/                   # Engine internals
│   ├── assets/             # Asset loading, caching, and fallback logic
│   ├── states/             # State Machine (Menu, Playing, HUD, Shop)
│   ├── database.py         # SQLite connection and query manager
│   └── controls.py         # Dynamic keybindings
├── entities/               # Game objects (Player, Plants, Animals, Items)
│   └── components/         # Modular logic (Animation, Interaction, Inventory)
├── groups/                 # Pygame sprite groups (Y-Sorting Camera, UI routing)
├── ui/                     # Component-based UI framework and wrappers
├── world/                  # Procedural level generation and tile logic
└── tools/                  # Developer scripts for auto-generating code
```

### ⌨️ Controls
* W, A, S, D or Arrow Keys: Move character
* Left Shift: Sprint
* Spacebar: Interact / Use Item (Tills soil, plants seeds, etc.)
* 1 - 8: Select Inventory Hotbar Slot
* P: Open Shop Menu
* ESC: Close Menus / Back
* Mouse: Click and drag to move inventory items, click UI buttons.

## 🛠️ Getting Started

### Prerequisites
You only need Python 3 installed. The only external dependency is Pygame.

```bash
pip install pygame
```

### Running the Game

1. Clone the repository:
```bash
git clone https://github.com/FlamboyantKiwi/Python-Plant-Sim.git
```
2. Navigate to the directory:
```bash
cd Python-Plant-Sim
```
3. Run the main executable:
```bash
python main.py
```

## 🔮 Future Roadmap

**Systems & Architecture**
* *Introduce save-state functionality via SQLite serialization.*
* **Settings & Customization Menu:** Implement a fully interactive settings UI to manage master volume, audio sliders, and custom keybinding/rebind options.
* *Entity Component Refactoring:* Finalize decoupling the main Player class into smaller, highly reusable ECS-style components.
* *Asset Pipeline & Growth Overhaul:* Restructure plant sprites into individual images or a unified grid layout to resolve growth stage ordering bugs and streamline rendering logic.
* *Crafting Architecture:* Build a data-driven crafting and recipe system utilizing the existing SQLite database structure.
* *Audio Engine:* Integrate a centralized audio manager for background music fading and spatial sound effects.
* *Gamepad Support:* Expand the `controls.py` module to dynamically map and support controllers alongside keyboard inputs.

**Gameplay & Entities**
* *Resource Generation & Harvesting:* Spawn interactable trees, boulders, and ore veins (copper, iron, gold) that players can break down for raw materials.
* *Shipping & Monetization:* Introduce a shipping bin or direct-sell merchant mechanic to convert harvested crops and crafted goods into currency.
* *Implement A\* Pathfinding for NPC and Farm Animal behavior.*
* *Livestock Integration:* Activate the existing farm animal framework and assets (Bull, Calf, Chick, Lamb, Piglet, Rooster, Sheep, Turkey) with dedicated AI state machines.
* *Expanded Tool Interactions:* Implement distinct mechanics and targeted hitboxes for gathering and combat tools (Sword, Bow & Arrow, Dagger, Fishing Rod, Hammer, Pickaxe, Scythe, Shovel, Staff, Watering Can).
* *Dynamic Economy:* Update the general store to feature all seed types and implement a rotating daily stock system.
* *Skill Progression:* Implement an RPG-style leveling system for activities like Farming, Mining, and Combat to unlock new crafting recipes and increase efficiency.
* *Farm Automation:* Allow players to craft mid-to-late game items like sprinklers and auto-feeders to scale up their agricultural output.

**World & Environment**
* *Day/Night Cycle:* Introduce an ambient lighting system and time-based environmental states.
* *Seasonal Cycles:* Create dynamic seasons that alter the visual palette, change weather patterns, and dictate which crops can be successfully grown.
* *Advanced Terrain:* Add new procedural tile types, expanded biomes, and unique map generation noise.

**Exploration & Survival**
* *Procedural Dungeons:* Generate endless, randomized cave systems and dungeon levels for deeper exploration.
* *Survival Mechanics:* Implement comprehensive Health and Stamina systems to manage player energy and gate continuous actions.
* *Hostile Mobs:* Introduce monster encounters and combat states specifically within the cave and dungeon environments.
* *Death & Respawn:* Create penalty mechanics and a respawn system tied to the new health and combat loops.

---
*Created by [Freddy Edmunds](https://github.com/FlamboyantKiwi) — View my full portfolio at [freddyedmunds.co.uk](https://freddyedmunds.co.uk).*

