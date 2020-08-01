if __name__ == '__main__':
    response = dict()
    try:
        import json
        import arcpy
        from procesos_validacion import *

        params = dict()

        params['xls'] = arcpy.GetParameterAsText(0)
        params['shp_17'] = arcpy.GetParameterAsText(1)
        params['shp_18'] = arcpy.GetParameterAsText(2)
        params['shp_19'] = arcpy.GetParameterAsText(3)
        params['out_dir'] = arcpy.GetParameterAsText(4)

        value = validate_coordenadas(**params)
        response['state'] = 1
        response['result'] = value
    except Exception as e:
        response['state'] = 0
        response['message'] = str(e)
    finally:
        response = json.dumps(response)
        arcpy.SetParameterAsText(5, response)