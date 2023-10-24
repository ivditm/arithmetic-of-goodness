from dataclasses import dataclass
from http import HTTPStatus
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import re
import requests
from scipy import stats as sst
import seaborn as sns
import streamlit as st
import sys
from typing import Optional, Union
from io import BytesIO
import warnings


from core.exceptions import BaseException


warnings.filterwarnings('ignore')

PATH_ERROR_TEXT = 'некоррекнто прописан путь к данным'
NOT_LIST = 'входные данные должны быть в форме списка'
NOT_STR = 'в списке должны быть строки'


@st.cache_data
def plot_plotly_distr(columns: list[str], data: pd.DataFrame) -> None:
    n_g: int = int(len(columns)/2 + 1)
    fig = make_subplots(rows=n_g, cols=2)
    cols: list[int] = [1, 2] * n_g
    rows: list[int] = sorted(
        [i for i in range(1, n_g + 1)] + [i for i in range(1, n_g + 1)]
    )
    for column, row, cal in zip(columns, rows, cols):
        trace = go.Histogram(x=data[column].to_list(), name=column)
        fig.append_trace(trace, row, cal)
    fig.layout.width = 1000
    fig.layout.height = 1000
    return fig


@st.cache_data
def url_is_valid(url: str) -> bool:
    if not isinstance(url, str):
        raise ValueError('url must be string')
    return True if requests.get(url).status_code == HTTPStatus.OK else False


@st.cache_data
def read_file(spreadsheet_id: str, gid: int, sep: str = ',') -> pd.DataFrame:
    """
    Функция считывает данные из файла и
    возвращает дата фрейм
    """
    file_name = ('https://docs.google.com'
                 '/spreadsheets/d/{}/export?format=csv&gid={}'
                 .format(spreadsheet_id, gid))
    if url_is_valid(file_name):
        data = pd.read_csv(BytesIO(requests.get(file_name).content))
        return data
    else:
        st.error(PATH_ERROR_TEXT)
        raise BaseException(PATH_ERROR_TEXT) and sys.exit()


@st.cache_data
def get_full_information(data: pd.DataFrame) -> None:
    """
    Функция дает нам полное
    представление о данных
    """
    st.info('первое представление о данных')
    for _ in [data.head(), data.describe()]:
        st.write(_)
        st.write("*"*100)
    if not all([True if data[column].dtype == 'object' else
                False for column in data.columns]):
        fig = plot_plotly_distr([column for column in data.columns
                                 if data[column].dtype != 'object'], data)
        st.plotly_chart(fig)


def check_names_columns(data: pd.DataFrame) -> list[str]:
    """
    Функция проверяет, соответствуют
    ли имена колонок snake_style
    """
    columns_to_change = []
    pattern = r"^[a-z]+(_[a-z]+)*$"
    for column in data.columns:
        match = re.match(pattern, column)
        if match:
            continue
        else:
            columns_to_change.append(column)
    return columns_to_change


def change_name_columns(columns_to_change: list[str]) -> dict[str, str]:
    """
    Функция возвращает словарь,
    ключ- неправильное название колонки
    значение - верное
    """
    def sup_right_name(column: str) -> str:
        cont: list[str] = list(column)
        new_name: str = ''
        while cont:
            char = cont.pop()
            if len(cont) == 0:
                new_name = char.lower() + new_name
            elif char.isupper():
                new_name = f'_{char.lower()}' + new_name
            else:
                new_name = char + new_name
        return new_name
    right_names = []
    if not isinstance(columns_to_change, list):
        raise BaseException(NOT_LIST)
    for column in columns_to_change:
        if not isinstance(column, str):
            raise BaseException(NOT_STR)
    else:
        for column in columns_to_change:
            column = column.strip()
            if len(column.split()) != 1:
                column = '_'.join(column.split())
                column = column.lower()
            elif column.isupper():
                column = column.lower()
            elif re.match(r'^[a-zA-Z]+$', column):
                column = sup_right_name(column)
            right_names.append(column)
    columns = {wrong_name: right_name for wrong_name,
               right_name in zip(columns_to_change, right_names)}
    return columns


def find_nan(data: pd.DataFrame) -> dict:
    """
    Функция считает по каждой колонке, сколько в ней пропусков,
    если пропусков 0, то с колонкой все хорошо
    и ее мы трогать не будем
    """
    return {column: data[column].isna().sum()/len(data)
            for column in data.columns
            if data[column].isna().sum() != 0}


def drop_nan_less_five_percent(data: pd.DataFrame) -> pd.DataFrame:
    """
    Функция удаляет строки по колонкам,
    если кол-во пропусков в них составляло
    менее 5 процентов
    """
    columns_with_nan = find_nan(data)
    for column, percent in columns_with_nan.items():
        if percent < .05:
            data = data[data[column].notna()]
    return data


def works_dupblicates(data: pd.DataFrame) -> pd.DataFrame:
    """
    Функция работает с дубликатами
    """
    for column in data.columns:
        if (data.dtypes[column] == 'object' and
                isinstance(data[column][0], str)):
            data[column] = data[column].str.lower()
    if data.duplicated().sum() > 0:
        data = data.drop_duplicates()
    return data


def change_type_to_date(data: pd.DataFrame) -> pd.DataFrame:
    """
    Меняет формат на время
    """
    pattern = r'\d{4}-\d{2}-\d{2}'
    for column in data.columns:
        match = re.match(pattern, str(data[column][0]))
        if match:
            data[column] = pd.to_datetime(data[column])
    return data


@st.cache_data
def process_data(spreadsheet_id: str,
                 gid: str, sep: str = ',') -> pd.DataFrame:
    """
    Функция содержит основную логику
    первичной обработки данных
    """
    try:
        # читаем данные и выводим всю правду о них
        data = read_file(spreadsheet_id, gid, sep)
        # get_full_information(data)

        # работаем с названиями колонок
        columns_to_change = check_names_columns(data)
        if len(columns_to_change) > 0:
            columns_with_correct_name = change_name_columns(columns_to_change)
            data = data.rename(columns=columns_with_correct_name)

        # поработаем с пропусками
        if len(find_nan(data)) > 0:
            data = drop_nan_less_five_percent(data)
        data = change_type_to_date(data)
        data = works_dupblicates(data)
        return data
    except BaseException as error_message:
        return error_message


def is_distribution_normal(data: pd.Series, alpha: float = .05) -> bool:
    """определяет нормальное ли распределение"""
    if sst.shapiro(data)[1] < alpha:
        return False
    return True


def calc_hypoteses(data_1, data_2,
                   alpha=0.05, equal_var=False,
                   bonferonnie=None):
    if bonferonnie is not None:
        alpha = alpha/bonferonnie
    results = sst.ttest_ind(data_1,
                            data_2,
                            equal_var=equal_var)
    st.write('p-value: ', round(results.pvalue, 5))
    if results.pvalue < alpha:
        st.write('Вывод: Отвергаем нулевую гипотезу о'
                 ' статистической незначимости')
    else:
        st.write('Вывод: Не получилось отвергнуть нулевую гипотезу'
                 ' о статистической незначимости')


def anal_hyp(data_1, data_2, alpha=0.05, bonferonnie=None):
    if is_distribution_normal(data_1) and is_distribution_normal(data_2):
        st.info('Данные распределены нормально')
        calc_hypoteses(data_1, data_2,
                       equal_var=True, alpha=alpha,
                       bonferonnie=bonferonnie)
    calc_hypoteses(data_1, data_2, alpha=alpha, bonferonnie=bonferonnie)


class BoxMath:
    """Parents math class for anomalies"""

    CONSTANT: Optional[Union[int, float]] = None

    def __init__(self, df: pd.DataFrame, column: str) -> None:
        """
        инициализация
        """
        self.df = df
        self.column = column
        if self.column not in set(self.df.columns):
            raise ValueError('ошибка при формировании класса')
        if self.df[self.column].isna().sum() > 0:
            self.df = self.df[self.df[self.column].notna()]

    @property
    def metrics(self) -> dict[str: Union[int, float]]:
        """
        Рассчитываем показатели:
        необходмые для вычислений
        """
        pass

    @property
    def max_not_anomal(self) -> Union[int, float]:
        """
        Вычисляет верхнюю границу усов
        """
        pass

    @property
    def min_not_anomal(self) -> Union[int, float]:
        """
        Вычисляет нижнюю границу усов
        """
        pass

    def is_distribution_normal(self, alpha: float = 0.05) -> bool:
        """определяет нормальное ли распределение"""
        if sst.shapiro(self.df[self.column])[1] < alpha:
            return False
        return True

    @property
    def anomalies(self) -> pd.Series:
        """
        аномальные значения
        """
        return (self.df[
                        (self.df[self.column] < self.min_not_anomal) |
                        (self.df[self.column] > self.max_not_anomal)
                        ][self.column])

    @property
    def anomalies_indexs(self) -> pd.Series:
        """Возращает индексы аномальных строк"""
        return self.anomalies.index


class BoxIQR(BoxMath):
    """
    Класс содержит анализ по выбросам
    """

    CONSTANT: float = 1.5

    @property
    def metrics(self) -> dict[str: Union[int, float]]:
        """
        Рассчитываем показатели:
        -второй квартиль
        -третий квартиль
        -межквартильный размах
        """
        q75, q25 = np.percentile(self.df[self.column], [75, 25])
        metrics: dict[str: float] = {'iqr': q75 - q25,
                                     'q75': q75,
                                     'q25': q25}
        return metrics

    @property
    def max_not_anomal(self) -> Union[int, float]:
        """
        Вычисляет верхнюю границу усов
        """
        max_not_anomal: float = (self.metrics['q75'] +
                                 self.CONSTANT * self.metrics['iqr'])
        if (max_not_anomal > self.df[self.column].max()):
            return self.df[self.column].max()
        else:
            return max_not_anomal

    @property
    def min_not_anomal(self) -> Union[int, float]:
        """
        Вычисляет нижнюю границу усов
        """
        min_not_anomal: float = (self.metrics['q25']
                                 - self.CONSTANT * self.metrics['iqr'])
        if min_not_anomal < self.df[self.column].min():
            return self.df[self.column].min()
        else:
            return min_not_anomal

    @property
    def min_p_anom(self) -> Union[int, float]:
        """минималльный положительный выброс по доходности"""
        return self.anomalies[self.anomalies > 0].min()


class BoxSTD(BoxMath):
    """Считает выбросы в нормальном распределении"""
    CONSTANT: int = 3

    @property
    def metrics(self) -> dict[str:Union[int, float]]:
        """возращает стандартное отклонение и среднее"""
        return {'std': self.df[self.column].std(),
                'mean': self.df[self.column].mean()}

    @property
    def max_not_anomal(self) -> Union[int, float]:
        """Возвращает верхнюю границу"""
        max_not_anomal: float = (self.metrics['mean']
                                 + self.CONSTANT * self.metrics['std'])
        if max_not_anomal > self.df[self.column].max():
            return self.df[self.column].max()
        else:
            return max_not_anomal

    @property
    def min_not_anomal(self) -> Union[int, float]:
        """Возвращает нижнюю границу"""
        min_not_anomal: float = (self.metrics['mean']
                                 - self.CONSTANT * self.metrics['std'])
        if min_not_anomal < self.df[self.column].min():
            return self.df[self.column].min()
        else:
            return min_not_anomal


class BoxVisualisation:
    """
    Строим графики к выбросам
    """

    def __init__(self, math_object: BoxMath,
                 level: Optional[str] = None) -> None:
        """инициализация"""
        self.math_object = math_object
        self.level = level
        if self.level is not None and not isinstance(self.level, str):
            raise TypeError('suplements parametr must be str')
        elif self.level is not None and self.level not in set(self.math_object
                                                              .df
                                                              .columns):
            raise TypeError('column not found - 404')

    def represent_violinplot(self, plots_size: tuple[int] = (15, 15)) -> None:
        sns.set_palette('dark')
        plt.figure(figsize=plots_size)
        plt.title("Violin plot", loc="left")
        if self.level is not None:
            sns.violinplot(x=self.math_object.df[self.math_object.column],
                           y=self.math_object.df[self.level])
        else:
            sns.violinplot(x=self.math_object.df[self.math_object.column])
        plt.show()

    def represent_box(self, plots_size: tuple[int] = (15, 15)) -> None:
        """выводит бокс-плот"""
        sns.set_palette('dark')
        plt.figure(figsize=plots_size)
        plt.title('Бокс-плот')
        if self.level is not None:
            sns.boxplot(x=self.math_object.df[self.math_object.column],
                        y=self.math_object.df[self.level],
                        color='mediumpurple')
        else:
            sns.boxplot(x=self.math_object.df[self.math_object.column])
        plt.show()

    def represent_in_detail(self, plots_size: tuple[int] = (15, 15)) -> None:
        """приближенный бокс-плот"""
        sns.set_palette('dark')
        plt.figure(figsize=plots_size)
        plt.title('Приближенный бокс-плот')
        if self.level is not None:
            sns.boxplot(x=self.math_object.df[self.math_object.column],
                        y=self.math_object.df[self.level], showcaps=False,
                        color='mediumpurple')
        else:
            sns.boxplot(x=self.math_object
                        .df[self.math_object.column]).set_xlim(
                [self.math_object.min_not_anomal,
                 self.math_object.max_not_anomal])
        plt.show()

    def represent_scatter(self, plots_size: tuple[int] = (20, 20)) -> None:
        """"выводит точечный график"""
        sns.set_palette('dark')
        plt.figure(figsize=plots_size)
        plt.title('Точечный график')
        if self.level is not None:
            sns.scatterplot(x=self.math_object.df.index,
                            y=self.math_object.df[self.math_object.column],
                            hue=self.math_object.df[self.level])
        else:
            sns.scatterplot(x=self.math_object.df.index,
                            y=self.math_object.df[self.math_object.column])
        plt.axhline(y=self.math_object.max_not_anomal,
                    color='red',
                    linestyle='dotted',
                    label='Максимальное значение без выбросов')
        plt.axhline(y=self.math_object.min_not_anomal,
                    color='red',
                    linestyle='dotted',
                    label='Минимальное значение без выбросов')
        plt.axhline(y=self.math_object.df[self.math_object.column].median(),
                    color='green',
                    linestyle='--',
                    label='Медиана')
        plt.axhline(y=self.math_object.df[self.math_object.column].mean(),
                    color='pink',
                    linestyle='--',
                    label='Среднее значение')
        plt.legend()
        plt.show()

    def represent_histplot(self, plots_size: tuple = (15, 15)) -> None:
        """распределение с выбросами"""
        sns.set_palette('dark')
        plt.figure(figsize=plots_size)
        sns.kdeplot(self.math_object.df[self.math_object.column])
        plt.axvline(x=self.math_object.df[self.math_object.column].mean(),
                    color='green', linestyle='--', label='Среднее значение')
        plt.axvline(x=self.math_object.min_not_anomal, color='orange',
                    linestyle=':', label='Минимальное значение без выбросов')
        plt.axvline(x=self.math_object.max_not_anomal, color='orange',
                    linestyle=':', label='Максимальное значение без выбросов')
        plt.title('гистограмма')
        plt.legend()
        plt.show()


@dataclass
class PrinterReport:
    """Выводим отчет"""

    math_object: BoxMath
    visual_object: BoxVisualisation
    visualisations = {'boxplot': 'represent_box',
                      'detail_box_plot': 'represent_in_detail',
                      'scatterplot': 'represent_scatter',
                      'violinplot': 'represent_violinplot',
                      'histplot': 'represent_histplot'}

    def print_result(self) -> None:
        graphs = st.selectbox('Choose a graph',
                              list(self.visualisations.keys()))
        getattr(self.visual_object, self.visualisations[graphs])()
        st.pyplot()

        for metric, value in self.math_object.metrics.items():
            st.write(f'{metric} - {value}')
        st.write(f"минимальное неаномальное значение"
                 f" {(self.math_object.min_not_anomal)}")
        st.write(f"максимальное неаномальное значение"
                 f" {(self.math_object.max_not_anomal)}")
        st.write('выбросов % - ',
                 round(
                     (len(self.math_object.anomalies) /
                      len(self.math_object.df)) * 100, 2))

        with st.expander("See anomalies"):
            df_anomalies = pd.DataFrame({'anomalies': (self.math_object
                                                       .anomalies),
                                         'index': (self.math_object
                                                   .anomalies_indexs)})
            st.dataframe(df_anomalies)


def make_full_analyses_anomalies(data: pd.DataFrame,
                                 column: str,
                                 factor: Optional[pd.Series] = None) -> None:
    if is_distribution_normal(data[column]):
        math: BoxMath = BoxSTD(data, column)
    else:
        math: BoxMath = BoxIQR(data, column)
    visualisation: BoxVisualisation = BoxVisualisation(math, factor)
    report: PrinterReport = PrinterReport(math, visualisation)
    report.print_result()


def process_city_name(city_name: str) -> str:
    """
    This function processes city names and returns the processed name.
    """
    if city_name.startswith("г."):
        return city_name[2:]
    elif city_name.endswith(" г"):
        return city_name[:-2]
    else:
        return city_name


def clean_city(city):
    city = re.sub(r'[^\w\s]', '', city)
    city = re.sub(r'\d+', '', city)
    city = city.strip()
    city = city.lower()
    return city


def exclude_date(df: pd.DataFrame) -> list[str]:
    return list(set(df.columns) - set([
        'Дата',
        'дата',
        'дата_первого_дня']))
