import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import streamlit as st


from core.const import (time_column, months, status_types, contact_data,
                        columns_contact, columns_contact_total)
from core.utils import read_file, exclude_date
from pages.achivments import achivments_debit
from pages.childrens import childrens
from pages.profi import number_profi
from data.schedule import schedule, shedule_rejected
from data.trainings import trainings


main_table = read_file(st.secrets['spreadsheet_id_main'],
                       st.secrets['main_gid'])

coverage = main_table[
    main_table['Показатели'] == 'Охват'][list(main_table.columns[1:-1])]
coverage['Критерии'] = coverage.apply(
    lambda row:
    row['Критерии'] + '_' + row['Сколько всего/сколько в этом месяце?'],
    axis=1
)
coverage = coverage[list(list(coverage.columns[3:-1]))]
coverage = coverage.set_index('Критерии')
coverage = coverage.T
coverage.drop(["За 2022 год\n(уникальные)"], axis=0, inplace=True)
coverage.index = coverage.index.map(
    lambda x:
    datetime.datetime(
        year=2023 if re.search(r'\d', x)
        else 2022,
        month=months[x.split('\n')[0].split(' ')[0].strip()],
        day=1))
coverage.dropna(inplace=True)
for column in coverage.columns:
    coverage[column] = coverage[column].astype(int)
coverage.reset_index(inplace=True)
coverage.rename(columns={'index': 'Дата'}, inplace=True)

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
schedule_2 = main_table[
    main_table['Критерии'] == 'Учителей'][
        list(main_table.columns[4:-1])]
schedule_2 = schedule_2.set_index('Критерии')
schedule_2 = schedule_2.T
schedule_2.drop(["За 2022 год\n(уникальные)"], axis=0, inplace=True)
schedule_2.index = schedule_2.index.map(
    lambda x:
    datetime.datetime(
        year=2023 if re.search(r'\d', x)
        else 2022,
        month=months[x.split('\n')[0].split(' ')[0].strip()],
        day=1))
schedule_2.dropna(inplace=True)
schedule_2.reset_index(inplace=True)
schedule_2.rename(columns={'index': 'Дата'}, inplace=True)
schedule_2['Дата'] = pd.to_datetime(schedule_2['Дата'])
schedule_2['Учителей'] = schedule_2['Учителей'].astype(int)
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
schedule_5 = main_table[
    main_table['Показатели'] == 'Уроки'][
        list(main_table.columns[4:-1])]
schedule_5 = schedule_5.set_index('Критерии')
schedule_5 = schedule_5.T
schedule_5.drop(["За 2022 год\n(уникальные)"], axis=0, inplace=True)
schedule_5.index = schedule_5.index.map(
    lambda x:
    datetime.datetime(
        year=2023 if re.search(r'\d', x)
        else 2022,
        month=months[x.split('\n')[0].split(' ')[0].strip()],
        day=1))
schedule_5.reset_index(inplace=True)
schedule_5.rename(columns={'index': 'Дата'}, inplace=True)
schedule_5 = schedule_5[
    [
     'Дата',
     'Окончательно отключенных участников',
     'Окончательно отключенных учителей'
    ]
]
schedule_5.dropna(inplace=True)
for column in exclude_date(schedule_5):
    schedule_5[column] = schedule_5[column].astype(int)
trainings_t = (trainings
               .groupby(by='дата_первого_дня', as_index=False)
               .agg(
                   {'id_тренинга': 'nunique',
                    'количество_участников': 'sum'})[['дата_первого_дня',
                                                      'id_тренинга',
                                                      'количество_участников']
                                                     ]
               .rename(columns={'id_тренинга': 'кол-во тренингов',
                                'дата_первого_дня': 'Дата'}))
admission = main_table[
    main_table['Показатели'] == 'Поступление'][
        list(main_table.columns[4:-1])]
admission = admission[
    [
        "Критерии",
        "За 2022 год\n(уникальные)"
    ]
]

profi_main_table = main_table[
    main_table['Показатели'] == 'Профориентация'][
        list(main_table.columns[4:-1])]
profi_main_table = profi_main_table.set_index('Критерии')
profi_main_table = profi_main_table.T
profi_main_table.drop(["За 2022 год\n(уникальные)"], axis=0, inplace=True)
profi_main_table.index = profi_main_table.index.map(
    lambda x:
    datetime.datetime(
        year=2023 if re.search(r'\d', x)
        else 2022,
        month=months[x.split('\n')[0].split(' ')[0].strip()],
        day=1))
profi_main_table.dropna(inplace=True)
profi_main_table.drop(['Первичных профориентационных тренингов (ЛД)',
                       'ЛД-Участников'],
                      axis=1, inplace=True)
profi_main_table.reset_index(inplace=True)
profi_main_table.rename(columns={'index': 'Дата'},
                        inplace=True)
for column in exclude_date(profi_main_table):
    profi_main_table[column] = profi_main_table[column].astype(int)

labor = main_table[
    main_table['Показатели'] == 'Сотрудники'][
        list(main_table.columns[4:-1])]
labor = labor.set_index('Критерии')
labor = labor.T
labor.drop(["За 2022 год\n(уникальные)"], axis=0, inplace=True)
labor.index = labor.index.map(
    lambda x:
    datetime.datetime(
        year=2023 if re.search(r'\d', x)
        else 2022,
        month=months[x.split('\n')[0].split(' ')[0].strip()],
        day=1))
labor.dropna(inplace=True)
labor.reset_index(inplace=True)
labor.rename(columns={'index': 'Дата'},
             inplace=True)
for column in exclude_date(labor):
    labor[column] = labor[column].astype(int)
achivments_debit_t = (achivments_debit
                      .groupby(
                          by="Дата исполнения заявки",
                          as_index=False
                      )[['ID ученика',
                         'Сумма',
                         'Профит']]
                      .agg({
                          'ID ученика': 'nunique',
                          'Сумма': 'sum',
                          'Профит': 'nunique'})
                      .rename(columns={
                          "Дата исполнения заявки": "Дата",
                          'ID ученика': 'Заказано профитов',
                          'Сумма': 'Профитов на сумму',
                          'Профит': 'Профитов для кол-ва участников'}))

tech = main_table[
    main_table['Показатели'] == 'Техника'][
        list(main_table.columns[4:-1])]
tech = tech.set_index('Критерии')
tech = tech.T
tech.drop(["За 2022 год\n(уникальные)"], axis=0, inplace=True)
tech.index = tech.index.map(
    lambda x:
    datetime.datetime(
        year=2023 if re.search(r'\d', x)
        else 2022,
        month=months[x.split('\n')[0].split(' ')[0].strip()],
        day=1))
tech.dropna(inplace=True)
tech.reset_index(inplace=True)
tech.rename(columns={'index': 'Дата'},
            inplace=True)
for column in exclude_date(tech):
    tech[column] = tech[column].astype(int)


childrens = childrens[[
    'ID ученика',
    'ID ученика_shans',
    'Тип места проживания',
    "Участник программы ШАНС  (за весь период)",
    'Статус контакта за Сентябрь 2022',
    'Статус контакта за Октябрь 2022',
    'Статус контакта за Ноябрь 2022',
    'Статус контакта за Декабрь 2022',
    'Статус контакта за Январь 2023',
    'Статус контакта за Февраль 2023',
    'Статус контакта за Март 2023',
    'Статус контакта за Апрель 2023',
    'Статус контакта за Май 2023',
    'Статус контакта за Июнь 2023',
    'Статус контакта за Июль 2023',
    'Статус контакта за Август 2023'
]]
children_contact_total = childrens[
    childrens['Тип места проживания'] == 'Проживает самостоятельно'
]
children_contact = children_contact_total[
    children_contact_total["Участник программы ШАНС  (за весь период)"]
    == 'Участник программы ШАНС'
]
for column in time_column:
    childrens[column].fillna("Не знаю", inplace=True)
    contact_data['Дата'].append(datetime.datetime(
        year=int(column.split()[4]),
        month=months[column.split()[3]],
        day=1))
    for status in status_types:
        contact_data[status+'_всего'].append(len(children_contact_total[
            children_contact_total[column] == status
            ]))
        contact_data[status].append(
            len(children_contact[children_contact[column] == status]))
contact_data = pd.DataFrame(contact_data)
contact_data['Есть контакт'] = (contact_data
                                .apply(
                                    lambda row:
                                    sum(row[column]
                                        for column in
                                        columns_contact[3:-1]),
                                    axis=1))
contact_data['Есть контакт_всего'] = (contact_data
                                      .apply(
                                        lambda row: sum(row[column]
                                                        for column in
                                                        columns_contact_total[
                                                            3:-1
                                                            ]
                                                        ),
                                        axis=1))
contact_data['Нет контакта'] = (contact_data
                                .apply(
                                    lambda row:
                                    sum(row[column]
                                        for column in
                                        columns_contact[0:2]),
                                    axis=1))
contact_data['Нет контакта_всего'] = (contact_data
                                      .apply(
                                        lambda row: sum(row[column]
                                                        for column in
                                                        columns_contact_total[
                                                            0:2
                                                            ]
                                                        ),
                                        axis=1))
contact_data.sort_values(by='Дата', inplace=True)
childrens_main_table = main_table[
    main_table['Показатели'] == 'Выпускники'][list(main_table.columns[4:-1])]
childrens_main_table['Критерии'] = [
    'Количество выпускников в проекте_всего',
    'Количество выпускников в проекте',
    'Количество выпускников на связи_всего',
    'Количество выпускников на связи',
    'Количесво присоединившихся впервые',
    'Количество внешних партнеров',
    'Количество перенаправлений к внешним партнерам',
    'Количество мероприятий для выпускников онлайн',
    'Количество мероприятий для выпускников офлайн',
    'Общее количество выпускников, участвующих в онлайн встречах',
    ('Количество активных участников сообщества'
     ' (участие в мероприятиях (минимум 2/мес),'
     ' присутствие в чате выпускников,'
     ' коммуникация в онлайн (контект, комментарии))'),
    'Количество выпускников, принявших участие в мониторинге',
    'Количество выпускников, состоящие в онлайн-сообществе']
childrens_main_table = childrens_main_table.set_index('Критерии')
childrens_main_table = childrens_main_table.T
childrens_main_table.drop(["За 2022 год\n(уникальные)"], axis=0, inplace=True)
childrens_main_table.index = childrens_main_table.index.map(
    lambda x:
    datetime.datetime(
        year=2023 if re.search(r'\d', x)
        else 2022,
        month=months[x.split('\n')[0].split(' ')[0].strip()],
        day=1))
childrens_main_table.dropna(inplace=True)
childrens_main_table.drop(['Количество внешних партнеров',
                           'Количество перенаправлений к внешним партнерам',
                           ('Количество выпускников,'
                            ' принявших участие в мониторинге')],
                          axis=1, inplace=True)
childrens_main_table.reset_index(inplace=True)
childrens_main_table.rename(columns={'index': 'Дата'},
                            inplace=True)
for column in exclude_date(childrens_main_table):
    childrens_main_table[column] = childrens_main_table[column].astype(int)


if __name__ == '__main__':
    st.title('Сводная аналитика 📈📊')
    changes = st.checkbox('Посмотреть изменения в %')
    if changes:
        for column in exclude_date(coverage):
            coverage[column] = coverage[column].pct_change().dropna()
        schedule_1['Кол-во уроков в день'] = (schedule_1[
            'Кол-во уроков в день'
            ].pct_change().dropna())
        schedule_2['Учителей'] = schedule_2['Учителей'].pct_change().dropna()
        schedule_3['Кол-во отмен уроков'] = (schedule_3[
            'Кол-во отмен уроков']
                                             .pct_change().dropna())
        schedule_4["% отмененных уроков"] = (schedule_4[
            "% отмененных уроков"]
                                             .pct_change().dropna())
        for column in exclude_date(schedule_5):
            schedule_5[column] = (schedule_5[column]
                                  .pct_change()
                                  .dropna())
        for column in exclude_date(trainings_t):
            trainings_t[column] = (
                trainings_t[column].pct_change().dropna())
        for column in exclude_date(profi_main_table):
            profi_main_table[column] = (profi_main_table[column]
                                        .pct_change()
                                        .dropna())
        labor['Кол-во дней в Командировках'] = (labor[
            'Кол-во дней в Командировках'].pct_change().dropna())
        for column in exclude_date(achivments_debit_t):
            achivments_debit_t[column] = (achivments_debit_t[column]
                                          .pct_change()
                                          .dropna())
        for column in exclude_date(tech):
            tech[column] = (tech[column].pct_change()
                                        .dropna())
        for column in exclude_date(schedule_5):
            schedule_5[column] = (schedule_5[column]
                                  .pct_change().dropna())
        for column in exclude_date(contact_data):
            contact_data[column] = (contact_data[column]
                                    .pct_change()
                                    .dropna())
        for column in exclude_date(childrens_main_table):
            childrens_main_table[column] = (
                childrens_main_table[column].pct_change()
                                            .dropna())
    st.header('Охваты')
    column = st.selectbox(
        "Выберете колонку",
        exclude_date(coverage)
    )
    fig = px.bar(
        coverage,
        x=coverage['Дата'],
        y=coverage[column],
        text_auto='.2s',
        title="Динамика {} по дате".format(column))
    st.plotly_chart(fig)
    with st.expander("Посмотреть данные"):
        st.dataframe(coverage)

    st.header('Уроки')
    st.line_chart(
        data=schedule_1,
        x='Дата',
        y='Кол-во уроков в день')
    with st.expander("Посмотреть данные"):
        st.dataframe(schedule_1)

    fig = px.bar(
        schedule_2,
        x=schedule_2['Дата'],
        y=schedule_2['Учителей'],
        text_auto='.2s',
        title="Динамика кол-во учителей по дате")
    st.plotly_chart(fig)
    with st.expander('Посмотреть данные'):
        st.dataframe(schedule_2)
    st.line_chart(
        data=schedule_3,
        x='Дата',
        y='Кол-во отмен уроков'
    )
    with st.expander('Посмотреть данные'):
        st.dataframe(schedule_3)
    fig = px.bar(
        schedule_4,
        x='Дата',
        y='% отмененных уроков',
        text_auto='.2s',
        title="Динамика % отмененных уроков по дате")
    st.plotly_chart(fig)
    with st.expander('Посмотреть данные'):
        st.dataframe(schedule_4)
    column = st.selectbox(
        "Выберете колонку",
        list(
            set(schedule_5.columns) - set(['Дата'])))
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=schedule_5['Дата'],
            y=schedule_5[column],
            mode='lines',
            name='lines'
            )
    )
    st.plotly_chart(fig)
    with st.expander('Посмотреть данные'):
        st.dataframe(schedule_5)

    st.header('Тренинги')
    column = st.selectbox(
        'Выберете колонку',
        list(set(trainings_t.columns)-set(['Дата', 'месяц']))
    )
    fig = px.bar(
        trainings_t, x="Дата", y=column)
    st.plotly_chart(fig)
    with st.expander("Посмотреть данные"):
        st.dataframe(trainings_t)

    st.header('Поступление')
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(admission)
    with col2:
        admission['Тип учебного заведения'] = admission['Критерии'].apply(
            lambda x: 'ВУЗ' if 'ВУЗ' in x else "ССУЗ"
        )
        admission_diag = admission.loc[10:15]
        admission_diag.drop([10, 13], axis=0, inplace=True)
        fig = px.sunburst(
            admission_diag, path=['Тип учебного заведения', 'Критерии'],
            values="За 2022 год\n(уникальные)",
        )
        st.plotly_chart(fig)

    st.header('Профориентация')
    st.write('Профессионалов в таблице Профи', number_profi - 1)
    column = st.selectbox(
        'Выберете колонку',
        exclude_date(profi_main_table),
        index=0,
        key=45)
    fig = px.bar(
        profi_main_table,
        y=column,
        x=profi_main_table['Дата'],
        text_auto='.2s',
        title="Динамика {} по годам".format(column))
    st.plotly_chart(fig)
    with st.expander("Посмотреть данные"):
        st.dataframe(profi_main_table)

    st.header('Сотрудники')
    fig = px.bar(
        labor,
        y='Кол-во дней в Командировках',
        x=labor["Дата"],
        text_auto='.2s',
        title="Динамика кол-во дней в командировках по дате")
    st.plotly_chart(fig)
    with st.expander('Посмотреть данные'):
        st.dataframe(labor)

    st.header('Геймификация')
    column = st.selectbox(
        "ВЫберете показатель",
        list(
            set(achivments_debit_t.columns) - set(
                ["Дата"])))
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=achivments_debit_t["Дата"],
            y=achivments_debit_t[column],
            name=column))
    st.plotly_chart(fig)
    with st.expander("Посмотреть данные"):
        st.dataframe(achivments_debit_t)

    st.header('Техника')
    fig = go.Figure()
    for column in exclude_date(tech):
        fig.add_trace(go.Bar(
            x=tech['Дата'],
            y=tech[column],
            name=column))
    fig.update_layout(
        barmode='group',
        xaxis_tickangle=-45,
        title='Техника',
        xaxis_title='дата',
        yaxis_title='кол-во заявок')
    st.plotly_chart(fig)
    with st.expander("Посмотреть данные"):
        st.dataframe(tech)

    st.header('Выпускники')
    column = st.selectbox(
        'Выберете колонки для визуализации',
        exclude_date(childrens_main_table),
        index=1,
        key=1000000)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            x=childrens_main_table['Дата'],
            y=childrens_main_table[column],
            mode='lines',
            name=column))
    fig.update_layout(
        autosize=False,
        width=800,
        height=800,
    )
    st.plotly_chart(fig)
    with st.expander("Посмотреть данные"):
        st.dataframe(childrens_main_table)

    st.subheader('Статус контакта')
    tab1, tab2 = st.tabs(["Столбчатая диаграмма", "Показатель"])
    with tab1:
        column = st.selectbox(
            'Выберете колонку',
            set(contact_data.columns) - set(['Дата']),
            index=0, key=55)
        fig = px.line(
            contact_data,
            y=column,
            x='Дата',
            title="Динамика {} по годам".format(column))
        st.plotly_chart(fig)
    with tab2:
        numerator = st.multiselect('Введите числитель', list(
            set(contact_data.columns) - set(
                    ['Дата',
                     'ID ученика',
                     'ID ученика_shans',
                     'Тип места проживания',
                     "Участник программы ШАНС  (за весь период)"])),
                    ['Есть контакт'], key=11000000)
        denominator = st.multiselect('Введите знаменатель', list(
            set(contact_data.columns) - set(
                ['Дата',
                 'ID ученика',
                 'ID ученика_shans',
                 'Тип места проживания',
                 "Участник программы ШАНС  (за весь период)"
                 ])),
                    ['Нет контакта'], key=21000000)
        column_name = st.text_input('Введите название колонки')
        if st.button('Рассчитать'):
            try:
                contact_data[column_name] = sum(
                    contact_data[column] for column in numerator)/sum(
                        contact_data[column] for column in denominator)
                fig = px.line(contact_data, x='Дата', y=column_name)
                st.plotly_chart(fig)
            except ZeroDivisionError:
                st.write('Ошибка: деление на ноль')
    with st.expander("Посмотреть данные"):
        st.dataframe(contact_data)
