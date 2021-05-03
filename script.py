import requests
x = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=230&date=03-05-2021')
jret = x.json()['centers']

pr_json = []
for acent in jret:
    app_json = {"Name":"","PinCode":"","Capacity":[],"Date":[]}
    for sess in acent['sessions']:
        if sess['available_capacity'] > 0 and sess['min_age_limit'] == 18:
            # print(sess)
            app_json['Name'] = acent['name']
            app_json['PinCode'] = acent['pincode']
            app_json['Capacity'].append(sess['available_capacity'])
            app_json['Date'].append(sess['date'])
    
    if app_json["Name"]:
        pr_json.append(app_json)

print(pr_json)
        
