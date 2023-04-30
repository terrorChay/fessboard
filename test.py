import pickle 
import pandas as pd
with open('counties.pkl', 'rb') as f:
    counties = pickle.load(f)
print(counties.keys())
# print(counties['features'][3]['properties']['name'])
# print(counties['features'][3]['properties']['cartodb_id'])
region_id_list = []
regions_list = []
for k in range(len(counties['features'])):
    region_id_list.append(counties['features'][k]['id'])
    regions_list.append(counties['features'][k]['properties']['name'])
df_regions = pd.DataFrame()
df_regions['region_id'] = region_id_list
df_regions['region_name'] = regions_list
df_regions.set_index('region_name',inplace=True)
print(df_regions)

