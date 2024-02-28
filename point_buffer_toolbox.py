'''
Charlie Britt
Python Toolboxes
'''
import arcpy


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Simple start"
        self.description = "First python toolbox"

    def getParameterInfo(self):
        """Define the tool parameters."""

        in_features_point = arcpy.Parameter(
            displayName   = "Input point features",
            name          = "in_features_point",
            datatype      = "GPFeatureLayer",
            parameterType = "Required",
            direction     = "Input")
        in_features_point.filter.list = ["Point"]

        in_buffer_distance = arcpy.Parameter(
            displayName   = "Buffer radius in miles",
            name          = "in_buffer_distance",
            datatype      = "GPDouble",
            parameterType = "Required",
            direction     = "Input")
        in_buffer_distance.value = 1

        in_features_polygon = arcpy.Parameter(
            displayName   = "Input polygon features",
            name          = "in_features_polygon",
            datatype      = "GPFeatureLayer",
            parameterType = "Required",
            direction     = "Input")
        in_features_polygon.filter.list = ["Polygon"]


        in_area_field = arcpy.Parameter(
            displayName   = "Polygon old area field",
            name          = "in_area_field",
            datatype      = "Field",
            parameterType = "Required",
            direction     = "Input")
        in_area_field.filter.list = ['Double']
        in_area_field.parameterDependencies = [in_features_polygon.name]

        
        in_join_field = arcpy.Parameter(
            displayName   = "Polygon join field",
            name          = "in_join_field",
            datatype      = "Field",
            parameterType = "Required",
            direction     = "Input")
        in_join_field.filter.list = ['String']
        in_join_field.parameterDependencies = [in_features_polygon.name]

        #####

        in_population_table = arcpy.Parameter(
            displayName   = "Population table",
            name          = "in_population_table",
            datatype      = "GPTableView",
            parameterType = "Required",
            direction     = "Input")

        in_table_join_field = arcpy.Parameter(
            displayName   = "Table join field",
            name          = "in_table_join_field",
            datatype      = "Field",
            parameterType = "Required",
            direction     = "Input")
        in_table_join_field.parameterDependencies = [in_population_table.name]

        in_table_population_field = arcpy.Parameter(
            displayName   = "Population field",
            name          = "in_table_population_field",
            datatype      = "Field",
            parameterType = "Required",
            direction     = "Input")
        in_table_population_field.parameterDependencies = [in_population_table.name]

        ######
        out_features_clip = arcpy.Parameter(
            displayName   = "Output",
            name          = "out_features_clip",
            datatype      = "GPFeatureLayer",
            parameterType = "Required",
            direction     = "Output")
        

        
        params = [in_features_point, in_buffer_distance, in_features_polygon,
                  in_area_field, in_join_field, in_population_table,
                  in_table_join_field, in_table_population_field,
                  out_features_clip]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        in_features_point          = parameters[0].valueAsText
        in_buffer_distance         = parameters[1].value
        in_features_polygon        = parameters[2].valueAsText
        in_area_field              = parameters[3].valueAsText
        in_join_field              = parameters[4].valueAsText
        in_population_table        = parameters[5].valueAsText
        in_table_join_field        = parameters[6].valueAsText
        in_table_population_field  = parameters[7].valueAsText
        out_features_clip          = parameters[8].valueAsText

        #step 1
        out_features_buffer = arcpy.env.scratchGDB + '/buffer'
        arcpy.analysis.Buffer(in_features_point, out_features_buffer, f'{in_buffer_distance} Mile')

        #step 2
        arcpy.analysis.Clip(in_features_polygon, out_features_buffer, out_features_clip)
        
        # Step 3. Joining fields

        arcpy.management.JoinField(out_features_clip, in_join_field, in_population_table, in_table_join_field, [in_table_population_field])

        # Step 4. Adding a new field

        new_field_name = "proportional_pop"
        arcpy.management.AddField(out_features_clip, new_field_name, "float", field_precision=10, field_scale=2)

        # Step 5. Calculating the new field

        in_new_area_field = 'Shape_Area'
        formula = f'!{in_table_population_field}! * !{in_new_area_field}! / !{in_area_field}!'
        arcpy.management.CalculateField(out_features_clip, new_field_name, formula, "PYTHON3")

        # Step 5. Get the percent

        cursor = arcpy.da.SearchCursor(in_population_table, [in_table_population_field])
        total = 0
        for row in cursor:
            total += row[0]

        cursor = arcpy.da.SearchCursor(out_features_clip, [new_field_name])
        sub_total = 0
        for row in cursor:
            sub_total += row[0]

        # Step 6. Message

        arcpy.AddMessage(f'''The percent of population in {in_buffer_distance} mile(s) is {100*sub_total/total:.2f}%.''')
            
        arcpy.AddMessage(f'''Here are the specified -
            + Parameter 1: {in_features_point}
            + Parameter 2: {in_buffer_distance}''')
        
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

