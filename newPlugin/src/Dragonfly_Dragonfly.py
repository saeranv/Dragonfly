# This is the heart of Dragonfly
#
# Dragonfly: A Plugin for Climate Data Generation (GPL) started by Chris Mackey <chris@ladybug.tools> 
# 
# This file is part of Dragonfly.
# 
# Copyright (c) 2015, Chris Mackey <chris@ladybug.tools> 
# Dragonfly is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Dragonfly is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
This component carries all of Dragonfly's main classes. Other components refer to these
classes to run the studies. Therefore, you need to let her fly before running the studies so the
classes will be copied to Rhinos shared space. So let her fly!

-
Dragonfly: A Plugin for Environmental Analysis (GPL) started by Chris Mackey
You should have received a copy of the GNU General Public License
along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

Source code is available at: https://github.com/mostaphaRoudsari/ladybug

-
Provided by Dragonfly 0.0.02
    Args:
        defaultFolder_: Optional input for Dragonfly default folder.
                       If empty default folder will be set to C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug\
    Returns:
        report: Current Dragonfly mood!!!
"""

ghenv.Component.Name = "Dragonfly_Dragonfly"
ghenv.Component.NickName = 'Dragonfly'
ghenv.Component.Message = 'VER 0.0.02\nAPR_29_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "0 | Dragonfly"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import math
import os
import System
System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
import datetime
import zipfile
import copy

PI = math.pi
rc.Runtime.HostUtils.DisplayOleAlerts(False)


class CheckIn():
    
    def __init__(self, defaultFolder, folderIsSetByUser = False):
        
        self.folderIsSetByUser = folderIsSetByUser
        self.letItFly = True
        
        if defaultFolder:
            # user is setting up the folder
            defaultFolder = os.path.normpath(defaultFolder) + os.sep
            
            # check if path has white space
            if (" " in defaultFolder):
                msg = "Default file path can't have white space. Please set the path to another folder." + \
                      "\nDragonfly failed to fly! :("
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                sc.sticky["Dragonfly_DefaultFolder"] = ""
                self.letItFly = False
                return
            else:
                # create the folder if it is not created
                if not os.path.isdir(defaultFolder):
                    try: os.mkdir(defaultFolder)
                    except:
                        msg = "Cannot create default folder! Try a different filepath" + \
                              "\Dragonfly failed to fly! :("
                        print msg
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        sc.sticky["Dragonfly_DefaultFolder"] = ""
                        self.letItFly = False
                        return
            
            # looks fine so let's set it up
            sc.sticky["Dragonfly_DefaultFolder"] = defaultFolder
            self.folderIsSetByUser = True
        
        #set up default pass
        if not self.folderIsSetByUser:
            if os.path.exists("c:\\ladybug\\") and os.access(os.path.dirname("c:\\ladybug\\"), os.F_OK):
                # folder already exists so it is all fine
                sc.sticky["Dragonfly_DefaultFolder"] = "c:\\ladybug\\"
            elif os.access(os.path.dirname("c:\\"), os.F_OK):
                #the folder does not exists but write privileges are given so it is fine
                sc.sticky["Dragonfly_DefaultFolder"] = "c:\\ladybug\\"
            else:
                # let's use the user folder
                username = os.getenv("USERNAME")
                # make sure username doesn't have space
                if (" " in username):
                    msg = "User name on this system: " + username + " has white space." + \
                          " Default fodelr cannot be set.\nUse defaultFolder_ to set the path to another folder and try again!" + \
                          "\nDragonfly failed to fly! :("
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    sc.sticky["Dragonfly_DefaultFolder"] = ""
                    self.letItFly = False
                    return
                
                sc.sticky["Dragonfly_DefaultFolder"] = os.path.join("C:\\Users\\", username, "AppData\\Roaming\\Ladybug\\")
    
    def getComponentVersion(self):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        ver, verDate = ghenv.Component.Message.split("\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
        
    def isNewerVersionAvailable(self, currentVersion, availableVersion):
        # print int(availableVersion.replace(".", "")), int(currentVersion.replace(".", ""))
        return int(availableVersion.replace(".", "")) > int(currentVersion.replace(".", ""))
    
    def checkForUpdates(self, DF = True):
        
        url = "https://github.com/mostaphaRoudsari/ladybug/raw/master/resources/versions.txt"
        versionFile = os.path.join(sc.sticky["Dragonfly_DefaultFolder"], "versions.txt")
        client = System.Net.WebClient()
        client.DownloadFile(url, versionFile)
        with open("c:/ladybug/versions.txt", "r")as vf:
            versions= eval("\n".join(vf.readlines()))
        
        if DF:
            dragonflyVersion = versions['Dragonfly']
            currentDragonflyVersion = self.getComponentVersion()
            if self.isNewerVersionAvailable(currentDragonflyVersion, dragonflyVersion):
                msg = "There is a newer version of Dragonfly available to download! " + \
                      "We strongly recommend you to download the newer version from the Dragonfly github: " + \
                      "https://github.com/chriswmackey/Dragonfly/archive/master.zip"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)

checkIn = CheckIn(defaultFolder_)



class versionCheck(object):
    
    def __init__(self):
        self.version = self.getVersion(ghenv.Component.Message)
    
    def getVersion(self, LBComponentMessage):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        try: ver, verDate = LBComponentMessage.split("\n")
        except: ver, verDate = LBComponentMessage.split("\\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
    
    def isCurrentVersionNewer(self, desiredVersion):
        return int(self.version.replace(".", "")) >= int(desiredVersion.replace(".", ""))
    
    def isCompatible(self, LBComponent):
        code = LBComponent.Code
        # find the version that is supposed to be flying
        try: version = code.split("compatibleLBVersion")[1].split("=")[1].split("\n")[0].strip()
        except: self.giveWarning(LBComponent)
        
        desiredVersion = self.getVersion(version)
        
        if not self.isCurrentVersionNewer(desiredVersion):
            self.giveWarning(LBComponent)
            return False
        
        return True
        
    def giveWarning(self, GHComponent):
        warningMsg = "You need a newer version of Dragonfly to use this compoent." + \
                     "Use updateDragonfly component to update userObjects.\n" + \
                     "If you have already updated userObjects drag Dragonfly_Dragonfly component " + \
                     "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        GHComponent.AddRuntimeMessage(w, warningMsg)


class df_findFolders(object):
    
    def __init__(self):
        self.UWGPath, self.UWGFile = self.which('UWGEngine.exe')
    
    def which(self, program):
        """
        Check for path. Modified from this link:
        http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
        """
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        
        fpath, fname = os.path.split(program)
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return path, exe_file
        return None, None


class UWGGeometry(object):
    
    def __init(self):
        self.groundProjection = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane.WorldXY)
    
    # function to get the center point and normal of surfaces.
    def getSrfCenPtandNormal(self, surface):
        """Extracts the center point and normal from a surface.
        
        Args:
            surface: A rhino surface to extract points from.
        Returns:
            centerPt: The center point of the surface.
            normalVector: The normal of the surface.
        
        """
        
        brepFace = surface.Faces[0]
        if brepFace.IsPlanar and brepFace.IsSurface:
            u_domain = brepFace.Domain(0)
            v_domain = brepFace.Domain(1)
            centerU = (u_domain.Min + u_domain.Max)/2
            centerV = (v_domain.Min + v_domain.Max)/2
            
            centerPt = brepFace.PointAt(centerU, centerV)
            normalVector = brepFace.NormalAt(centerU, centerV)
        else:
            centroid = rc.Geometry.AreaMassProperties.Compute(brepFace).Centroid
            uv = brepFace.ClosestPoint(centroid)
            centerPt = brepFace.PointAt(uv[1], uv[2])
            normalVector = brepFace.NormalAt(uv[1], uv[2])
        
        return centerPt, normalVector
    
    def separateBrepSrfs(self, brep, maxRoofAngle=45, maxFloorAngle=60):
        """Separates the surfaces of a brep into those facing up, down and sideways
        
        Args:
            brep: A closed rhino brep representing a building.
            maxRoofAngle: The roof normal angle from the positive Z axis (in degrees) beyond 
                which a surface is no longer considered a roof. Default is 45.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond 
                which a surface is no longer considered a floor. Default is 60.
        
        Returns:
            down: The brep surfaces facing down.
            up: The brep surfaces facing up.
            side: The brep surfaces facing to the side.
            sideNormals: The normals of the surfaces facing to the side.
            roofNormals: The normals of the surfaces facing upwards.
            bottomNormVectors: The normals of the surfaces facing down.
            bottomCentPts: The genter points of the surfaces facing down.
        """
        
        up = []
        down = []
        side = []
        bottomNormVectors = []
        bottomCentPts = []
        roofNormals = []
        sideNormals = []
        for i in range(brep.Faces.Count):
            surface = brep.Faces[i].DuplicateFace(False)
            # find the normal
            findNormal = self.getSrfCenPtandNormal(surface)
            
            #Get the angle to the Z-axis
            if findNormal:
                normal = findNormal[1]
                angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normal, rc.Geometry.Vector3d.ZAxis))
            else:
                angle2Z = 0
            
            if  angle2Z < maxRoofAngle or angle2Z > 360- maxRoofAngle:
                up.append(surface)
                roofNormals.append((90 - angle2Z)/90)
            elif  180 - maxFloorAngle < angle2Z < 180 + maxFloorAngle:
                down.append(surface)
                bottomNormVectors.append(normal)
                bottomCentPts.append(findNormal[0])
            else:
                side.append(surface)
                sideNormals.append((90 - angle2Z)/90)
        
        return down, up, side, sideNormals, roofNormals, bottomNormVectors, bottomCentPts
    
    def unionAllBreps(self, bldgBreps):
        """Unioned breps into one so that correct facade areas can be computed.
        
        Args:
            bldgBreps: A list of closed rhino brep representing a building.
        
        Returns:
            result: The building breps after being unioned.
        """
        
        result = []
        for i in range(0, len(bldgBreps), 2):
            try:
                x = bldgBreps[i]
                y = bldgBreps[i + 1]
                x.Faces.SplitKinkyFaces(rc.RhinoMath.DefaultAngleTolerance, False)
                y.Faces.SplitKinkyFaces(rc.RhinoMath.DefaultAngleTolerance, False)
                a = rc.Geometry.Brep.CreateBooleanUnion([x, y], sc.doc.ModelAbsoluteTolerance)
                if a == None:
                    a = [bldgBreps[i], bldgBreps[i + 1]]
            except:
                a = [bldgBreps[i]]
            
            if a:
                result.extend(a)
        
        return result
    
    def calculateBldgFootprint(self, bldgBrep, maxFloorAngle=60):
        """Extracts building footprint and footprint area
        
        Args:
            bldgBrep: A closed rhino brep representing a building.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond 
                which a surface is no longer considered a floor. Default is 60.
        
        Returns:
            footprintArea: The footprint area of the building.
            footprintBrep: A Brep representing the footprint of the building.
        """
        
        # separate out the surfaces of the building brep.
        footPrintBreps, upSrfs, sideSrfs, sideNormals, roofNormals, bottomNormVectors, bottomCentPts = \
            self.separateBrepSrfs(bldgBrep, 45, maxFloorAngle)
        
        # check to see if there are any building breps that self-intersect once they are projected into the XYPlane. 
        # if so, the building cantilevers over itslef and we have to use an alternative method to get the footprint.
        meshedBrep = rc.Geometry.Mesh.CreateFromBrep(bldgBrep, rc.Geometry.MeshingParameters.Coarse)
        selfIntersect = False
        for count, normal in enumerate(bottomNormVectors):
            srfRay = rc.Geometry.Ray3d(bottomCentPts[count], normal)
            for mesh in meshedBrep:
                intersectTest = rc.Geometry.Intersect.Intersection.MeshRay(mesh, srfRay)
                if intersectTest <= sc.doc.ModelAbsoluteTolerance: pass
                else: selfIntersect = True
        
        if selfIntersect == True:
            # Use any downward-facing surfaces that we can identify as part of the building footprint.
            # Boolean them together to get the projected area.
            groundBreps = []
            for srf in footPrintBreps:
                srf.Transform(self.groundProjection)
                groundBreps.append(srf)
            booleanSrf = rc.Geometry.Brep.CreateBooleanUnion(groundBreps, sc.doc.ModelAbsoluteTolerance)[0]
            footprintBrep = booleanSrf
            footprintArea = rc.Geometry.AreaMassProperties.Compute(booleanSrf).Area
        else:
            #Project the whole building brep into the X/Y plane and take half its area.
            brepCopy = copy.deepcopy(bldgBrep)
            brepCopy.Transform(self.groundProjection)
            footprintBrep = brepCopy
            footprintArea = rc.Geometry.AreaMassProperties.Compute(brepCopy).Area/2
        
        return footprintArea, footprintBrep
    
    def extractBldgHeight(self, bldgBrep):
        """Extracts building height
        
        Args:
            bldgBrep: A closed rhino brep representing a building.
        
        Returns:
            bldgHeight: The height of the building.
        """
        
        bldgBBox = rc.Geometry.Brep.GetBoundingBox(bldgBrep, rc.Geometry.Plane.WorldXY)
        bldgHeight = bldgBBox.Diagonal[2]
        
        return bldgHeight
    
    def extractBldgFacades(self, bldgBreps, maxRoofAngle=45, maxFloorAngle=60):
        """Extracts building facades and facade area
        
        Args:
            bldgBrep: A closed rhino brep representing a building.
            maxRoofAngle: The roof normal angle from the positive Z axis (in degrees) beyond 
                which a surface is no longer considered a roof. Default is 45.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond 
                which a surface is no longer considered a floor. Default is 60.
        
        Returns:
            facadeArea: The footprint area of the building.
            facadeBreps: A list if breps representing the facades of the building.
        """
        
        facadeAreas = []
        facadeBreps = []
        
        for bldgBrep in bldgBreps:
            # separate out the surfaces of the building brep.
            footPrintBreps, upSrfs, sideSrfs, sideNormals, roofNormals, bottomNormVectors, bottomCentPts = \
                self.separateBrepSrfs(bldgBrep, maxRoofAngle, maxFloorAngle)
            
            # calculate the facade area
            facadeBreps.extend(sideSrfs)
            fArea = 0
            for srf in sideSrfs:
                fArea += rc.Geometry.AreaMassProperties.Compute(srf).Area
        
        facadeArea = sum(facadeAreas)
        
        return facadeArea, facadeBreps
    
    def calculateTypologyGeoParams(self, bldgBreps, maxRoofAngle=45, maxFloorAngle=60):
        """Extracts building footprint and footprint area
        
        Args:
            bldgBreps: A list of closed rhino brep representing buildings of the same typology.
            maxRoofAngle: The roof normal angle from the positive Z axis (in degrees) beyond 
                which a surface is no longer considered a roof. Default is 45.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond 
                which a surface is no longer considered a floor. Default is 60.
        
        Returns:
            avgBldgHeight: The average height of the buildings in the typology
            footprintArea: The footprint area of the buildings in this typology.
            facadeArea: The facade are of the buildings in this typology.
            footprintBreps: A list of breps representing the footprints of the buildings.
            facadeBreps: A list of breps representing the exposed facade surfaces of the typology.
        """
        
        bldgHeights = []
        footprintAreas = []
        footprintBreps = []
        
        for bldgBrep in bldgBreps:
            # get the building height
            bldgHeights.append(self.extractBldgHeight(bldgBrep))
            
            # get the footprint area
            ftpA, ftpBrep = self.calculateBldgFootprint(bldgBreps, maxFloorAngle)
            footprintAreas.append(ftpA)
            footprintBreps.append(ftpBrep)
        
        # get the area-weighted hieght of the buildings and total footprint area
        footprintArea = sum(footprintAreas)
        footprintWeights = [y/footprintArea for y in footprintAreas]
        avgBldgHeight = sum([x*footprintWeights[i] for x,i in enumerate(bldgHeights)])
        
        # compute the facade area of all of the building breps after they have been boolean unioned.
        unionedBreps = self.unionAllBreps(bldgBreps)
        facadeArea, facadeBreps = self.extractBldgFacades(bldgBreps, maxRoofAngle, maxFloorAngle)
        
        return avgBldgHeight, footprintArea, facadeArea, footprintBreps, facadeBreps


class BuildingTypology(object):
    """Represents a group of buildings of the same typology in an urban area.
    
    Attributes:
        average_height: The average height of the buildings of this typology in meters.
        footprint_area: The footprint area of the buildings of this typology in square meteres.
        facade_area: The facade area of the buildings of this typology in square meters.
        bldg_program: A text string representing one of the 16 DOE building program types to be 
            used as a template for this typology.  Choose from the following options:
                FullServiceRestaurant
                Hospital
                LargeHotel
                LargeOffice
                MediumOffice
                MidRiseApartment
                OutPatient
                PrimarySchool
                QuickServiceRestaurant
                SecondarySchool
                SmallHotel
                SmallOffice
                StandAloneRetail
                StripMall
                SuperMarket
                Warehouse
        bldg_age: A text string that sets the age of the buildings represented by this typology.  
            This is used to determine what constructions make up the walls, roofs, and windows based on international building codes over the last several decades.  Choose from the following options:
                Pre1980s
                1980sPresent
                NewConstruction
        glz_ratio: An optional number from 0 to 1 that represents the fraction of the walls of the building typology that are glazed.
            If none, a default of 0.4 is used
        roof_albedo: An optional number from 0 to 1 that represents the albedo (or reflectivity) of the roof.
            If none, a default of 0.5 will be used.
        roof_veg_fraction: An optional number from 0 to 1 that represents the fraction of the roof that is vegetated.
            If none, a default of 0 is used.
    """
    
    def __init__(self, average_height, footprint_area, facade_area, bldg_program, 
                bldg_age, glz_ratio=None, roof_albedo=None, roof_veg_fraction=None):
        """Initialize a dragonfly building typology"""
        
        # critical geometry parameters that all typologies must have.
        self.average_height = float(average_height)
        self.footprint_area = float(footprint_area)
        self.facade_area = float(facade_area)
        
        # optional parameters with default values.
        if glz_ratio is not None:
            if self.inRange(glz_ratio, 0, 1):
                self.glz_ratio = float(glz_ratio)
            else:
                raise ValueError(
                    "glz_ratio must be between 0 and 1. Current value is {}".format(str(glz_ratio))
                )
        else:
            self.glz_ratio = 0.4
        if roof_albedo is not None:
            if self.inRange(float(roof_albedo), 0, 1):
                self.roof_albedo = float(roof_albedo)
            else:
                raise ValueError(
                    "roof_albedo must be between 0 and 1. Current value is {}".format(str(roof_albedo))
                )
        else:
            self.roof_albedo = 0.5
        if roof_veg_fraction is not None:
            if self.inRange(float(roof_veg_fraction), 0, 1):
                self.roof_veg_fraction = float(roof_veg_fraction)
            else:
                raise ValueError(
                    "roof_veg_fraction must be between 0 and 1. Current value is {}".format(str(roof_veg_fraction))
                )
        else:
            self.roof_veg_fraction = 0
        
        # dictionary of building ages.
        self.ageDict = {
            'PRE1980S': 'Pre1980s',
            '1980SPRESENT': '1980sPresent',
            'NEWCONSTRUCTION': 'NewConstruction',
            
            '0': 'Pre1980s',
            '1': '1980sPresent',
            '2': 'NewConstruction',
            
            "Pre-1980's": 'Pre1980s',
            "1980's-Present": '1980sPresent',
            'New Construction': 'NewConstruction'
        }
        
        if str(bldg_age).upper() in self.ageDict.keys():
            self.bldg_age = self.ageDict[str(bldg_age).upper()]
        else:
            raise ValueError(
                "bldg_age {} not recognized.".format(str(bldg_age))
            )
        
        # dictionary of building programs.
        self.programsDict = {
            'FULLSERVICERESTAURANT': 'FullServiceRestaurant',
            'HOSPITAL': 'Hospital',
            'LARGEHOTEL': 'LargeHotel',
            'LARGEOFFICE': 'LargeOffice',
            'MEDIUMOFFICE': 'MediumOffice',
            'MIDRISEAPARTMENT': 'MidRiseApartment',
            'OUTPATIENT': 'OutPatient',
            'PRIMARYSCHOOL': 'PrimarySchool',
            'QUICKSERVICERESTAURANT': 'QuickServiceRestaurant',
            'SECONDARYSCHOOL': 'SecondarySchool',
            'SMALLHOTEL': 'SmallHotel',
            'SMALLOFFICE': 'SmallOffice',
            'STANDALONERETAIL': 'StandAloneRetail',
            'STRIPMALL': 'StripMall',
            'SUPERMARKET': 'SuperMarket',
            'WAREHOUSE': 'Warehouse',
            
            'FULL SERVICE RESTAURANT': 'FullServiceRestaurant',
            'LARGE HOTEL': 'LargeHotel',
            'LARGE OFFICE': 'LargeOffice',
            'MEDIUM OFFICE': 'MediumOffice',
            'MIDRISE APARTMENT': 'MidRiseApartment',
            'OUT PATIENT': 'OutPatient',
            'PRIMARY SCHOOL': 'PrimarySchool',
            'QUICK SERVICE RESTAURANT': 'QuickServiceRestaurant',
            'SECONDARY SCHOOL': 'SecondarySchool',
            'SMALL HOTEL': 'SmallHotel',
            'SMALL OFFICE': 'SmallOffice',
            'STANDALONE RETAIL': 'StandAloneRetail',
            'STRIP MALL': 'StripMall',
            
            '0': 'LargeOffice',
            '1': 'StandAloneRetail',
            '2': 'MidRiseApartment',
            '3': 'PrimarySchool',
            '4': 'SecondarySchool',
            '5': 'SmallHotel',
            '6': 'LargeHotel',
            '7': 'Hospital',
            '8': 'OutPatient',
            '9': 'Warehouse',
            '10': 'SuperMarket',
            '11': 'FullServiceRestaurant',
            '12': 'QuickServiceRestaurant',
            
            'Office': 'LargeOffice',
            'Retail': 'StandAloneRetail'
        }
        
        if str(bldg_program).upper() in self.programsDict.keys():
            self.bldg_program = self.programsDict[str(bldg_program).upper()]
        else:
            raise ValueError(
                "bldg_program {} not recognized.".format(str(bldg_program))
            )
    
    def __str__(self):
        return 'Building Typology: ' + self.bldg_program + \
               '\nAverage Height: ' + str(self.average_height) + " m" + \
               '\nFootprint Area: ' + str(self.footprint_area) + " m2" + \
               '\nFacade Area: ' + str(self.facade_area) + " m2" + \
               '\n-------------------------------------'
    
    @classmethod
    def from_geometry(cls, bldg_breps, bldg_program, bldg_age, glz_ratio=None, 
        roof_albedo=None, roof_veg_fraction=None):
        geometryLib = UWGGeometry
        avgBldgHeight, footprintArea, facadeArea, footprintBreps, facadeBreps = UWGGeometry.calculateTypologyGeoParams(bldg_breps)
        
        return cls(avgBldgHeight, footprintArea, facadeArea, bldg_program, bldg_age, glz_ratio, roof_albedo, roof_veg_fraction)
    
    def inRange(val, low, high):
        if val <= high and val >= low:
            return True
        else:
            return False



try:
    checkIn.checkForUpdates(True)
except:
    # no internet connection
    pass

now = datetime.datetime.now()

def checkGHPythonVersion(target = "0.6.0.3"):
    
    currentVersion = int(ghenv.Version.ToString().replace(".", ""))
    targetVersion = int(target.replace(".", ""))
    
    if targetVersion > currentVersion: return False
    else: return True

GHPythonTargetVersion = "0.6.0.3"

try:
    if not checkGHPythonVersion(GHPythonTargetVersion):
        assert False
except:
    msg =  "Dragonfly failed to fly! :(\n" + \
           "You are using an old version of GHPython. " +\
           "Please update to version: " + GHPythonTargetVersion
    print msg
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    checkIn.letItFly = False
    sc.sticky["dragonfly_release"] = False



def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('\\')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)



if checkIn.letItFly:
    sc.sticky["dragonfly_release"] = versionCheck()       
    
    if sc.sticky.has_key("dragonfly_release") and sc.sticky["dragonfly_release"]:
        folders = df_findFolders()
        sc.sticky["dragonfly_folders"] = {}
        if folders.UWGPath == None:
            if os.path.isdir("C:\\ladybug" + "\\UWG\\"):
                folders.UWGPath = "C:\\ladybug" + "\\UWG\\"
            else:
                # Try to download these files in the background.
                try:
                    ## download File
                    print 'Downloading UWG to ', "C:\\ladybug\\UWG\\"
                    updatedLink = "https://github.com/hansukyang/UWG_Matlab/raw/master/ArchivedCodes/UWG.zip"
                    localFilePath = "C:\\ladybug" + 'UWG.zip'
                    client = System.Net.WebClient()
                    client.DownloadFile(updatedLink, localFilePath)
                    #Unzip the file
                    unzip(localFilePath, "C:\\ladybug")
                    os.rename("C:\\ladybug" + '\\UWG\\UWGEngine_mcr\\META\\', "C:\\ladybug" + '\\UWG\\UWGEngine_mcr\\.META\\')
                    folders.UWGPath = "C:\\ladybug" + "\\UWG\\"
                except:
                    msg1 = "Dragonfly failed to download the Urban Weather Generator (UWG) folder in the background.\n" + \
                         "Download the following file and unzip it into the C:\ drive of your system:"
                    msg2 = "https://github.com/hansukyang/UWG_Matlab/raw/master/ArchivedCodes/UWG.zip"
                    
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
                    
                    folders.UWGPath = ""
        
        if os.path.isdir("c:\\Program Files\\MATLAB\\MATLAB Runtime\\v90\\"):
            folders.matlabPath = "c:\\Program Files\\MATLAB\\MATLAB Runtime\\v90\\"
        else:
            
            msg3 = "Dragonfly cannot find the correct version of the Matlab Runtime Compiler v9.0 (MRC 9.0) in your system. \n" + \
            "You won't be able to morph EPW files to account for urban heat island effects without this application. \n" + \
            "You can download an installer for the the Matlab Runtime Compiler from this link on the UWG github:"
            msg4 = "https://www.mathworks.com/supportfiles/downloads/R2015b/deployment_files/R2015b/installers/win64/MCR_R2015b_win64_installer.exe"
            
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg3)
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg4)
            
            folders.matlabPath = ""
        
        sc.sticky["dragonfly_folders"]["UWGPath"] = folders.UWGPath
        sc.sticky["dragonfly_folders"]["matlabPath"] = folders.matlabPath
        sc.sticky["dragonfly_UWGGeometry"] = UWGGeometry
        
        
        print "Hi " + os.getenv("USERNAME")+ "!\n" + \
              "Dragonfly is Flying! Vviiiiiiizzz...\n\n" + \
              "Default path is set to: " + sc.sticky["Dragonfly_DefaultFolder"] + "\n" + \
              "UWGEngine path is set to: " + sc.sticky["dragonfly_folders"]["UWGPath"]