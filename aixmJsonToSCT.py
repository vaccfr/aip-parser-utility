import geojson

with open("airspaces-all-2013.geojson") as f:
    gj = geojson.load(f)

parse_tmas_for = ["LFSB"]
output = []

for airport in parse_tmas_for:
    output.append('AERONAV:'+ airport +':TMA:TMA:ES:ES:') 
    for j in gj.features:
        if airport in j['properties']['id'] and j['properties']['type'] == "TMA":
            # Loop through all coordinates
            previous_coord = []
            first_coord = []
            for coord in j['geometry']['coordinates'][0]:
                if len(previous_coord) != 0:
                    output.append(str(previous_coord[1])+' '+str(previous_coord[0])+' '+str(coord[1])+' '+str(coord[0])+' COLOR_AirspaceD')
                else:
                    first_coord = coord
                
                previous_coord = coord
            output.append(str(previous_coord[1])+' '+str(previous_coord[0])+' '+str(first_coord[1])+' '+str(first_coord[0])+' COLOR_AirspaceD')

with open("gng_sct_tma.txt", 'w') as g:
    g.writelines('\n'.join(output))