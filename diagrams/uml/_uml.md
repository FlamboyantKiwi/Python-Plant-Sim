```mermaid
classDiagram
    Group <|-- UIGroup
    AssetGroup <|-- DatabaseGroup
    MovingEntity <|-- Player
    Button <|-- Slot
    UIElement <|-- ShopMenu
    Tile <|-- GroundTile
    UIElement <|-- ProgressBar
    BaseUIState <|-- CharacterSelectState
    SpriteGroup <|-- TileGroup
    NamedTuple <|-- EntityConfig
    ConfigGroup <|-- ColourGroup
    StateElement <|-- Button
    AssetGroup <|-- ConfigGroup
    Group <|-- CameraGroup
    Entity <|-- Plant
    SpriteGroup <|-- FruitGroup
    SpriteGroup <|-- ToolGroup
    BaseWrapper <|-- ImageSwapWrapper
    Entity <|-- MovingEntity
    Tile <|-- WaterTile
    UIElement <|-- StateElement
    Item <|-- SeedItem
    SpriteRect <|-- ScaleRect
    Item <|-- ToolItem
    BaseUIState <|-- SettingsState
    SpriteGroup <|-- EntityGroup
    AssetGroup <|-- FontGroup
    Sprite <|-- Entity
    BaseWrapper <|-- BaseButton
    Button <|-- BaseButton
    BaseWrapper <|-- BaseProgressBar
    ProgressBar <|-- BaseProgressBar
    BaseWrapper <|-- BaseSlot
    Slot <|-- BaseSlot
    BaseWrapper <|-- BaseStateElement
    StateElement <|-- BaseStateElement
    BaseWrapper <|-- BaseTextBox
    TextBox <|-- BaseTextBox
    BaseWrapper <|-- BaseUIElement
    UIElement <|-- BaseUIElement
    BorderWrapper <|-- BorderButton
    Button <|-- BorderButton
    BorderWrapper <|-- BorderProgressBar
    ProgressBar <|-- BorderProgressBar
    BorderWrapper <|-- BorderSlot
    Slot <|-- BorderSlot
    BorderWrapper <|-- BorderStateElement
    StateElement <|-- BorderStateElement
    BorderWrapper <|-- BorderTextBox
    TextBox <|-- BorderTextBox
    BorderWrapper <|-- BorderUIElement
    UIElement <|-- BorderUIElement
    FlashWrapper <|-- FlashButton
    Button <|-- FlashButton
    FlashWrapper <|-- FlashProgressBar
    ProgressBar <|-- FlashProgressBar
    FlashWrapper <|-- FlashSlot
    Slot <|-- FlashSlot
    FlashWrapper <|-- FlashStateElement
    StateElement <|-- FlashStateElement
    FlashWrapper <|-- FlashTextBox
    TextBox <|-- FlashTextBox
    FlashWrapper <|-- FlashUIElement
    UIElement <|-- FlashUIElement
    ImageSwapWrapper <|-- ImageSwapButton
    Button <|-- ImageSwapButton
    ImageSwapWrapper <|-- ImageSwapProgressBar
    ProgressBar <|-- ImageSwapProgressBar
    ImageSwapWrapper <|-- ImageSwapSlot
    Slot <|-- ImageSwapSlot
    ImageSwapWrapper <|-- ImageSwapStateElement
    StateElement <|-- ImageSwapStateElement
    ImageSwapWrapper <|-- ImageSwapTextBox
    TextBox <|-- ImageSwapTextBox
    ImageSwapWrapper <|-- ImageSwapUIElement
    UIElement <|-- ImageSwapUIElement
    ShadowWrapper <|-- ShadowButton
    Button <|-- ShadowButton
    ShadowWrapper <|-- ShadowProgressBar
    ProgressBar <|-- ShadowProgressBar
    ShadowWrapper <|-- ShadowSlot
    Slot <|-- ShadowSlot
    ShadowWrapper <|-- ShadowStateElement
    StateElement <|-- ShadowStateElement
    ShadowWrapper <|-- ShadowTextBox
    TextBox <|-- ShadowTextBox
    ShadowWrapper <|-- ShadowUIElement
    UIElement <|-- ShadowUIElement
    TooltipWrapper <|-- TooltipButton
    Button <|-- TooltipButton
    TooltipWrapper <|-- TooltipProgressBar
    ProgressBar <|-- TooltipProgressBar
    TooltipWrapper <|-- TooltipSlot
    Slot <|-- TooltipSlot
    TooltipWrapper <|-- TooltipStateElement
    StateElement <|-- TooltipStateElement
    TooltipWrapper <|-- TooltipTextBox
    TextBox <|-- TooltipTextBox
    TooltipWrapper <|-- TooltipUIElement
    UIElement <|-- TooltipUIElement
    UIElement <|-- TextBox
    BaseWrapper <|-- TooltipWrapper
    Sprite <|-- Tile
    Item <|-- FoodItem
    SpriteGroup <|-- PlantGroup
    Group <|-- MapTileGroup
    Sprite <|-- UIElement
    BaseUIState <|-- ShopState
    UIElement <|-- InventoryUI
    BaseWrapper <|-- FlashWrapper
    BaseWrapper <|-- ShadowWrapper
    AssetGroup <|-- ImageGroup
    GameState <|-- PlayingState
    BaseUIState <|-- MenuState
    GameState <|-- BaseUIState
    Group <|-- PlantGroup
    AssetGroup <|-- SpriteGroup
    BaseUIState <|-- HUD
    ConfigGroup <|-- TextGroup
    BaseWrapper <|-- BorderWrapper
    StateStack *-- T : contains
    Entity *-- Tile : contains
    TextConfig *-- Colour : contains
    ShopState *-- ShopMenu : contains
    Player *-- InteractionHandler : component
    AssetLoader *-- EntityGroup : contains
    AssetLoader *-- ItemCategory : contains
    PlayingState *-- HUD : contains
    AssetLoader *-- TextGroup : contains
    Tile *-- Level : contains
    InventoryManager *-- InventoryController : component
    PlayingState *-- CameraGroup : contains
    DragController *-- InventoryController : component
    GroundTile *-- Plant : contains
    RectPair *-- SpriteRect : contains
    AnimationGrid *-- SpriteRect : contains
    Tile *-- Entity : contains
    AssetLoader *-- DatabaseGroup : contains
    UIFactory *-- InventoryUI : contains
    PlantData *-- SpriteRect : contains
    Plant *-- PlantData : contains
    InteractionController *-- Direction : contains
    AssetLoader *-- FruitGroup : contains
    PlayingState *-- Level : contains
    MovingEntity *-- Direction : contains
    FlashWrapper *-- Timer : contains
    PlayingState *-- PlantGroup : contains
    PlayingState *-- Player : contains
    UIFactory *-- FlashWrapper : contains
    ShopMenu *-- ShopData : contains
    Player *-- InputController : component
    InventoryController *-- Inventory : contains
    MovingEntity *-- Num : contains
    EntityConfig *-- AnimationGrid : contains
    InventoryManager *-- DragController : component
    InventoryUI *-- Slot : contains
    EntityConfig *-- EntityState : contains
    AssetLoader *-- ImageGroup : contains
    Player *-- PlayerType : contains
    Player *-- AnimationController : component
    Inventory *-- Item : contains
    AssetLoader *-- TileGroup : contains
    SpriteGroup *-- SpriteSheet : contains
    DatabaseGroup *-- DatabaseManager : component
    AssetLoader *-- PlantGroup : contains
    BaseUIState *-- UIElement : contains
    AssetLoader *-- ColourGroup : contains
    Player *-- InteractionController : component
    MovingEntity *-- EntityState : contains
    AssetLoader *-- ToolGroup : contains
    AssetLoader *-- AssetGroup : contains
    Level *-- Tile : contains
    Player *-- CameraGroup : contains
    ShopMenu *-- UIElement : contains
    Level *-- MapTileGroup : contains
    ItemData *-- ItemCategory : contains
    ShopMenu *-- Inventory : contains
    AssetLoader *-- FontGroup : contains
    Slot *-- TextBox : contains
    InventoryUI *-- Inventory : contains
    EntityGroup *-- SpriteSheet : contains
    UIFactory *-- TextBox : contains
    Player *-- InventoryController : component
    BaseUIState *-- UIGroup : contains
    Slot *-- Item : contains
    DragController *-- Item : contains
    ItemData *-- ToolType : contains
    Player *-- InventoryManager : component
    UIFactory *-- Button : contains
    GameState ..> StateID : uses
    class Colour {
        <<EXTERNAL>>
    }
    class Group {
        <<EXTERNAL>>
    }
    class NamedTuple {
        <<EXTERNAL>>
    }
    class Num {
        <<EXTERNAL>>
    }
    class PlayerType {
        <<EXTERNAL>>
    }
    class Sprite {
        <<EXTERNAL>>
    }
    class T {
        <<EXTERNAL>>
    }
    class StateID {
        +CHAR_SELECT
        +HUD
        +MENU
        +PLAYING
        +SETTINGS
        +SHOP
    }
    class EntityState {
        +IDLE
        +RUN
        +WALK
    }
    class Direction {
        +DOWN
        +LEFT
        +RIGHT
        +UP
    }
    class EntityCategory {
        +FARM_ANIMALS
        +NPC
        +PLAYER
    }
    class ItemType {
        +AXE
        +BOW
        +COPPER
        +CROP
        +DAGGER
        +FRUIT
        +GENERIC
        +GOLD
        +HAMMER
        +HOE
        +IRON
        +PICKAXE
        +ROD
        +SCYTHE
        +SEED
        +SHOVEL
        +STAFF
        +STONE
        +SWORD
        +TOOL
        +WATERING_CAN
        +WOOD
        +category
        +use_id
        -__init__()
    }
    class ItemCategory {
        +CROP
        +FRUIT
        +MISC
        +SEED
        +TOOL
    }
    class ToolType {
        +AXE
        +BOW
        +DAGGER
        +GENERIC
        +HAMMER
        +HOE
        +PICKAXE
        +ROD
        +SCYTHE
        +SHOVEL
        +STAFF
        +SWORD
        +WATER
    }
    class Material {
        +COPPER
        +GOLD
        +IRON
        +WOOD
    }
    class Quality {
        +BRONZE
        +GOLD
        +SILVER
    }
    class FontType {
        +HUD
        +SLOT
    }
    class UIGroup {
        +draw()
        +elements()
        +handle_event()
        +update()
    }
    class DatabaseGroup {
        +db
        +missing_ids
        -__init__()
        -_log_missing()
        +clean_up()
        +debug_print()
        +get_item()
        +get_plant()
        +get_shop()
        +load()
    }
    class UIFactory {
        -_create_solid_surf()
        +bordered_slot()
        +bordered_text_button()
        +bubble_text()
        +bubble_text_button()
        +button()
        +color_swap_text_button()
        +create_grid()
        +create_vertical_stack()
        +flashing_text()
        +image_element()
        +inventory_ui()
        +inventory_with_tooltip()
        +progress_bar()
        +slot()
        +solid_element()
        +static_border_element()
        +text()
    }
    class Player {
        +INV_PADDING
        +INV_SIZE
        +SLOT_SIZE
        +animator
        +camera_group
        +image
        +input_controller
        +interaction_handler
        +inventory
        +inventory_manager
        +money
        +player_type
        +targeter
        -__init__()
        +active_item()
        +interact()
        +receive_item()
        +refill_active_watering_can()
        +setup_inventory()
        +update()
    }
    class Slot {
        +index
        +info_text
        +item
        +last_count
        +price
        -__init__()
        -_update_text()
        +draw()
        +set_item()
        +set_price()
        +update()
    }
    class DatabaseManager {
        +conn
        +cursor
        -__init__()
        -_row_to_item()
        -_row_to_plant()
        +close()
        +get_item_data()
        +get_items_by_category()
        +get_plant_data()
        +get_shop_data()
        +insert_record()
        +setup_tables()
    }
    class ShopMenu {
        +background
        +buy_callback
        +inventory_data
        +is_open
        +money_getter
        +shop_data
        +title_box
        +ui_grid
        -__init__()
        +draw()
        +handle_click()
        +is_click()
        +populate_shop()
        +try_buy_item()
        +update()
    }
    class Inventory {
        +items
        +max_size
        -__init__()
        +add_item()
        +get_amount()
        +remove_item()
        +transfer_to()
    }
    class InventoryController {
        +active_slot_index
        +background
        +data
        +rect
        +size
        +slots
        +tooltip
        -__init__()
        +consume_active_item()
        +draw()
        +get_active_item()
        +get_clicked_index()
        +handle_click()
        +handle_event()
        +set_active_slot()
        +update()
    }
    class Log {
        -_debug_enabled
        -_print()
        +divider()
        +error()
        +info()
        +line()
        +set_debug()
        +success()
        +todo()
        +whisper()
    }
    class BaseWrapper {
        +target
        -__getattr__()
        -__init__()
        -__setattr__()
        +draw()
        +update()
    }
    class Level {
        +MAP_HEIGHT
        +MAP_WIDTH
        +all_tiles
        +node_map
        +plant_group
        +player_sprite
        +tile_grid
        -__init__()
        -_get_node_status()
        -_get_tile_assets()
        +draw()
        +generate_level()
        +get_tile()
        +spawn_plant()
        +tile_list()
        +till_map_node()
        +update()
    }
    class MapGenerator {
        +DIRT_NODE
        +GRASS_NODE
        +WATER_NODE
        +draw_blob()
        +generate()
    }
    class DragController {
        +cursor_item
        +drag_origin
        +drag_start_pos
        +is_dragging
        +manager
        -__init__()
        -_handle_mouse_down()
        -_handle_mouse_motion()
        -_handle_mouse_up()
        +draw()
        +handle_event()
    }
    class GroundTile {
        +base_image
        +image
        +is_tilled
        +tillable
        +watered
        -__init__()
        +plant()
        +refresh_terrain()
        +till()
        +water()
    }
    class ItemID {
        +APPLE
        +APPLE_SEEDS
        +BANANA
        +BANANA_SEEDS
        +BEET
        +BEET_SEEDS
        +CABBAGE
        +CABBAGE_SEEDS
        +CAULIFLOWER
        +CAULIFLOWER_SEEDS
        +CHESTNUT_MUSHROOM
        +CHESTNUT_MUSHROOM_SEEDS
        +COCONUT
        +COCONUT_SEEDS
        +COPPER
        +COPPER_ARROW
        +COPPER_AXE
        +COPPER_BOW
        +COPPER_DAGGER
        +COPPER_FISHING_ROD
        +COPPER_HAMMER
        +COPPER_HOE
        +COPPER_PICKAXE
        +COPPER_SCYTHE
        +COPPER_SHOVEL
        +COPPER_STAFF
        +COPPER_SWORD
        +COPPER_WATERING_CAN
        +CORN
        +CORN_SEEDS
        +CUCUMBER
        +CUCUMBER_SEEDS
        +GOLD
        +GOLD_ARROW
        +GOLD_AXE
        +GOLD_BOW
        +GOLD_DAGGER
        +GOLD_FISHING_ROD
        +GOLD_HAMMER
        +GOLD_HOE
        +GOLD_PICKAXE
        +GOLD_SCYTHE
        +GOLD_SHOVEL
        +GOLD_STAFF
        +GOLD_SWORD
        +GOLD_WATERING_CAN
        +GRAPE
        +GRAPE_SEEDS
        +GREEN_BEAN
        +GREEN_BEAN_SEEDS
        +IRON
        +IRON_ARROW
        +IRON_AXE
        +IRON_BOW
        +IRON_DAGGER
        +IRON_FISHING_ROD
        +IRON_HAMMER
        +IRON_HOE
        +IRON_PICKAXE
        +IRON_SCYTHE
        +IRON_SHOVEL
        +IRON_STAFF
        +IRON_SWORD
        +IRON_WATERING_CAN
        +LEMON
        +LEMON_SEEDS
        +MELON
        +MELON_SEEDS
        +MUSHROOM
        +MUSHROOM_SEEDS
        +ONION
        +ONION_SEEDS
        +PINEAPPLE
        +PINEAPPLE_SEEDS
        +PLUM
        +PLUM_SEEDS
        +RED_PEPPER
        +RED_PEPPER_SEEDS
        +SQUASH
        +SQUASH_SEEDS
        +SUNFLOWER
        +SUNFLOWER_SEEDS
        +TOMATO
        +TOMATO_SEEDS
        +WHEAT
        +WHEAT_SEEDS
        +WOOD
        +WOOD_ARROW
        +WOOD_AXE
        +WOOD_BOW
        +WOOD_DAGGER
        +WOOD_FISHING_ROD
        +WOOD_HAMMER
        +WOOD_HOE
        +WOOD_PICKAXE
        +WOOD_SCYTHE
        +WOOD_SHOVEL
        +WOOD_STAFF
        +WOOD_SWORD
        +WOOD_WATERING_CAN
    }
    class ShopID {
        +GENERAL_STORE
    }
    class ProgressBar {
        -_cached_size
        -_fill_surface_base
        +alignment
        +bg_element
        +fill_element
        +is_horizontal
        +percentage
        +value_getter
        -__init__()
        -_update_fill_rect()
        +draw()
        +update()
    }
    class CharacterSelectState {
        +state_id
        -__init__()
        +select_character()
    }
    class TileGroup {
        +build_marching_tile()
        +load()
    }
    class InventoryManager {
        +drag_controller
        +open_controllers
        -__init__()
        +close_inventory()
        +draw_cursor_item()
        +drop_item()
        +find_closest_slot()
        +get_slot_at()
        +handle_event()
        +open_inventory()
        +return_to_origin()
    }
    class EntityConfig {
        +animations
        +frame_size
        +sheets
        +get_animation()
    }
    class ItemData {
        +buy_price
        +category
        +description
        +energy_gain
        +grow_time
        +image_key
        +max_stack
        +name
        +sell_price
        +stackable
        +tool_type
        +calculate_sell_price()
    }
    class PlantData {
        +grow_time
        +harvest_item
        +image_rect
        +image_stages
        +is_tree
        +name
        +regrows
        +get_stage_index()
    }
    class ShopData {
        +items_ids
        +store_name
    }
    class TextConfig {
        +antialias
        +bold
        +colour
        +italic
        +name
        +size
        +render()
    }
    class StateStack {
        -_stack
        -__init__()
        -__len__()
        +change()
        +draw()
        +peek()
        +pop()
        +push()
        +update()
    }
    class ColourGroup {
        +default
        -__init__()
        +get_colour()
        +load()
    }
    class KeyBindings {
        +down
        +facing_map
        +interact
        +left
        +refill
        +right
        +run
        +slots
        +up
        -__init__()
        +direction_keys()
        +rebind()
    }
    class Button {
        +content
        +function
        -__getattr__()
        -__init__()
        +draw()
        +handle_click()
        +is_click()
        +update()
    }
    class ConfigGroup {
        +default
        +missing
        -__init__()
        +debug_print()
        +get_val()
    }
    class CameraGroup {
        +display_surface
        +offset
        -__init__()
        +custom_draw()
        +entities()
    }
    class GameState {
        <<ABSTRACT>>
        +back_button
        +game
        +key_binds
        +mouse_binds
        +state_id
        +suppress_update
        +transparent
        -__init__()
        -__init_subclass__()
        +draw()
        +enter_state()
        +exit_state()
        +handle_event()
        +on_left_click()
        +on_middle_click()
        +on_right_click()
        +update()
    }
    class Plant {
        +age
        +data
        +days_old
        +hitbox
        +hitbox_scale
        +image
        +is_harvested
        +obstructed
        +plant_id
        +rect
        -__init__()
        -_get_current_image()
        +grow()
        +harvest()
        +is_dead()
        +on_interact()
        +till()
        +update_visuals()
    }
    class FruitGroup {
        +cache
        +containers
        +seed_bags
        -__init__()
        -_create_strip()
        -_extract_supplies()
        +get()
        +get_seed()
        +load()
    }
    class ToolGroup {
        +ITEM_SIZE
        +get()
        +load()
    }
    class AnimationController {
        +category
        +current_time
        +frame_index
        +name
        +speed
        -__init__()
        -_get_state_speed()
        +get_frame()
    }
    class ImageSwapWrapper {
        +surf_active
        +surf_hover
        +surf_normal
        -__init__()
        +update()
    }
    class MovingEntity {
        +base_speed
        +current_speed
        +direction
        +facing
        +pos
        +state
        -__init__()
        -_hitbox_collide()
        +check_horizontal()
        +check_vertical()
        +finalize_movement()
        +move()
    }
    class WaterTile {
        -_base_obstructed
        +base_image
        +image
        -__init__()
        +refresh_terrain()
        +water()
    }
    class StateElement {
        +image
        +is_active
        +is_hovered
        -__init__()
        +update()
    }
    class SeedItem {
        +use()
    }
    class SpriteRect {
        +h
        +w
        +x
        +y
    }
    class ScaleRect {
        +tile_h
        +tile_w
    }
    class RectPair {
        +a
        +b
    }
    class AnimationGrid {
        -__init__()
        +non_directional()
    }
    class MarchingLayout {
        +mapping
        +raw_mapping
        -__post_init__()
        +get_variant()
    }
    class InputController {
        +base_speed
        +entity
        +run_multiplier
        -__init__()
        +update()
    }
    class ToolItem {
        +max_water
        +water_level
        -__init__()
        +consume_water()
        +has_water()
        +refill()
        +use()
    }
    class InteractionController {
        +distance
        +entity
        +offsets
        -__init__()
        -_generate_offsets()
        +get_target_objects()
    }
    class SettingsState {
        +panel
        +state_id
        +suppress_update
        -__init__()
    }
    class ItemFactory {
        +create()
    }
    class InteractionHandler {
        +camera_group
        +player
        -__init__()
        +handle_interaction()
    }
    class EntityGroup {
        +get_sprite()
        +load()
    }
    class FontGroup {
        -__init__()
        +debug_print()
        +get_font()
        +load()
    }
    class Entity {
        +hitbox
        +hitbox_offset
        +image
        +rect
        +tile
        -__init__()
        -_calculate_hitbox()
        +draw()
        +on_interact()
        +sync_rect_to_hitbox()
        +till()
    }
    class BaseButton {
    }
    class BaseProgressBar {
    }
    class BaseSlot {
    }
    class BaseStateElement {
    }
    class BaseTextBox {
    }
    class BaseUIElement {
    }
    class BorderButton {
    }
    class BorderProgressBar {
    }
    class BorderSlot {
    }
    class BorderStateElement {
    }
    class BorderTextBox {
    }
    class BorderUIElement {
    }
    class FlashButton {
    }
    class FlashProgressBar {
    }
    class FlashSlot {
    }
    class FlashStateElement {
    }
    class FlashTextBox {
    }
    class FlashUIElement {
    }
    class ImageSwapButton {
    }
    class ImageSwapProgressBar {
    }
    class ImageSwapSlot {
    }
    class ImageSwapStateElement {
    }
    class ImageSwapTextBox {
    }
    class ImageSwapUIElement {
    }
    class ShadowButton {
    }
    class ShadowProgressBar {
    }
    class ShadowSlot {
    }
    class ShadowStateElement {
    }
    class ShadowTextBox {
    }
    class ShadowUIElement {
    }
    class TooltipButton {
    }
    class TooltipProgressBar {
    }
    class TooltipSlot {
    }
    class TooltipStateElement {
    }
    class TooltipTextBox {
    }
    class TooltipUIElement {
    }
    class Item {
        +count
        +data
        +image
        +item_id
        +max_water
        +water_level
        -__getattr__()
        -__init__()
        +add_to_stack()
        +copy_one()
        +max_stack()
        +remove_from_stack()
        +use()
    }
    class TextBox {
        -_text
        +align
        +config
        +is_visible
        +text_getter
        +text_rect
        +text_surf
        -__init__()
        -_render_text()
        +draw()
        +set_text()
        +update()
    }
    class TooltipWrapper {
        +offset
        +tooltip
        -__init__()
        +draw()
        +update()
    }
    class Tile {
        -_base_obstructed
        +detail_image
        +grid_x
        +grid_y
        +image
        +is_tilled
        +level
        +occupant
        +position
        +rect
        +tile_type_key
        +tillable
        +watered
        -__init__()
        +add_occupant()
        +plant()
        +refresh_terrain()
        +till()
        +water()
    }
    class FoodItem {
        +use()
    }
    class PlantGroup {
        -__init__()
        +add()
        +get_plant_at_grid()
        +grow_all()
        +plants()
    }
    class MapTileGroup {
        +display_surface
        -__init__()
        +custom_draw()
    }
    class UIElement {
        +image
        +is_visible
        +rect
        -__init__()
        +copy_image()
        +draw()
        +handle_click()
        +is_click()
        +update()
    }
    class ShopState {
        +panel
        +player
        +shop_menu
        +state_id
        -__init__()
        -_handle_purchase()
        +on_right_click()
    }
    class InventoryUI {
        +data
        +slots
        +tooltip
        -__init__()
        +click()
        +draw()
        +is_click()
        +update()
    }
    class FlashWrapper {
        +flash_timer
        +interval
        +is_blank
        +is_flashing
        -__init__()
        +draw()
        +start_flash()
        +stop_flash()
        +update()
    }
    class ShadowWrapper {
        -_last_getter_text
        +cached_shadow_surf
        +offset
        +shadow_config_data
        -__init__()
        -_render_shadow()
        +draw()
        +set_text()
        +update()
    }
    class Animal {
        +pos
        +type
        -__init__()
    }
    class ImageGroup {
        +failures
        -__init__()
        +debug_print()
        +generate_fallback()
        +get_image()
        +load()
    }
    class AssetLoader {
        -_image_routers
        +colours
        +database
        +entities
        +fonts
        +fruits
        +groups
        +images
        +plants
        +text
        +tiles
        +tools
        -__init__()
        -_get_fallback_image()
        +autotile()
        +clean_up()
        +colour()
        +config()
        +debug_assets()
        +font()
        +get_image()
        +get_image_path()
        +item()
        +item_image()
        +load_all()
        +load_image()
        +load_raw_image()
        +plant()
        +shop()
        +sprite()
    }
    class AssetGroup {
        <<ABSTRACT>>
        +manager
        +raw_data
        +storage
        -__init__()
        +clean_up()
        +debug_print()
        +load()
        +print_line_break()
    }
    class SpriteSheet {
        +name
        +path
        +sheet
        -__init__()
        +extract_tiles_by_dimensions()
        +get_image()
    }
    class Timer {
        +active
        +duration
        +paused
        +start_time
        +time_left
        -__init__()
        +progress()
        +start()
        +toggle_pause()
        +update()
    }
    class PlayingState {
        +all_sprites
        +hud
        +key_binds
        +level
        +plant_group
        +player
        +state_id
        +suppress_update
        +transparent
        -__init__()
        +draw()
        +handle_event()
        +on_left_click()
        +on_right_click()
        +open_shop()
        +update()
    }
    class MenuState {
        +menu_actions
        +state_id
        +suppress_update
        -__init__()
    }
    class BaseUIState {
        +back_button
        +background
        +click_exit
        +colour
        +draw_bg
        +panel
        +suppress_update
        +transparent
        +ui_group
        -__init__()
        +add_back_button()
        +draw()
        +handle_event()
        +on_left_click()
        +update()
    }
    class PlantFactory {
        +create()
    }
    class SpriteGroup {
        +SCALE_FACTOR
        +TILE_SIZE
        +loaded_sheets
        +sheet_files
        -__init__()
        -_get_tight_strip()
        -_iter_rows()
        +debug_print()
        +get_sheet()
    }
    class HUD {
        +player
        +state_id
        +suppress_update
        +transparent
        -__init__()
        +draw()
        +escape()
        +handle_event()
        +open_settings()
        +player_open_shop()
        +update()
    }
    class TextGroup {
        +default
        +get_config()
        +load()
    }
    class BorderWrapper {
        +surf_active
        +surf_hover
        +surf_normal
        -__init__()
        -_create_border_surf()
        +draw()
    }
```