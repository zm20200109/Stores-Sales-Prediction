import pandas as pd
import numpy as np
import re

def load_data():
    holidays_events = pd.read_csv('../data/holidays_events.csv')
    holidays_events['date'] = pd.to_datetime(holidays_events['date'])
    oil = pd.read_csv('../data/oil.csv')
    oil['date'] = pd.to_datetime(oil['date'])
    stores = pd.read_csv('../data/stores.csv')
    transactions = pd.read_csv('../data/transactions.csv')
    transactions['date'] = pd.to_datetime(transactions['date'])
    sample_submissions = pd.read_csv('../data/sample_submission.csv')
    train = pd.read_csv('../data/train.csv')
    train['date'] = pd.to_datetime(train['date'])
    test = pd.read_csv('../data/test.csv')
    test['date'] = pd.to_datetime(test['date'])
    return holidays_events, oil, stores, transactions, sample_submissions, train, test

# holidays_events, oil, stores, transactions, sample_submissions, train, test = load_data()
#
def find_transfered_date(holidays_events, holiday,year):
    holidays_events['holiday_indicator'] = holidays_events[['description']].applymap(lambda x:str(holiday) in str(x)) # vraca sve ntokre dataframe-a koje sadrze naziv praznika u sebi
    list_of_dates = holidays_events.loc[(holidays_events['holiday_indicator']==True)&(holidays_events['date'].dt.year==year)&(holidays_events['type']=='Transfer'),:]['date'].to_list()
    if len(list_of_dates) == 0:
        return None
    else:
        return pd.DataFrame({'date':list_of_dates,'description':[holiday]})
#
def find_transferred_holidays(holidays_events):

    transferred_holidays_names = holidays_events.loc[holidays_events['transferred']==True,:]['description'].drop_duplicates().values.tolist()
    transferred_holidays_years = holidays_events.loc[holidays_events['transferred']==True,:]['date'].dt.year.drop_duplicates().values.tolist()

    transferred_dataframe = pd.DataFrame()

    for holiday in transferred_holidays_names:
        for year in transferred_holidays_years:
            current_df = find_transfered_date(holidays_events,holiday,year)
            transferred_dataframe = pd.concat([transferred_dataframe,current_df],axis=0)
    return transferred_dataframe

def find_transferred_holidays_date_locale_name(holidays_events):
    transferred_holidays_final = find_transferred_holidays(holidays_events)
    transferred_holidays_date_locale_name =pd.merge(transferred_holidays_final,holidays_events,on=['date']).groupby(['date','locale_name']).agg({
        'description_x':lambda x: ','.join(sorted(set(x))),
        'locale':lambda x: ','.join(sorted(set(x)))
    }).reset_index()
    transferred_holidays_date_locale_name.rename(columns={'description_x':'description'},inplace=True) # 13 observacija
    return transferred_holidays_date_locale_name # 13 observacija

# # Non transferred holidays :
def find_non_transferred_holidays(holidays_events):
    non_transferred_holidays_date_locale_name = holidays_events.loc[holidays_events['type']=='Holiday',:].groupby(['date','locale_name']).agg({
        'description':''.join,
        'locale':''.join
    }).reset_index()
    return non_transferred_holidays_date_locale_name # 221 observacija

# # Additionals:
def find_additional_days(holidays_events):
    holidays_events_additional_type = holidays_events.loc[holidays_events['type']=='Additional',:]
    holidays_events_additional_type['description_corrected'] = holidays_events_additional_type['description'].apply(lambda x:re.sub(r'[+-123456789]+$','',x))
    holidays_additional_type_date_locale_name = holidays_events_additional_type.groupby(['date','locale_name']).agg({
        'description_corrected':''.join,
        'locale':''.join
    }).reset_index()
    holidays_additional_type_date_locale_name.rename(columns={'description_corrected':'description'},inplace=True) # 51
    return holidays_additional_type_date_locale_name # 51 observacija

# # Events
def find_all_events(holidays_events):
    all_events = holidays_events.loc[holidays_events['type']=='Event',:]
    all_events['description_corrected'] = all_events['description'].apply(lambda x:re.sub(r'[+\d-]+$','',x)).apply(lambda s:'Mundial' if 'Mundial' in s else s)
    all_events_date_locale_name=all_events.groupby(['date','locale_name']).agg({
        #"'description_corrected':''.join # dopustio sam da Terremoto ManabiDia de la Madre bude jedna kategorija
        'description_corrected':lambda x: ','.join(sorted(set(x))),
        'locale': lambda x: ','.join(sorted(set(x)))
    }).reset_index()
    all_events_date_locale_name.rename(columns={'description_corrected':'description'},inplace=True) # 55 zato što sam spojio gornju kolonu jer ima 2 praznika, a ne jedan
    return all_events_date_locale_name # 55 observacija

#
# # Bridge dates
#
def find_bridge_dates(holidays_events):
    all_bridge_dates = holidays_events.loc[holidays_events['type']=='Bridge',:]
    all_bridge_dates['description_corrected'] = all_bridge_dates['description'].str.replace(r'^Puente\s*','',regex=True)
    all_bridge_date_locale_name = all_bridge_dates.groupby(['date','locale_name']).agg({
        'description_corrected':''.join,
        'locale':''.join
    }).reset_index()
    all_bridge_date_locale_name.rename(columns={'description_corrected':'description'},inplace=True)
    return all_bridge_date_locale_name # 5 observacija

# # Unusuall work days:
def find_unusuall_work_days(holidays_events):
    unusuall_work_days = holidays_events.loc[holidays_events['type']=='Work Day',:].groupby(['date','locale_name']).agg({
        'type':''.join,
        'locale':''.join
    }).reset_index()
    unusuall_work_days.rename(columns={'type':'description'},inplace=True)
    return unusuall_work_days # 5 observacija
#
# # Final:
def clean_data_holidays_events(holidays_events):
    transferred_holidays_date_locale_name = find_transferred_holidays_date_locale_name(holidays_events)
    non_transferred_holidays_date_locale_name = find_non_transferred_holidays(holidays_events)
    holidays_additional_type_date_locale_name = find_additional_days(holidays_events)
    all_events_date_locale_name = find_all_events(holidays_events)
    all_bridge_date_locale_name = find_bridge_dates(holidays_events)
    unusuall_work_days = find_unusuall_work_days(holidays_events)
    holidays_events_corrected = pd.concat([transferred_holidays_date_locale_name, non_transferred_holidays_date_locale_name, holidays_additional_type_date_locale_name, all_events_date_locale_name, all_bridge_date_locale_name, unusuall_work_days],axis=0)
    holidays_events_corrected_final = holidays_events_corrected.groupby(['date','locale_name']).agg({
        'description':lambda x: ','.join(sorted(set(x))) if not ''.join(x).endswith('-1') else ''.join(x).rstrip('-1'),
        'locale':lambda x: ','.join(sorted(set(x)))
    }).reset_index()
    return holidays_events_corrected_final # 343 observacije

def determine_holiday(row):
    local_holiday = row['description_x']
    national_holiday = row['description_y']  # Work day moze biti samo National Holdiay zato sto je to 5/343 reda moje holiday_events restricted kolone
    if (local_holiday == 'No local holiday') & (national_holiday == 'No national holiday'):
        return 'Work Day'
    elif (local_holiday != 'No local holiday') & (national_holiday == 'No national holiday'):   # postoji lokalni, ne postoji drzavni praznik
        return local_holiday
    elif (local_holiday == 'No local holiday') & (national_holiday != 'No national holiday'): # postoji samo nacionalni holiday, ovde ce vratiti Work Day uoliko je national_holiday Work Day
        return national_holiday # work day moze biti samo National Holdiay
    #elif (local_holiday != 'No local holiday') & (national_holiday != 'No national holiday'): # postoji i nacionalni i lokalni
    else:
        return f"{local_holiday}, {national_holiday}"


# # Merging:
def create_dataset():
    holidays_events, oil, stores, transactions, sample_submissions, train, test = load_data()

    onpromotion = test['onpromotion'].copy() # id, date, store, family, onpromotion, sales
    test.drop(columns=['onpromotion'],inplace=True)
    test['sales'] = np.NaN
    test['onpromotion'] = onpromotion
    train = pd.concat([train,test],axis=0)

    train_oil = pd.merge(train,oil,on=['date'],how='left')
    train_oil_transactions = pd.merge(train_oil,transactions,on=['date','store_nbr'],how='left')
    train_oil_transactions_stores = pd.merge(train_oil_transactions,stores,on=['store_nbr'])
    holidays_events_corrected_final = clean_data_holidays_events(holidays_events)
    training_data_final = pd.merge(train_oil_transactions_stores,holidays_events_corrected_final,left_on=['date','city'],right_on=['date','locale_name'],how='left')
    training_data_final = training_data_final.sort_values(by='date',ascending=True)

    # adding National holidays
    national_holidays = holidays_events_corrected_final.loc[holidays_events_corrected_final['locale'] == 'National', :]
    national_holidays = national_holidays[['date','description']]
    temporary = pd.merge(training_data_final, national_holidays,on=['date'],how='left') # description_y
    temporary['description_x'] = temporary['description_x'].fillna('No local holiday')
    temporary['description_y'] = temporary['description_y'].fillna('No national holiday')
    temporary['all_holidays'] = temporary[['description_x','description_y']].apply(determine_holiday, axis=1)
    temporary.drop(columns=['description_x','description_y','locale','locale_name'],inplace=True)
    return temporary

def create_test_dataset():
    holidays_events, oil, stores, transactions, sample_submissions, train, test = load_data()
    test_oil = pd.merge(test,oil,on=['date'],how='left')





