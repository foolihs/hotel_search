#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import streamlit as st
import plotly.express as px

# 1. 读取数据
df = pd.read_csv('hotel_cleaned.csv', encoding='utf-8-sig')

# 2. 页面标题
st.title('ホテル検索＆評価分析アプリ')

# 3. 都道府県絞り込み
prefs = df['prefecture'].dropna().unique().tolist()
selected_prefs = st.multiselect(
    '都道府県を選択',
    options=prefs,
    default=prefs
)

# 4. 1名あたり価格の上限スライダー
min_pp = int(df['price_per_person'].min())
max_pp = int(df['price_per_person'].max())
pp_limit = st.slider(
    '1名あたり価格（円）の上限',
    min_value=min_pp,
    max_value=max_pp,
    value=max_pp,
    step=500
)

# 5. 評価下限スライダー
if 'rating' in df.columns:
    min_rating = float(df['rating'].min())
    max_rating = float(df['rating'].max())
    rating_limit = st.slider(
        '評価の下限',
        min_value=min_rating,
        max_value=max_rating,
        value=min_rating,
        step=0.1
    )
else:
    st.warning("データに 'rating' 列がありません。評価フィルタは無効化されます。")
    rating_limit = None

# 6. データフィルタリング
filtered = df[
    (df['prefecture'].isin(selected_prefs)) &
    (df['price_per_person'] <= pp_limit)
]
if rating_limit is not None:
    filtered = filtered[filtered['rating'] >= rating_limit]

st.write(f"✨ 該当ホテル数：{len(filtered)}")

# 7. 价格×评分 散布図
if 'rating' in filtered.columns:
    fig_scatter = px.scatter(
        filtered,
        x='price_per_person',
        y='rating',
        hover_data=['name','city'],
        title='価格 vs. 評価 の散布図'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# 8. 人均価格が安い上位10件
st.subheader('💴 人均価格が安い上位10件')
cheap10 = filtered.sort_values(
    by='price_per_person', ascending=True
).head(10)
st.dataframe(
    cheap10[['name','prefecture','city','price_per_person','rating'] 
            if 'rating' in df.columns else
            ['name','prefecture','city','price_per_person']],
    use_container_width=True
)

# 9. 評価が高い上位10件
if 'rating' in filtered.columns:
    st.subheader('⭐️ 評価が高い上位10件')
    top10 = filtered.sort_values(
        by='rating', ascending=False
    ).head(10)
    st.dataframe(
        top10[['name','prefecture','city','rating','price_per_person']],
        use_container_width=True
    )

# 10. コストパフォーマンス（rating/price）ランキング
if 'rating' in filtered.columns:
    st.subheader('🏆 コスパ指標（評価/価格） 上位10件')
    filtered['value_score'] = filtered['rating'] / filtered['price_per_person']
    best_value = filtered.sort_values(
        by='value_score', ascending=False
    ).head(10)
    st.dataframe(
        best_value[['name','prefecture','city','rating','price_per_person','value_score']],
        use_container_width=True
    )

