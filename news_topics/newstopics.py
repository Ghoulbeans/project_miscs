import requests, zipfile, io, os
import pandas as pd
#import torch
#from transformers import AutoTokenizer, AutoModel
import matplotlib.pyplot as mplt


#TODO need article names - use gdelt themes in interim?
# hf_model = "distilbert-base-uncased-finetuned-sst-2-english"
# tokenizer = AutoTokenizer.from_pretrained(hf_model)
# model = AutoModel.from_pretrained(hf_model)

#get gdlet data and extract export csv(today only) 
gdelt_today = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
gdelt_data = requests.get(gdelt_today)
gdelt_data = gdelt_data.text.split("\n")

zip_url = None
for x in gdelt_data:
    if "export" in x:
        zip_url = x.split(" ")[2]
        break

response = requests.get(zip_url)
with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    z.extractall('news_topics/gdelt_data')
gdelt_csv = 'news_topics/gdelt_data/' + os.listdir('news_topics/gdelt_data')[0]


#column ids from https://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf
gdelt_columns = [
    "GlobalEventID", "SQLDATE", "MonthYear", "Year", "FractionDate", "Actor1Code", "Actor1Name",
    "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode", "Actor1Religion1Code",
    "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code", "Actor2Code",
    "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode", "Actor2EthnicCode",
    "Actor2Religion1Code", "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code",
    "Actor2Type3Code", "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode", "QuadClass",
    "GoldsteinScale", "NumMentions", "NumSources", "NumArticles", "AvgTone", "Actor1Geo_Type",
    "Actor1Geo_FullName", "Actor1Geo_CountryCode", "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code",
    "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID", "Actor2Geo_Type",
    "Actor2Geo_FullName", "Actor2Geo_CountryCode", "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code",
    "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID", "ActionGeo_Type",
    "ActionGeo_FullName", "ActionGeo_CountryCode", "ActionGeo_ADM1Code", "ActionGeo_ADM2Code",
    "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID", "DATEADDED", "SOURCEURL"
]

gdelt_columns_data_types = {
    "GlobalEventID": int,
    "SQLDATE": str,
    "MonthYear": str,
    "Year": int,
    "IsRootEvent": int,
    "EventCode": str,
    "EventBaseCode": str,
    "EventRootCode": str,
    "QuadClass": int,
    "AvgTone": float,
    "DATEADDED": str,
    "SOURCEURL": str
}


df = pd.read_csv(gdelt_csv, delimiter = "\t", header=None, names=gdelt_columns, dtype=gdelt_columns_data_types)
os.remove(gdelt_csv)

#create bar chart on theme by sentiment
#normalise tone of article and bucket
df['NormalisedTone'] = (df['AvgTone'] - df['AvgTone'].min()) / (df['AvgTone'].max() - df['AvgTone'].min())

def tone_bucket(tone):
    if tone > 0.66:
        return 'Positive'
    elif tone < 0.33:
        return 'Negative'
    else:
        return 'Neutral'

df['BucketedTone'] = df['NormalisedTone'].apply(tone_bucket)

#convert eventcodes to meaning
event_codes = {
    "010": "Make a public statement",
    "011": "Decline to comment",
    "012": "Make an optimistic comment",
    "013": "Make a pessimistic comment",
    "014": "Consider policy change",
    "015": "Acknowledge or claim responsibility",
    "016": "Reject accusation or responsibility",
    "017": "Engage in diplomatic cooperation",
    "018": "Apologize",
    "019": "Express accord",
    "020": "Appeal for peace",
    "021": "Appeal for economic cooperation",
    "022": "Appeal for military cooperation",
    "023": "Appeal for humanitarian aid",
    "024": "Express intent to institute policy",
    "025": "Express intent to provide material aid",
    "026": "Express intent to change policy",
    "027": "Express intent to cooperate",
    "028": "Express intent to yield",
    "030": "Express intent to engage in material cooperation",
    "031": "Demand policy change",
    "032": "Demand material aid",
    "033": "Demand political reform",
    "034": "Threaten to reduce or stop aid",
    "035": "Threaten with economic sanctions",
    "036": "Threaten with military action",
    "037": "Give ultimatum",
    "038": "Engage in diplomatic dispute",
    "039": "Protest verbally",
    "040": "Accuse",
    "041": "Criticize or denounce",
    "042": "Blame",
    "043": "Question policy",
    "044": "Engage in political dissent",
    "045": "Threaten non-forceful action",
    "050": "Threaten use of force",
    "051": "Demonstrate military force",
    "052": "Deploy armed forces",
    "053": "Use conventional force",
    "054": "Use unconventional force",
    "055": "Assassinate",
    "056": "Attack civilians",
    "057": "Conduct suicide bombing",
    "058": "Attempt to assassinate",
    "060": "Impose embargo, boycott, or sanctions",
    "061": "Reduce or stop aid",
    "062": "Halt negotiations",
    "063": "Break diplomatic relations",
    "064": "Reduce military presence",
    "070": "Extend economic aid",
    "071": "Provide humanitarian aid",
    "072": "Provide military aid",
    "073": "Increase military presence",
    "074": "Extend policy support",
    "075": "Cooperate economically",
    "080": "Provide diplomatic cooperation",
    "081": "Engage in material cooperation",
    "082": "Engage in military cooperation",
    "083": "Engage in intelligence cooperation",
    "084": "Conduct counterterrorism cooperation",
    "090": "Form a new organization",
    "091": "Sign formal agreement",
    "092": "Make an alliance",
    "093": "Grant political asylum",
    "100": "Yield to demands",
    "101": "Retreat or surrender",
    "102": "Grant concession",
    "103": "Release prisoners",
    "110": "Engage in military surrender",
    "120": "Return or allow return",
    "121": "Return territory",
    "122": "Release detainees",
    "130": "Investigate",
    "131": "Seek arbitration or mediation",
    "132": "Offer mediation",
    "133": "Agree to mediation",
    "134": "Arbitrate dispute",
    "135": "Investigate crimes",
    "136": "Investigate corruption",
    "140": "Reject request or demand",
    "141": "Reject appeal for negotiation",
    "142": "Reject mediation",
    "143": "Reject arbitration",
    "150": "Defy international pressure",
    "160": "Expel or force to leave",
    "161": "Expel or deport individuals",
    "162": "Expel diplomats",
    "163": "Expel peacekeepers",
    "170": "Impose restrictions",
    "171": "Censor media",
    "172": "Impose curfew",
    "173": "Block or restrict internet",
    "174": "Restrict social media",
    "175": "Close down NGOs",
    "180": "Arrest or detain",
    "181": "Arrest leaders",
    "182": "Arrest journalists",
    "190": "Torture",
    "200": "Execute prisoners",
    "201": "Assassinate opposition",
    "202": "Conduct genocide",
    "210": "Destroy property",
    "211": "Demolish homes",
    "212": "Burn buildings",
    "220": "Violently disrupt protests",
    "230": "Use chemical weapons",
    "240": "Use biological weapons",
    "250": "Use nuclear weapons",
}

df['EventCodeName'] = df['EventCode'].map(event_codes)

#create stacked bar
count_by_tone = df.groupby(['EventCodeName', 'BucketedTone']).size().unstack(fill_value=0)
#alt by actor one (mostly shows countries)
#count_by_tone = df.groupby(['Actor1Name', 'BucketedTone']).size().unstack(fill_value=0)
#count_by_tone = count_by_tone[count_by_tone.sum(axis=1) > 5]

fig, ax = mplt.subplots(figsize=(12, 8))
count_by_tone.plot(kind='bar', stacked=True, ax=ax, color=['red', 'gray', 'green'])

ax.set_xlabel('Event')
ax.set_ylabel('Mentions')
ax.set_title('Events by article tone')
ax.legend(title='Tone')

mplt.xticks(rotation=90)
mplt.show()

