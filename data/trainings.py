import pandas as pd
import streamlit as st


from core.utils import process_data


trainings = process_data(st.secrets['spreadsheet_id_trainings'],
                         st.secrets['zero_gid'])
trainings['дата_первого_дня'] = pd.to_datetime(
    trainings['дата_первого_дня'], format='mixed'
)
trainings['количество_участников'].fillna(0, inplace=True)
trainings_t = (trainings
               .groupby(by='дата_первого_дня', as_index=False)
               .agg(
                   {'id_тренинга': 'nunique',
                    'количество_участников': 'sum'})[['дата_первого_дня',
                                                      'id_тренинга',
                                                      'количество_участников']
                                                     ]
               .rename(columns={'id_тренинга': 'кол-во тренингов'}))
trainings_t['месяц'] = trainings_t['дата_первого_дня'].dt.month
