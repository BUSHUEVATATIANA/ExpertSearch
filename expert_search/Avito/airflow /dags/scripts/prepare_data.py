import pandas as pd
import json
def prepare_data(data):
  df = pd.DataFrame(data)
  df = df.T
  df = d.drop_duplicates(subset=['num','description','rate', 'sum_review'])
  df = df.drop(columns=['education'])
  values = {'rate': 0, 'sum_review': 0}
  df=df.fillna(value = values)
  df = df.reset_index()

  keywords = ['ресниц', 'мастер', 'бровей','бровист', 'бровиста', 'макияж', 'кератин', 'брови', 'массаж', 'маникюр','педикюр','подолог' 'татуаж', 'шугаринг','депиляция' 'наращивание', 'ламинирование']

  filtered = {}
  for i,row in enumerate(df['review']):
    l_f = []
      #reviews = row.get('review', [])

      # 2) Если review — список списков, пробегаем по каждому подсписку,
      #    иначе — обрабатываем сам список как единый блок
    blocks = row if isinstance(row[0], list) else [row]

    for rev in blocks:
        # rev — список строк: дата, сделка, текст, дата, сделка, текст...
        for date, deal, text in zip(rev[::3], rev[1::3], rev[2::3]):
            if deal.startswith('Сделка состоялась') and any(kw in deal.lower() for kw in keywords):
              l_f.append([date, deal, text])



    # 3) Запишем обратно — получили одну «плоскую» выверенную группу строк
    df['review'].iloc[i] = l_f

  df['review'] = df['review'].apply(
      lambda x: ['нет отзывов'] if isinstance(x, list) and len(x) == 0 else x
  )

  df = df.reset_index(drop=True)
  return df

  