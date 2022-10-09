# Решение задачи трэка DATA от команды **Punk Butterfly**  


## Источники

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


