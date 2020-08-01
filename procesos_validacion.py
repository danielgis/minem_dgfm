from gfunctions import *
import arcpy
import pandas as pd
import random
from messages import *
import uuid

# Fields
_ID = 'ID'
_CODIGOU = 'codigou'
_ZONA = 'zona'
_N_P56 = 'N_P56'
_E_P56 = 'E_P56'
_N_W84_1P = 'N_W84_1P'
_E_W84_1P = 'E_W84_1P'
_N_W84_2P = 'N_W84_2P'
_E_W84_2P = 'E_W84_2P'
_N_W84_N = 'N_W84_N'
_E_W84_N = 'E_W84_N'

# EPSG
PSAD56 = 24860
WGS84 = 32700


def validate_dm(codigou, codigous):
    if codigou not in codigous:
        raise RuntimeError("No existe el identificador en la base grafica")


def validate_zona(zona):
    if zona not in (17, 18, 19):
        raise RuntimeError("El registro no presenta un zona geografica valida")


def validate_position(row, x, y, flayer, wgs=True):
    # res = int()
    zona = row[_ZONA]
    codigou = row[_CODIGOU]
    lyr = flayer[zona]
    if x and y:
        epsg = WGS84 + zona if wgs else PSAD56 + zona
        epsg_origin = arcpy.SpatialReference(epsg)
        point_ini = arcpy.Point(x, y)
        point = arcpy.PointGeometry(point_ini, epsg_origin)
        if not wgs:
            epsg_unique = arcpy.SpatialReference(WGS84 + zona)
            point = point.projectAs(epsg_unique)
        arcpy.SelectLayerByLocation_management(lyr, 'INTERSECT', point, "#", "NEW_SELECTION")
        rows = filter(lambda i: i[0] == codigou, arcpy.da.SearchCursor(lyr, [_CODIGOU]))
        res = 1 if len(rows) else 0
    else:
        res = 9  # 'El registro no presenta coordenadas validas'
    return res


# @script_tool_decore
def validate_coordenadas(**kwargs):
    response = list()

    arcpy.AddMessage(MSG_READ_XLS)
    df = pd.read_excel(kwargs['xls'], converters={_CODIGOU: str})

    flayer = dict()
    arcpy.AddMessage(MSG_READ_FEATURES)
    flayer[17] = arcpy.MakeFeatureLayer_management(kwargs['shp_17'], 'feature_17')
    flayer[18] = arcpy.MakeFeatureLayer_management(kwargs['shp_18'], 'feature_18')
    flayer[19] = arcpy.MakeFeatureLayer_management(kwargs['shp_19'], 'feature_19')

    flayer_selected = random.choice(list(flayer.values()))
    codigous = map(lambda i: i[0], arcpy.da.SearchCursor(flayer_selected, [_CODIGOU]))

    arcpy.AddMessage(MSG_EVALUATE_ROWS)
    for i, r in df.iterrows():
        arcpy.AddMessage('{}. [{}] {} {}S'.format(i, r[_ID], r[_CODIGOU], r[_ZONA]))
        res = dict()
        res[_ID] = r[_ID]
        res[_CODIGOU] = r[_CODIGOU]
        res[_ZONA] = r[_ZONA]
        try:
            validate_dm(r[_CODIGOU], codigous)
            validate_zona(r[_ZONA])
            res['P56'] = validate_position(r, r[_E_P56], r[_N_P56], flayer, wgs=False)
            res['W84_1P'] = validate_position(r, r[_E_W84_1P], r[_N_W84_1P], flayer)
            res['W84_2P'] = validate_position(r, r[_E_W84_2P], r[_N_W84_2P], flayer)
            res['W84_N'] = validate_position(r, r[_E_W84_N], r[_N_W84_N], flayer)
        except Exception as e:
            res['error'] = e.message
        finally:
            response.append(res)

    if not response:
        arcpy.AddMessage(MSG_NO_DATA)
        return MSG_NO_DATA

    arcpy.AddMessage(MSG_EXPORT_TO_XLS)
    df_res = pd.DataFrame(response)
    out_xls = os.path.join(kwargs['out_dir'], 'response_{}.xls'.format(uuid.uuid4().get_hex()))
    df_res.to_excel(out_xls, index=False)

    arcpy.AddMessage(MSG_FINISH_PROCESS)
    return 1
