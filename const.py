# -*- coding: utf-8 -*-
"""File that has all constants"""


class Const:
    """Constains all the constants used in the plugin."""
    # Link labels value (it is formatted later on)
    LINK_NORMATIVA = u"<a href='file:///{:s}'>Veure normativa</a>"
    LINK_ORDENACIO = u"<a href='file:///{:s}'>{:s}</a>"
    LINK_COND = u"<a href='{:s}/condicions_generals.htm'>Condicions Generals</a>"
    LINK_DOT = u"<a href='{:s}/dotacio_aparcament.htm'>Dotació mínima d'aparcaments</a>"
    LINK_REG = u"<a href='{:s}/regulacio_aparcament.htm'>Regulació particular de l'ús d'aparcaments</a>"
    LINK_FINCA = u"<a href='{:s}/param_finca.htm'>Paràmetres Finca</a>"
    LINK_EDIF = u"<a href='{:s}/param_edificacio.htm'>Paràmetres Edificació</a>"

    # Query result columns
    REFCAT = 0
    AREA = 1
    ADRECA = 2
    CODI_CLASSI = 3
    DESCR_CLASSI = 4
    CODI_ZONES = 5
    PERCENT_ZONES = 6
    CODI_GENERAL_ZONES = 7
    CODI_SECTOR = 8
    DESCR_SECTOR = 9

    # PDF composite index
    PDF_UBICACIO = u'Fitxa 1 - Ubicació'
    PDF_ZONES = u'Fitxa 2 - Zones'

    # Query the infrmation from the database
    MAIN_QUERY = 'SELECT * FROM data.ficha_urbanistica(%s);'

    # Zones query
    ZONES_QUERY = 'SELECT * FROM data.ficha_urbanistica_zones(%s);'
    ZONES_COLUMNS = ['qua_codi', 'qua_descripcio', 'area_int', 'per_int', 'qg_tipus', 'qg_subzona', 'qg_definicio', 'tord_codi', 'tord_descripcio', 'hab_unifamiliar', 'hab_plurifamiliar', 'hab_rural', 'res_especial', 'res_mobil', 'hoteler', 'com_petit', 'com_mitja', 'com_gran', 'oficines_serveis', 'restauracio', 'recreatiu', 'magatzem', 'industrial_1', 'industrial_2', 'industrial_3', 'industrial_4', 'industrial_5', 'taller_reparacio', 'educatiu', 'sanitari', 'assistencial', 'cultural', 'associatiu', 'esportiu', 'serveis_publics', 'serveis_tecnics', 'serveis_ambientals', 'serveis_radio', 'aparcament', 'estacions_servei', 'agricola', 'ramader', 'forestal', 'lleure', 'ecologic', 'fondaria_edif', 'edificabilitat', 'ocupacio', 'densitat_hab', 'vol_max_edif', 'fondaria_edif_pb', 'pb', 'alcada', 'punt_aplic', 'sep_min', 'constr_aux_alcada', 'constr_auxo_cupacio', 'tanques', 'nplantes', 'alcada_lliure', 'entresol_pb', 'sotacoberta', 'pendent', 'terrasses', 'elem_sort', 'cossos_sort', 'cossos_annexes', 'porxos', 'tract_facana', 'comp_facana', 'prop_obertura', 'material_facana', 'material_coberta', 'fusteria', 'espai_lliure', 'altell', 'altres', 'front_min', 'parce_min', 'prof_min']
