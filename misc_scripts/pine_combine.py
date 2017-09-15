import arcpy, sys, os, math, datetime, time

root_dir = '<root>/GIS_pine/'

pine1_dir = root_dir + 'GIS_pine1/pine_Products/'
pine2_dir = root_dir + 'GIS_pine2/pine_Products/'
product_dir = root_dir + 'pine_combine/'

lc_stages = ['establishment', 'feedstock_transport', 'maintenance_harvest']

total_impacts_dict = {}
est_impacts_dict = {}
mh_impacts_dict = {}
fs_transport_impacts_dict = {}

for stage in lc_stages:
    pine1 = pine1_dir + stage + '.shp'
    pine2 = pine2_dir + stage + '.shp'

    if stage == 'establishment':
        print ('starting establishment summations')
        pine1_cursor = arcpy.da.SearchCursor(pine1, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        pine2_cursor = arcpy.da.SearchCursor(pine2, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])

        print ('pine 1 shape = {0}'.format(pine1))
        print ('pine 2 shape = {0}'.format(pine2))

        # get pine1 impacts
        for pine1 in pine1_cursor:
            pine1_fid = pine1[0]
            pine1_impacts = pine1[1:]
            if pine1_fid in est_impacts_dict:
                est_impacts_dict[pine1_fid] = [est_impacts_dict[pine1_fid][i] + pine1_impacts[i] for i in xrange(len(est_impacts_dict[pine1_fid]))]
            else:
                est_impacts_dict[pine1_fid] = pine1_impacts
               
            if pine1_fid in total_impacts_dict:
                total_impacts_dict[pine1_fid] = [total_impacts_dict[pine1_fid][i] + pine1_impacts[i] for i in xrange(len(total_impacts_dict[pine1_fid]))]
            else:
                total_impacts_dict[pine1_fid] = pine1_impacts
        del pine1_cursor
        del pine1_fid
        del pine1_impacts

        # get pine2 impacts
        for pine2 in pine2_cursor:
            pine2_fid = pine2[0]
            pine2_impacts = pine2[1:]
            if pine2_fid in est_impacts_dict:
                est_impacts_dict[pine2_fid] = [est_impacts_dict[pine2_fid][i] + pine2_impacts[i] for i in xrange(len(est_impacts_dict[pine2_fid]))]
            else:
                est_impacts_dict[pine2_fid] = pine2_impacts
               
            if pine2_fid in total_impacts_dict:
                total_impacts_dict[pine2_fid] = [total_impacts_dict[pine2_fid][i] + pine2_impacts[i] for i in xrange(len(total_impacts_dict[pine2_fid]))]
            else:
                total_impacts_dict[pine2_fid] = pine2_impacts
        del pine2_cursor
        del pine2_fid
        del pine2_impacts

        print ('establishment complete')


    elif stage == 'feedstock_transport':
        print ('starting feedstock transport summations')
        pine1_cursor = arcpy.da.SearchCursor(pine1, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        pine2_cursor = arcpy.da.SearchCursor(pine2, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        
        print ('pine 1 shape = {0}'.format(pine1))
        print ('pine 2 shape = {0}'.format(pine2))
                
        # get pine1 impacts
        for pine1 in pine1_cursor:
            pine1_fid = pine1[0]
            pine1_impacts = pine1[1:]
            if pine1_fid in fs_transport_impacts_dict:
                fs_transport_impacts_dict[pine1_fid] = [fs_transport_impacts_dict[pine1_fid][i] + pine1_impacts[i] for i in xrange(len(fs_transport_impacts_dict[pine1_fid]))]
            else:
                fs_transport_impacts_dict[pine1_fid] = pine1_impacts
               
            if pine1_fid in total_impacts_dict:
                total_impacts_dict[pine1_fid] = [total_impacts_dict[pine1_fid][i] + pine1_impacts[i] for i in xrange(len(total_impacts_dict[pine1_fid]))]
            else:
                total_impacts_dict[pine1_fid] = pine1_impacts
        del pine1_cursor
        del pine1_fid
        del pine1_impacts

        # get pine2 impacts
        for pine2 in pine2_cursor:
            pine2_fid = pine2[0]
            pine2_impacts = pine2[1:]
            if pine2_fid in fs_transport_impacts_dict:
                fs_transport_impacts_dict[pine2_fid] = [fs_transport_impacts_dict[pine2_fid][i] + pine2_impacts[i] for i in xrange(len(fs_transport_impacts_dict[pine2_fid]))]
            else:
                fs_transport_impacts_dict[pine2_fid] = pine2_impacts
               
            if pine2_fid in total_impacts_dict:
                total_impacts_dict[pine2_fid] = [total_impacts_dict[pine2_fid][i] + pine2_impacts[i] for i in xrange(len(total_impacts_dict[pine2_fid]))]
            else:
                total_impacts_dict[pine2_fid] = pine2_impacts
        del pine2_cursor
        del pine2_fid
        del pine2_impacts

        print ('feedstock transport complete')


    elif stage == 'maintenance_harvest':
        print ('starting maintenance/harvest summations')
        
        pine1_cursor = arcpy.da.SearchCursor(pine1, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        pine2_cursor = arcpy.da.SearchCursor(pine2, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        
        print ('pine 1 shape = {0}'.format(pine1))
        print ('pine 2 shape = {0}'.format(pine2))
        

        # get pine1 impacts
        for pine1 in pine1_cursor:
            pine1_fid = pine1[0]
            pine1_impacts = pine1[1:]
            if pine1_fid in mh_impacts_dict:
                mh_impacts_dict[pine1_fid] = [mh_impacts_dict[pine1_fid][i] + pine1_impacts[i] for i in xrange(len(mh_impacts_dict[pine1_fid]))]
            else:
                mh_impacts_dict[pine1_fid] = pine1_impacts
               
            if pine1_fid in total_impacts_dict:
                total_impacts_dict[pine1_fid] = [total_impacts_dict[pine1_fid][i] + pine1_impacts[i] for i in xrange(len(total_impacts_dict[pine1_fid]))]
            else:
                total_impacts_dict[pine1_fid] = pine1_impacts
        del pine1_cursor
        del pine1_fid
        del pine1_impacts

        # get pine2 impacts
        for pine2 in pine2_cursor:
            pine2_fid = pine2[0]
            pine2_impacts = pine2[1:]
            if pine2_fid in mh_impacts_dict:
                mh_impacts_dict[pine2_fid] = [mh_impacts_dict[pine2_fid][i] + pine2_impacts[i] for i in xrange(len(mh_impacts_dict[pine2_fid]))]
            else:
                mh_impacts_dict[pine2_fid] = pine2_impacts
               
            if pine2_fid in total_impacts_dict:
                total_impacts_dict[pine2_fid] = [total_impacts_dict[pine2_fid][i] + pine2_impacts[i] for i in xrange(len(total_impacts_dict[pine2_fid]))]
            else:
                total_impacts_dict[pine2_fid] = pine2_impacts
        del pine2_cursor
        del pine2_fid
        del pine2_impacts

        print ('maintenance/harvest complete')


print ('getting biorefinery impacts')
biorefinery = product_dir + 'biorefinery.shp'
bio_cursor = arcpy.da.SearchCursor(biorefinery, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for bio_quad in bio_cursor:
    bio_fid = bio_quad[0]
    bio_impacts = bio_quad[1:]

    if bio_fid in total_impacts_dict:
        total_impacts_dict[bio_fid] = [total_impacts_dict[bio_fid][i] + bio_impacts[i] for i in xrange(len(total_impacts_dict[bio_fid]))]
    else:
        total_impacts_dict[bio_fid] = bio_impacts
del bio_cursor

print ('getting fuel dist impacts')
fuel_dist = product_dir + 'fuel_dist.shp'
fuel_dist_cursor = arcpy.da.SearchCursor(fuel_dist, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for fd_quad in fuel_dist_cursor:
    fd_fid = fd_quad[0]
    fd_impacts = fd_quad[1:]
    
    if fd_fid in total_impacts_dict:
        total_impacts_dict[fd_fid] = [total_impacts_dict[fd_fid][i] + fd_impacts[i] for i in xrange(len(total_impacts_dict[fd_fid]))]
    else:
        total_impacts_dict[fd_fid] = fd_impacts
del fuel_dist_cursor

print ('summations complete, writing to shapefiles')


est_quads = product_dir + 'establishment.shp'
est_quad_cursor = arcpy.da.UpdateCursor(est_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for est_quad in est_quad_cursor:
    quad_fid = est_quad[0]
    if quad_fid in est_impacts_dict:
        est_quad[1:] = est_impacts_dict[quad_fid]
        est_quad_cursor.updateRow(est_quad)
del est_quad_cursor
del quad_fid


mh_quads = product_dir + 'maintenance_harvest.shp'
mh_quad_cursor = arcpy.da.UpdateCursor(mh_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for mh_quad in mh_quad_cursor:
    quad_fid = mh_quad[0]
    if quad_fid in mh_impacts_dict:
        mh_quad[1:] = mh_impacts_dict[quad_fid]
        mh_quad_cursor.updateRow(mh_quad)
del mh_quad_cursor
del quad_fid


fs_transport_quads = product_dir + 'feedstock_transport.shp'
fs_transport_quad_cursor = arcpy.da.UpdateCursor(fs_transport_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for fs_transport_quad in fs_transport_quad_cursor:
    quad_fid = fs_transport_quad[0]
    if quad_fid in fs_transport_impacts_dict:
        fs_transport_quad[1:] = fs_transport_impacts_dict[quad_fid]
        fs_transport_quad_cursor.updateRow(fs_transport_quad)
del fs_transport_quad_cursor
del quad_fid


total_quads = product_dir + 'total.shp'
total_quad_cursor = arcpy.da.UpdateCursor(total_quads, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
for total_quad in total_quad_cursor:
    quad_fid = total_quad[0]
    if quad_fid in total_impacts_dict:
        total_quad[1:] = total_impacts_dict[quad_fid]
        total_quad_cursor.updateRow(total_quad)
del total_quad_cursor
del quad_fid
