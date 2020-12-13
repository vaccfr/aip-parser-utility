import geojson
import math

with open("airspaces-all-2013.geojson") as f:
    gj = geojson.load(f)

parse_tmas_for = ["LFSB"]
output = []
output_text = []

def deg_to_dms(deg, type='lat'):
    decimals, number = math.modf(deg)
    d = int(number)
    m = int(decimals * 60)
    s = (deg - d - m / 60) * 3600.00
    compass = {
        'lat': ('N','S'),
        'lon': ('E','W')
    }
    compass_str = compass[type][0 if d >= 0 else 1]
    return '{}{}.{}.{:.3f}'.format(compass_str, abs(d), abs(m), abs(s))

for airport in parse_tmas_for:
    output.append('AERONAV:'+ airport +':TMA:AIXM IMPORT:GEO::') 
    for j in gj.features:
        if airport in j['properties']['id'] and j['properties']['type'] == "TMA":
            # Loop through all coordinates
            previous_coord = []
            first_coord = []
            for coord in j['geometry']['coordinates'][0]:
                if len(previous_coord) != 0:
                    output.append(deg_to_dms(previous_coord[1])+' '+deg_to_dms(previous_coord[0], 'lon')+' '
                    +deg_to_dms(coord[1])+' '+deg_to_dms(coord[0], 'lon')+' COLOR_AirspaceD')
                else:
                    first_coord = coord
                
                previous_coord = coord
            output.append(deg_to_dms(previous_coord[1])+' '+deg_to_dms(previous_coord[0], 'lon')+' '
                    +deg_to_dms(first_coord[1])+' '+deg_to_dms(first_coord[0], 'lon')+' COLOR_AirspaceD')

with open("gng_sct_tma.txt", 'w') as g:
    g.writelines('\n'.join(output))
with open("gng_labels_tma.txt", 'w') as g:
    g.writelines('\n'.join(output_text))