

############################################################################################################################################
import xarray as xr
import pandas as pd
import geopandas as gpd
import cfgrib
import xesmf as xe

############################################################################################################################################
def _load_climate_data(input_file_path, batch_load, batch_number):
	"""
	Loads climate data from and input file and returns it on a dataframe format.
	For the moment only grib files are accepted but this function can be adapted to cover other file formats.


    Parameters
    ----------
	input_file_path: str, Path to the climate data to be loaded
	batch_load: bool, Indicates if a batch processing should be done. Used to load heavy ECMWF datasets
	batch_number: int, In the case of batch processing, indicates which model is to be load for a ECMWF dataset

	Returns
    -------
	DataFrame, A DataFrame with the data contained in the input file

	"""

	#Load grib data into pandas dataframe. Change this function if another data format is used
	input_xr = xr.open_dataset(input_file_path, engine="cfgrib")

	#If batch_load = True, loads only one model from a ECMWF dataset
	if batch_load:
		df = input_xr.where(input_xr['number'] == batch_number, drop = True).to_dataframe().dropna().reset_index()

	else:
		df = input_xr.to_dataframe().dropna().reset_index()

	return(df)

############################################################################################################################################
def _regrid_climate_data(era5_file_path, ecmwf_file_path):
	"""
	Re-gridding of a climate dataset following a reference dataset. The result is returned as a DataFrame.
	The current version uses the xesmf package


    Parameters
    ----------
	era5_file_path: str, Path to the ERA5 climate data to be processed
	ecmwf_file_path: str, Path to the climate data file used as a reference grid (ECMWF) 

	Returns
    -------
	DataFrame, Resulting ERA5 dataset following the new grid
	
	"""

	#Re-grid of ERA5 data following the ECMWF grid (1deg)
	ds_era = xr.open_dataset(era5_file_path, engine="cfgrib")
	ds_ecmwf = xr.open_dataset(ecmwf_file_path, engine="cfgrib")
	regridder = xe.Regridder(ds_era, ds_ecmwf, "conservative")
	ds_era1deg = regridder(ds_era, keep_attrs=True)
	df = ds_era1deg.to_dataframe().dropna().reset_index()

	return(df)


############################################################################################################################################
def _create_reference_grid(input_df, admin_df, admin_code_label):
	"""
	Create a reference lat/lon grid based on the ECMWF grid. Also performs a geospatial join between the grid points and the admin boundaries.

    Parameters
    ----------
	input_df: DataFrame, Reference grid with lat/lon coordinates
	admin_df: GeoDataFrame, Admin boundaries used for aggregation analysis
	admin_code_label: str, Column name to be used as an unique admin code

	Returns
    -------
	GeoDataFrame, Reference lat/lon grid together with the link with admin boundaries 

	"""

	grid_df = input_df.copy()

	#Create point geoDataFrame from lat/lon grid. Supposes the projection EPSG:4326 
	grid_df = gpd.GeoDataFrame(grid_df, geometry=gpd.points_from_xy(grid_df.longitude, grid_df.latitude), crs="EPSG:4326")
	#Create a square buffer around the point following the grid. This is useful when doing the spatial join 
	#with admin boundaries to include pixels there are just outside of the admin boundary. Specially necessary for
	#small admin boundaries.	
	grid_df['geometry'] = grid_df['geometry'].buffer(0.5, cap_style = 3)
	
	#Rename the admin code column name
	admin_df.rename(columns = {admin_code_label: 'adm1_pcode'}, errors = 'ignore', inplace = True)

	admin_df = admin_df[['adm1_pcode','geometry']]
	#Finds all grid points that are close to the admin boundary (intersection with the square buffer)
	grid_df = grid_df.sjoin(admin_df, how="inner", predicate='intersects')
	#Returns the geometry to the lat/lon point grid
	grid_df = gpd.GeoDataFrame(grid_df, geometry=gpd.points_from_xy(grid_df.longitude, grid_df.latitude), crs="EPSG:4326")
	grid_df = grid_df[['pixel_geom_id','adm1_pcode','geometry']]


	return(grid_df)


############################################################################################################################################
def _compute_era5_climatology(input_df, geom_id_label):
	"""
	Compute the climatology per location (pixel or admin boundary) based one ERA5. The climatology includes the average
	precipitation per month but also different quantiles (50%, 33%, 25% and 20%)


    Parameters
    ----------
	input_df: DataFrame, DataFrame containing ERA5 climate data
	geom_id_label: str, Name of the column containing the unique geometry id. It can be either pixel_geom_id or adm1_pcode

	Returns
    -------
	DataFrame, Adds two set of columns (climatology_q and prob_q) to the input DataFrame. climatology_qX is the X% precipitation quantile
	for a given location and month. prob_qX has a value of 1 (0 otherwise) if, for a given location, month and year, the precipitation level
	is below the climatology X% precipitation quantile. The name "prob" is used to keep the same nomenclature of the ECMWF dataset where an ensemble model is used

	"""
    
	df = input_df.copy()

	#Compute climatology average and quantiles (50%, 33%, 25% and 20%) for any given location and month
	climatology_era5_df = df.groupby([geom_id_label,'valid_time_month']).agg(
		climatology_avg = ('tp_mm_day',  lambda x: x.mean()),
		climatology_q50 = ('tp_mm_day',  lambda x: x.quantile(1/2)),
		climatology_q33 = ('tp_mm_day',  lambda x: x.quantile(1/3)),
		climatology_q25 = ('tp_mm_day',  lambda x: x.quantile(1/4)),
		climatology_q20 = ('tp_mm_day',  lambda x: x.quantile(1/5))).reset_index()

	df = pd.merge(df,climatology_era5_df, on = [geom_id_label,'valid_time_month'])

	#Computes, for a given location, month and year, if the precipiation level is below the corresponding climatology quantile 
	for q in ['50','33','25','20']:
		df['prob_q'+q] = (df['tp_mm_day'] <= df['climatology_q'+q])*1

	return(df)


############################################################################################################################################
def pre_process_ecmwf_data(input_file_path, admin_boundary_file_path, ref_grid_file_path, pixel_output_file_path, adm_output_file_path, admin_code_label):
	"""
	Loads the ECMWF climate data grib file and converts it to a DataFrame. Also adapt columns names, precipitation units and link grid 
	points to administrative boundaries. Finally, computes a reference grid by linking grid points to administrative boundaries. 
	The process is executed ensemble model per ensemble model (out of 51 in total) to limit memory use.


    Parameters
    ----------
	input_file_path: str, Path to the ECMWF climate data grib file to be processed
	admin_boundary_file_path: str, Path to the admin boundary file to be used when aggregating grid points
	ref_grid_file_path: str, Path where the reference grid, combining both grid points and admin boundaries link, is to be exported 
	pixel_output_file_path: str, Path where the processed file at the grid point level should be exported
	adm_output_file_path: str, Path where the processed file at the admin boundary level should be exported
	admin_code_label: str, Column name to be used as an unique admin code

	Returns
    -------
	
	"""
	#Prints out progress
	print('processing ecmwf data...')

	#Executes each ensemble model separately  
	for batch_number in range(0,51):

		#Prints out progress
		if batch_number % 10 == 0:
			print(str(batch_number) + '/50')    

		#Load ECMWF grib file and converts it to a DataFrame
		df = _load_climate_data(input_file_path, batch_load = True, batch_number = batch_number)
	    
		#Each data source uses a different unit (meters/day for ERA5 and meters/second for ECMWF). Converting both into mm/day here
		df['tp_mm_day'] = df['tprate']*1000*60*60*24 

		#Compute lead time in months for ECMWF
		df['lead_time'] = 0
		for lead_days in df['step'].unique():
			lead_months = round(float(str(lead_days).split(" ")[0])/30) # converting lead time in days into months
			df.loc[df['step'] == lead_days, 'lead_time'] = lead_months

		#Correct valid time convention - ECMWF prediction month ends on the valid_time date so there is a 1-month shift
		df['valid_time_year'] = df['valid_time'].apply(lambda x : x.year)
		df['valid_time_month'] = df['valid_time'].apply(lambda x : x.month-1)
		df.loc[df['valid_time_month'] == 0, 'valid_time_year'] = df.loc[df['valid_time_month'] == 0, 'valid_time_year'] - 1
		df.loc[df['valid_time_month'] == 0, 'valid_time_month'] = 12


		#link to reference grid and retrieve pixel hash code and admin1 pcode
		df['pixel_geom_id'] = df['latitude'].astype('str') + '-' + df['longitude'].astype('str') 
		df['pixel_geom_id'] = df['pixel_geom_id'].apply(lambda x: hash(x))
		lat_lon_df = df[['latitude','longitude','pixel_geom_id']].copy()
		lat_lon_df = lat_lon_df.drop_duplicates()
		admin_df = gpd.read_file(admin_boundary_file_path)
		
		#Computes a reference grid by linking grid points to administrative boundaries.
		#Only done once as all the ensemble models use the same spatial grid
		if batch_number == 0:
			grid_df = _create_reference_grid(lat_lon_df, admin_df,admin_code_label)

		#Link_df is a MxN link table between grid points and administrative boundaries. The groupby allows to drop grid points duplicate in the first case
		#or aggregate into admin boundaries in the second one
		link_df = pd.merge(df, grid_df, on='pixel_geom_id')
		batch_data_grid_df = link_df.groupby(['pixel_geom_id','latitude','longitude','number','valid_time_year','valid_time_month','lead_time'])['tp_mm_day'].mean().reset_index()
		batch_data_adm_df = link_df.groupby(['adm1_pcode','number','valid_time_year','valid_time_month','lead_time'])['tp_mm_day'].mean().reset_index()
		
		#Concatenate all ensemble model into a single DataFrame 
		if batch_number == 0:
			data_grid_df = batch_data_grid_df
			data_adm_df = batch_data_adm_df
		else:
			data_grid_df = pd.concat([data_grid_df,batch_data_grid_df])
			data_adm_df = pd.concat([data_adm_df,batch_data_adm_df])
		
		
	data_grid_df.reset_index(inplace = True, drop = True)
	data_adm_df.reset_index(inplace = True, drop = True)

	#Export data to parquet file
	grid_df.to_parquet(ref_grid_file_path, compression='gzip')  
	data_grid_df.to_parquet(pixel_output_file_path, compression='gzip')
	data_adm_df.to_parquet(adm_output_file_path, compression='gzip')


	print('data exported')

	return

############################################################################################################################################
def pre_process_era5_data(era5_file_path, ecmwf_file_path, ref_grid_file_path, pixel_output_file_path, adm_output_file_path):
	"""
	Loads the ERA5 climate data grib file and converts it to a DataFrame. Also adapt columns names, precipitation units and link grid 
	points to administrative boundaries. Finally, computes the average climatology (per location and month) and export the resulting 
	DataFrame to a parquet file.


    Parameters
    ----------
	input_file_path: str, Path to the ERA5 climate data grib file to be processed. This dataset should have been previously regridded to the ECMWF grid
	ref_grid_file_path: str, Path where the reference grid, combining both grid points and admin boundaries link, is to be exported 
	pixel_output_file_path: str, Path where the processed file at the grid point level should be exported
	adm_output_file_path: str, Path where the processed file at the admin boundary level should be exported

	Returns
    -------
	
	"""

	#Load both ERA5 and ECMWF initial grib file, re-grid the ERA5 dataset to match the one from ECMWF and returns it on 
	#a DataFrame format
	era5_df = _regrid_climate_data(era5_file_path,ecmwf_file_path)
	grid_df = gpd.read_parquet(ref_grid_file_path) 

	#Extract month and year information.  
	era5_df['valid_time_year'] = era5_df['valid_time'].apply(lambda x : x.year)
	era5_df['valid_time_month'] = era5_df['valid_time'].apply(lambda x : x.month)
	#Add column lead time (always 0 for ERA5)
	era5_df['lead_time'] = 0 
	#Each source uses a different unit (meters/day for ERA5 and meters/second for ECMWF). Converting both into mm/day here
	era5_df['tp_mm_day'] = era5_df['tp']*1000 

	##########################
	#ERA5 valid time is changed after the CDO grid matching, not sure why. Using time here instead and adding a shift to correct it
	#To do: check if the error persists with the new method used by Sarah and drop these lines
	cdo_error = False
	if cdo_error:
		era5_df['valid_time_year'] = era5_df['time'].apply(lambda x : x.year)
		era5_df['valid_time_month'] = era5_df['time'].apply(lambda x : x.month+1)
		era5_df.loc[era5_df['valid_time_month'] == 13, 'valid_time_year'] = era5_df.loc[era5_df['valid_time_month'] == 13, 'valid_time_year'] + 1
		era5_df.loc[era5_df['valid_time_month'] == 13, 'valid_time_month'] = 1
	##########################

	#Link to reference grid and retrieve pixel hash code and admin1 pcode
	geo_df = gpd.GeoDataFrame(era5_df, geometry=gpd.points_from_xy(era5_df.longitude, era5_df.latitude), crs="EPSG:4326")
	geo_df = geo_df.sjoin_nearest(grid_df, max_distance = 0.1)
	data_grid_df = geo_df.groupby(['pixel_geom_id','latitude','longitude','valid_time_year','valid_time_month','lead_time'])['tp_mm_day'].mean().reset_index()
	data_adm_df = geo_df.groupby(['adm1_pcode','valid_time_year','valid_time_month','lead_time'])['tp_mm_day'].mean().reset_index()
	
	#Compute ERA5 climatology
	data_grid_df = _compute_era5_climatology(data_grid_df, 'pixel_geom_id')
	data_adm_df = _compute_era5_climatology(data_adm_df, 'adm1_pcode')

	#Export data to parquet file
	data_grid_df.to_parquet(pixel_output_file_path, compression='gzip')
	data_adm_df.to_parquet(adm_output_file_path, compression='gzip')


	return



############################################################################################################################################
def ecmwf_bias_correction(ecmwf_file_path, era5_file_path, output_file_path):
	"""
	Compute the bias between the average precipitation prediction (ECMWF) and ground truth (ERA5) 
	per location, month, model and lead time. Correct the bias for every individual prediction.

    Parameters
    ----------
	ecmwf_file_path: str, Path to the processed ECMWF climate data
	era5_file_path: str, Path to the processed ERA5 climate data
	output_file_path: str, Path where the bias-corrected ECMWF file should be exported

	Returns
    -------
	
	"""


	#Load ECMWF and ERA5 processed dataFrames from parquet files. 
	ecmwf_df = pd.read_parquet(ecmwf_file_path)
	era5_df = pd.read_parquet(era5_file_path)

	
	#Detects which location is being used (pixel or adminstrative boundary level)
	if 'adm1_pcode' in ecmwf_df.columns.values:
		geom_id = 'adm1_pcode'
	else:
		geom_id = 'pixel_geom_id'
		
	ecmwf_corr_df = ecmwf_df.copy()

	#Computes average precipitation for a given location and month (also model number and lead time in the case of ECMWF)
	era5_avg_df = era5_df.groupby([geom_id,'valid_time_month'])['tp_mm_day'].mean().reset_index()
	ecmwf_avg_df = ecmwf_df.groupby(['number',geom_id,'valid_time_month','lead_time'])[['tp_mm_day']].mean().reset_index()

	#Compute bias between the average precipitation per location, month, model and lead time 
	avg_df = pd.merge(ecmwf_avg_df, era5_avg_df, on=['valid_time_month',geom_id], suffixes=('_ecmwf', '_era5'))
	avg_df['bias'] = avg_df['tp_mm_day_ecmwf'] - avg_df['tp_mm_day_era5']
	avg_df.drop(['tp_mm_day_ecmwf','tp_mm_day_era5'], inplace = True, axis = 1)
		
	#Correct the bias by adding (or subtracting) the average bias to every single prediction. 
	#Limits the result to only positive values (negative values are possible when subtracting bias for small predictions)
	ecmwf_corr_df = pd.merge(ecmwf_corr_df, avg_df, on=['number','valid_time_month',geom_id,'lead_time'])
	ecmwf_corr_df['tp_mm_day'] = ecmwf_corr_df['tp_mm_day'] - ecmwf_corr_df['bias']
	ecmwf_corr_df.loc[ecmwf_corr_df['tp_mm_day'] < 0, 'tp_mm_day'] = 0
	ecmwf_corr_df.drop(['bias'], inplace = True, axis = 1)

	#Export resulting ECMWF bias-corrected dataFrame to a parquet file
	ecmwf_corr_df.to_parquet(output_file_path, compression='gzip') 

	return

############################################################################################################################################
def compute_quantile_probability(input_file_path, climatology_file_path, output_file_path):
	"""
	Computes the probability of the ECMWF predicted precipitation being under different quantile thresholds foe every location, month and year. 
	Quantiles thresholds are computd from ERA5 climatology for a given location and month. Different thresholds are used following the quantiles values 
	(quantiles 50%, 33%, 25% and 20%). Probability is based on the share of ECMWF model predicting a below quantile value. Individual predictions bias and 
	mean absolute error are also computed.



    Parameters
    ----------
	input_file_path: str, Path to the processed ECMWF climate data (before or after bias correction)
	climatology_file_path: str, Path to the processed ERA5 climate data containing the climatology data
	output_file_path: str, Path where the computed quantiles probability and bias / maae score ECMWF file should be exported

	Returns
    -------
	
	"""
	#Load ECMWF and ERA5 processed dataFrames from parquet files. 
	ecmwf_prob_df = pd.read_parquet(input_file_path)
	era5_df = pd.read_parquet(climatology_file_path)
	
	#Detects which location is being used (pixel or adminstrative boundary level)
	if 'adm1_pcode' in ecmwf_prob_df.columns.values:
		geom_id = 'adm1_pcode'
	else:
		geom_id = 'pixel_geom_id'
		
	#Extracts the climatology per location and month (every year has the same value)
	climatology_era5_df = era5_df[[geom_id,'valid_time_month','climatology_q50','climatology_q33','climatology_q25','climatology_q20']].drop_duplicates()
	#Merges ECMWF dataFrame with the corresponding ERA5 climatology
	ecmwf_prob_df = pd.merge(ecmwf_prob_df, climatology_era5_df, on=[geom_id,'valid_time_month'])

	#Compute a flag (1 or 0) to indicates if a given prediction (location, month, year and ensemble model number) is below the ERA5 climatology
	#for the same location and month. This is used later to compute the probability based on all models
	for q in ['50','33','25','20']:
		ecmwf_prob_df['prob_q'+q] = (ecmwf_prob_df['tp_mm_day'] <= ecmwf_prob_df['climatology_q'+q])*1

	#Combine all model predictions into a single average value plus the probability of it being under each climatology quantile.
	ecmwf_prob_df = ecmwf_prob_df.groupby([geom_id,'valid_time_year','valid_time_month','lead_time'])[['tp_mm_day','prob_q50','prob_q33','prob_q25','prob_q20']].mean().reset_index()
	
	#Compute bias and MAE (mean absolute error) for every single ECMWF prediction compared to ERA5 values
	ecmwf_prob_df = pd.merge(ecmwf_prob_df, era5_df, on=[geom_id, 'valid_time_year','valid_time_month'], suffixes=('', '_era5'), how = 'left')
	ecmwf_prob_df['bias'] = ecmwf_prob_df['tp_mm_day'] -  ecmwf_prob_df['tp_mm_day_era5']
	ecmwf_prob_df['mae'] = abs(ecmwf_prob_df['bias'])

	#Export resulting ECMWF dataFrame to a parquet file
	ecmwf_prob_df.to_parquet(output_file_path, compression='gzip') 
	
	return

	

############################################################################################################################################
