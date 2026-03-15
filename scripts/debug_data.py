# -*- coding: utf-8 -*-
import json

data = json.load(open('D:/HBNU/2026InnovationCompetition/CropBelt_Prediction/public/data/crop_data.json', 'r', encoding='utf-8'))

# Check if any year has data
for year_data in data:
    if len(year_data['crops']['水稻']) > 0:
        print(f"Year {year_data['year']}: {len(year_data['crops']['水稻'])} provinces with data")
        print(year_data['crops']['水稻'][:2])
        break
else:
    print('No data found in any year!')

# Print first year full data
print("\n--- First year data ---")
print(json.dumps(data[0], ensure_ascii=False, indent=2))
