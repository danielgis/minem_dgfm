if __name__ == '__main__':
    response = dict()
    try:
        import json
        from gfunctions import *
        from messages import *

        require_dir = arcpy.GetParameterAsText(0)
        install_modules(require_dir)
        value = True

        response['state'] = 1
        response['result'] = value
    except Exception as e:
        response['state'] = 0
        response['message'] = e.message.__str__()
    finally:
        response = json.dumps(response)
        arcpy.AddMessage(response)
        arcpy.AddWarning(MSG_ARCGIS_RESTART)
        arcpy.SetParameterAsText(1, response)
