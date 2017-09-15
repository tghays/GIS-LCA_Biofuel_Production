import arcpy, sys, os, math, datetime, time

root_dir = <mix directory>

pine_dir = root_dir + 'pine_mix/'
swg_dir = root_dir + 'swg_mix/'
ref_dir = root_dir + 'Ref_Files/'
product_dir = root_dir + 'products/'

lc_stages = ['establishment', 'feedstock_transport', 'maintenance_harvest']

total_impacts_dict = {}
est_impacts_dict = {}
mh_impacts_dict = {}
fs_transport_impacts_dict = {}

for stage in lc_stages:
    pine_shp = pine_dir + stage + '.shp'
    swg_shp = swg_dir + stage + '.shp'

    if stage == 'establishment':
        print ('starting establishment summations')
        pine_cursor = arcpy.da.SearchCursor(pine_shp, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        swg_cursor = arcpy.da.SearchCursor(swg_shp, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])

        print ('pine shape = {0}'.format(pine_shp))
        print ('swg shape = {0}'.format(swg_shp))

        for pine in pine_cursor:
            pine_fid = pine_cursor[0]
            pine_impacts = pine_cursor[1:]
            if pine_fid in est_impacts_dict:
                est_impacts_dict[pine_fid] = [est_impacts_dict[pine_fid][i] + pine_impacts[i] for i in xrange(len(est_impacts_dict[pine_fid]))]
            else:
                est_impacts_dict[pine_fid] = pine_impacts
                
            if pine_fid in total_impacts_dict:
                total_impacts_dict[pine_fid] = [total_impacts_dict[pine_fid][i] + pine_impacts[i] for i in xrange(len(total_impacts_dict[pine_fid]))]
            else:
                total_impacts_dict[pine_fid] = pine_impacts
        del pine_cursor
        del pine_fid

        for swg in swg_cursor:
            swg_fid = swg_cursor[0]
            swg_impacts = swg_cursor[1:]
            if swg_fid in est_impacts_dict:
                est_impacts_dict[swg_fid] = [est_impacts_dict[swg_fid][i] + swg_impacts[i] for i in xrange(len(est_impacts_dict[swg_fid]))]
            else:
                est_impacts_dict[swg_fid] = swg_impacts

            if swg_fid in total_impacts_dict:
                total_impacts_dict[swg_fid] = [total_impacts_dict[swg_fid][i] + swg_impacts[i] for i in xrange(len(total_impacts_dict[swg_fid]))]
            else:
                total_impacts_dict[swg_fid] = swg_impacts
        del swg_cursor
        del swg_fid

        print ('establishment complete')


    elif stage == 'feedstock_transport':
        print ('starting feedstock transport summations')
        pine_cursor = arcpy.da.SearchCursor(pine_shp, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        swg_cursor = arcpy.da.SearchCursor(swg_shp, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        
        print ('pine shape = {0}'.format(pine_shp))
        print ('swg shape = {0}'.format(swg_shp))
        
        for pine in pine_cursor:
            pine_fid = pine_cursor[0]
            pine_impacts = pine_cursor[1:]
            if pine_fid in fs_transport_impacts_dict:
                fs_transport_impacts_dict[pine_fid] = [fs_transport_impacts_dict[pine_fid][i] + pine_impacts[i] for i in xrange(len(fs_transport_impacts_dict[pine_fid]))]
            else:
                fs_transport_impacts_dict[pine_fid] = pine_impacts
                
            if pine_fid in total_impacts_dict:
                total_impacts_dict[pine_fid] = [total_impacts_dict[pine_fid][i] + pine_impacts[i] for i in xrange(len(total_impacts_dict[pine_fid]))]
            else:
                total_impacts_dict[pine_fid] = pine_impacts
        del pine_cursor
        del pine_fid

        for swg in swg_cursor:
            swg_fid = swg_cursor[0]
            swg_impacts = swg_cursor[1:]
            if swg_fid in fs_transport_impacts_dict:
                fs_transport_impacts_dict[swg_fid] = [fs_transport_impacts_dict[swg_fid][i] + swg_impacts[i] for i in xrange(len(fs_transport_impacts_dict[swg_fid]))]
            else:
                fs_transport_impacts_dict[swg_fid] = swg_impacts

            if swg_fid in total_impacts_dict:
                total_impacts_dict[swg_fid] = [total_impacts_dict[swg_fid][i] + swg_impacts[i] for i in xrange(len(total_impacts_dict[swg_fid]))]
            else:
                total_impacts_dict[swg_fid] = swg_impacts
        del swg_cursor
        del swg_fid

        print ('feedstock transport complete')


    elif stage == 'maintenance_harvest':
        print ('starting maintenance/harvest summations')
        pine_cursor = arcpy.da.SearchCursor(pine_shp, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        swg_cursor = arcpy.da.SearchCursor(swg_shp, ['quadSource', 'GWA', 'AA','HHPA','EA','SA', 'HHC','HHNC'])
        print ('pine shape = {0}'.format(pine_shp))
        print ('swg shape = {0}'.format(swg_shp))

        for pine in pine_cursor:
            pine_fid = pine_cursor[0]
            pine_impacts = pine_cursor[1:]
            if pine_fid in mh_impacts_dict:
                mh_impacts_dict[pine_fid] = [mh_impacts_dict[pine_fid][i] + pine_impacts[i] for i in xrange(len(mh_impacts_dict[pine_fid]))]
            else:
                mh_impacts_dict[pine_fid] = pine_impacts
                
            if pine_fid in total_impacts_dict:
                total_impacts_dict[pine_fid] = [total_impacts_dict[pine_fid][i] + pine_impacts[i] for i in xrange(len(total_impacts_dict[pine_fid]))]
            else:
                total_impacts_dict[pine_fid] = pine_impacts
        del pine_cursor
        del pine_fid

        for swg in swg_cursor:
            swg_fid = swg_cursor[0]
            swg_impacts = swg_cursor[1:]
            if swg_fid in mh_impacts_dict:
                mh_impacts_dict[swg_fid] = [mh_impacts_dict[swg_fid][i] + swg_impacts[i] for i in xrange(len(mh_impacts_dict[swg_fid]))]
            else:
                mh_impacts_dict[swg_fid] = swg_impacts

            if swg_fid in total_impacts_dict:
                total_impacts_dict[swg_fid] = [total_impacts_dict[swg_fid][i] + swg_impacts[i] for i in xrange(len(total_impacts_dict[swg_fid]))]
            else:
                total_impacts_dict[swg_fid] = swg_impacts
        del swg_cursor
        del swg_fid

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