-- Funcio que retorna una taula amb tots els valors necesaris pel formulari.
DROP FUNCTION IF EXISTS data.ficha_urbanistica( INT );
CREATE FUNCTION data.ficha_urbanistica(INT)
  RETURNS TABLE(
    refcat             TEXT,
    area               DOUBLE PRECISION,
    adreca             TEXT,
    codi_classi        TEXT,
    descr_classi       TEXT,
    codi_zones         CHARACTER VARYING(10) [],
    percent_zones      DOUBLE PRECISION [],
    codi_general_zones CHARACTER VARYING(10) [],
    desc_general_zones CHARACTER VARYING [],
    codi_sector        TEXT,
    descr_sector       TEXT
  ) AS $$

WITH
    _parcela AS (
      SELECT
        refcat,
        geom,
        ST_Area(geom) AS area,
        numero,
        via           AS id_via
      FROM carto.parcela
      WHERE ninterno = $1
      LIMIT 1
  ),
    _quali AS (
      SELECT
        __quali.codi                                               AS codi,
        SUM(ST_Area(ST_Intersection(_parcela.geom, __quali.geom))) AS area
      FROM carto.qualificacions AS __quali, _parcela
      WHERE ST_Intersects(_parcela.geom, __quali.geom)
      GROUP BY __quali.codi
  )


SELECT
  _parcela.refcat AS refcat,
  _parcela.area   AS area,
  _via.adreca     AS adreca,
  _classi.codi    AS codi_classi,
  _classi.descr   AS descr_classi,
  codi_zones,
  percent_zones,
  codi_general_zones,
  desc_general_zones,
  _sector.codi    AS codi_sector,
  _sector.descr   AS descr_sector

FROM
  _parcela

  LEFT JOIN (-- Subquery per aconseguir a quin sector partany el terreny
              SELECT
                codi,
                descripcio AS descr
              FROM carto.sectors, _parcela
              WHERE ST_Intersects(_parcela.geom, sectors.geom)
              -- Hi pot haver petits errors deguts al mapa. Utilitzem el sector amb més area
              ORDER BY ST_Area(ST_Intersection(sectors.geom, _parcela.geom)) DESC
              LIMIT 1
            ) AS _sector ON TRUE


  LEFT JOIN (
              SELECT COALESCE(tipo_via || ' ', '') ||
                     COALESCE(nombre_via, '<desconegut>') ||
                     COALESCE(', ' || primer_numero_policia, ', SN') ||
                     COALESCE(' ' || primera_letra, '')
                AS adreca
              FROM
                cadastre.cat_11, _parcela
              WHERE
                cat_11.parcela_catastral = _parcela.refcat
              LIMIT 1
            ) AS _via ON TRUE


  LEFT JOIN (
              WITH
                  _2_ AS (
                    SELECT
                      __.codi    AS codi,
                      __.percent AS percent
                    FROM (
                           SELECT
                             _quali.codi,
                             100 * area / sum_area AS percent
                           FROM _quali
                             FULL JOIN (
                                         SELECT SUM(area) AS sum_area
                                         FROM _quali
                                       ) AS _ ON TRUE
                         ) AS __
                    WHERE percent >= 3
                    ORDER BY percent DESC, codi ASC
                    LIMIT 4
                )
              SELECT
                ARRAY(SELECT codi
                      FROM _2_) AS codi_zones,
                ARRAY(SELECT percent
                      FROM _2_) AS percent_zones,
                ARRAY(
                    SELECT COALESCE(cod_ord, codi, '<error>')
                    FROM data.qualificacio_general, _2_
                    WHERE qualificacio_general.id = _2_.codi
                    ORDER BY _2_.percent DESC, _2_.codi ASC
                )               AS codi_general_zones,
                ARRAY(
                    SELECT desc_qualif
                    FROM data.qualificacio_general, _2_
                    WHERE qualificacio_general.id = _2_.codi
                    ORDER BY _2_.percent DESC, _2_.codi ASC
                )               AS desc_general_zones
              LIMIT 1
            ) AS _zones ON TRUE


  LEFT JOIN (
              SELECT
                class.codi       AS codi,
                class.descripcio AS descr
              FROM planejament_urba.classificacio AS class, _parcela
              WHERE ST_Intersects(class.geom, _parcela.geom)
              ORDER BY ST_Area(ST_Intersection(class.geom, _parcela.geom))
              LIMIT 1
            ) AS _classi ON TRUE;

$$ LANGUAGE SQL;