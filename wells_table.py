"""Диаграмма Ганта из работ ГРР."""
import plotly.figure_factory as ff
import pandas as pd
import datetime as dt

# Load the xlsx file
data = pd.read_excel('wells.xlsx', sheet_name='wells')
drills: int = 5


def search(data):
    """Загрузка исходных данных из файла."""
    data.sort_values(
        by=[
            'Priority_S',
            'Priority_Name',
            ]).to_excel(
                'wells_search.xlsx',
                sheet_name ='wells',
                index=False,
        )
    return pd.read_excel('wells_search.xlsx', sheet_name='wells')

def plot(list_of):
    """
    

    Parameters
    ----------
    list_of : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    df = []

    for i in range(len(list_of['Name'])):
        name = list_of['Name'][i]
        start = list_of['Start_data'][i]
        finish = list_of['End_data'][i]
        resource = list_of['Type'][i]
        df.append(dict(Task=name, Start=start, Finish=finish, Resource=resource))

    colors = {'Search': 'rgb(127, 127, 127)',
              'Exploration': 'rgb(230, 89, 7)',
              'Complete': 'rgb(0, 255, 100)'}

    fig = ff.create_gantt(df, colors=colors, index_col='Resource', show_colorbar=True,
                          group_tasks=True)
    fig.show()
    
def check(something_a):
    #print(something_a)
    for i in range(len(something_a['Name'])):
        print(something_a['Name'][i])
    #print('++++++++++++++++++++++++++++++++')
    
def test(something):
    for i in range(drills-1):
        # Проверяем что скважина зависимая
        if something['if_well'][i+2] != 0:
            index_of1 = list(something[something['Name']==something['if_well'][i+2]].index)[0]
            print(something['Name'][index_of1])
            # Проверяем, что первоочередной скважине не назначена дата завершения
            if something['End_data'][index_of1] == 0:
                something['Start_data'][i+2] = dt.datetime(year=2024, month=1, day=10) + dt.timedelta(137+10+90+180)
                something['End_data'][i+2] = dt.datetime(year=2024, month=1, day=10) + dt.timedelta(137+10+90+180) + dt.timedelta(days=(160+10+90))      
            # Если первоочередной скважине дата была назначена, то проверяем ее дату завершения, она должна быть на 180 дней раньше, чем планируемая дата начала бурения зависимой скважины
            elif (something['End_data'][index_of1] + dt.timedelta(180)) < dt.datetime(year=2024, month=1, day=1):
                something['Start_data'][i+2] = dt.datetime(year=2024, month=1, day=10)
                something['End_data'][i+2] = dt.datetime(year=2024, month=1, day=10) + dt.timedelta(days=(160+10+90))
            # Иначе добавляем 180 дней к дате завершения бурения первоочердной скважины
            else:
                something['Start_data'][i+2] = something['End_data'][index_of1] + dt.timedelta(180)
                something['End_data'][i+2] = something['End_data'][index_of1] + dt.timedelta(180) + dt.timedelta(days=(160+10+90))
        else:
            something['Start_data'][i+2] = dt.datetime(year=2024, month=1, day=10)
            something['End_data'][i+2] = dt.datetime(year=2024, month=1, day=10) + dt.timedelta(days=(160+10+90))
    for j in range(drills+1,len(something['Name']), drills):
        for c in range(drills):
            # Проверка начала бурения зависимых разведочных от первоочередных поисковых (не ранее полугода)

            # Костыль, позволяющий использовать количество станков не являющееся делителем для количества скважин
            if j+c < len(something['Name']):
                # Проверяем что скважина зависимая
                if something['if_well'][j+c] != 0:
                    index_of = list(something[something['Name']==something['if_well'][j+c]].index)[0]
                    # Проверяем что первоочередной скважине назначена дата завершения
                    if something['End_data'][index_of] != 0:
                        # Проверяем если зависимая скважина начинается раньше чем первоочередная, то присваиваем ей дату начала: дату завершения первоочередной + 180 дней (отправляем станок в StandBy)
                        if (something['End_data'][j+c-drills]+dt.timedelta(days=45)) < (something['End_data'][index_of] + dt.timedelta(days=180)):
                            something['Start_data'][j+c] = something['End_data'][index_of] + dt.timedelta(days=180)
                            something['End_data'][j+c] = something['Start_data'][j+c] + dt.timedelta(days=137+10+90) 
                        # Если зависимая скважина начинается бурением после чем завершается первоочередная +180сут, то продолжаем ее бурить тем же станком
                        else:
                            something['Start_data'][j+c] = something['End_data'][j+c-drills] + dt.timedelta(days=45)- dt.timedelta(days=90)
                            something['End_data'][j+c] = something['Start_data'][j+c] + dt.timedelta(days=137+10+90)
                    # Если скважина зависимая, но первоочередной не успели назначить дату завершения бурения, то
                            
                # Если скважина незаивисимая от первоочередных, то продолжаем ее бурить тем же станком
                else:
                    # Проверка, чтобы зависимые от СРР 3Д скважины начали буриться не раньше, чем закончилась интерпретация СРР 3Д
                    if something['if_SRR_3D'][j+c] == 0 or (something['End_data'][j+c-drills] + dt.timedelta(days=45)- dt.timedelta(days=90)) > dt.datetime(year=2026, month=1, day=1):
                        something['Start_data'][j+c] = something['End_data'][j+c-drills] + dt.timedelta(days=45)- dt.timedelta(days=90) 
                        something['End_data'][j+c] = something['Start_data'][j+c] + dt.timedelta(days=137+10+90)
                    else:
                        something['Start_data'][j+c] = dt.datetime(year=2026, month=1, day=1)
                        something['End_data'][j+c] = something['Start_data'][j+c] + dt.timedelta(days=137+10+90)

    return something


if __name__ == '__main__':
    plot(test(search(data)))
