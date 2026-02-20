import copy
import math


def ceil(x):
    """Ceiling function"""
    return math.ceil(x)


def calculate_materials(inputs):
    """Calculate detailed material quantities based on structural inputs (Imperial Units).

    Uses a set of Indian-standards-inspired defaults (typical IS practice values):
    - Cement bag = 50 kg
    - Concrete density = 2400 kg/m3
    - Cement content per m3 for nominal mixes (M20/M25/M30)
    - Typical steel consumption ranges (kg per m3) by element

    These are configurable via the `STANDARDS` dict below.
    """

    # Conversion factors
    FT_TO_M = 0.3048
    INCH_TO_M = 0.0254
    SQFT_TO_SQM = 0.092903

    # Indian-standards inspired defaults (can be tuned per project)
    STANDARDS = {
        'cement_bag_kg': 50,
        'concrete_density_kg_m3': 2400,
        'cement_bulk_density_kg_m3': 1440,  # bulk density used for cement mass <-> volume
        'sand_bulk_density_kg_m3': 1600,
        'aggregate_bulk_density_kg_m3': 1500,
        # Typical cement content (kg per m3 concrete) for nominal mixes
        'cement_content_per_m3': {
            'm20': 320,
            'm25': 360,
            'm30': 400
        },
        # Volumetric nominal mix ratios (cement : sand : aggregate)
        'mix_ratios': {
            'm20': (1.0, 1.5, 3.0),
            'm25': (1.0, 1.0, 2.0),
            'm30': (1.0, 0.75, 1.5)
        },
        # Typical steel consumption (kg per m3) by element (rule-of-thumb ranges per IS practice)
        'steel_usage_kg_per_m3': {
            'footing': 90,
            'column': 130,
            'beam': 120,
            'slab': 100
        },
        'steel_density_kg_m3': 7850,
        # Paint coverage (sq.m per litre per coat) - commonly 10-12; use 10 as conservative value
        'paint_coverage_m2_per_litre': 10
    }

    materials = {
        'concrete': {},
        'cement': {},
        'sand': {},
        'aggregate': {},
        'steel': {},
        'masonry': {},
        'finishing': {}
    }
    
    # Parse inputs and convert to metric
    num_floors = int(inputs['num_floors'])
    structure_type = inputs['structure_type']
    
    # ============ CONCRETE CALCULATIONS ============
    # Foundation (Footing + PCC)
    num_footings = int(inputs['num_footings'])
    footing_length = float(inputs['footing_length']) * FT_TO_M
    footing_width = float(inputs['footing_width']) * FT_TO_M
    footing_depth = float(inputs['footing_depth']) * FT_TO_M
    pcc_thickness = float(inputs['pcc_thickness']) * INCH_TO_M
    
    footing_vol = num_footings * footing_length * footing_width * footing_depth
    pcc_vol = num_footings * footing_length * footing_width * pcc_thickness
    
    # RCC Columns
    num_columns = int(inputs['num_columns'])
    column_length = float(inputs['column_length']) * INCH_TO_M
    column_width = float(inputs['column_width']) * INCH_TO_M
    column_height = float(inputs['column_height']) * FT_TO_M
    
    column_vol = num_columns * num_floors * column_length * column_width * column_height
    
    # RCC Beams
    total_beam_length = float(inputs['total_beam_length']) * FT_TO_M
    beam_width = float(inputs['beam_width']) * INCH_TO_M
    beam_depth = float(inputs['beam_depth']) * INCH_TO_M
    
    beam_vol = total_beam_length * beam_width * beam_depth * num_floors
    
    # RCC Slabs
    slab_area = float(inputs['slab_area']) * SQFT_TO_SQM
    slab_thickness = float(inputs['slab_thickness']) * INCH_TO_M
    
    slab_vol = slab_area * slab_thickness * num_floors
    
    materials['concrete']['pcc_volume'] = round(pcc_vol, 2)
    materials['concrete']['footing_rcc'] = round(footing_vol, 2)
    materials['concrete']['column_rcc'] = round(column_vol, 2)
    materials['concrete']['beam_rcc'] = round(beam_vol, 2)
    materials['concrete']['slab_rcc'] = round(slab_vol, 2)
    materials['concrete']['total_rcc'] = round(footing_vol + column_vol + beam_vol + slab_vol, 2)
    
    # ============ CEMENT & MIX CALCULATIONS ============
    concrete_grade = inputs.get('concrete_grade', 'm20').lower()

    total_concrete = materials['concrete']['pcc_volume'] + materials['concrete']['total_rcc']  # in m³

    # Use standardized cement content per m³ for nominal mixes (kg/m³) where available
    cement_content_map = STANDARDS['cement_content_per_m3']
    cement_kg_per_m3 = cement_content_map.get(concrete_grade, cement_content_map['m20'])
    cement_for_concrete_kg = total_concrete * cement_kg_per_m3
    cement_bags_concrete = ceil(cement_for_concrete_kg / STANDARDS['cement_bag_kg'])

    # Derive sand & aggregate quantities using volumetric nominal mix ratios
    mix_ratios = STANDARDS['mix_ratios'].get(concrete_grade, STANDARDS['mix_ratios']['m20'])
    cement_part, sand_part, agg_part = mix_ratios
    total_parts = cement_part + sand_part + agg_part

    # Volumes of constituents (approximate, assumes no major void adjustments)
    # cement_volume_from_nominal = (cement_part / total_parts) * total_concrete
    sand_vol = (sand_part / total_parts) * total_concrete
    agg_vol = (agg_part / total_parts) * total_concrete

    sand_mass_kg = sand_vol * STANDARDS['sand_bulk_density_kg_m3']
    agg_mass_kg = agg_vol * STANDARDS['aggregate_bulk_density_kg_m3']
    
    # ============ MORTAR & PLASTER (BRICKWORK) ============
    mortar_mix = inputs.get('mortar_mix', '1:6')
    mortar_ratio = {'1:6': (1.0, 6.0), '1:4': (1.0, 4.0), '1:3': (1.0, 3.0)}

    # Wall calculations
    external_wall_length = float(inputs['external_wall_length']) * FT_TO_M
    internal_wall_length = float(inputs['internal_wall_length']) * FT_TO_M
    total_wall_length = (external_wall_length + internal_wall_length) * num_floors
    wall_thickness = float(inputs['wall_thickness']) * INCH_TO_M
    wall_height = float(inputs['wall_height']) * FT_TO_M
    
    wall_volume = total_wall_length * wall_thickness * wall_height
    
    # Mortar requirement (approx. 10% of wall volume for joints and bedding)
    mortar_volume = wall_volume * 0.10
    mortar_parts = mortar_ratio.get(mortar_mix, mortar_ratio['1:6'])
    mortar_total_parts = mortar_parts[0] + mortar_parts[1]
    cement_for_mortar_kg = mortar_volume * (mortar_parts[0] / mortar_total_parts) * STANDARDS['cement_bulk_density_kg_m3']

    
    # Plaster cement
    internal_plaster_thickness = float(inputs['internal_plaster_thickness']) * INCH_TO_M
    external_plaster_thickness = float(inputs['external_plaster_thickness']) * INCH_TO_M
    plaster_area_internal = total_wall_length * wall_height * 0.8  # 80% internal
    plaster_area_external = external_wall_length * num_floors * wall_height
    
    plaster_vol_internal = plaster_area_internal * internal_plaster_thickness
    plaster_vol_external = plaster_area_external * external_plaster_thickness
    total_plaster_vol = plaster_vol_internal + plaster_vol_external
    
    # Plaster assumed 1:3 (cement : sand) by parts unless specified; compute cement mass
    plaster_cement_part = 1.0
    plaster_sand_part = 3.0
    plaster_total_parts = plaster_cement_part + plaster_sand_part
    cement_for_plaster_kg = total_plaster_vol * (plaster_cement_part / plaster_total_parts) * STANDARDS['cement_bulk_density_kg_m3']

    # Totals (cement in bags)
    cement_for_mortar_bags = ceil(cement_for_mortar_kg / STANDARDS['cement_bag_kg'])
    cement_for_plaster_bags = ceil(cement_for_plaster_kg / STANDARDS['cement_bag_kg'])

    materials['cement']['for_concrete'] = round(cement_bags_concrete, 0)
    materials['cement']['for_mortarbrickwork'] = round(cement_for_mortar_bags, 0)
    materials['cement']['for_plaster'] = round(cement_for_plaster_bags, 0)
    materials['cement']['total_bags'] = round(materials['cement']['for_concrete'] + materials['cement']['for_mortarbrickwork'] + materials['cement']['for_plaster'], 0)
    
    # ============ SAND CALCULATIONS ============
    # Use sand_vol and convert to m³ mass where needed
    materials['sand']['concrete_sand_m3'] = round(sand_vol, 3)
    materials['sand']['concrete_sand_kg'] = round(sand_mass_kg, 1)

    # Mortar sand (m³ and kg)
    mortar_sand_vol = mortar_volume * (mortar_parts[1] / mortar_total_parts)
    mortar_sand_kg = mortar_sand_vol * STANDARDS['sand_bulk_density_kg_m3']
    materials['sand']['brickwork_sand_m3'] = round(mortar_sand_vol, 3)
    materials['sand']['brickwork_sand_kg'] = round(mortar_sand_kg, 1)

    # Plaster sand
    plaster_sand_vol = total_plaster_vol * (plaster_sand_part / plaster_total_parts)
    plaster_sand_kg = plaster_sand_vol * STANDARDS['sand_bulk_density_kg_m3']
    materials['sand']['plaster_sand_m3'] = round(plaster_sand_vol, 3)
    materials['sand']['plaster_sand_kg'] = round(plaster_sand_kg, 1)

    materials['sand']['total_sand_kg'] = round(sand_mass_kg + mortar_sand_kg + plaster_sand_kg, 1)
    
    # ============ AGGREGATE CALCULATIONS ============
    materials['aggregate']['concrete_aggregate_m3'] = round(agg_vol, 3)
    materials['aggregate']['concrete_aggregate_kg'] = round(agg_mass_kg, 1)
    materials['aggregate']['total_aggregate_kg'] = round(agg_mass_kg, 1)
    
    # ============ STEEL CALCULATIONS (IS-based typical values) ============
    su = STANDARDS['steel_usage_kg_per_m3']
    steel_for_footing = footing_vol * su['footing']
    steel_for_column = column_vol * su['column']
    steel_for_beam = beam_vol * su['beam']
    steel_for_slab = slab_vol * su['slab']

    materials['steel']['footing_steel_kg'] = round(steel_for_footing, 1)
    materials['steel']['column_steel_kg'] = round(steel_for_column, 1)
    materials['steel']['beam_steel_kg'] = round(steel_for_beam, 1)
    materials['steel']['slab_steel_kg'] = round(steel_for_slab, 1)
    materials['steel']['total_steel_kg'] = round(steel_for_footing + steel_for_column + steel_for_beam + steel_for_slab, 1)
    
    # ============ MASONRY CALCULATIONS ============
    # Default brick size (m): 0.230 x 0.115 x 0.075 (common) - user may override via inputs
    brick_size = float(inputs.get('brick_length_m', 0.230)) * float(inputs.get('brick_width_m', 0.115)) * float(inputs.get('brick_height_m', 0.075))
    bricks_per_m3 = 1.0 / brick_size if brick_size > 0 else 0

    bricks_required = wall_volume * bricks_per_m3

    materials['masonry']['brick_quantity'] = round(bricks_required, 0)
    materials['masonry']['mortar_volume_m3'] = round(mortar_volume, 3)
    
    # ============ FINISHING CALCULATIONS ============
    flooring_area_sqft = float(inputs.get('flooring_area', 0.0))
    tile_size_inch = int(inputs.get('tile_size', 12))
    tile_area_sqft = ((tile_size_inch / 12.0) ** 2)
    tiles_required = (flooring_area_sqft / tile_area_sqft) if tile_area_sqft > 0 else 0
    tiles_with_waste = tiles_required * 1.05  # 5% waste

    # Paint: convert plaster areas (m²) and use standard coverage
    # plaster_area_internal and external were computed in m (wall lengths * height) earlier
    paint_area_m2 = (plaster_area_internal + plaster_area_external)  # already in m²
    paint_coats = int(inputs.get('paint_coats', 2))
    coverage = STANDARDS['paint_coverage_m2_per_litre']
    paint_required_l = (paint_area_m2 * paint_coats) / coverage

    materials['finishing']['floor_tiles_qty'] = round(tiles_with_waste, 0)
    materials['finishing']['paint_liters'] = round(paint_required_l, 2)
    materials['finishing']['plaster_volume_m3'] = round(total_plaster_vol, 3)
    # Expose flooring and tile area for cost calculations
    materials['finishing']['flooring_area_sqft'] = round(flooring_area_sqft, 2)
    materials['finishing']['flooring_area_m2'] = round(flooring_area_sqft * SQFT_TO_SQM, 3)
    materials['finishing']['tile_area_m2'] = round(tile_area_sqft * SQFT_TO_SQM, 4)
    
    return materials


def generate_plan_variants(materials, plan_type='standard'):
    """Generate materials and cost for different plan types (economy, standard, or premium)

    Args:
        materials: Base materials dictionary
        plan_type: 'economy', 'standard', or 'premium'

    Returns:
        Modified materials dictionary with plan-specific adjustments
    """
    adjusted_materials = copy.deepcopy(materials)

    if plan_type == 'economy':
        # Economy plan: increase material quantities by 8% (lower efficiency, less quality control)
        # Use basic materials to minimize cost
        adjustment_factor = 1.08

    elif plan_type == 'premium':
        # Premium plan: reduce material quantities by 5% (higher efficiency)
        # and use better quality which results in less waste
        adjustment_factor = 0.95
    else:
        # Standard plan: no adjustment to quantities
        adjustment_factor = 1.0

    if adjustment_factor != 1.0:
        # Adjust concrete components
        if 'concrete' in adjusted_materials:
            for key in adjusted_materials['concrete']:
                if isinstance(adjusted_materials['concrete'][key], (int, float)):
                    adjusted_materials['concrete'][key] = round(adjusted_materials['concrete'][key] * adjustment_factor, 2)

        # Adjust cement
        if 'cement' in adjusted_materials:
            for key in adjusted_materials['cement']:
                if isinstance(adjusted_materials['cement'][key], (int, float)):
                    adjusted_materials['cement'][key] = round(adjusted_materials['cement'][key] * adjustment_factor, 0)

        # Adjust other materials
        for section in ['sand', 'aggregate', 'steel']:
            if section in adjusted_materials:
                for key in adjusted_materials[section]:
                    if isinstance(adjusted_materials[section][key], (int, float)):
                        adjusted_materials[section][key] = round(adjusted_materials[section][key] * adjustment_factor, 1)

        # Adjust masonry
        if 'masonry' in adjusted_materials:
            if 'brick_quantity' in adjusted_materials['masonry']:
                adjusted_materials['masonry']['brick_quantity'] = round(
                    adjusted_materials['masonry']['brick_quantity'] * adjustment_factor, 0
                )

        # Adjust finishing
        if 'finishing' in adjusted_materials:
            if 'floor_tiles_qty' in adjusted_materials['finishing']:
                adjusted_materials['finishing']['floor_tiles_qty'] = round(
                    adjusted_materials['finishing']['floor_tiles_qty'] * adjustment_factor, 0
                )

    return adjusted_materials


def calculate_cost(materials, plan_type='standard', custom_rates=None):
    """Calculate total cost based on material quantities and rates.

    Args:
        materials: Dictionary of material quantities
        plan_type: 'economy', 'standard', or 'premium'
        custom_rates: Optional dictionary with custom rates (loaded from Excel).
                     If provided, these override default rates and plan adjustments.
    """
    # Default rates (fallback if no custom rates provided)
    default_rates = {
        'cement_per_bag': 420.0,      # INR per 50kg bag
        'sand_per_m3': 1200.0,        # INR per m3
        'aggregate_per_m3': 900.0,    # INR per m3
        'steel_per_kg': 65.0,         # INR per kg
        'brick_per_100': 350.0,       # INR per 100 bricks
        'tile_per_sqm': 300.0,        # INR per sqm of tiles
        'paint_per_liter': 500.0,     # INR per litre
        'plaster_per_m3': 2000.0      # INR per m3 for plaster (material+labour estimate)
    }

    # Use custom rates if provided, otherwise use defaults
    base_rates = custom_rates if custom_rates else default_rates

    # Apply plan-type adjustments
    if plan_type == 'economy':
        # Economy plan: reduce rates by 10%
        rates = {k: v * 0.90 for k, v in base_rates.items()}
    elif plan_type == 'premium':
        # Premium plan: increase rates by 15%
        rates = {k: v * 1.15 for k, v in base_rates.items()}
    else:
        # Standard plan: no adjustment
        rates = dict(base_rates)

    # Helper to safely pull nested values
    def g(d, *keys, default=0.0):
        v = d
        for k in keys:
            v = v.get(k, {}) if isinstance(v, dict) else {}
        return v if v not in ({}, []) else default

    itemized = {}
    material_costs = {}

    # Cement cost (by bags)
    cement_bags = materials.get('cement', {}).get('total_bags', 0)
    itemized['cement'] = cement_bags * rates['cement_per_bag']
    material_costs['cement'] = itemized['cement']

    # Sand cost (use m3 where available)
    sand_m3 = (
        materials.get('sand', {}).get('concrete_sand_m3', 0)
        + materials.get('sand', {}).get('brickwork_sand_m3', 0)
        + materials.get('sand', {}).get('plaster_sand_m3', 0)
    )
    if sand_m3 == 0 and materials.get('sand', {}).get('total_sand_kg'):
        # fallback: convert kg->m3 using typical density 1600 kg/m3
        sand_m3 = materials['sand']['total_sand_kg'] / 1600.0
    itemized['sand'] = sand_m3 * rates['sand_per_m3']
    material_costs['sand'] = itemized['sand']

    # Aggregate cost
    agg_m3 = materials.get('aggregate', {}).get('concrete_aggregate_m3', 0)
    if agg_m3 == 0 and materials.get('aggregate', {}).get('concrete_aggregate_kg'):
        agg_m3 = materials['aggregate']['concrete_aggregate_kg'] / 1500.0
    itemized['aggregate'] = agg_m3 * rates['aggregate_per_m3']
    material_costs['aggregate'] = itemized['aggregate']

    # Steel cost
    steel_kg = materials.get('steel', {}).get('total_steel_kg', 0)
    itemized['steel'] = steel_kg * rates['steel_per_kg']
    material_costs['steel'] = itemized['steel']

    # Masonry / bricks
    bricks = materials.get('masonry', {}).get('brick_quantity', 0)
    itemized['bricks'] = (bricks / 100.0) * rates['brick_per_100']
    material_costs['bricks'] = itemized['bricks']

    # Finishing: tiles, paint, plaster
    flooring_area_m2 = materials.get('finishing', {}).get('flooring_area_m2', 0)
    tile_cost = flooring_area_m2 * rates['tile_per_sqm']
    itemized['tiles'] = tile_cost
    material_costs['tiles'] = tile_cost

    paint_l = materials.get('finishing', {}).get('paint_liters', 0)
    itemized['paint'] = paint_l * rates['paint_per_liter']
    material_costs['paint'] = itemized['paint']

    plaster_m3 = materials.get('finishing', {}).get('plaster_volume_m3', 0)
    itemized['plaster'] = plaster_m3 * rates['plaster_per_m3']
    material_costs['plaster'] = itemized['plaster']

    # Sum totals
    total_material_cost = sum(material_costs.values())

    # Cost per sqft: need total built-up area. Use flooring_area_sqft as proxy for built-up area
    total_built_area_sqft = materials.get('finishing', {}).get('flooring_area_sqft', 0)
    cost_per_sqft = (total_material_cost / total_built_area_sqft) if total_built_area_sqft else None

    # Prepare result
    result = {
        'itemized_costs': {k: round(v, 2) for k, v in itemized.items()},
        'material_costs': {k: round(v, 2) for k, v in material_costs.items()},
        'applied_rates': rates,
        'total_material_cost': round(total_material_cost, 2),
        'cost_per_sqft': round(cost_per_sqft, 2) if cost_per_sqft is not None else None,
        'total_built_area_sqft': round(total_built_area_sqft, 2)
    }

    return result


def generate_boq(materials, cost):
    """Generate BOQ rows for all major elements."""
    boq = []

    concrete = materials.get('concrete', {})
    cement = materials.get('cement', {})
    sand = materials.get('sand', {})
    aggregate = materials.get('aggregate', {})
    steel = materials.get('steel', {})
    masonry = materials.get('masonry', {})
    finishing = materials.get('finishing', {})
    rates = cost.get('applied_rates', {})
    itemized = cost.get('itemized_costs', {})

    boq.extend([
        {'item': 'PCC (Plain Cement Concrete)', 'quantity': concrete.get('pcc_volume', 0), 'unit': 'm3', 'rate': None, 'amount': None},
        {'item': 'RCC Footing Concrete', 'quantity': concrete.get('footing_rcc', 0), 'unit': 'm3', 'rate': None, 'amount': None},
        {'item': 'RCC Column Concrete', 'quantity': concrete.get('column_rcc', 0), 'unit': 'm3', 'rate': None, 'amount': None},
        {'item': 'RCC Beam Concrete', 'quantity': concrete.get('beam_rcc', 0), 'unit': 'm3', 'rate': None, 'amount': None},
        {'item': 'RCC Slab Concrete', 'quantity': concrete.get('slab_rcc', 0), 'unit': 'm3', 'rate': None, 'amount': None},
        {'item': 'Cement', 'quantity': cement.get('total_bags', 0), 'unit': 'bags', 'rate': rates.get('cement_per_bag'), 'amount': itemized.get('cement')},
        {'item': 'Sand', 'quantity': round(sand.get('concrete_sand_m3', 0) + sand.get('brickwork_sand_m3', 0) + sand.get('plaster_sand_m3', 0), 3), 'unit': 'm3', 'rate': rates.get('sand_per_m3'), 'amount': itemized.get('sand')},
        {'item': 'Aggregate', 'quantity': aggregate.get('concrete_aggregate_m3', 0), 'unit': 'm3', 'rate': rates.get('aggregate_per_m3'), 'amount': itemized.get('aggregate')},
        {'item': 'Steel Reinforcement', 'quantity': steel.get('total_steel_kg', 0), 'unit': 'kg', 'rate': rates.get('steel_per_kg'), 'amount': itemized.get('steel')},
        {'item': 'Bricks', 'quantity': masonry.get('brick_quantity', 0), 'unit': 'nos', 'rate': rates.get('brick_per_100'), 'amount': itemized.get('bricks')},
        {'item': 'Floor Tiles', 'quantity': finishing.get('flooring_area_m2', 0), 'unit': 'm2', 'rate': rates.get('tile_per_sqm'), 'amount': itemized.get('tiles')},
        {'item': 'Paint', 'quantity': finishing.get('paint_liters', 0), 'unit': 'liters', 'rate': rates.get('paint_per_liter'), 'amount': itemized.get('paint')},
        {'item': 'Plaster', 'quantity': finishing.get('plaster_volume_m3', 0), 'unit': 'm3', 'rate': rates.get('plaster_per_m3'), 'amount': itemized.get('plaster')}
    ])

    return boq


def generate_floor_plan_svg(inputs, layout_type='layout1'):
    """Generate SVG floor plan visualization based on building inputs

    Args:
        inputs: Building input parameters
        layout_type: 'layout1' or 'layout2' for different room configurations

    Returns:
        SVG string for the floor plan
    """
    # Parse dimensions
    plot_length = float(inputs['plot_length'])
    plot_width = float(inputs['plot_width'])
    num_floors = int(inputs['num_floors'])

    # Increased scale for better visibility
    scale = 3
    width = max(int(plot_length * scale), 600)
    height = max(int(plot_width * scale), 500)

    # Padding and gaps
    padding = 30
    wall_thickness = 5
    room_gap = 25  # Increased gap between rooms

    # Available space for rooms
    usable_width = width - (2 * padding)
    usable_height = height - (2 * padding)

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .room-text {{ font-family: Arial, sans-serif; font-weight: bold; overflow: hidden; }}
            .room-label {{ font-size: 13px; fill: #333; }}
            .legend-text {{ font-size: 11px; fill: #333; }}
        </style>
        <clipPath id="clip-room-1">
            <rect x="0" y="0" width="100%" height="100%"/>
        </clipPath>
    </defs>

    <!-- Background -->
    <rect width="{width}" height="{height}" fill="#ffffff" stroke="#333" stroke-width="2"/>

    <!-- Outer walls -->
    <rect x="{padding}" y="{padding}" width="{usable_width}" height="{usable_height}" fill="none" stroke="#000000" stroke-width="3"/>
    '''

    if layout_type == 'layout1':
        # Layout 1: Open Concept
        # Kitchen (left side)
        kitchen_width = (usable_width - room_gap) * 0.28

        # Bedrooms and other rooms (right side)
        rooms_width = usable_width - kitchen_width - room_gap
        bed1_height = (usable_height - room_gap) * 0.48
        bed2_height = (usable_height - room_gap) * 0.48

        # Kitchen
        svg += f'''
    <!-- KITCHEN -->
    <rect x="{padding}" y="{padding}" width="{kitchen_width}" height="{usable_height}"
          fill="#fff8dc" stroke="#8b7500" stroke-width="2" rx="3"/>
    <text x="{padding + kitchen_width/2}" y="{padding + 35}" text-anchor="middle"
          class="room-label" font-size="14">KITCHEN</text>
    <text x="{padding + kitchen_width/2}" y="{padding + 55}" text-anchor="middle"
          class="room-label" font-size="10" fill="#666">{plot_length/3:.0f} × {plot_width:.0f}</text>

    <!-- Wall divider -->
    <line x1="{padding + kitchen_width + room_gap/2}" y1="{padding}"
          x2="{padding + kitchen_width + room_gap/2}" y2="{padding + usable_height}"
          stroke="#333" stroke-width="{wall_thickness}" stroke-dasharray="5,5"/>

    <!-- BEDROOM 1 (top right) -->
    <rect x="{padding + kitchen_width + room_gap}" y="{padding}"
          width="{rooms_width * 0.5 - room_gap/2}" height="{bed1_height}"
          fill="#ffe6e6" stroke="#cc6666" stroke-width="2" rx="3"/>
    <text x="{padding + kitchen_width + room_gap + rooms_width * 0.25 - room_gap/4}"
          y="{padding + bed1_height/2 - 5}" text-anchor="middle" class="room-label">BEDROOM 1</text>
    <text x="{padding + kitchen_width + room_gap + rooms_width * 0.25 - room_gap/4}"
          y="{padding + bed1_height/2 + 12}" text-anchor="middle" class="room-label" font-size="9" fill="#666">{plot_length/4:.0f} × {plot_width/2:.0f}</text>

    <!-- BEDROOM 2 (top right) -->
    <rect x="{padding + kitchen_width + room_gap + rooms_width * 0.5 + room_gap/2}" y="{padding}"
          width="{rooms_width * 0.5 - room_gap/2}" height="{bed1_height}"
          fill="#ffe6e6" stroke="#cc6666" stroke-width="2" rx="3"/>
    <text x="{padding + kitchen_width + room_gap + rooms_width * 0.75 + room_gap/4}"
          y="{padding + bed1_height/2 - 5}" text-anchor="middle" class="room-label">BEDROOM 2</text>
    <text x="{padding + kitchen_width + room_gap + rooms_width * 0.75 + room_gap/4}"
          y="{padding + bed1_height/2 + 12}" text-anchor="middle" class="room-label" font-size="9" fill="#666">{plot_length/4:.0f} × {plot_width/2:.0f}</text>

    <!-- MASTER BEDROOM (bottom right) -->
    <rect x="{padding + kitchen_width + room_gap}" y="{padding + bed1_height + room_gap}"
          width="{rooms_width * 0.65 - room_gap/2}" height="{bed2_height}"
          fill="#ffe6cc" stroke="#d9a574" stroke-width="2" rx="3"/>
    <text x="{padding + kitchen_width + room_gap + rooms_width * 0.32 - room_gap/4}"
          y="{padding + bed1_height + room_gap + bed2_height/2 - 5}" text-anchor="middle" class="room-label" font-size="13">MASTER</text>
    <text x="{padding + kitchen_width + room_gap + rooms_width * 0.32 - room_gap/4}"
          y="{padding + bed1_height + room_gap + bed2_height/2 + 12}" text-anchor="middle" class="room-label" font-size="13">BEDROOM</text>
    <text x="{padding + kitchen_width + room_gap + rooms_width * 0.32 - room_gap/4}"
          y="{padding + bed1_height + room_gap + bed2_height/2 + 26}" text-anchor="middle" class="room-label" font-size="9" fill="#666">{plot_length/3:.0f} × {plot_width/2:.0f}</text>

    <!-- BATHROOM (bottom right) -->
    <rect x="{padding + kitchen_width + room_gap + rooms_width * 0.65 + room_gap/2}"
          y="{padding + bed1_height + room_gap}"
          width="{rooms_width * 0.35 - room_gap/2}" height="{bed2_height}"
          fill="#e6f8f8" stroke="#66cccc" stroke-width="2" rx="3"/>
    <text x="{padding + kitchen_width + room_gap + rooms_width * 0.825 + room_gap/4}"
          y="{padding + bed1_height + room_gap + bed2_height/2}" text-anchor="middle" class="room-label" font-size="12">BATHROOM</text>
    '''

    else:  # layout2
        # Layout 2: Separate Rooms
        bed_width = (usable_width - 2*room_gap) / 3
        bath_width = (usable_width - 2*room_gap) / 4
        kitchen_width = (usable_width - 2*room_gap) * 0.35
        living_width = usable_width - bed_width - bath_width - kitchen_width - 3*room_gap

        top_height = (usable_height - room_gap) * 0.5
        bottom_height = (usable_height - room_gap) * 0.5

        svg += f'''
    <!-- BEDROOM 1 (top left) -->
    <rect x="{padding}" y="{padding}" width="{bed_width}" height="{top_height}"
          fill="#ffe6e6" stroke="#cc6666" stroke-width="2" rx="3"/>
    <text x="{padding + bed_width/2}" y="{padding + top_height/2 - 8}" text-anchor="middle" class="room-label">BEDROOM</text>
    <text x="{padding + bed_width/2}" y="{padding + top_height/2 + 10}" text-anchor="middle" class="room-label">1</text>

    <!-- BEDROOM 2 (top middle-left) -->
    <rect x="{padding + bed_width + room_gap}" y="{padding}" width="{bed_width}" height="{top_height}"
          fill="#ffe6e6" stroke="#cc6666" stroke-width="2" rx="3"/>
    <text x="{padding + bed_width + room_gap + bed_width/2}" y="{padding + top_height/2 - 8}" text-anchor="middle" class="room-label">BEDROOM</text>
    <text x="{padding + bed_width + room_gap + bed_width/2}" y="{padding + top_height/2 + 10}" text-anchor="middle" class="room-label">2</text>

    <!-- MASTER BEDROOM (top right) -->
    <rect x="{padding + 2*bed_width + 2*room_gap}" y="{padding}"
          width="{usable_width - 2*bed_width - 2*room_gap}" height="{top_height}"
          fill="#ffe6cc" stroke="#d9a574" stroke-width="2" rx="3"/>
    <text x="{padding + 2*bed_width + 2*room_gap + (usable_width - 2*bed_width - 2*room_gap)/2}"
          y="{padding + top_height/2 - 8}" text-anchor="middle" class="room-label" font-size="13">MASTER</text>
    <text x="{padding + 2*bed_width + 2*room_gap + (usable_width - 2*bed_width - 2*room_gap)/2}"
          y="{padding + top_height/2 + 10}" text-anchor="middle" class="room-label" font-size="13">BEDROOM</text>

    <!-- BATHROOM (bottom left) -->
    <rect x="{padding}" y="{padding + top_height + room_gap}" width="{bath_width}" height="{bottom_height}"
          fill="#e6f8f8" stroke="#66cccc" stroke-width="2" rx="3"/>
    <text x="{padding + bath_width/2}" y="{padding + top_height + room_gap + bottom_height/2}"
          text-anchor="middle" class="room-label" font-size="12">BATH</text>

    <!-- KITCHEN (bottom middle-left) -->
    <rect x="{padding + bath_width + room_gap}" y="{padding + top_height + room_gap}"
          width="{kitchen_width}" height="{bottom_height}"
          fill="#fff8dc" stroke="#8b7500" stroke-width="2" rx="3"/>
    <text x="{padding + bath_width + room_gap + kitchen_width/2}"
          y="{padding + top_height + room_gap + bottom_height/2 - 8}" text-anchor="middle" class="room-label">KITCHEN</text>
    <text x="{padding + bath_width + room_gap + kitchen_width/2}"
          y="{padding + top_height + room_gap + bottom_height/2 + 10}" text-anchor="middle" class="room-label" font-size="10" fill="#666">{plot_length/3:.0f} × {plot_width/2:.0f}</text>

    <!-- LIVING/DINING (bottom right) -->
    <rect x="{padding + bath_width + kitchen_width + 2*room_gap}" y="{padding + top_height + room_gap}"
          width="{usable_width - bath_width - kitchen_width - 2*room_gap}" height="{bottom_height}"
          fill="#e6f2ff" stroke="#4a90e2" stroke-width="2" rx="3"/>
    <text x="{padding + bath_width + kitchen_width + 2*room_gap + (usable_width - bath_width - kitchen_width - 2*room_gap)/2}"
          y="{padding + top_height + room_gap + bottom_height/2 - 8}" text-anchor="middle" class="room-label">LIVING</text>
    <text x="{padding + bath_width + kitchen_width + 2*room_gap + (usable_width - bath_width - kitchen_width - 2*room_gap)/2}"
          y="{padding + top_height + room_gap + bottom_height/2 + 10}" text-anchor="middle" class="room-label">DINING</text>
    '''

    # Legend
    svg += f'''
    <!-- Legend -->
    <g transform="translate({width - 180}, {height - 120})">
        <text x="0" y="0" font-size="12" font-weight="bold" fill="#333">Legend:</text>

        <rect x="0" y="15" width="18" height="15" fill="#ffe6e6" stroke="#333" stroke-width="1"/>
        <text x="25" y="27" class="legend-text">Bedrooms</text>

        <rect x="0" y="38" width="18" height="15" fill="#fff8dc" stroke="#333" stroke-width="1"/>
        <text x="25" y="50" class="legend-text">Kitchen</text>

        <rect x="0" y="61" width="18" height="15" fill="#e6f2ff" stroke="#333" stroke-width="1"/>
        <text x="25" y="73" class="legend-text">Living Area</text>

        <rect x="0" y="84" width="18" height="15" fill="#e6f8f8" stroke="#333" stroke-width="1"/>
        <text x="25" y="96" class="legend-text">Bathroom</text>
    </g>

    <!-- Title -->
    <text x="{width/2}" y="25" font-size="18" font-weight="bold" text-anchor="middle" fill="#000">
        {"LAYOUT 1: OPEN CONCEPT" if layout_type == 'layout1' else "LAYOUT 2: SEPARATE ROOMS"}
    </text>

    <!-- Dimensions -->
    <text x="{width/2}" y="{height - 8}" font-size="12" text-anchor="middle" fill="#666">
        {plot_length}ft × {plot_width}ft | {num_floors} Floor{"s" if num_floors != 1 else ""}
    </text>
    '''

    svg += '</svg>'

    return svg
