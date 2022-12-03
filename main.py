import pandas as pd

FILE = 'задание для аналитика_Окт 2021.xlsx'

xl = pd.ExcelFile(FILE)
forest_guide, collection_result, task = xl.sheet_names

fg = pd.read_excel(FILE, sheet_name=forest_guide)
cr = pd.read_excel(FILE, sheet_name=collection_result).rename({'Unnamed: 0': 'ягода'}, axis=1)


# Сколько можно сделать шагов максимально/минимально при утилизации ягод в разрезе разных данных
def max_min_steps(df_guide, df_collection):
    """
    Не до конца понятно как вес ягоды влияет на движение. Будем решать задачу из следующих предположений:
    1. Собрав ягоду, ее утилизируют, получают число шагов (шагов дает) и прибавляют к числу накопленных шагов.
    2. Если число накопленных шагов становится меньше 1, то будем считать, что движение прекратилось.
    3. В начале каждого дня количество шагов сбрасывается.
    :param df_guide: dataframe of forest guide
    :param df_collection: dataframe of the result of picking berries in the forest
    :return: max_steps: int, min_steps: int
    """

    df_steps_max = df_guide[['ягода', 'шагов дает']].sort_values(by=['ягода', 'шагов дает'])
    df_steps_min = df_guide[['ягода', 'шагов дает']].sort_values(by=['ягода', 'шагов дает'])
    df_steps_max.drop_duplicates(subset=['ягода'], keep='last', inplace=True)
    df_steps_min.drop_duplicates(subset=['ягода'], keep='first', inplace=True)

    df_collection_max = pd.merge(left=df_collection[['ягода', 'дата обнаружения']], right=df_steps_max, on='ягода')
    max_steps = df_collection_max.groupby('дата обнаружения').sum().max()[0]

    df_collection_min = pd.merge(left=df_collection[['ягода', 'дата обнаружения']], right=df_steps_min, on='ягода')
    df_collection_min.groupby('дата обнаружения').sum()
    min_steps = df_collection_min.groupby('дата обнаружения').sum().min()[0]
    return max_steps, min_steps


# Дайте полный анализ несоответствия данных справочника и выгрузки
def find_all_incongruity(df_guide, df_collection):
    df_berry_guide_duplicate_error = df_guide.assign(повтор=df_guide.duplicated('ягода').values)
    df_berry_guide_duplicate_error = df_berry_guide_duplicate_error[['ягода', 'повтор']]
    df_berry_collection_mass_error = pd.merge(left=df_collection, right=df_guide[['ягода', 'вес']], on='ягода',
                                              suffixes=('_нашли', '_по_справочнику'))
    df_berry_collection_mass_error = df_berry_collection_mass_error.assign(
        вес_отличается=lambda x: x['вес_нашли'] != x['вес_по_справочнику'])
    df_berry_collection_mass_error = df_berry_collection_mass_error[
        ['ягода', 'дата обнаружения', 'вес_нашли', 'вес_по_справочнику', 'вес_отличается']]
    series_berry_collection_quantity_error = df_collection.groupby('ягода').size()
    df_berry_collection_quantity_error = pd.merge(left=df_guide,
                                                  right=series_berry_collection_quantity_error.to_frame(), on='ягода')
    df_berry_collection_quantity_error = df_berry_collection_quantity_error.rename({0: 'собрано'}, axis=1)[
        ['ягода', 'количество в лесу', 'собрано']]

    with pd.ExcelWriter('result.xlsx') as writer:
        df_berry_guide_duplicate_error.to_excel(writer, sheet_name='повторы справочника')
        df_berry_collection_mass_error.to_excel(writer, sheet_name='масса(справочник, выгрузка)')
        df_berry_collection_quantity_error.to_excel(writer, sheet_name='кол-во(справочник, выгрузка)')
    return writer


# Составьте сводную таблицу с итогами количества ягод по цвету
def color_distribution(df_collection):
    series_berry_collection_color_distribution = df_collection.groupby('цвет').size()
    df_berry_collection_color_distribution = pd.DataFrame({'цвет': series_berry_collection_color_distribution.index,
                                                           'количество': series_berry_collection_color_distribution.values})
    with pd.ExcelWriter('result.xlsx', mode='a') as writer:
        df_berry_collection_color_distribution.to_excel(writer, sheet_name='распределение цветов')
    return writer


# Укажите сколько ягод имеют разные цвета в пределах первой половины справочника
def color_difference(df_guide, df_collection):
    df_color_difference = pd.merge(left=df_guide.head(len(df_guide) // 2)[['ягода']],
                                   right=df_collection[['ягода', 'цвет']], on='ягода')
    df_color_difference.drop_duplicates(keep='first', inplace=True)
    with pd.ExcelWriter('result.xlsx', mode='a') as writer:
        df_color_difference.to_excel(writer, sheet_name='ягоды(цвета)')
    return df_color_difference.nunique()['ягода']


# Найти соотношение количества ягод из выгрузки при котором будет сделано 0 шагов
def zero_step(df_guide, df_collection):
    """
    Ввиду того, что не совсем понятно, как в задаче реализуется механика движения и как связаны между собой вес,
    количество шагов и дата, будем решать задачу следующим методом: найдем те дни,
    когда перед сбором "волчьей ягоды" (-18 шагов) собирались:
    - "черника" (18 шагов) или
    - "малина" (13 шагов) и крыжовник (5 шагов) или
    - крыжовник (5 шагов), крыжовник (5 шагов) и "брусника" (8 шагов).
    """
    pass
    # df_collection_by_date = pd.merge(left=df_collection[['ягода', 'дата обнаружения']],
    #                                  right=df_guide[['ягода', 'шагов дает']],
    #                                  on='ягода').groupby(['дата обнаружения', 'ягода']).min()
    # df_collection_by_date['1 день назад'] = df_collection_by_date['шагов дает'].shift()
    # df_collection_by_date['2 дня назад'] = df_collection_by_date['1 день назад'].shift()
    # df_collection_by_date['3 дня назад'] = df_collection_by_date['2 дня назад'].shift()
    # df_collection_by_date = df_collection_by_date[df_collection_by_date['шагов дает'] == -18]
    # print(df_collection_by_date)
    # print(df_collection_by_date[df_collection_by_date['шагов дает'] == -18])


# Определить в какие по счету дни ягоды не обнаруживаются
def days_without_berries(df_collection):
    begin_date = df_collection['дата обнаружения'].min()
    end_date = df_collection['дата обнаружения'].max()
    df_date = pd.DataFrame({'дата обнаружения': pd.date_range(start=begin_date, end=end_date)})
    df_days_without_berries = pd.concat([df_date, df_collection[['дата обнаружения']]]).drop_duplicates(
        subset=['дата обнаружения'],
        keep=False)
    df_days_without_berries = df_days_without_berries.rename({'дата обнаружения': 'дата без ягод'}, axis=1)
    with pd.ExcelWriter('result.xlsx', mode='a') as writer:
        df_days_without_berries.to_excel(writer, sheet_name='дни без ягод')
    return writer


# Определить в какой день недели обнаружено больше всего ягод белого цвета
def white_berries_day(df_collection):
    df_white_berries_day = df_collection[df_collection['цвет'] == 'белый'][['дата обнаружения']]
    df_result = df_white_berries_day.groupby(df_white_berries_day.columns.tolist()).size().reset_index().rename(
        columns={0: 'белых ягод'})
    df_result = df_result[df_result['белых ягод'] > 1]
    with pd.ExcelWriter('result.xlsx', mode='a') as writer:
        df_result.to_excel(writer, sheet_name='дни белых ягод')
    return writer


if __name__ == '__main__':
    max_step, min_step = max_min_steps(fg, cr)
    print(
        f'При утилизации ягод в разрезе разных данных можно сделать:\n- максимум {max_step} шагов;\n- минимум {min_step} шагов.')
    find_all_incongruity(fg, cr)
    color_distribution(cr)
    print(f'{color_difference(fg, cr)} ягод имеют разные цвета в пределах первой половины справочника.')
    zero_step(fg, cr)
    days_without_berries(cr)
    white_berries_day(cr)
