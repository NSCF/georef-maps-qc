import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend which is non-interactive
from os import path, mkdir
from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from progress.bar import Bar

csv_name = 'AcocksExport20240426_OR.csv'
maps_dir = 'maps'
datefield = 'Date'

### SCRIPT ###

# Read the CSV file with points
print('reading csv data')
points_df = pd.read_csv(csv_name)
uniquedates = list(set(points_df[datefield]))
validuniquedates = list(filter(lambda x: isinstance(x, str) and r'/' in x and len(x.split('/')) == 3, uniquedates))
fixeddates = list(map(lambda x: str(datetime.strptime(x, '%m/%d/%Y')).split(' ')[0], validuniquedates))
fixeddates.sort()
firstdateindex = fixeddates.index(next(x for x in fixeddates if int(x.split('-')[0]) >= 1936)) 
lastdateindex = fixeddates.index(next(x for x in fixeddates if int(x.split('-')[0]) >= 1977))
searchdates = fixeddates[firstdateindex : lastdateindex]

#we need to add the corrected dates in the dataframe so we can filter later
print('fixing dates')
points_df['FormattedDate'] = None
for index, row in points_df.iterrows():
  if isinstance(row[datefield], str) and r'/' in row[datefield] and len(row[datefield].split('/')) == 3:
    points_df.at[index, 'FormattedDate'] = str(datetime.strptime(row[datefield], '%m/%d/%Y')).split(' ')[0]

# if we only want to create the plots to save to file, and not display on screen:
plt.ioff()

# Read the shapefile
print('reading country shapefile')
shapefile_path = r'C:\GISData\GISData\admin'
shapefile_name = r'southafrica_Merge_FSA.shp'
gdf = gpd.read_file(path.join(shapefile_path, shapefile_name))

# Plot the shapefile
print('plotting country shapefile')
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(ax=ax, color='white', edgecolor='black')



# Plot the points on the same map
# print('plotting csv data')
geometry = [Point(xy) for xy in zip(points_df['Longitude'], points_df['Latitude'])]
points_gdf = GeoDataFrame(points_df, geometry=geometry)
points_gdf.plot(ax=ax, color='lightgray', marker='o', markersize=30)

if not path.exists(maps_dir):
  mkdir(maps_dir)

# # Customize the map appearance if needed
# ax.set_title('Shapefile with Points Overlay')
# ax.set_xlabel('Longitude')
# ax.set_ylabel('Latitude')
bar = Bar('Mapping', max=len(searchdates))
for date in searchdates:
  daterecords = points_gdf[points_gdf['FormattedDate'] == date]
  daterecords.plot(ax=ax, color='red', marker='o', markersize=30)

  # Add text annotation for the date
  ax.text(0.80, 0.95, date, transform=ax.transAxes, fontsize=12, color='black', verticalalignment='top')

  #Save the map as a JPEG
  output_path = date + '.jpg'
  plt.savefig(path.join(maps_dir, output_path), format='jpeg', dpi=300)

  # plot over the red markers again
  daterecords.plot(ax=ax, color='lightgrey', marker='o', markersize=30)

  # and the date
  ax.text(0.80, 0.95, date, transform=ax.transAxes, fontsize=12, color='white', verticalalignment='top')
  
  bar.next()

bar.finish()
print('all done!')

# Display the map
plt.show()
