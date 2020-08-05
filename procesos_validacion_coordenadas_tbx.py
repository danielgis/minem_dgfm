if __name__ == '__main__':
    response = dict()
    try:
        import json
        from procesos_validacion import *

        params = dict()

        params['xls'] = arcpy.GetParameterAsText(0)
        params['shp_dm_17'] = arcpy.GetParameterAsText(1)
        params['shp_dm_18'] = arcpy.GetParameterAsText(2)
        params['shp_dm_19'] = arcpy.GetParameterAsText(3)
        params['shp_ar_17'] = arcpy.GetParameterAsText(4)
        params['shp_ar_18'] = arcpy.GetParameterAsText(5)
        params['shp_ar_19'] = arcpy.GetParameterAsText(6)
        params['out_dir'] = arcpy.GetParameterAsText(7)

        value = validate_coordenadas(**params)
        response['state'] = 1
        response['result'] = value
    except Exception as e:
        response['state'] = 0
        response['message'] = str(e)
    finally:
        response = json.dumps(response)
        arcpy.SetParameterAsText(8, response)
