# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ficha_urbanistica - A QGIS plugin that creates GML files of plots for the spainish catastre
                             -------------------
        begin                : 2016-09-19
        copyright            : (C) 2016 by Martí Angelats
        email                : martiangelats@hotmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ficha_urbanistica class from file ficha_urbanistica.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ficha_urbanistica import FichaUrbanistica

    # Construct the plugin
    plugin = FichaUrbanistica(iface)

    # Add plugin project change triggers
    iface.projectRead.connect(plugin.projectChange)
    iface.newProjectCreated.connect(plugin.projectChange)

    # return the plugin
    return plugin
