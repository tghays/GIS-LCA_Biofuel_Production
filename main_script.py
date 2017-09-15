from __future__ import division, print_function
import arcpy, sys, os, math, datetime, time
import pandas as pd

#Main directory (dir) must have 'Ref_Files' folder inside

#***REQUIRED ARGUMENTS***
#Argument 1: location of main directory
root_dir = sys.argv[1]
#Argument 2: specify CG or SWG feedstock
feedstock = sys.argv[2]

arcpy.env.overwriteOutput = True
arcpy.CreateFileGDB_management(root_dir, 'scratch.gdb')
scratch_dir = root_dir + 'scratch.gdb'
fs_transport_dir = arcpy.CreateFeatureDataset_management(scratch_dir, 'fs_transport_routes', root_dir + 'Ref_Files/biorefinery/cbf_proj.prj')

arcpy.env.workspace = scratch_dir
arcpy.env.overwriteOutput = True
ref_dir = root_dir + 'Ref_Files/'

biorefinery = ref_dir + 'biorefinery/CBF_proj.shp'

########## Get Life Cycle Impacts ##########
# Feedstock impacts are in ( kg impact / ha- 25 years )
# establishment impacts
est_impacts_csv = ref_dir + 'impact_csv/establishment_impacts.csv'
est_impacts_df = pd.DataFrame.from_csv(est_impacts_csv)
est_impacts = list(est_impacts_df[feedstock])

# maintenance and harvest impacts
mh_impacts_csv = ref_dir + 'impact_csv/maint_harvest_impacts.csv'
mh_impacts_df = pd.DataFrame.from_csv(mh_impacts_csv)
mh_impacts = list(mh_impacts_df[feedstock])

# Adding Establishment and Maintenance & Harvest Impacts
total_fs_impacts = [E + H for E,H in zip(est_impacts, mh_impacts)]

# transportation impacts - for establishment, maint & harvest, and fuel distribution stages - in ( kg impact / t*km )
transport_impacts_csv = ref_dir + 'impact_csv/transport_impacts.csv'
transport_impacts_df = pd.DataFrame.from_csv(transport_impacts_csv)
transport_impacts = list(transport_impacts_df['impact/tkm'])

# biorefinery impacts
bio_impacts_csv = ref_dir + 'impact_csv/biorefinery_impacts.csv'
bio_impacts_df = pd.DataFrame.from_csv(bio_impacts_csv)
bio_impacts = list(bio_impacts_df[feedstock])

# fuel distribution route
fuel_dist_route_file = ref_dir + 'fuel_dist/fuel_dist_route.shp'
fuel_dist_route_geo = arcpy.da.SearchCursor(fuel_dist_route_file, ['SHAPE@']).next()[0]

# get shapefiles for feedstock
if feedstock == 'pine':
    farm_polygons = ref_dir + 'main_feedstock/pine/pine_fill1ha_20ac_50%_CB.shp'
    farm_centroid = ref_dir + 'main_feedstock/pine/pine_centroid.shp'
    fs_transport_routes = ref_dir + 'feedstock_transport/pine_routes.shp'
    collection_radius = '75 miles'
    farm_yield = 88.06 # green tonnes/hectare
elif feedstock == 'swg':
    farm_polygons = ref_dir + 'main_feedstock/swg/swg_fill2ac_10ac_50%_CB.shp'
    farm_centroid = ref_dir + 'main_feedstock/swg/swg_centroid.shp'
    fs_transport_routes = ref_dir + 'feedstock_transport/swg_routes.shp'
    collection_radius = '65 miles'
    farm_yield = 21.76 # green tonnes/hectare
elif feedstock == '50-50':
    # [pine files, swg files]
    farm_polygons = [ref_dir + 'main_feedstock/50-50_mix/pine_fill2ac_20ac_50%_MIX_CB.shp', ref_dir + 'main_feedstock/50-50_mix/swg_fill2ac_10ac_50%_MIX_CB.shp']
    farm_centroid = [ref_dir + 'main_feedstock/50-50_mix/pine_MIX_centroid.shp', ref_dir + 'main_feedstock/50-50_mix/swg_MIX_centroid.shp']
    fs_transport_routes = [ref_dir + 'feedstock_transport/pine_mix_routes.shp', ref_dir + 'feedstock_transport/swg_mix_routes.shp']
    collection_radius  = ['45 miles', '50 miles']
    farm_yield = [88.06, 21.76] # green tonnes/hectare
else:
    print ('Invalid feedstock')

#Quadrant File
quads = ref_dir + 'quads/2kmquad.shp'

#Spatial Reference: NAD_1983_StatePlane_North_Carolina_FIPS_3200_Feet
sr = arcpy.SpatialReference(2264)
g = arcpy.Geometry()


####################    START LOOP FOR MIXED FEEDSTOCK HERE     #####################


#Transport emissions associated with 1 tkm of truck transport using Diesel fuel. Format is [GWA, AA, HHPA, EA, SA, HHC,HHNC]. Kg of impact/tkm
fs_transport_impacts = [2.46E-01, 1.50E-03, 1.10E-04, 2.28E-04, 4.24E-02, 7.57E-09, 3.42E-08]
# feedstock transportation cursor
global fs_transport_route_cursor
fs_transport_route_cursor = arcpy.da.SearchCursor(fs_transport_routes, ['SHAPE@', 'SHAPE@XY', 'FID'])



# get biorefinery geometry token
global bio_geo
bio_geo = arcpy.da.SearchCursor(biorefinery, ['SHAPE@']).next()[0]



#Create product Directories
arcpy.CreateFolder_management(root_dir, '/{0}_Products'.format(feedstock))
product_dir = root_dir + '/{0}_Products/'.format(feedstock)

# Create product files based on quadrant size
arcpy.MakeFeatureLayer_management(quads, 'quad_layer')
total_quads = arcpy.CopyFeatures_management('quad_layer', product_dir + '/total.shp')

# select quads within collection basket
arcpy.SelectLayerByLocation_management('quad_layer', 'WITHIN_A_DISTANCE', bio_geo, collection_radius, 'NEW_SELECTION')

est_quads = arcpy.CopyFeatures_management('quad_layer', product_dir + 'establishment.shp')
mh_quads = arcpy.CopyFeatures_management('quad_layer', product_dir + 'maintenance_harvest.shp')
fs_transport_quads = arcpy.CopyFeatures_management('quad_layer', product_dir + 'feedstock_transport.shp')
#Transportation quadrant layer creation to determine feedstock transportation route from each farmland.
arcpy.MakeFeatureLayer_management(fs_transport_quads, 'fs_transport_layer')

# select quads around biorefinery and save to biorefinery.shp
arcpy.SelectLayerByLocation_management('quad_layer', 'CONTAINS', bio_geo, '', 'NEW_SELECTION')
arcpy.SelectLayerByLocation_management('quad_layer', 'WITHIN_A_DISTANCE', 'quad_layer', '4 kilometers', 'NEW_SELECTION')
bio_quads = arcpy.CopyFeatures_management('quad_layer', product_dir + 'biorefinery.shp')

arcpy.Delete_management('centroid_layer')


# -------------- GET FUEL DISTRIBUTION QUAD SHAPEFILES ---------------
fuel_dist_quads_ref = ref_dir + 'fuel_dist/fuel_dist_quads.shp'
fuel_dist_quads = arcpy.CopyFeatures_management(fuel_dist_quads_ref, product_dir + 'fuel_dist.shp')

# get count of feedstock polygons
fs_quads = int(str(arcpy.GetCount_management(farm_centroid)))

#Dictionary definitions for each life cycle stage, to retain impact values.  Key = quadrant FID, Values = impact values for quadrant
total_impacts_dict = {}
est_impacts_dict = {}
mh_impacts_dict = {}
fs_transport_impacts_dict = {}
bio_impacts_dict = {}
fuel_dist_impacts_dict = {}

#Variables for tracking totals
total_farm_area_ha = 0
total_fs_tkm = 0
total_fs_yield_green_tons = 0
total_fs_transport_distance_km = 0

# percent of total impact distributed to primary, secondary, and tertiary quadrants
quad_1_percent = .307917889
quad_2_percent = .051319648
quad_3_percent = .017595308

###############################################################################################################
#  define function to get feedstock transportation routes
def getClosestRoute(local_farm_geometry, local_farm_FID):
    fs_transport_route_cursor.reset()
    min_dist_to_route = 9999999999
    # iterate through 12 main routes
    for fs_route in fs_transport_route_cursor:
        first_route_geometry = fs_route[0]
        route_query = first_route_geometry.queryPointAndDistance(local_farm_geometry)
        route_dist_to_farm = route_query[2]
        # check if distance from farm to closest route point is shorter than previous point
        if route_dist_to_farm < min_dist_to_route:
            min_dist_to_route = route_dist_to_farm
            # save geometry of the current route
            total_route_geometry = first_route_geometry
            # get intercept point on route line that is closest to feedstock polygon centroid
            intercept_point_geo = route_query[0]
    # get distance from feedstock polygon centroid to biorefinery and check if shorter than distance from feedstock polygon centroid to closest route
    dist_to_biorefinery = local_farm_geometry.distanceTo(bio_geo)


    if dist_to_biorefinery > min_dist_to_route and abs(dist_to_biorefinery - min_dist_to_route) > 1:
        # print ('route type: farm to itermediate route')
        intercept_point = intercept_point_geo.firstPoint
        # get point from feedstock polygon centroid
        local_farm_point = farm_geometry.firstPoint
        # create line between the intercept point and the farm point
        array = arcpy.Array([local_farm_point, intercept_point])
        centroid_to_route_line = arcpy.Polyline(array, sr)
        # split main route at the intercept point
        split_line = arcpy.SplitLineAtPoint_management(total_route_geometry, intercept_point_geo, 'in_memory/split_line')
        # get line segment closest to the biorefinery
        line_split_cursor = arcpy.da.SearchCursor(split_line, ['SHAPE@'])
        segment_min_dist = 9999999999
        for segment in line_split_cursor:
            first_segment_geo = segment[0]
            line_dist = first_segment_geo.distanceTo(bio_geo)
            if line_dist < segment_min_dist:
                segment_min_dist = line_dist
                segment_geo = first_segment_geo
        fs_transport_route_geo = segment_geo.union(centroid_to_route_line)

        arcpy.CopyFeatures_management(fs_transport_route_geo, str(fs_transport_dir) + '\\fs_transport_route_{0}'.format(local_farm_FID))

    elif abs(dist_to_biorefinery - min_dist_to_route) < 1:
        # print ('route type: farm straight to biorefinery')
        local_farm_point = farm_geometry.firstPoint
        array = arcpy.Array([local_farm_point, bio_geo.firstPoint])
        fs_transport_route_geo = arcpy.Polyline(array, sr)
        arcpy.CopyFeatures_management(fs_transport_route_geo, str(fs_transport_dir) + '\\fs_transport_route_bio_{0}'.format(local_farm_FID))

    return fs_transport_route_geo

###############################################################################################################


# *******TIME******
t0 = datetime.datetime.now()
print ('Number of farm polygons: {0} - initiating time'.format(fs_quads))
#sys.stderr.write('Number of farm polygons: {0} - initiating time'.format(fs_quads))
# *******TIME******

feedstock_polygon = 1 #Number farmland tracker
#-----------Calculate Impacts from ESTABLISHMENT & MAINTENANCE/HARVEST stages ----------
farm_centroid_cursor = arcpy.da.SearchCursor(farm_centroid, ['FID', 'SHAPE@', 'hectare'])
global farm_FID

feedstock_errors = 0

for farm in farm_centroid_cursor:
    try:
        farm_FID = farm[0]
        farm_geometry = farm[1]
        farm_area = farm[2] # Farm area in hectares
        total_farm_area_ha += farm_area # add to total farm area


    ##### DETERMINING FEEDSTOCK PRODUCTION IMPACTS #####
        print ('get fs polygon impact quads for polygon {0}'.format(feedstock_polygon))

        # get primary quad for feedstock polygon
        arcpy.SelectLayerByLocation_management('quad_layer', 'CONTAINS', farm_geometry, '', 'NEW_SELECTION')
        primary_quad = arcpy.CopyFeatures_management('quad_layer', 'in_memory/primary_quad')
        # get secondary quads for feedstock polygon
        arcpy.SelectLayerByLocation_management('quad_layer', 'BOUNDARY_TOUCHES', primary_quad, '', 'NEW_SELECTION')
        arcpy.SelectLayerByLocation_management('quad_layer', 'CONTAINS', farm_geometry, '', 'REMOVE_FROM_SELECTION')
        secondary_quads = arcpy.CopyFeatures_management('quad_layer','in_memory/secondary_quad')
        # get tertiary quads for feedstock polygon
        arcpy.SelectLayerByLocation_management('quad_layer', 'CROSSED_BY_THE_OUTLINE_OF', secondary_quads, '', 'NEW_SELECTION')
        arcpy.SelectLayerByLocation_management('quad_layer', 'WITHIN_A_DISTANCE', primary_quad, '1 kilometers', 'REMOVE_FROM_SELECTION')
        tertiary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/tertiary_quads')

        # get FID list of quadrants for each radius from emitter
        primary_quad_FID = [int(f[0]) for f in arcpy.da.SearchCursor(primary_quad, ['quadSource'])][0]
        secondary_quad_FID_list = [int(f[0]) for f in arcpy.da.SearchCursor(secondary_quads, ['quadSource'])]
        tertiary_quad_FID_list = [int(f[0]) for f in arcpy.da.SearchCursor(tertiary_quads, ['quadSource'])]

    # scale impacts based on feedstock production area
        # scale impacts to farm area
        farm_est_impacts                = [farm_area * x for x in est_impacts]
        farm_mh_impacts                 = [farm_area * x for x in mh_impacts]
        farm_total_fs_impacts           = [farm_area * x for x in total_fs_impacts]
        # scale impacts for primary quadrants
        primary_farm_est_impacts        = [quad_1_percent * x for x in farm_est_impacts]
        primary_farm_mh_impacts         = [quad_1_percent * x for x in farm_mh_impacts]
        primary_farm_total_fs_impacts   = [quad_1_percent * x for x in farm_total_fs_impacts]
        # scale impacts for secondary quadrants
        secondary_farm_est_impacts      = [quad_2_percent * x for x in farm_est_impacts]
        secondary_farm_mh_impacts       = [quad_2_percent * x for x in farm_mh_impacts]
        secondary_farm_total_fs_impacts = [quad_2_percent * x for x in farm_total_fs_impacts]
        # scale impacts for tertiary quadrants
        tertiary_farm_est_impacts       = [quad_3_percent * x for x in farm_est_impacts]
        tertiary_farm_mh_impacts        = [quad_3_percent * x for x in farm_mh_impacts]
        tertiary_farm_total_fs_impacts  = [quad_3_percent * x for x in farm_total_fs_impacts]

    # write impacts to dictionaries
        # write primary quadrant impacts
        key = primary_quad_FID
        if key in est_impacts_dict:
            est_impacts_dict[key] = [est_impacts_dict[key][i] + primary_farm_est_impacts[i] for i in xrange(len(est_impacts_dict[key]))]
        else:
            est_impacts_dict[key] = primary_farm_est_impacts
        if key in mh_impacts_dict:
            mh_impacts_dict[key] = [mh_impacts_dict[key][i] + primary_farm_mh_impacts[i] for i in xrange(len(mh_impacts_dict[key]))]
        else:
            mh_impacts_dict[key] = primary_farm_mh_impacts
        if key in total_impacts_dict:
            total_impacts_dict[key] = [total_impacts_dict[key][i] + primary_farm_total_fs_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
        else:
            total_impacts_dict[key] = primary_farm_total_fs_impacts
        del key

        # write secondary quadrant impacts
        for key in secondary_quad_FID_list:
            if key in est_impacts_dict:
                est_impacts_dict[key] = [est_impacts_dict[key][i] + secondary_farm_est_impacts[i] for i in xrange(len(est_impacts_dict[key]))]
            else:
                est_impacts_dict[key] = secondary_farm_est_impacts
            if key in mh_impacts_dict:
                mh_impacts_dict[key] = [mh_impacts_dict[key][i] + secondary_farm_mh_impacts[i] for i in xrange(len(mh_impacts_dict[key]))]
            else:
                mh_impacts_dict[key] = secondary_farm_mh_impacts
            if key in total_impacts_dict:
                total_impacts_dict[key] = [total_impacts_dict[key][i] + secondary_farm_total_fs_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
            else:
                total_impacts_dict[key] = secondary_farm_total_fs_impacts
        del key

        # write tertiary quadrant impacts
        for key in tertiary_quad_FID_list:
            if key in est_impacts_dict:
                est_impacts_dict[key] = [est_impacts_dict[key][i] + tertiary_farm_est_impacts[i] for i in xrange(len(est_impacts_dict[key]))]
            else:
                est_impacts_dict[key] = tertiary_farm_est_impacts
            if key in mh_impacts_dict:
                mh_impacts_dict[key] = [mh_impacts_dict[key][i] + tertiary_farm_mh_impacts[i] for i in xrange(len(mh_impacts_dict[key]))]
            else:
                mh_impacts_dict[key] = tertiary_farm_mh_impacts
            if key in total_impacts_dict:
                total_impacts_dict[key] = [total_impacts_dict[key][i] + tertiary_farm_total_fs_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
            else:
                total_impacts_dict[key] = tertiary_farm_total_fs_impacts
        del key

        # *******TIME******
        t01 = datetime.datetime.now()
        c= t01-t0
        min = divmod(c.total_seconds(), 60)[0]
        sec = divmod(c.total_seconds(), 60)[1]
        print ('Impacts for feedstock polygon {0}/{1} ({4}%) complete - elapsed Time: {2} min {3} seconds. \nStart transportation calculations. \n'.format(feedstock_polygon, fs_quads, min, sec, str((float(feedstock_polygon) / float(fs_quads))*100)[:4]))
        #sys.stderr.write('Impacts for feedstock polygon {0}/{1} ({4}%) complete. Start transportation calculations. Elapsed Time: {2} min {3} seconds'.format(feedstock_polygon, fs_quads, min, sec, str((float(feedstock_polygon) / float(fs_quads))*100)[:4]))
        # *******TIME******


    ##### DETERMINING FEEDSTOCK TRANSPORTATION IMPACTS #####
        print ('determine fs transportation route')
        t_time_0 = time.time()

        # get feedstock transportation route
        fs_transport_route_geo = getClosestRoute(farm_geometry, farm_FID)
        fs_transport_route_dist = fs_transport_route_geo.length * 0.0003048 # convert from ft to km

        # calculate metrics and add to totals
        local_farm_yield = farm_area * farm_yield # feedstock yield from farm, calculated with farm_area
        total_fs_yield_green_tons += local_farm_yield
        total_fs_transport_distance_km += fs_transport_route_dist
        local_fs_tkm = local_farm_yield * fs_transport_route_dist
        total_fs_tkm += local_fs_tkm

        # calculate local fs transportation impacts
        local_fs_transport_impacts = [local_fs_tkm * i for i in transport_impacts]

        t_time_1 = time.time()
        print ('getting primary quadrants for transportation route {0} secs'.format(str(t_time_1 - t_time_0)[:5]))

        #Get primary quadrants intersecting feedstock transportation route
        arcpy.SelectLayerByLocation_management('quad_layer', 'INTERSECT', fs_transport_route_geo, '', 'NEW_SELECTION')
        fs_transport_primary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/fs_transport_primary_quad')
        fs_transport_primary_quad_FID_list = [f[0] for f in arcpy.da.SearchCursor(fs_transport_primary_quads, ['quadSource'])]
        fs_transport_primary_quad_geo_list = [f[0] for f in arcpy.da.SearchCursor(fs_transport_primary_quads, ['SHAPE@'])]

        t_time_2 = time.time()
        print ('getting secondary quadrants for transportation route  {0} secs'.format(str(t_time_2 - t_time_0)[:5]))

        # get secondary quadrants and tertiary quadrant FID by looping through primary quads
        fs_transport_secondary_quad_FID_list = []
        fs_transport_tertiary_quad_FID_list = []
        fs_primary_quad_count = 1
        for fs_transport_primary_quad_geo in fs_transport_primary_quad_geo_list:
            # get secondary quadrants
            arcpy.SelectLayerByLocation_management('quad_layer', 'BOUNDARY_TOUCHES', fs_transport_primary_quad_geo, '', 'NEW_SELECTION')
            arcpy.SelectLayerByLocation_management('quad_layer', 'ARE_IDENTICAL_TO', fs_transport_primary_quad_geo, '', 'REMOVE_FROM_SELECTION')
            fs_transport_secondary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/fs_transport_secondary_quads')
            fs_transport_secondary_quad_FID_list.extend([f[0] for f in arcpy.da.SearchCursor(fs_transport_secondary_quads, ['quadSource'])])
            # get tertiary quadrants
            arcpy.SelectLayerByLocation_management('quad_layer', 'WITHIN_A_DISTANCE', fs_transport_primary_quad_geo, '3 kilometers', 'NEW_SELECTION')
            arcpy.SelectLayerByLocation_management('quad_layer', 'WITHIN_A_DISTANCE', fs_transport_primary_quad_geo, '1 kilometers', 'REMOVE_FROM_SELECTION')
            fs_transport_tertiary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/fs_transport_tertiary_quads')
            fs_transport_tertiary_quad_FID_list.extend([f[0] for f in arcpy.da.SearchCursor(fs_transport_tertiary_quads, ['quadSource'])])

            t_time_3 = time.time()
            print('\rsecondary/tertiary quads determined for fs polygon {0}  -  {1}% complete'.format(fs_primary_quad_count, str((float(fs_primary_quad_count) / float(len(fs_transport_primary_quad_geo_list)))*100)[:4]), end= '\r')
            fs_primary_quad_count += 1


        t_time_4 = time.time()
        print ('calculating fs transportation route impacts {0} secs'.format(str(t_time_4 - t_time_0)[:5]))

        # calculate scaled fs transportation impacts for primary quads
        # divide fs transportation impacts for the whole route between each primary quadrant
        fs_transport_quad_division_impacts  = [x / len(fs_transport_primary_quad_FID_list) for x in local_fs_transport_impacts]

        # multiply by the percentage of impacts allocated to primary quadrants
        fs_transport_primary_quad_impacts   = [x * quad_1_percent for x in fs_transport_quad_division_impacts]
        fs_transport_secondary_quad_impacts = [x * quad_2_percent for x in fs_transport_quad_division_impacts]
        fs_transport_tertiary_quad_impacts  = [x * quad_3_percent for x in fs_transport_quad_division_impacts]

        t_time_5 = time.time()
        print ('writing fs transportation values to dicts {0} secs'.format(str(t_time_5 - t_time_0)[:5]))

        # write primary quad impacts to fs transport impact and total impact dictionaries
        for key in fs_transport_primary_quad_FID_list:
            if key in fs_transport_impacts_dict:
                fs_transport_impacts_dict[key] = [fs_transport_impacts_dict[key][i] + fs_transport_primary_quad_impacts[i] for i in xrange(len(fs_transport_impacts_dict[key]))]
            else:
                fs_transport_impacts_dict[key] = fs_transport_primary_quad_impacts
            if key in total_impacts_dict:
                total_impacts_dict[key] = [total_impacts_dict[key][i] + fs_transport_primary_quad_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
            else:
                total_impacts_dict[key] = fs_transport_primary_quad_impacts
        del key

        # write secondary quad impacts to fs transport impact and total impact dictionaries
        for key in fs_transport_secondary_quad_FID_list:
            if key in fs_transport_impacts_dict:
                fs_transport_impacts_dict[key] = [fs_transport_impacts_dict[key][i] + fs_transport_secondary_quad_impacts[i] for i in xrange(len(fs_transport_impacts_dict[key]))]
            else:
                fs_transport_impacts_dict[key] = fs_transport_secondary_quad_impacts
            if key in total_impacts_dict:
                total_impacts_dict[key] = [total_impacts_dict[key][i] + fs_transport_secondary_quad_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
            else:
                total_impacts_dict[key] = fs_transport_secondary_quad_impacts
        del key

        # write tertiary quad impacts to fs transport impact and total impact dictionaries
        for key in fs_transport_tertiary_quad_FID_list:
            if key in fs_transport_impacts_dict:
                fs_transport_impacts_dict[key] = [fs_transport_impacts_dict[key][i] + fs_transport_tertiary_quad_impacts[i] for i in xrange(len(fs_transport_impacts_dict[key]))]
            else:
                fs_transport_impacts_dict[key] = fs_transport_tertiary_quad_impacts
            if key in total_impacts_dict:
                total_impacts_dict[key] = [total_impacts_dict[key][i] + fs_transport_tertiary_quad_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
            else:
                total_impacts_dict[key] = fs_transport_tertiary_quad_impacts
        del key

        feedstock_polygon += 1

        # --------------------------------------

    except:
        time.sleep(.5)
        feedstock_errors += 1
        continue

# *******TIME******
t02 = datetime.datetime.now()
c= t02-t0
min = divmod(c.total_seconds(), 60)[0]
sec = divmod(c.total_seconds(), 60)[1]
print ('Feedstock and fs transportation impacts complete for polygon {0}/{1} - ({4}%) complete, elapsed time {2} min {3} seconds. \nStart biorefinery impact calculations. \n'.format(feedstock_polygon, fs_quads, min, sec, str((float(feedstock_polygon) / float(fs_quads))*100)[:4]))
#arcpy.AddMessage('Feedstock and fs transportation impacts complete for polygon {0}/{1} - ({4}%) complete. Start biorefinery impact calculations. Elapsed time {2} min {3} seconds'.format(feedstock_polygon, fs_quads, min, sec, str((float(feedstock_polygon) / float(fs_quads))*100)[:4]))
# *******TIME******


##### DETERMINING BIOREFINERY IMPACTS #####

# calculate biorefinery impacts for quadrant levels
bio_impacts_primary   = [quad_1_percent * x for x in bio_impacts]
bio_impacts_secondary = [quad_2_percent * x for x in bio_impacts]
bio_impacts_tertiary  = [quad_3_percent * x for x in bio_impacts]

# get bio primary quads
arcpy.SelectLayerByLocation_management('quad_layer', 'CONTAINS', bio_geo, '', 'NEW_SELECTION')
bio_primary_quad = arcpy.CopyFeatures_management('quad_layer', 'in_memory/bio_primary_quad')
# get bio secondary quads
arcpy.SelectLayerByLocation_management('quad_layer', 'BOUNDARY_TOUCHES', bio_primary_quad, '', 'NEW_SELECTION')
arcpy.SelectLayerByLocation_management('quad_layer', 'CONTAINS', bio_primary_quad, '', 'REMOVE_FROM_SELECTION')
bio_secondary_quads = arcpy.CopyFeatures_management('quad_layer','in_memory/bio_secondary_quads')
# get bio tertiary quads
arcpy.SelectLayerByLocation_management('quad_layer', 'CROSSED_BY_THE_OUTLINE_OF', bio_secondary_quads, '', 'NEW_SELECTION')
arcpy.SelectLayerByLocation_management('quad_layer', 'WITHIN_A_DISTANCE', bio_primary_quad, '1 kilometers', 'REMOVE_FROM_SELECTION')
bio_tertiary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/bio_tertiary_quads')

bio_primary_quad_FID = [int(f[0]) for f in arcpy.da.SearchCursor(bio_primary_quad, ['quadSource'])][0]
bio_secondary_quad_FID_list = [int(f[0]) for f in arcpy.da.SearchCursor(bio_secondary_quads, ['quadSource'])]
bio_tertiary_quad_FID_list = [int(f[0]) for f in arcpy.da.SearchCursor(bio_tertiary_quads, ['quadSource'])]

# write bio impacts to biorefinery and total impacts dictionary
# write primary bio impacts
key = bio_primary_quad_FID
bio_impacts_dict[key] = bio_impacts_primary
if key in total_impacts_dict:
    total_impacts_dict[key] = [total_impacts_dict[key][i] + bio_impacts_primary[i] for i in xrange(len(total_impacts_dict[key]))]
else:
    total_impacts_dict[key] = bio_impacts_primary
del key
# write secondary bio impacts
for key in bio_secondary_quad_FID_list:
    bio_impacts_dict[key] = bio_impacts_secondary
    if key in total_impacts_dict:
        total_impacts_dict[key] = [total_impacts_dict[key][i] + bio_impacts_secondary[i] for i in xrange(len(total_impacts_dict[key]))]
    else:
        total_impacts_dict[key] = bio_impacts_secondary
del key
# write tertiary bio impacts
for key in bio_tertiary_quad_FID_list:
    bio_impacts_dict[key] = bio_impacts_tertiary
    if key in total_impacts_dict:
        total_impacts_dict[key] = [total_impacts_dict[key][i] + bio_impacts_tertiary[i] for i in xrange(len(total_impacts_dict[key]))]
    else:
        total_impacts_dict[key] = bio_impacts_tertiary
del key

print ('biorefinery impact calcluations complete, determining fuel distribution impacts')

##### DETERMINING FUEL DISTRIBUTION IMPACTS #####
fuel_product_csv = ref_dir + 'impact_csv/fuel_dist_tkm.csv'
fuel_product_df = pd.DataFrame.from_csv(fuel_product_csv)
fuel_dist_tkm = fuel_product_df[feedstock][0]
fuel_dist_impacts = [fuel_dist_tkm * x for x in transport_impacts]

arcpy.SelectLayerByLocation_management('quad_layer', 'INTERSECT', fuel_dist_route_geo, '', 'NEW_SELECTION')
fuel_dist_primary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/fuel_dist_primary_quad')
fuel_dist_primary_quad_FID_list = [f[0] for f in arcpy.da.SearchCursor(fuel_dist_primary_quads, ['quadSource'])]
fuel_dist_primary_quad_geo_list = [f[0] for f in arcpy.da.SearchCursor(fuel_dist_primary_quads, ['SHAPE@'])]

# get secondary quadrants and tertiary quadrant FID by looping through primary quads
fuel_dist_secondary_quad_FID_list = []
fuel_dist_tertiary_quad_FID_list = []

for fuel_dist_primary_quad_geo in fuel_dist_primary_quad_geo_list:
    # get secondary quadrants
    arcpy.SelectLayerByLocation_management('quad_layer', 'BOUNDARY_TOUCHES', fuel_dist_primary_quad_geo, '', 'NEW_SELECTION')
    arcpy.SelectLayerByLocation_management('quad_layer', 'ARE_IDENTICAL_TO', fuel_dist_primary_quad_geo, '', 'REMOVE_FROM_SELECTION')
    fuel_dist_secondary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/fuel_dist_secondary_quads')
    fuel_dist_secondary_quad_FID_list.extend([f[0] for f in arcpy.da.SearchCursor(fuel_dist_secondary_quads, ['quadSource'])])
    # get tertiary quadrants
    arcpy.SelectLayerByLocation_management('quad_layer', 'WITHIN_A_DISTANCE', fuel_dist_primary_quad_geo, '3 kilometers', 'NEW_SELECTION')
    arcpy.SelectLayerByLocation_management('quad_layer', 'WITHIN_A_DISTANCE', fuel_dist_primary_quad_geo, '1 kilometers', 'REMOVE_FROM_SELECTION')
    fuel_dist_tertiary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/fs_transport_tertiary_quads')
    fuel_dist_tertiary_quad_FID_list.extend([f[0] for f in arcpy.da.SearchCursor(fuel_dist_tertiary_quads, ['quadSource'])])

    # calculate scaled fuel dist impacts for primary quads
    # divide fuel dist impacts for the whole route between each primary quadrant
    fuel_dist_quad_division_impacts  = [x / len(fuel_dist_primary_quad_FID_list) for x in fuel_dist_impacts]

    # multiply by the percentage of impacts allocated to primary quadrants
    fuel_dist_primary_quad_impacts   = [x * quad_1_percent for x in fuel_dist_quad_division_impacts]
    fuel_dist_secondary_quad_impacts = [x * quad_2_percent for x in fuel_dist_quad_division_impacts]
    fuel_dist_tertiary_quad_impacts  = [x * quad_3_percent for x in fuel_dist_quad_division_impacts]

    # write primary quad impacts to fuel dist impact and total impact dictionaries
for key in fuel_dist_primary_quad_FID_list:
    if key in fuel_dist_impacts_dict:
        fuel_dist_impacts_dict[key] = [fuel_dist_impacts_dict[key][i] + fuel_dist_primary_quad_impacts[i] for i in xrange(len(fuel_dist_impacts_dict[key]))]
    else:
        fuel_dist_impacts_dict[key] = fuel_dist_primary_quad_impacts
    if key in total_impacts_dict:
        total_impacts_dict[key] = [total_impacts_dict[key][i] + fuel_dist_primary_quad_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
    else:
        total_impacts_dict[key] = fuel_dist_primary_quad_impacts
del key

# write secondary quad impacts to fuel dist impact and total impact dictionaries
for key in fuel_dist_secondary_quad_FID_list:
    if key in fuel_dist_impacts_dict:
        fuel_dist_impacts_dict[key] = [fuel_dist_impacts_dict[key][i] + fuel_dist_secondary_quad_impacts[i] for i in xrange(len(fuel_dist_impacts_dict[key]))]
    else:
        fuel_dist_impacts_dict[key] = fuel_dist_secondary_quad_impacts
    if key in total_impacts_dict:
        total_impacts_dict[key] = [total_impacts_dict[key][i] + fuel_dist_secondary_quad_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
    else:
        total_impacts_dict[key] = fuel_dist_secondary_quad_impacts
del key

# write tertiary quad impacts to fuel dist impact and total impact dictionaries
for key in fuel_dist_tertiary_quad_FID_list:
    if key in fuel_dist_impacts_dict:
        fuel_dist_impacts_dict[key] = [fuel_dist_impacts_dict[key][i] + fuel_dist_tertiary_quad_impacts[i] for i in xrange(len(fuel_dist_impacts_dict[key]))]
    else:
        fuel_dist_impacts_dict[key] = fuel_dist_tertiary_quad_impacts
    if key in total_impacts_dict:
        total_impacts_dict[key] = [total_impacts_dict[key][i] + fuel_dist_tertiary_quad_impacts[i] for i in xrange(len(total_impacts_dict[key]))]
    else:
        total_impacts_dict[key] = fuel_dist_tertiary_quad_impacts
del key

print('Calculations complete, saving impact values to each life cycle stage shapefile')
#-----------------------------------CALCULATIONS COMPLETE-----------------------------------
#-------------WRITING IMPACTS FOR EACH LIFE CYCLE STAGE TO A UNIQUE SHAPEFILE-----

# writing impact values from feedstock establishment to shapefile
est_quad_cursor = arcpy.da.UpdateCursor(est_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for est_quad in est_quad_cursor:
    quad_fid = est_quad[0]
    if quad_fid in est_impacts_dict:
        est_quad[1:] = est_impacts_dict[quad_fid]
        est_quad_cursor.updateRow(est_quad)
del est_quad_cursor
del quad_fid

# writing impact values from feedstock maintenance and harvest to shapefile
mh_quad_cursor = arcpy.da.UpdateCursor(mh_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for mh_quad in mh_quad_cursor:
    quad_fid = mh_quad[0]
    if quad_fid in mh_impacts_dict:
        mh_quad[1:] = mh_impacts_dict[quad_fid]
        mh_quad_cursor.updateRow(mh_quad)
del mh_quad_cursor
del quad_fid

# writing impact values from feedstock transportation to shapefile
fs_transport_quad_cursor = arcpy.da.UpdateCursor(fs_transport_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for fs_transport_quad in fs_transport_quad_cursor:
    quad_fid = fs_transport_quad[0]
    if quad_fid in fs_transport_impacts_dict:
        fs_transport_quad[1:] = fs_transport_impacts_dict[quad_fid]
        fs_transport_quad_cursor.updateRow(fs_transport_quad)
del fs_transport_quad_cursor
del quad_fid

# writing impact values from biorefinery to shapefile
bio_quad_cursor = arcpy.da.UpdateCursor(bio_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for bio_quad in bio_quad_cursor:
    quad_fid = bio_quad[0]
    if quad_fid in bio_impacts_dict:
        bio_quad[1:] = bio_impacts_dict[quad_fid]
        bio_quad_cursor.updateRow(bio_quad)
del bio_quad_cursor
del quad_fid

# writing impact values from fuel distribution to shapefile
fuel_dist_quad_cursor = arcpy.da.UpdateCursor(fuel_dist_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for fuel_dist_quad in fuel_dist_quad_cursor:
    quad_fid = fuel_dist_quad[0]
    if quad_fid in fuel_dist_impacts_dict:
        fuel_dist_quad[1:] = fuel_dist_impacts_dict[quad_fid]
        fuel_dist_quad_cursor.updateRow(fuel_dist_quad)
del fuel_dist_quad_cursor
del quad_fid

#Writing total impacts to shapefile
total_quad_cursor = arcpy.da.UpdateCursor(total_quads, ['FID', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for total_quad in total_quad_cursor:
    quad_fid = total_quad[0]
    if quad_fid in total_impacts_dict:
        total_quad[1:] = total_impacts_dict[quad_fid]
        total_quad_cursor.updateRow(total_quad)
del total_quad_cursor
del quad_fid


#----------TEXT FILE: Writing transportation data to text file, in 'Products' directory------------------------
out_file = open(product_dir + '/runInfo.text', 'w')
out_file.write('total farm area = ' + str(total_farm_area_ha) +'\n'+ 'total feedstock tkm = ' + str(total_fs_tkm) \
              +'\n'+ 'total feedstock yield (green tonnes) = ' + str(total_fs_yield_green_tons) \
              +'\n'+ 'total fs transport distance (km) = ' + str(total_fs_transport_distance_km) \
               + '\n' + 'skipped feedstock polygons = {0}'.format(feedstock_errors))
out_file.close()
del out_file

#******TIME*********
t6 = datetime.datetime.now()
c= t6-t0
min = divmod(c.total_seconds(), 60)[0]
sec = divmod(c.total_seconds(), 60)[1]
print ('Script complete. Total runtime: {0} min {1} seconds'.format(min, sec))
sys.stderr.write('Script complete. Total runtime: {0} min {1} seconds'.format(min, sec))
#******TIME*********




# TESTING

'''
# testing describe function
test_t0 = datetime.datetime.now()
arcpy.SelectLayerByLocation_management('quad_layer', 'INTERSECT', fs_transport_route_geo, '', 'NEW_SELECTION')
fidset = arcpy.Describe('quad_layer').fidset
fidset_list = [float(x) for x in fidset.split('; ')]
test_t1 = datetime.datetime.now()
print (fidset_list)
print (test_t1 - test_t0)

# testing cursor function
test_t0 = datetime.datetime.now()
arcpy.SelectLayerByLocation_management('quad_layer', 'INTERSECT', fs_transport_route_geo, '', 'NEW_SELECTION')
fidset_list = [f[0] for f in arcpy.da.SearchCursor('quad_layer', ['quadSource'])]
test_t1 = datetime.datetime.now()
print (fidset_list)
print (test_t1 - test_t0)


# geometry testing
test_t0 = datetime.datetime.now()
arcpy.SelectLayerByLocation_management('quad_layer', 'INTERSECT', fs_transport_route_geo, '', 'NEW_SELECTION')
fs_transport_primary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/fs_transport_primary_quad')
fs_transport_primary_quad_geo_list = [f[0] for f in arcpy.da.SearchCursor(fs_transport_primary_quads, ['SHAPE@'])]
test_t1 = datetime.datetime.now()
print (test_t1 - test_t0)

test_t0 = datetime.datetime.now()
arcpy.SelectLayerByLocation_management('quad_layer', 'INTERSECT', fs_transport_route_geo, '', 'NEW_SELECTION')
fs_transport_primary_quads = arcpy.CopyFeatures_management('quad_layer', 'in_memory/fs_transport_primary_quad')
fs_transport_primary_quad_geo_list = arcpy.CopyFeatures_management('quad_layer', g)
test_t1 = datetime.datetime.now()
print (test_t1 - test_t0)
'''
