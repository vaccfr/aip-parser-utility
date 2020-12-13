#!/usr/bin/env python3

import bpaTools
from shapely.geometry import LineString, Point

errLocalisationPoint:list = [-5,45]

#geojson Colors attributes
def addColorProperties(prop:dict, oLog:bpaTools.Logger):
    sClass = prop["class"]

    #Red            - #ff0000
    #medium red     - #ff6480
    #ligth Red      - #ff8080
    #Purple         - #800080
    #medium purple  - #ffb9dc
    #light purple   - #ff96dc
    #bordeau        - #aa0014
    #Gres           - #444444
    #ligth Gres     - #a0868b
    #Orange         - #f07800
    #Blue           - #0000ff
    #ligth blue     - #ceeffe
    #bright blue    - #80ffff

    #Red and fill
    if sClass in ["A","B","C","P","CTR","CTR-P","TMA","TMA-P","TMZ","RMZ/TMZ","TMZ/RMZ"]:
        sStroke = "#ff0000"
        sFill = "#ff8080"
        if prop.get("lower", None)=="SFC":
            nFillOpacity = 0.6
        else:
            nFillOpacity = 0.3
    #Red and No-Fill
    elif sClass in ["CTA","CTA-P","FIR","FIR-P","NO-FIR","PART","CLASS","SECTOR","SECTOR-C","OCA","OCA-P","OTA","OTA-P","UTA","UTA-P","UIR","UIR-P","TSA","CBA","RCA","RAS","TRA","AMA","ASR","ADIZ","POLITICAL","OTHER","AWY"]:
        sStroke = "#ff0000"
        sFill = "#ff8080"
        nFillOpacity = 0
    #Purple and No-fill
    elif sClass=="D" and prop.get("type", None)=="LTA":
        sStroke = "#800080"
        sFill = "#ff96dc"
        nFillOpacity = 0
    #Red and fill
    elif sClass in ["D","D-AMC"] and prop.get("declassifiable", None)!="Yes":
        sStroke = "#ff0000"
        sFill = "#ff8080"
        if prop.get("lower", None)=="SFC":
            nFillOpacity = 0.6
        else:
            nFillOpacity = 0.3
    #Light-Red and Purple fill
    elif sClass in ["D","D-AMC"] and prop.get("declassifiable", None)=="Yes":
        sStroke = "#ff0000"
        sFill = "#ffb9dc"
        if prop.get("lower", None)=="SFC":
            nFillOpacity = 0.6
        else:
            nFillOpacity = 0.3
    #Purple and fill
    elif sClass in ["R","R-AMC"] and prop.get("type", None)!="RTBA":
        sStroke = "#800080"
        sFill = "#ffb9dc"
        if prop.get("lower", None)=="SFC":
            nFillOpacity = 0.6
        else:
            nFillOpacity = 0.3
    #Gres and fill
    elif sClass in ["R","R-AMC"] and prop.get("type", None)=="RTBA":
        sStroke = "#444444"
        sFill = "#a0868b"
        if prop.get("lower", None)=="SFC":
            nFillOpacity = 0.6
        else:
            nFillOpacity = 0.3
    #Orange and ligth-fill
    elif sClass in ["Q","GP"]:
        sStroke = "#f07800"
        sFill = "#f07800"
        if prop.get("lower", None)=="SFC":
            nFillOpacity = 0.3
        else:
            nFillOpacity = 0.1
    #Orange and No-Fill
    elif sClass in ["RMZ","W"]:
        sStroke = "#f07800"
        sFill = "#f07800"
        nFillOpacity = 0
    #Blue
    elif sClass in ["ZSM","BIRD","PROTECT","D-OTHER","SUR","AER","TRPLA","TRVL","VOL"]:
        sStroke = "#0000ff"
        sFill = "#ceeffe"
        if prop.get("lower", None)=="SFC":
            nFillOpacity = 0.4
        else:
            nFillOpacity = 0.2
    #Green
    elif sClass in ["E","F","G"]:
        sStroke = "#008040"
        sFill = "#80ff80"
        if prop.get("lower", None)=="SFC":
            nFillOpacity = 0.4
        else:
            nFillOpacity = 0.2
    else:
        oLog.warning("GeoJSON Color not found for Class={0}".format(sClass), outConsole=False)
        return

    #Quasi transparence pour toutes les zones au dessus de FL115
    if nFillOpacity!=0 and prop.get("lowerM", None)>=3505:
            nFillOpacity = 0.1

    prop.update({"stroke": sStroke})
    prop.update({"stroke-width": 2})
    prop.update({"stroke-opacity": 0.8})
    prop.update({"fill": sFill})
    prop.update({"fill-opacity": nFillOpacity})
    return


class Aixm2json4_5:

    def __init__(self, oCtrl) -> None:
        bpaTools.initEvent(__file__, oCtrl.oLog)
        self.oCtrl = oCtrl
        self.oAirspacesCatalog = None
        self.geoBorders = None                    #Geographic borders dictionary
        self.geoAirspaces = None                  #Geographic airspaces dictionary
        return

    def parseControlTowers(self) -> None:
        sTitle = "Aerodrome control towers"
        sXmlTag = "Uni"

        sMsg = "Parsing {0} to GeoJSON - {1}".format(sXmlTag, sTitle)
        self.oCtrl.oLog.info(sMsg)

        oList = self.oCtrl.oAixm.root.find_all(sXmlTag, recursive=False)
        barre = bpaTools.ProgressBar(len(oList), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
        idx = 0
        geojson = []
        for uni in oList:
            idx+=1
            twr = self.tower2json(uni)
            if twr:
                geojson.append(twr)
            barre.update(idx)
        barre.reset
        self.oCtrl.oAixmTools.writeGeojsonFile("towers", geojson)
        return

    def tower2json(self, uni) -> dict:
        if uni.codeType.string in ("TWR", "OTHER"):
            if uni.find("geoLat", recursive=False):
                prop = self.oCtrl.oAixmTools.initProperty("Aerodrome Control Tower")
                prop = self.oCtrl.oAixmTools.addProperty(prop, uni.OrgUid, "txtName", "organisationAuthority")
                prop = self.oCtrl.oAixmTools.addProperty(prop, uni, "codeType", "codeType")
                prop = self.oCtrl.oAixmTools.addProperty(prop, uni.UniUid, "txtName", "name")
                geom = {"type":"Point", "coordinates":self.oCtrl.oAixmTools.geo2coordinates(uni)}
                return {"type":"Feature", "properties":prop, "geometry":geom}
            else:
                self.oCtrl.oLog.warning("Missing TWR coordinates {0}".format(uni.UniUid), outConsole=False)
        return

    def parseAerodromes(self) -> None:
        sTitle = "Aerodromes / Heliports"
        sXmlTag = "Ahp"

        sMsg = "Parsing {0} to GeoJSON - {1}".format(sXmlTag, sTitle)
        self.oCtrl.oLog.info(sMsg)

        oList = self.oCtrl.oAixm.root.find_all(sXmlTag, recursive=False)
        barre = bpaTools.ProgressBar(len(oList), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
        idx = 0
        geojson = []
        for ahp in oList:
            idx+=1
            geojson.append(self.ahp2json(ahp))
            barre.update(idx)
        barre.reset()
        self.oCtrl.oAixmTools.writeGeojsonFile("aerodromes", geojson)
        return

    def ahp2json(self, ahp) -> dict:
        prop = self.oCtrl.oAixmTools.initProperty("Aerodrome / Heliport")
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp.OrgUid, "txtName", "organisationAuthority")
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "codeType")
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "txtName", "name")
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp.AhpUid, "codeId", "codeId")
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "codeIcao", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "codeIata", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "valElev", "elevation", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "uomDistVer", "verticalUnit", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "txtDescrRefPt", "description", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "txtDescrSite", "descriptionSite", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "txtNameCitySer", "cityServing", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "txtNameAdmin", "nameAdmin", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, ahp, "txtRmk", "remark", optional=True)
        geom = {"type":"Point", "coordinates":self.oCtrl.oAixmTools.geo2coordinates(ahp)}
        return {"type":"Feature", "properties":prop, "geometry":geom}

    def parseObstacles(self) -> None:
        sTitle = "Obstacles"
        sXmlTag = "Obs"

        sMsg = "Parsing {0} to GeoJSON - {1}".format(sXmlTag, sTitle)
        self.oCtrl.oLog.info(sMsg)

        oList = self.oCtrl.oAixm.root.find_all(sXmlTag, recursive=False)
        barre = bpaTools.ProgressBar(len(oList), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
        idx = 0
        geojson = []
        for obs in oList:
            idx+=1
            geojson.append(self.obs2json(obs))
            barre.update(idx)
        barre.reset()
        self.oCtrl.oAixmTools.writeGeojsonFile("obstacles", geojson)
        return

    def obs2json(self, obs) -> dict:
        prop = self.oCtrl.oAixmTools.initProperty("Obstacle")
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "txtDescrType", "type")
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "txtName", "name")
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "txtDescrMarking", "marked", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "codeLgt", "codeLight")
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "txtDescrLgt", "descrLight", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "valElev", "elevation")
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "valHgt", "height", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "uomDistVer", "verticalUnit")
        prop = self.oCtrl.oAixmTools.addProperty(prop, obs, "txtRmk", "remark", optional=True)
        geom = {"type":"Point", "coordinates":self.oCtrl.oAixmTools.geo2coordinates(obs.ObsUid)}
        return {"type":"Feature", "properties":prop, "geometry":geom}

    def parseRunwayCenterLinePosition(self) -> None:
        sTitle = "Runway Center Line Position"
        sXmlTag = "Rcp"

        sMsg = "Parsing {0} to GeoJSON - {1}".format(sXmlTag, sTitle)
        self.oCtrl.oLog.info(sMsg)

        oList = self.oCtrl.oAixm.root.find_all(sXmlTag, recursive=False)
        barre = bpaTools.ProgressBar(len(oList), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
        idx = 0
        geojson = []
        for rcp in oList:
            idx+=1
            geojson.append(self.rcp2json(rcp))
            barre.update(idx)
        barre.reset()
        self.oCtrl.oAixmTools.writeGeojsonFile("runwaysCenter", geojson)
        return

    def rcp2json(self, rcp) -> dict:
        prop = self.oCtrl.oAixmTools.initProperty("Runway Center")
        prop = self.oCtrl.oAixmTools.addProperty(prop, rcp.RcpUid.RwyUid.AhpUid, "codeId")
        prop = self.oCtrl.oAixmTools.addProperty(prop, rcp.RcpUid.RwyUid, "txtDesig", "designator")
        prop = self.oCtrl.oAixmTools.addProperty(prop, rcp, "valElev", "elevation", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, rcp, "uomDistVer", "verticalUnit", optional=True)
        geom = {"type":"Point", "coordinates":self.oCtrl.oAixmTools.geo2coordinates(rcp.RcpUid)}
        return {"type":"Feature", "properties":prop, "geometry":geom}

    def parseGateStands(self) -> None:
        sTitle = "Gates and Stands"
        sXmlTag = "Gsd"

        sMsg = "Parsing {0} to GeoJSON - {1}".format(sXmlTag, sTitle)
        self.oCtrl.oLog.info(sMsg)

        oList = self.oCtrl.oAixm.root.find_all(sXmlTag, recursive=False)
        barre = bpaTools.ProgressBar(len(oList), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
        idx = 0
        geojson = []
        for gsd in oList:
            idx+=1
            geojson.append(self.gsd2json(gsd))
            barre.update(idx)
        barre.reset()
        self.oCtrl.oAixmTools.writeGeojsonFile("gates-stands", geojson)
        return

    def gsd2json(self, gsd) -> dict:
        prop = self.oCtrl.oAixmTools.initProperty("Gate or Stand")
        prop = self.oCtrl.oAixmTools.addProperty(prop, gsd.GsdUid, "txtDesig", "designator")
        prop = self.oCtrl.oAixmTools.addProperty(prop, gsd.ApnUid, "txtName", "parkingPosition")
        prop = self.oCtrl.oAixmTools.addProperty(prop, gsd.ApnUid.AhpUid, "codeId")
        prop = self.oCtrl.oAixmTools.addProperty(prop, gsd, "codeType")
        prop = self.oCtrl.oAixmTools.addProperty(prop, gsd, "txtDescrRestrUse", optional=True)
        prop = self.oCtrl.oAixmTools.addProperty(prop, gsd, "txtRmk", optional=True)
        geom = {"type":"Point", "coordinates":self.oCtrl.oAixmTools.geo2coordinates(gsd)}
        return {"type":"Feature", "properties":prop, "geometry":geom}

    def parseGeographicBorders(self) -> None:
        sTitle = "Geographic borders"
        sXmlTag = "Gbr"

        sMsg = "Parsing {0} to GeoJSON - {1}".format(sXmlTag, sTitle)
        self.oCtrl.oLog.info(sMsg)

        if self.geoBorders == None:
            self.geoBorders = dict()
            oList = self.oCtrl.oAixm.root.find_all(sXmlTag, recursive=False)
            barre = bpaTools.ProgressBar(len(oList), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
            idx = 0
            geojson = []
            for gbr in oList:
                idx+=1
                j,l = self.gbr2json(gbr)
                geojson.append(j)
                self.geoBorders[gbr.GbrUid["mid"]] = LineString(l)
                barre.update(idx)
        barre.reset()
        self.oCtrl.oAixmTools.writeGeojsonFile("borders", geojson)
        return

    def gbr2json(self, gbr):
        prop = self.oCtrl.oAixmTools.initProperty("Geographic border")
        prop = self.oCtrl.oAixmTools.addProperty(prop, gbr, "codeType", "type")
        prop = self.oCtrl.oAixmTools.addProperty(prop, gbr.GbrUid, "txtName", "name")
        prop = self.oCtrl.oAixmTools.addProperty(prop, gbr, "txtRmk", "desc", optional=True)
        # geometry
        g = []
        l = []
        for gbv in gbr.find_all("Gbv", recursive=False):
            if gbv.codeType.string not in ("GRC", "END"):
                self.oCtrl.oLog.critical("Not recognized codetype\n{0}".format(gbv), outConsole=True)
            g.append(self.oCtrl.oAixmTools.geo2coordinates(gbv))
            l.append((g[-1][0], g[-1][1]))
        geom = {"type":"LineString", "coordinates":g}
        return ({"type":"Feature", "properties":prop, "geometry":geom}, l)

    def findJsonObjectAirspacesBorders(self, sAseUid) -> dict:
        for o in self.geoAirspaces:
            if o["properties"]["UId"]==sAseUid:
                return o["geometry"]
        return None

    def parseAirspacesBorders(self, airspacesCatalog) -> None:
        self.oAirspacesCatalog = airspacesCatalog

        #Controle de prerequis
        if self.geoBorders == None:
            self.parseGeographicBorders()

        sTitle = "Airspaces Borders"
        sXmlTag = "Abd"

        if not self.oCtrl.oAixm.root.find(sXmlTag, recursive=False):
            sMsg = "Missing tags {0} - {1}".format(sXmlTag, sTitle)
            self.oCtrl.oLog.warning(sMsg, outConsole=True)
            return

        sMsg = "Parsing {0} to GeoJSON - {1}".format(sXmlTag, sTitle)
        self.oCtrl.oLog.info(sMsg)

        barre = bpaTools.ProgressBar(len(self.oAirspacesCatalog.oAirspaces), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
        idx = 0
        self.geoAirspaces = []                #Réinitialisation avant traitement global
        for k,oZone in self.oAirspacesCatalog.oAirspaces.items():
            idx+=1
            if not oZone["groupZone"]:          #Ne pas traiter les zones de type 'Regroupement'
                sAseUid = oZone["UId"]

                #Map 20200801
                #if oZone["id"] in ["EBS27"]:  #[W] LOW FLYING AREA GOLF ONE
                #    self.oCtrl.oLog.critical("just for bug {0}".format(oZone["id"]), outConsole=False)

                oBorder = self.oAirspacesCatalog.findAixmObjectAirspacesBorders(sAseUid)
                if oBorder:
                    self.parseAirspaceBorder(oZone, oBorder)
                else:
                    sAseUidBase = self.oAirspacesCatalog.findZoneUIdBase(sAseUid)       #Identifier la zone de base (de référence)
                    if sAseUidBase==None:
                        self.oCtrl.oLog.warning("Missing Airspaces Borders AseUid={0} of {1}".format(sAseUid, oZone["nameV"]), outConsole=False)
                        self.geoAirspaces.append({"type":"Feature", "properties":oZone, "geometry":{"type": "Point", "coordinates": errLocalisationPoint}})
                    else:
                        geom = self.findJsonObjectAirspacesBorders(sAseUidBase)         #Recherche si la zone de base a déjà été parsé
                        if geom:
                            if geom["coordinates"]==errLocalisationPoint:
                                self.oCtrl.oLog.warning("Missing Airspaces Borders sAseUidBase={0} used by AseUid={1} of {2}".format(sAseUidBase, sAseUid, oZone["nameV"]), outConsole=False)
                            self.geoAirspaces.append({"type":"Feature", "properties":oZone, "geometry":geom})
                        else:
                            oBorder = self.oAirspacesCatalog.findAixmObjectAirspacesBorders(sAseUidBase)
                            if oBorder==None:
                                self.oCtrl.oLog.warning("Missing Airspaces Borders AseUid={0} AseUidBase={1} of {2}".format(sAseUid, sAseUidBase, oZone["nameV"]), outConsole=False)
                                self.geoAirspaces.append({"type":"Feature", "properties":oZone, "geometry":{"type": "Point", "coordinates": errLocalisationPoint}})
                            else:
                                self.parseAirspaceBorder(oZone, oBorder)
            barre.update(idx)

        barre.reset()
        return

    def parseAirspaceBorder(self, oZone, oBorder) -> None:
        g = []              #geometry
        points4map = []

        if oBorder.Circle:
            lon_c, lat_c = self.oCtrl.oAixmTools.geo2coordinates(oBorder.Circle,
                                           latitude=oBorder.Circle.geoLatCen.string,
                                           longitude=oBorder.Circle.geoLongCen.string,
                                           oZone=oZone)

            radius = float(oBorder.Circle.valRadius.string)
            radius = self.oCtrl.oAixmTools.convertLength(radius, oBorder.uomRadius.string, "M")   #Convert radius in Meter for GeoJSON format

            Pcenter = Point(lon_c, lat_c)
            if self.oCtrl.MakePoints4map:
                points4map.append(self.oCtrl.oAixmTools.make_point(Pcenter, "Circle Center of {0}".format(oZone["nameV"])))
            g = self.oCtrl.oAixmTools.make_arc(Pcenter, radius)
            geom = {"type":"Polygon", "coordinates":[g]}
        else:
            avx_list = oBorder.find_all("Avx", recursive=False)
            for avx_cur in range(0,len(avx_list)):
                avx = avx_list[avx_cur]
                codeType = avx.codeType.string

                # 'Great Circle' or 'Rhumb Line' segment
                if codeType in ["GRC", "RHL"]:
                    lon, lat = self.oCtrl.oAixmTools.geo2coordinates(avx,oZone=oZone)
                    if self.oCtrl.MakePoints4map:
                        pt = Point(lon, lat)
                        points4map.append(self.oCtrl.oAixmTools.make_point(pt, "Point {0} of {1}; type={2}".format(avx_cur, oZone["nameV"], codeType)))
                    g.append([lon, lat])

                # 'Counter Clockwise Arc' or 'Clockwise Arc'
                #Nota: 'ABE' = 'Arc By Edge' ne semble pas utilisé dans les fichiers SIA-France et Eurocontrol-Europe
                elif codeType in ["CCA", "CWA"]:
                    start = self.oCtrl.oAixmTools.geo2coordinates(avx, oZone=oZone)
                    if avx_cur+1 == len(avx_list):
                        stop = g[0]
                    else:
                        stop = self.oCtrl.oAixmTools.geo2coordinates(avx_list[avx_cur+1], oZone=oZone)

                    center = self.oCtrl.oAixmTools.geo2coordinates(avx,
                                             latitude=avx.geoLatArc.string,
                                             longitude=avx.geoLongArc.string,
                                             oZone=oZone)

                    Pcenter = Point(center[0], center[1])
                    Pstart = Point(start[0], start[1])
                    Pstop = Point(stop[0], stop[1])

                    if self.oCtrl.MakePoints4map:
                        points4map.append(self.oCtrl.oAixmTools.make_point(Pstart, "Arc Start {0} of {1}".format(avx_cur, oZone["nameV"])))
                        points4map.append(self.oCtrl.oAixmTools.make_point(Pcenter, "Arc Center {0} of {1}".format(avx_cur, oZone["nameV"])))
                        points4map.append(self.oCtrl.oAixmTools.make_point(Pstop, "Arc Stop {0} of {1}".format(avx_cur, oZone["nameV"])))

                    #Alignement pas toujours idéal sur les extremités d'arcs
                    radius = float(avx.valRadiusArc.string)
                    radius = self.oCtrl.oAixmTools.convertLength(radius, oBorder.uomRadiusArc.string, "M")   #Convert radius in Meter for GeoJSON format

                    #Test non-concluant - Tentative d'amélioration des arc par recalcul systématique du rayon sur la base des coordonnées des points
                    #arc = self.oCtrl.oAixmTools.make_arc2(Pcenter, Pstart, Pstop, 0.0, (codeType=="CWA"))
                    arc = self.oCtrl.oAixmTools.make_arc2(Pcenter, Pstart, Pstop, radius, (codeType=="CWA"))
                    for o in arc:
                        g.append(o)

                # 'Sequence of geographical (political) border vertexes'
                elif codeType == "FNT":
                    # geographic borders
                    start = self.oCtrl.oAixmTools.geo2coordinates(avx, oZone=oZone)
                    if avx_cur+1 == len(avx_list):
                        stop = g[0]
                    else:
                        stop = self.oCtrl.oAixmTools.geo2coordinates(avx_list[avx_cur+1], oZone=oZone)

                    if avx.GbrUid["mid"] in self.geoBorders:
                        fnt = self.geoBorders[avx.GbrUid["mid"]]
                        start_d = fnt.project(Point(start[0], start[1]), normalized=True)
                        stop_d = fnt.project(Point(stop[0], stop[1]), normalized=True)
                        geom = self.oCtrl.oAixmTools.substring(fnt, start_d, stop_d, normalized=True)
                        for c in geom.coords:
                            lon, lat = c
                            g.append([lon, lat])
                    else:
                        self.oCtrl.oLog.warning("Missing geoBorder GbrUid='{0}' Name={1} of {2}".format(avx.GbrUid["mid"], avx.GbrUid.txtName.string, oZone["nameV"]), outConsole=False)
                        g.append(start)
                else:
                    self.oCtrl.oLog.warning("Default case - GbrUid='{0}' Name={1} of {2}".format(avx.GbrUid["mid"], avx.GbrUid.txtName.string, oZone["nameV"]), outConsole=False)
                    g.append(self.oCtrl.oAixmTools.geo2coordinates(avx, oZone=oZone))

            if len(g) == 0:
                self.oCtrl.oLog.error("Geometry vide of {0}\n{1}".format(oZone["nameV"], oBorder.prettify()), outConsole=True)
                geom = None
            elif len(g) == 1:
                geom = {"type":"Point", "coordinates":g[0]}
            elif len(g) == 2:
                geom = {"type":"LineString", "coordinates":g}
            else:
                #Contrôle de fermeture du Polygone
                if g[0] != g[-1]:
                    g.append(g[0])
                geom = {"type":"Polygon", "coordinates":[g]}

        #Ajout spécifique des points complémentaires pour map des cartographies
        for g0 in points4map:
            for g1 in g0:
                self.geoAirspaces.append(g1)
        self.geoAirspaces.append({"type":"Feature", "properties":oZone, "geometry":geom})
        return

    def saveAirspacesFilter(self, aContext) -> None:
        context = aContext[0]
        sMsg = "Prepare GeoJSON file - {0}".format(aContext[1])
        self.oCtrl.oLog.info(sMsg)
        barre = bpaTools.ProgressBar(len(self.oAirspacesCatalog.oAirspaces), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
        idx = 0
        geojson = []       #Initialisation avant filtrage spécifique
        for o in self.geoAirspaces:
            oZone = o["properties"]
            idx+=1
            include = not oZone["groupZone"]                         				#Ne pas traiter les zones de type 'Regroupement'
            #if include and ("excludeAirspaceNotCoord" in oZone):     				#Ne pas traiter les zones qui n'ont pas de coordonnées geometriques
            #    include = not oZone["excludeAirspaceNotCoord"]
            if include:
                include = False
                if context=="all":
                    include = True
                elif context=="ifr":
                    include = (not oZone["vfrZone"]) and (not oZone["groupZone"])
                elif context=="vfr":
                    include = oZone["vfrZone"]
                    include = include or oZone.get("vfrZoneExt", False)     		#Exporter l'extension de vol possible en VFR de 0m jusqu'au FL175/5334m
                elif context=="ff":
                    include = oZone["freeFlightZone"]
                    include = include or oZone.get("freeFlightZoneExt", False) 	    #Exporter l'extension de vol possible en VFR de 0m jusqu'au FL175/5334m
                    include = include and (o["geometry"]["coordinates"]!=errLocalisationPoint)
            if include:
                addColorProperties(o["properties"], self.oCtrl.oLog)                #Ajout des propriétés pour colorisation de la zone
                geojson.append(o)
            barre.update(idx)
        barre.reset()
        if geojson:
            self.oCtrl.oAixmTools.writeGeojsonFile("airspaces", geojson, context)
        return

    #Nétoyage du catalogue de zones pour desactivation des éléments qui ne sont pas valides ; ou constitués que d'un ou deux 'Point' a exclure uniquement pour le freefligth
    #Ces simples 'Point remarquable' sont supprimés de la cartographie freefligth (ex: un VOR, un émmzteur radio, un centre de piste)
    #Idem, suppression des 'lignes' (ex: Axe d'approche d'un aérodrome ou autres...)
    def cleanAirspacesCalalog(self, airspacesCatalog) -> None:
        self.oAirspacesCatalog = airspacesCatalog
        if self.oAirspacesCatalog.cleanAirspacesCalalog:     #Contrôle si l'optimisation est déjà réalisée
            return

        sMsg = "Clean catalog"
        self.oCtrl.oLog.info(sMsg)
        barre = bpaTools.ProgressBar(len(self.geoAirspaces), 20, title=sMsg, isSilent=self.oCtrl.oLog.isSilent)
        idx = 0
        lNbChange = 0
        for o in self.geoAirspaces:
            oZone = o["properties"]
            idx+=1

            #Flag all not valid area
            oGeom:dict = o["geometry"]                              #Sample - "geometry": {"type": "Polygon", "coordinates": [[[3.069444, 45.943611], [3.539167, 45.990556], ../..
            if oGeom["type"] in ["Point"] and oGeom["coordinates"]==errLocalisationPoint:
                oZone.update({"excludeAirspaceNotCoord":True})       #Flag this change in catalog
                lNbChange+=1

            #if oZone["freeFlightZone"]:
            if oGeom["type"] in ["Point","LineString"]:
                exclude=True
            elif len(oGeom["coordinates"][0])<3:
                exclude=True
            else:
                exclude=False
            if exclude:
                oZone.update({"freeFlightZone":False})              #Change value in catalog
                if oZone.get("freeFlightZoneExt", False)==True:
                    oZone.update({"freeFlightZoneExt":False})       #Change value in catalog
                oZone.update({"excludeAirspaceNotFfArea":True})     #Flag this change in catalog
                oZone.update({"geometryType":oGeom["type"]})        #info for catalog "Point" or "LineString"
                lNbChange+=1
            barre.update(idx)
        barre.reset()

        if lNbChange>0:
            self.oAirspacesCatalog.saveAirspacesCalalog()               #Save the new catalogs

        self.oAirspacesCatalog.cleanAirspacesCalalog = True  #Marqueur de traitement réalisé
        return
