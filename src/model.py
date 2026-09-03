import pandas as pd
import numpy as np

# beregner coverline for en syklus. Dette er grensen mellom follikulær og luteal fase.
# bruker median av 10 første dager + 0.1 grader som margin
def calculate_coverline(cycle_df):
    follicular = cycle_df[cycle_df['cycle_day'] <=10]['Temperature']
    if len(follicular) == 0:
        return None
    return follicular.median() + 0.1


# sjekker om eggløsning er bekreftet. 3 påfølgende temperaturer over coverline
def detect_ovulation_confirmed(cycle_df, coverline):
    temps = cycle_df['Temperature'].values
    confirmed_day = None
    for i in range(2, len(temps)):
        if (temps[i] > coverline and
            temps[i-1] > coverline and
            temps[i-2] > coverline):
            confirmed_day = i
            break
    return confirmed_day


def predict_fertile(cycle_df):
    coverline = calculate_coverline(cycle_df)
    if coverline is None:
        return cycle_df.assign(fertile=True)
    confirmed_day = detect_ovulation_confirmed(cycle_df, coverline)
    cycle_df = cycle_df.copy()
    if confirmed_day is None:
        cycle_df['fertile'] = True
    else:
        cycle_df['fertile'] = True
        cycle_df.iloc[confirmed_day + 1:, cycle_df.columns.get_loc('fertile')] = False
    cycle_df['coverline'] = coverline
    cycle_df['ovulation_confirmed_day'] = confirmed_day
    return cycle_df


def add_features(df):
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Temperature'] = df['Temperature'].interpolate(method='linear')
    df['Temperature'] = df['Temperature'].ffill().bfill()
    df['is_menstruation'] = df['Menstruation'] == 'MENSTRUATION'
    df['cycle_number'] = (
        df['is_menstruation'] &
        ~df['is_menstruation'].shift(1, fill_value=False)
    ).cumsum()
    df['temp_rolling_mean'] = df['Temperature'].rolling(window=5, min_periods=1).mean()

    cycle_day = []
    current_cycle_day = 0
    for i, row in df.iterrows():
        if row['is_menstruation'] and (i == 0 or not df.loc[i-1, 'is_menstruation']):
            current_cycle_day = 1
        else:
            current_cycle_day += 1
        cycle_day.append(current_cycle_day)
    df['cycle_day'] = cycle_day

    return df 

