import pandas as pd
import streamlit as st


from core.utils import process_data

schedule = process_data(
    st.secrets['spreadsheet_id_schedule'],
    st.secrets['zero_gid']
)
shedule_rejected = process_data(
    st.secrets['spreadsheet_id_schedule'],
    st.secrets['rejected_gid']
)
schedule['Дата'] = pd.to_datetime(schedule['Дата'])
shedule_rejected['Дата'] = pd.to_datetime(shedule_rejected['Дата'])
schedule_1 = (schedule[
   (schedule['оплачивается_ли_урок_(1/0)'] == 1)
   & (schedule['пришел_ли_ученик_на_урок_(1/0)'] == 1)]
    .groupby(
        by='Дата'
    ).agg(
        {'Номер': 'count'}
        )['Номер']
    .reset_index()
    .rename(
        columns={'Номер': 'Кол-во уроков в день'}
        )
)
schedule_3 = schedule[
    schedule['оплачивается_ли_урок_(1/0)'] == 1
]
schedule_3 = (schedule_3[
    schedule_3['пришел_ли_ученик_на_урок_(1/0)'] == 0
].groupby(
        by='Дата'
    ).agg(
        {'Номер': 'count'}
        )['Номер']
    .reset_index()
    .rename(
        columns={'Номер': 'Кол-во отмен уроков'}
        )
)
shedule_4_1 = (shedule_rejected[
    (
     shedule_rejected['оплачивается_ли_урок_(1/0)'] == 1)
    & (shedule_rejected[
        'тип_урока_(перенесённый,_дополнительный,_отмена_урока)'
        ]
        == 'Отмена урока')
].groupby(
        by='Дата'
    ).agg(
        {'Номер': 'count'}
        )['Номер']
    .reset_index()
    .rename(
        columns={'Номер': 'Кол-во отмен уроков'}
        )
)
shedule_4_2 = (schedule[
    schedule['оплачивается_ли_урок_(1/0)'] == 1]
    .groupby(
        by='Дата'
    ).agg(
        {'Номер': 'count'}
        )['Номер']
    .reset_index()
    .rename(
        columns={'Номер': 'Кол-во уроков в день'}
        )
)
schedule_4 = pd.merge(shedule_4_1, shedule_4_2, on='Дата', how='outer')
schedule_4.fillna(0, inplace=True)
schedule_4['% отмененных уроков'] = schedule_4.apply(
    lambda row: round(
        (row['Кол-во отмен уроков']/row['Кол-во уроков в день'])*100, 2
        )
    if row['Кол-во уроков в день'] != 0 else 100, axis=1)
