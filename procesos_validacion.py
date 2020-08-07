import pandas as pd
from gfunctions import *
import random
from messages import *
import os

arcpy.env.overwriteOutput = True

# Fields
_ID = 'ID'
_CODIGOU = 'codigou'
_ZONA = 'zona'
_ZONA_DM = 'zona_dm'

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


def validate_dm(codigou, data):
    reg = data.loc[data[_CODIGOU] == codigou]
    if not reg.shape[0]:
        raise RuntimeError("No existe el identificador en la base grafica")


def validate_zona(zona, codigou, data):
    if zona in (17, 18, 19):
        return zona
    else:
        reg = data.loc[data[_CODIGOU] == codigou]
        zona_dm = int(reg[_ZONA].tolist()[0])
        if zona_dm in (17, 18, 19):
            return zona_dm
        else:
            raise RuntimeError("El registro no presenta un zona geografica valida")


def validate_position(row, x, y, flayer_dm, flayer_ar, wgs=True):
    res = list()
    zona = row[_ZONA_DM]
    codigou = row[_CODIGOU]
    lyr_dm = flayer_dm[zona]
    lyr_ar = flayer_ar[zona]
    if x and y:
        epsg = WGS84 + zona if wgs else PSAD56 + zona
        epsg_origin = arcpy.SpatialReference(epsg)
        point_ini = arcpy.Point(x, y)
        point = arcpy.PointGeometry(point_ini, epsg_origin)
        if not wgs:
            epsg_unique = arcpy.SpatialReference(WGS84 + zona)
            point = point.projectAs(epsg_unique)
        res_dm = intersect_by_point(point, lyr_dm, 'dm', codigou=codigou)
        res_ar = intersect_by_point(point, lyr_ar, 'ar')
        res.append(res_dm)
        res.append(res_ar)
    else:
        res = [9] * 2  # El registro no presenta coordenadas validas
    return res


def intersect_by_point(point, feature_layer, case, **kwargs):
    res = int()
    arcpy.SelectLayerByLocation_management(feature_layer, 'INTERSECT', point, "#", "NEW_SELECTION")
    if case == 'dm':
        if kwargs.get(_CODIGOU):
            rows = filter(lambda i: i[0] == kwargs[_CODIGOU], arcpy.da.SearchCursor(feature_layer, [_CODIGOU]))
            res = 1 if len(rows) else 0
        else:
            res = 8  # El identificador del derecho minero es nulo
    elif case == 'ar':
        rows = int(arcpy.GetCount_management(feature_layer).__str__())
        res = 0 if rows else 1
    return res


@script_tool_decore
def validate_coordenadas(**kwargs):
    response = list()

    arcpy.AddMessage(MSG_READ_XLS)
    df = pd.read_excel(kwargs['xls'], converters={_CODIGOU: str})
    df[_ZONA_DM] = 0

    # FeaturesLayers de derechos mineros
    flayer_dm = dict()
    arcpy.AddMessage(MSG_READ_FEATURES)
    flayer_dm[17] = arcpy.MakeFeatureLayer_management(kwargs['shp_dm_17'], 'feature_dm_17')
    flayer_dm[18] = arcpy.MakeFeatureLayer_management(kwargs['shp_dm_18'], 'feature_dm_18')
    flayer_dm[19] = arcpy.MakeFeatureLayer_management(kwargs['shp_dm_19'], 'feature_dm_19')

    arcpy.AddMessage('seleccionando layer aleatoriamente')
    flayer_selected = random.choice(flayer_dm.values())
    arcpy.AddMessage('obteniendo codigous {}'.format(flayer_selected))

    nparray = arcpy.da.FeatureClassToNumPyArray(flayer_selected, [_CODIGOU, _ZONA])
    df_dm = pd.DataFrame(nparray)

    # data_dm = map(lambda re: re, arcpy.da.SearchCursor(flayer_dm[flayer_selected], [_CODIGOU, _ZONA]))
    # codigous = [i[0] for i in data_dm]

    arcpy.AddMessage('layer de areas restringidas')
    # FeaturesLayers de areas restringidas
    flayer_ar = dict()
    arcpy.AddMessage('repollo')
    flayer_ar[17] = arcpy.MakeFeatureLayer_management(kwargs['shp_ar_17'], 'feature_ar_17')
    flayer_ar[18] = arcpy.MakeFeatureLayer_management(kwargs['shp_ar_18'], 'feature_ar_18')
    flayer_ar[19] = arcpy.MakeFeatureLayer_management(kwargs['shp_ar_19'], 'feature_ar_19')

    arcpy.AddMessage(MSG_EVALUATE_ROWS)
    for i, r in df.iterrows():
        # Habilitar para tets
        # if i > 100:
        #     break
        arcpy.AddMessage('{}. [{}] {} {}S'.format(i, r[_ID], r[_CODIGOU], r[_ZONA]))
        res = dict()
        res[_ID] = r[_ID]
        res[_CODIGOU] = r[_CODIGOU]
        res[_ZONA] = r[_ZONA]
        try:
            validate_dm(r[_CODIGOU], df_dm)
            res[_ZONA_DM] = validate_zona(r[_ZONA], r[_CODIGOU], df_dm)
            r[_ZONA_DM] = res[_ZONA_DM]
            res['P56_DM'], res['P56_AR'] = validate_position(r, r[_E_P56], r[_N_P56], flayer_dm, flayer_ar, wgs=False)
            res['W84_1P_DM'], res['W84_1P_AR'] = validate_position(r, r[_E_W84_1P], r[_N_W84_1P], flayer_dm, flayer_ar)
            res['W84_2P_DM'], res['W84_2P_AR'] = validate_position(r, r[_E_W84_2P], r[_N_W84_2P], flayer_dm, flayer_ar)
            res['W84_N_DM'], res['W84_N_AR'] = validate_position(r, r[_E_W84_N], r[_N_W84_N], flayer_dm, flayer_ar)
        except Exception as e:
            res['error'] = e.message
        finally:
            response.append(res)

    if not response:
        arcpy.AddMessage(MSG_NO_DATA)
        return MSG_NO_DATA

    arcpy.AddMessage(MSG_EXPORT_TO_XLS)
    df_res = pd.DataFrame(response)  # type: DataFrame

    from datetime import datetime
    identi = datetime.now().strftime("%m%d%Y%H%M%S")
    out_xls = os.path.join(kwargs['out_dir'], 'response_{}.xls'.format(identi))
    df_res.to_excel(out_xls, index=False)
    arcpy.AddMessage(MSG_FINISH_PROCESS)
    return out_xls
