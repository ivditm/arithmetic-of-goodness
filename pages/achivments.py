import pandas as pd
import streamlit as st
import warnings


from core.utils import read_file, make_full_analyses_anomalies


warnings.filterwarnings('ignore')
st.set_option('deprecation.showPyplotGlobalUse', False)


achivments = read_file(st.secrets['spreadsheet_id_achivments'],
                       st.secrets['zero_gid'])
achivments['Дата операции'] = pd.to_datetime(achivments['Дата операции'])
achivments['Месяц операции'] = achivments['Месяц и год операции'].apply(
    lambda x: x.split(' ')[0]
)
achivments['Год операции'] = achivments['Месяц и год операции'].apply(
    lambda x: int(x.split(' ')[1])
)
achivments['Сумма'].fillna(0, inplace=True)
achivments['Сумма'] = achivments['Сумма'].apply(
    lambda x: 0 if not isinstance(x, float) else x)
achivments['Сумма'] = achivments['Сумма'].astype(float)
achivments['Сумма'].fillna(0, inplace=True)
achivments_debit = achivments[achivments['Тип операции'] == 'Списание']
achivments_debit = achivments_debit[
    achivments_debit['Статус заявки'] == 'Заявка выполнена'
]
achivments_debit['Дата исполнения заявки'] = pd.to_datetime(
    achivments_debit['Дата исполнения заявки']
)
achivments_debit['Дата исполнения заявки'] = achivments_debit[
    'Дата исполнения заявки'
].dt.date
achivments_debit['Сумма'] = achivments_debit['Сумма'].astype(float)
achivments_debit['Сумма'].fillna(0, inplace=True)


if __name__ == '__main__':
    st.title('Достижения 🏅')
    factor = st.selectbox(
        'Выберете фактор', [
            None, *['Профит',
                    'Тип операции',
                    'Месяц операции',
                    'Год операции',
                    'Статус заявки',
                    'Менеджер']])
    make_full_analyses_anomalies(achivments, 'Сумма', factor)
    with st.expander("Посмотреть данные"):
        st.dataframe(achivments)
