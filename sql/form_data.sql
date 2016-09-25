-- Funcio que retorna una taula amb tots els valors necesaris pel formulari.
CREATE OR REPLACE FUNCTION ficha_tecnica(int) RETURNS TABLE(refcat text, area int, adreca text, codi_sector text, descr_sector text, codi_classi text, descr_classi text, codi_zones text[] percent_zones numeric[])
AS $$

  WITH
    _parcela AS (
      SELECT refcat, geom, ST_Area(geom) as area
      FROM parcela
      WHERE ninterno = $1
    )

  SELECT
    _parcela.refat AS refcat,
    _parcela.area AS area,
    (
      -- TODO
    ) AS adreca,
    _sector.codi AS codi_sector,
    _sector.descr AS descr_sector,
    _classi.codi AS codi_classi,
    _classi.descr AS descr_classi,
    ARRAY(SELECT codi FROM _zones) AS codi_zones,
    ARRAY(SELECT percent FROM _zones) AS percent_zones

  FROM
    _parcela,
    ( -- Subquery per aconseguir a quin sector partany el terreny
      SELECT codi, descipcio
      FROM sectors_urbanistics, _parcela
      WHERE TS_Intersects(_parcela.geom, sectors_urbanistics.geom)
      -- Hi pot haver petits errors deguts al mapa. Utilitzem el sector amb més area
      ORDER BY TS_Area(TS_Intersection(sectors_urbanistics.geom)) DESC
      LIMIT 1
    ) AS _sector,

    ( -- Subquery per aconseguir quina calificacio té el terreny
      SELECT codi, descipcio
      FROM classificacio, _parcela
      WHERE TS_Intersects(_parcela.geom, classificacio.geom)
      -- Hi pot haver petits errors deguts al mapa. Utilitzem el sector amb més area
      ORDER BY TS_Area(TS_Intersection(classificacio.geom)) DESC
      LIMIT 1
    ) AS _classi,

    (
      -- Aconseguim el parcentatge de l'area i descartem totes les ares que son < 3%
      SELECT _zones.codi, 100 * TS_Area(_zones.area) / SUN(TS_Area(_zones.area)) AS percent
      FROM (
        -- Troba les zones i les areas.
        -- TODO
      ) AS _zones
      WHERE percent >= 3
      GROUP BY _zones.codi
      ORDER BY percent DESC
    ) _zones;

$$ LANGUAGE SQL;