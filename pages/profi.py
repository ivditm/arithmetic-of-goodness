import plotly.express as px
import streamlit as st


from core.utils import (clean_city,
                        make_full_analyses_anomalies,
                        process_city_name,
                        read_file)


categories_city = {
    'Москва и Московская область': [
        'москва', 'дмитров',
        'балашиха', 'мытищи',
        'рп томилино', 'химки',
        'иваново', 'щелково', 'moscow'],
    'Южный федеральный округ': [
        'волгоград', 'астрахань',
        'краснодар', 'сочи'],
    'Приволжский федеральный округ': [
        'тольятти', 'уфа', 'оренбург',
        'рязань', 'нижний новгород', 'новочебоксарск'],
    'Северо-Западный федеральный округ': [
        'санктпетербург', 'череповец', 'великий новгород'],
    'Сибирский федеральный округ': [
        'омск', 'уланудэ', 'новосибирск'],
    'Уральский федеральный округ': ['екатеринбург'],
    'Зарубежные города': [
        'новая зеландия гамельтон',
        'австрия вена', 'германия бад кёниг хессен']
}


profi_table = read_file(st.secrets['spreadsheet_id_profi'],
                        st.secrets['zero_gid'])
for column in ['Город', 'Профессия']:
    profi_table[column].fillna('Не знаю', inplace=True)
    profi_table[column] = profi_table[column].apply(
        lambda x: x.lower())
    profi_table[column] = profi_table[column].apply(
        lambda x: x.strip())
profi_table['Город'] = profi_table['Город'].apply(func=process_city_name)
profi_table['Город'] = profi_table['Город'].apply(clean_city)
profi_table['Город'] = profi_table['Город'].apply(lambda x: 'москва'
                                                  if x == "moscow" else x)
profi_table['Регион'] = profi_table['Город'].apply(
    lambda x: [category for category,
               cities in categories_city.items()
               if x in cities][0]
    if any(x in cities for cities in categories_city.values()) else '')
number_profi = profi_table['ID профи'].count()


if __name__ == '__main__':
    st.title("Профи 🧑‍💼")
    st.dataframe(profi_table)
    categoris_profi = st.text_input('Введите название категорий через запятую')
    categoris_profi = [i.strip() for i in categoris_profi.split(',')]
    profi_category_prof = {}
    for idx, category in enumerate(categoris_profi):
        widget = st.multiselect("Выберите профессии в категории {}".format(
            category),
                                profi_table['Профессия'].unique(), key=idx)
        profi_category_prof[category] = widget
    profi_table['Категории профессии'] = profi_table['Профессия'].apply(
        lambda x: [category for category,
                   prof in profi_category_prof.items()
                   if x in prof][0]
        if any(x in prof for prof in profi_category_prof.values())
        else 'Другое')
    factor = st.selectbox('Выберите фактор', ['Регион', 'Категории профессии'],
                          key=110000000)
    plot_table = (profi_table.groupby(by=factor)
                             .agg({'Кол-во встреч c детьми': 'sum'})
                             .reset_index())
    fig = px.pie(plot_table, values='Кол-во встреч c детьми', names=factor,
                 title='Распределение встреч c детьми по {}'.format(factor),
                 hole=0.5, color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig)
    agree = st.checkbox('Хотите посмотреть распределение по факторам?')
    if agree:
        factor = st.selectbox('Выберите фактор',
                              ['Регион', 'Категории профессии'],
                              key=31000000)
        make_full_analyses_anomalies(profi_table,
                                     'Кол-во встреч c детьми',
                                     factor)
    else:
        make_full_analyses_anomalies(profi_table, 'Кол-во встреч c детьми')
