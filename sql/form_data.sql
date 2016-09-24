------------ FINAL RESULT ------------


------------ QUERY IN A FUNCTION ------------
-- The plugin doesn't need to know the implementation. Using a function separates te server side from the client side better.
CREATE OR REPLACE FUNCTION getIntersectingInfo(IN selected geometry)
AS '
	SELECT 
		ARRAY(
			WITH edif_areas_table AS (
				SELECT ref, AREA(ST_Multi(ST_Intersection(selected, edif.geo))) AS edif_area
				FROM edif
				WHERE ST_Intersects(selected, edif.geo)
				GROUP BY ref
			)
			SELECT ROW(ref, 100 * edif_area / SUM(edif_area) AS percent)
			WHERE percent >= 3
			ORDER BY percent DESC
		) AS resultat_edif,
		ARRAY(
			SELECT ref
				FROM zones
				WHERE ST_Intersects(selected, zones.geo)
		) AS resultat_zones
	;
'
LANGUAGE SQL
;