from flask import Flask, render_template, request
from calculations import calculate_materials, calculate_cost, generate_plan_variants, generate_floor_plan_svg, generate_boq
from cost_loader import load_material_costs

app = Flask(__name__)

# Load material costs from Excel file at startup
MATERIAL_RATES = load_material_costs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/estimate', methods=['POST'])
def estimate():
    try:
        # Collect all form data
        inputs = {
            'plot_length': request.form.get('plot_length', ''),
            'plot_width': request.form.get('plot_width', ''),
            'num_floors': request.form.get('num_floors', ''),
            'floor_height': request.form.get('floor_height', ''),
            'structure_type': request.form.get('structure_type', ''),
            'footing_type': request.form.get('footing_type', ''),
            'num_footings': request.form.get('num_footings', ''),
            'footing_length': request.form.get('footing_length', ''),
            'footing_width': request.form.get('footing_width', ''),
            'footing_depth': request.form.get('footing_depth', ''),
            'pcc_thickness': request.form.get('pcc_thickness', ''),
            'num_columns': request.form.get('num_columns', ''),
            'column_length': request.form.get('column_length', ''),
            'column_width': request.form.get('column_width', ''),
            'column_height': request.form.get('column_height', ''),
            'total_beam_length': request.form.get('total_beam_length', ''),
            'beam_width': request.form.get('beam_width', ''),
            'beam_depth': request.form.get('beam_depth', ''),
            'slab_area': request.form.get('slab_area', ''),
            'slab_thickness': request.form.get('slab_thickness', ''),
            'external_wall_length': request.form.get('external_wall_length', ''),
            'internal_wall_length': request.form.get('internal_wall_length', ''),
            'wall_thickness': request.form.get('wall_thickness', ''),
            'wall_height': request.form.get('wall_height', ''),
            'internal_plaster_thickness': request.form.get('internal_plaster_thickness', ''),
            'external_plaster_thickness': request.form.get('external_plaster_thickness', ''),
            'flooring_area': request.form.get('flooring_area', ''),
            'tile_size': request.form.get('tile_size', ''),
            'paint_type': request.form.get('paint_type', ''),
            'paint_coats': request.form.get('paint_coats', ''),
            'concrete_grade': request.form.get('concrete_grade', ''),
            'cement_type': request.form.get('cement_type', ''),
            'mortar_mix': request.form.get('mortar_mix', '')
        }
        
        # Validate all inputs
        required_fields = list(inputs.keys())
        for field in required_fields:
            if not inputs[field]:
                return render_template('error.html', message=f'Please fill in all required fields'), 400
        
        # Validate numeric fields
        numeric_fields = ['plot_length', 'plot_width', 'num_floors', 'floor_height', 'num_footings',
                         'footing_length', 'footing_width', 'footing_depth', 'pcc_thickness',
                         'num_columns', 'column_length', 'column_width', 'column_height',
                         'total_beam_length', 'beam_width', 'beam_depth', 'slab_area', 'slab_thickness',
                         'external_wall_length', 'internal_wall_length', 'wall_thickness', 'wall_height',
                         'internal_plaster_thickness', 'external_plaster_thickness', 'flooring_area', 'paint_coats']
        
        try:
            for field in numeric_fields:
                val = float(inputs[field])
                if val <= 0:
                    return render_template('error.html', message=f'{field.replace("_", " ").title()} must be greater than 0'), 400
        except ValueError:
            return render_template('error.html', message='All numeric fields must contain valid numbers'), 400
        
        # Validate select fields
        valid_structures = ['rcc_framed', 'load_bearing']
        if inputs['structure_type'] not in valid_structures:
            return render_template('error.html', message='Invalid structure type'), 400
        
        valid_footings = ['isolated', 'combined']
        if inputs['footing_type'] not in valid_footings:
            return render_template('error.html', message='Invalid footing type'), 400
        
        valid_grades = ['m20', 'm25', 'm30']
        if inputs['concrete_grade'] not in valid_grades:
            return render_template('error.html', message='Invalid concrete grade'), 400
        
        valid_mortars = ['1:6', '1:4', '1:3']
        if inputs['mortar_mix'] not in valid_mortars:
            return render_template('error.html', message='Invalid mortar mix'), 400
        
        # Calculate materials for all three plans
        base_materials = calculate_materials(inputs)

        # Generate Economy Plan
        economy_materials = generate_plan_variants(base_materials, plan_type='economy')
        economy_cost = calculate_cost(economy_materials, plan_type='economy', custom_rates=MATERIAL_RATES)
        economy_boq = generate_boq(economy_materials, economy_cost)

        # Generate Standard Plan
        standard_materials = generate_plan_variants(base_materials, plan_type='standard')
        standard_cost = calculate_cost(standard_materials, plan_type='standard', custom_rates=MATERIAL_RATES)
        standard_boq = generate_boq(standard_materials, standard_cost)

        # Generate Premium Plan
        premium_materials = generate_plan_variants(base_materials, plan_type='premium')
        premium_cost = calculate_cost(premium_materials, plan_type='premium', custom_rates=MATERIAL_RATES)
        premium_boq = generate_boq(premium_materials, premium_cost)

        # Generate floor plan layouts
        layout1_svg = generate_floor_plan_svg(inputs, layout_type='layout1')
        layout2_svg = generate_floor_plan_svg(inputs, layout_type='layout2')

        return render_template(
            'result.html',
            inputs=inputs,
            economy_plan={'materials': economy_materials, 'cost': economy_cost},
            standard_plan={'materials': standard_materials, 'cost': standard_cost},
            premium_plan={'materials': premium_materials, 'cost': premium_cost},
            economy_boq=economy_boq,
            standard_boq=standard_boq,
            premium_boq=premium_boq,
            total_cost_economy=round(economy_cost.get('total_material_cost', 0), 2),
            total_cost_standard=round(standard_cost.get('total_material_cost', 0), 2),
            total_cost_premium=round(premium_cost.get('total_material_cost', 0), 2),
            layout1_svg=layout1_svg,
            layout2_svg=layout2_svg
        )
        
    except Exception as e:
        return render_template('error.html', message=f'An error occurred: {str(e)}'), 500

if __name__ == '__main__':
    # For production deployment on Replit/cloud
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
