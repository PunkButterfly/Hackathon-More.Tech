# Решение задачи трэка DATA от команды **Punk Butterfly**  

## Результаты проделанной работы

- [Презентация](https://drive.google.com/file/d/1GnpSwvSbfGClLCCIcpZbu28kYOhJ79s1/view?usp=sharing)

## Модель для формирования ответа
В нашей модели используется 3 разных больших языковых моделей и алгоритм кластеризации, а личные компьютеры у нас не обладают хоть какими-то вычислительными мощностями, поэтому мы использовлаи google colab. У этого етсь один большой недостаток: по сути весь скрипт инференса модели это один .ipynb файл. Но в нём всё разбито на классы и функции, а так же подписаны markdown-заголовки для лучшего понимания. Также весь код оснащён подробными комментариями.

Сразу о главном. 
## Как запускать модель? 
Раздел для запуска называется **Основное взаимодествие**. В нём реализуется структура API.

В функцию get_response передаётся DataFrame, в который считан файл с новостями и датами публикации этих новостей. 

```python
def get_response(input_data, start_date, end_date):
    """
        Получение инсайтов, трендов и дайджеста.
        Вход:
            df - DataFrame с колонками 'content' и 'date'
            start_date_string - строка задающая начало временного периода, 
        в формате yyyy-mm-dd
            end_date_string - строка задающая конец временного периода.
        Выход:
            ответ в формате Json
    """
    text_pool = get_data_by_period(input_data, start_date, end_date) # выделение новостей из конкретного временного периода

    embeddins_pool = RuBertEmbedder().encode_data(text_pool, data_column='content') # получшение эмбеддингов из содержимого новостей

    clustering_data, centroids = KMeansClustering(text_pool, embeddins_pool).clustering() # кластеризация
    centroids_map = {i: centroids[i] for i in range(len(centroids))}

    insites = get_insites(clustering_data, centroids_map, top_for_cluster=30, max_news_len=150) # инсайты
    trends = get_trends(clustering_data, centroids_map, top_for_cluster=5, max_news_len=100) # тренды
    digest = get_digest(clustering_data, centroids_map, top_clusters=3) # дайджест

    response = format_json_response(insites, trends, digest, start_date, end_date) # агрегация результатов в формат Json

    return response
```
На выходе этой функции мы получаем ответ в формате Json, это сделано для некой эмуляции взаимодействия клиент-сервер.
По сути, самое важное в ```get_response()```, это ```get_insites()```, ```get_trends()```, ```get_digest()```. Эти функции выдают данные о инсайтах, трендах и дайджесте, которые далее преобразуются в ```format_json_response()```.

После этого, мы имеем данные в Json-формате, чтобы их вывести, вызывается функция ```format_output()```. 

То есть мы преобразовали данные в Json, а потом распарсили обратно. **Это некая эмуляция клиент-серверного взаимодействия с нашим API.**
Ниже представлен код, чтобы из всей этой солянки функций получить ответ, который мы хотим увидеть:
```python
ceo_data = pd.read_csv('/content/ceo_data.csv')
ceo_json_response = get_response(ceo_data, '2022-02-14', '2022-02-28')

acc_data = pd.read_csv('/content/acc_data.csv')
acc_json_response = get_response(acc_data, '2022-02-14', '2022-02-28')

print("Директора")
format_output(ceo_json_response)

print("Бухгалтеры")
format_output(acc_json_response)
```

А вот пример ответа, который выводит программа 
```
Директора
Дайджесты:
1. Российские биржи приостановили торги
2. ФАС разбертся, насколько обоснованным было резкое повышение цен в сети магазинов бытовой техники и электроники DNS.
3. У России есть наджный план на случай введения Западом новых санкций от драматичного сценария страну уберегут прочные макрофинансовые показатели, уверен министр финансов Антон Силуанов.

Тренды:
космический мусор
космонавтика
сбербанк
экосистема
финансы
хабекс
управление продуктом
сбер
транспорт
маркетплейс
сбер
управление продуктом

Инсайты:
1. Акции американской космической компании Virgin Galactic выросли на 13,11 до 8,85 за бумагу.
2. Российские биржи приостановили торги по всем видам ценных бумаг изза приближения котировок к установленным границам
3. Путин снял начальника Генштаба за провал операции по Украине
4. Инвестиции в ETF нашли больше полезных новостей для инвесторов
5. В ближайшую неделю Роскомнадзор готов начать процедуру приземления сайтов, продающих незарегистрированные БАДы
6. Сбербанк одобрил кредит под ИЖС, чтобы построить собственный дом на льготных условиях без подтверждения дохода
```

## Основная идея
Наша идея заключалась в разбиении пространства эмбеддингов новостей, выделении кластеров в этом пространстве и дальнейшем извлечении информации для генерации дайджеста, трендов и инсайтов. Мы утверждаем, что центроиды кластеров в многомерном пространстве эмбеддингов являются некой *информационной сущностью*, а сами эмбеддинги новостей - обобщением, в котором так или иначе содержится информация о *сущности*. 

#### Получение эмбеддингов 
Векторные представления новостей мы получали с помощью предобученной языковой модели [rubert-tiny2](https://huggingface.co/cointegrated/rubert-tiny2). Мы пробовали и другие encoder-ы, но их выходы были больше rubert-'a, а последующие преобразования ембеддингов в нашей глобальной модели были достаточно ресурсоёмки. К тому же, судя по распределению кластеров, он выигрывал у того же t5-encoder. 
#### Кластеризация 
Для кластеризации использовался алгоритм **K-means**, но он имеет большой недостаток: ему на вход нужно подавать число кластеров. Мы хотели использовать метод локтя для автоматического определения оптимального количества кластеров, но столкнулись с проблемой, что он работает слишком долго, поэтому мы запустили его на нескольких объемах данных и для них получили требуемые величины. После этого мы подобрали функцию зависимости числа кластеров от количества статей, которая проходит примерно через найденные нами точки(точки это объем данных, оптимальное число кластеров). Этой функцией стала: $num_{opt} = \sqrt[2.2]{num_{news}}$, где $num_{opt}$ - число оптимальных кластеров, $num_{news}$ - количество новостей. 

Далее нужно было из полученных кластеров выделить дайджест, инсайты и тренды. 

#### Дайджест

У нас есть сформированное пространство эмбеддингов, разбитое на кластеры. Для выделения дайджеста мы берём 3 самых больших кластера и выделям из них эмбеддинг статьи, который ближе всего к центроиде своего кластера. Далее по эмбеддингам просто находим статьи и выводим их заголовки.

#### Инсайты 

Мы решили что будем выделять один инсайт для каждого кластера. Для этого мы пользуемся предобученной языковой моделью [rut5-base-absum](https://huggingface.co/cointegrated/rut5-base-absum). В этой модели нас привлекла функция summarize. Она позволяет из нескольких текстов выделить выжимку, при этом не просто главный смысл, а именно заключение, основанное на анализе суммы текстов, а это очень подходит под определение инсайта. Для каждого кластера мы брали несколько самых близких новостей к центроиде и прогоняли их через summarize. На выходе получали одно предложение, которое является инсатом. 

#### Тренды 

Для трендов мы использовали модель [keyt5-large](https://huggingface.co/0x7194633/keyt5-large), которая умеет выделять ключевые сущности(слова, которые характеризуют текст) из новости. После получения набора ключевых слов для нескольких близких новостей к центроиде кластера мы дополнительно объединяли похожие ключевые слова. Делали это с помощью сравнения косинусного расстояния между эмбеддингами.


## Источники
Ссылки на каналы и сайты, с которых мы парсили новости.
### Генеральные директоры   

Новостные сайты:
- [journal.tinkoff.ru](https://journal.tinkoff.ru/)  
- [secretmag.ru](https://secretmag.ru/)  
- [svoedeloplus.ru](https://svoedeloplus.ru/)  

Telegram-каналы:
- [economika](https://t.me/economika)
- [avenuenews](https://t.me/avenuenews)
- [mislinemisli](https://t.me/mislinemisli)

### Бухгалтеры  
Новостные сайты:
- [glavkniga.ru](https://glavkniga.ru/)  
- [buh.ru](https://buh.ru/)  

Telegram-каналы:
- [netipichniy_buh](https://t.me/netipichniy_buh)
- [mytar](https://t.me/mytar_rf)


## Датасеты

Все парсеры источников собраны в этой [директории](https://github.com/PunkButterfly/Hackathon-More.Tech/tree/main/parsers).  

Парсер телеграм-каналов является универсальным для всех каналов, а парсеры новостных сайтов сильно схожи по архитектуре, что **позволяет без особых трудностей увеличить количество источников**.

Ссылки на собранные и обработанные данные:
- [Сырые собранные данные](https://drive.google.com/drive/folders/1V4ZMtgA38QiJx6qQkw4InsIRFFuydazU?usp=sharing)  
- [Предобработанные данные](https://drive.google.com/drive/folders/1fUA08bB6mYo96hwA1fkBMg0AEPfAF3dO?usp=sharing)  

Готовые данные, которые мы использовали в модели:
- [Бухгалтер](https://drive.google.com/file/d/1YCHUjPVQ5mYxyGzbinkVoQBFs5EXDCxC/view?usp=sharing)
- [Генеральный директор](https://drive.google.com/file/d/1-kgHALJgkiQyVZt5j-d8zRwO_G_kmp41/view?usp=sharing)

> Можно скачать всю директорию, например, в colab
```
import gdown

url = 'https://drive.google.com/drive/folders/1PJtRA-iecfLpJqVAiFuzP_KP1anTSuMw?usp=sharing'
folder_name = 'punk_butterfly_datasets'
gdown.download_folder(url, output=folder_name)
```


