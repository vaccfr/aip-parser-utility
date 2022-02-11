import geojson
import math
from shapely.geometry import Polygon, Point


with open("data/airspaces-all.geojson") as f:
    gj = geojson.load(f)

parse_tmas_for = ["LFKB", "LFLL", "LFLB"]
output = []
output_text = []

text_already_place = []

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

def travelFrom(Lat, Lon, Degrees, d = 2):
    lat1 = math.radians(Lat)
    lon1 = math.radians(Lon)
    brng = math.radians(Degrees)
    R = 3443.898488

    lat2 = math.asin(math.sin(lat1) * math.cos(d / R) +
            math.cos(lat1) * math.sin(d / R) * math.cos(brng))

    lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(d / R) * math.cos(lat1),
            math.cos(d / R) - math.sin(lat1) * math.sin(lat2))

    return [math.degrees(lat2), math.degrees(lon2)]

def distanceTo(Lat1, Lon1, Lat2, Lon2):
    lat1 = math.radians(Lat1)
    lon1 = math.radians(Lon1)
    lat2 = math.radians(Lat2)
    lon2 = math.radians(Lon2)

    if Lat1 == Lat2 and Lon1 == Lon2:
        return 0

    x = math.sin((lat1 - lat2) / 2.0)
    y = math.sin((lon1 - lon2) / 2.0)

    d = 2 * math.sin(math.sqrt(x*x + math.cos(lat1) * math.cos(lat2) * (y*y)))

    return d * 180 * 60 / math.pi

for airport in parse_tmas_for:
    output.append('AERONAV:'+ airport +':TMA:AIXM IMPORT:ES:ARTCC:') 
    output_text.append('AERONAV:'+ airport +':TMA AIXM IMPORT:ES-ESE:NOTES')
    for j in gj.features:
        if airport in j['properties']['id'] and j['properties']['type'] == "TMA":
            # Loop through all coordinates
            previous_coord = []
            first_coord = []
            # Draw the SCT delimitation
            
            ShapelyData = []
            for coord in j['geometry']['coordinates'][0]:
                if len(previous_coord) != 0:
                    # Simplify polygon by removing points too close together
                    if distanceTo(previous_coord[1], previous_coord[0], coord[1], coord[0]) < 0.1:
                        continue

                    output.append(deg_to_dms(previous_coord[1])+' '+deg_to_dms(previous_coord[0], 'lon')+' '
                    +deg_to_dms(coord[1])+' '+deg_to_dms(coord[0], 'lon')+' COLOR_AirspaceD')
                else:
                    first_coord = coord

                previous_coord = coord
                ShapelyData.append([coord[1], coord[0]])

            output.append(deg_to_dms(previous_coord[1])+' '+deg_to_dms(previous_coord[0], 'lon')+' '
                    +deg_to_dms(first_coord[1])+' '+deg_to_dms(first_coord[0], 'lon')+' COLOR_AirspaceD')

            # Text Label Position Calculation
            ShapelyShape = Polygon(ShapelyData)
            centroid = ShapelyShape.representative_point()
            center = centroid

            if center in text_already_place:
                # Move it
                bigmaths = travelFrom(center.x, center.y, 180)
                center = Point(bigmaths[0], bigmaths[1])
            
            text_already_place.append(center)

            # Calculating text value
            vertical_limit = ''
            if "FT" in j['properties']['lower']:
                vertical_limit += str(int(int(j['properties']['lower'].replace("FT", "").replace("AMSL", "").replace("AGL", ""))/100)).rjust(3, '0')
            else:
                vertical_limit += str(j['properties']['lower'])
            
            vertical_limit += '/'
            if "FT" in j['properties']['upper']:
                vertical_limit += str(int(int(j['properties']['upper'].replace("FT", "").replace("AMSL", "").replace("AGL", ""))/100)).rjust(3, '0')
            else:
                vertical_limit += str(j['properties']['upper'])

            text = '"'+ j['properties']['class'] + ' ' + vertical_limit +'" '+deg_to_dms(center.x)+' '+deg_to_dms(center.y, 'lon')
            output_text.append(text.replace(' AMSL', ''))


with open("gng_sct_tma.txt", 'w') as g:
    g.writelines('\n'.join(output))
with open("gng_labels_tma.txt", 'w') as g:
    g.writelines('\n'.join(output_text))