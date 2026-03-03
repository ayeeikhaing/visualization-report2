
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import seaborn as sns

st.title("都道府県人口の変化を可視化")
url = "https://en.wikipedia.org/wiki/List_of_Japanese_prefectures_by_population"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
table = pd.read_html(response.text)[0]
df = table.iloc[1:, [1, 4, 5]] 

df.columns = ["Prefecture", "Pop_2022", "Pop_2020"]

for col in ["Pop_2022", "Pop_2020"]:
    df[col] = df[col].astype(str).str.replace(",", "").str.replace(r"\[.*\]", "", regex=True)
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna()

pref = st.selectbox("詳しく見たい都道府県を選んでください", df["Prefecture"])
selected = df[df["Prefecture"] == pref].iloc[0]


diff = selected["Pop_2022"] - selected["Pop_2020"]
diff_label = f"+{int(diff):,}" if diff > 0 else f"{int(diff):,}"

main_color = "#00c0f2" if diff > 0 else "#ff4b4b" 

fig, ax = plt.subplots(figsize=(10, 5))


labels = ["2020年", "2022年"]
values = [selected["Pop_2020"], selected["Pop_2022"]]

ax.bar(labels[0], values[0], color="lightgray")
ax.bar(labels[1], values[1], color=main_color) 

st.pyplot(fig)

col1, col2, col3 = st.columns(3)
col1.metric("2020年 人口", f"{int(selected['Pop_2020']):,}")
col2.metric("2022年 人口", f"{int(selected['Pop_2022']):,}")
col3.metric("増減", diff_label, delta=int(diff))


st.subheader("人口ランキング 上位10（2022年）")
top10 = df.sort_values("Pop_2022", ascending=True).tail(10) 
fig1, ax1 = plt.subplots(figsize=(10, 6))
pop_manin = top10["Pop_2022"] / 10000

bars = ax1.barh(top10["Prefecture"], pop_manin, color="skyblue")

ax1.set_xlabel("人口（万人）")
ax1.set_title("人口が多い都道府県 TOP10")

for bar in bars:
    width = bar.get_width()
    ax1.text(width, bar.get_y() + bar.get_height()/2, 
             f' {int(width):,}万人', 
             va='center', fontsize=10)

ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)

st.pyplot(fig1)
df = table.iloc[1:, [1, 4, 5, 7]].copy() 
df.columns = ["Prefecture", "Pop_2022", "Pop_2020", "Percent_Change"]

st.subheader(" 人口増減率ランキング（2020→2022）")

if "Percent_Change" in df.columns:
    df["Percent_Change"] = df["Percent_Change"].astype(str).str.replace("%", "")
    df["Percent_Change"] = df["Percent_Change"].str.replace("−", "-") # 全角マイナス対策
    df["Percent_Change"] = pd.to_numeric(df["Percent_Change"], errors="coerce")
    change_sorted = df.dropna(subset=["Percent_Change"]).sort_values("Percent_Change", ascending=True)

    fig2, ax2 = plt.subplots(figsize=(10, 12))

    colors = ['#00c0f2' if x >= 0 else '#ff4b4b' for x in change_sorted["Percent_Change"]]
    
    ax2.barh(change_sorted["Prefecture"], change_sorted["Percent_Change"], color=colors)
    ax2.axvline(0, color='black', linewidth=1) # 0の基準線
    
    ax2.set_xlabel("人口増減率（%）")
    ax2.set_title("都道府県別 人口増減率 (2020年-2022年)")
    ax2.grid(axis='x', linestyle='--', alpha=0.5)

    st.pyplot(fig2)
else:
    st.error("列 'Percent_Change' が見つかりませんでした。データ取得部分を確認してください。")



st.subheader("都道府県内の時系列比較")

pref_single = st.selectbox(
    "推移を見たい都道府県を選んでください",
    df["Prefecture"],
    key="pref_select_single"
)

selected_single = df[df["Prefecture"] == pref_single].iloc[0]

fig3, ax3 = plt.subplots(figsize=(6, 4))
pops = [selected_single["Pop_2020"] / 10000, selected_single["Pop_2022"] / 10000]
labels = ["2020年", "2022年"]

ax3.bar(labels, pops, color=["#8D1C1C", "#f2ca00"])
ax3.set_ylabel("人口（万人）")
ax3.set_title(f"{pref_single} の人口推移")

for i, v in enumerate(pops):
    ax3.text(i, v, f"{v:.1f}万", ha='center', va='bottom')

st.pyplot(fig3)


st.subheader("2つの都道府県を直接比較")

col1, col2 = st.columns(2)

with col1:
    comp_a = st.selectbox("比較対象 A", df["Prefecture"], index=12, key="pref_a") # デフォルト東京都(13番目)付近

with col2:
    comp_b = st.selectbox("比較対象 B", df["Prefecture"], index=26, key="pref_b") # デフォルト大阪府付近
data_a = df[df["Prefecture"] == comp_a].iloc[0]
data_b = df[df["Prefecture"] == comp_b].iloc[0]

fig4, ax4 = plt.subplots(figsize=(7, 5))

compare_pops = [data_a["Pop_2022"] / 10000, data_b["Pop_2022"] / 10000]
ax4.bar([comp_a, comp_b], compare_pops, color=["#5865f2", "#eb459e"])

ax4.set_ylabel("人口（万人）")
ax4.set_title(f"{comp_a} vs {comp_b} (2022年)")

for i, v in enumerate(compare_pops):
    ax4.text(i, v, f"{int(v):,}万人", ha='center', va='bottom', fontweight='bold')

st.pyplot(fig4)

st.subheader(" 増減率の分布（日本全体の傾向）")

fig_hist, ax_hist = plt.subplots()
ax_hist.hist(df["Percent_Change"].dropna(), bins=15, color="green", alpha=0.7, edgecolor="white")

ax_hist.axvline(0, color='red', linestyle='dashed', linewidth=2, label="増減なしライン")
ax_hist.set_xlabel("増減率（%）")
ax_hist.set_ylabel("都道府県数")
ax_hist.legend()

st.pyplot(fig_hist)

st.subheader("全国人口におけるシェア")

top_selected = df[df["Prefecture"] == pref_single].iloc[0]
total_pop = df["Pop_2022"].sum()
other_pop = total_pop - top_selected["Pop_2022"]

labels = [pref_single, "その他46都道府県"]
sizes = [top_selected["Pop_2022"], other_pop]
colors = ["#ff9999", "#66b3ff"]

fig_pie, ax_pie = plt.subplots()
ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, explode=[0.1, 0])
ax_pie.axis('equal') 

st.pyplot(fig_pie)

df_plot = df[df["Prefecture"] != "Japan"].copy()

st.subheader("都道府県別の人口推移（詳細表示）")


fig1, ax1 = plt.subplots(figsize=(8, 5))
labels = ["2020年", "2022年"]
values = [selected["Pop_2020"], selected["Pop_2022"]]

ax1.bar(labels, values, color=["#123A91", "#f28900"], width=0.5)

ax1.set_ylim(min(values) * 0.995, max(values) * 1.005) 


for i, v in enumerate(values):
    ax1.text(i, v, f"{int(v):,}人", ha='center', va='bottom', fontsize=12, fontweight='bold')

ax1.set_title(f"{pref} の人口微増減 (ズーム表示)")
st.pyplot(fig1)

st.subheader(" 人口規模 vs 増減率 の傾向")

fig2, ax2 = plt.subplots(figsize=(10, 6))

sns.regplot(data=df_plot, x=df_plot["Pop_2022"]/10000, y="Percent_Change", 
            scatter_kws={'alpha':0.5}, line_kws={'color':'red'}, ax=ax2)


top_cities = df_plot.sort_values("Pop_2022", ascending=False).head(10)
for i, row in top_cities.iterrows():
    ax2.annotate(row["Prefecture"], (row["Pop_2022"]/10000, row["Percent_Change"]), fontsize=9)

ax2.axhline(0, color='black', linestyle='--', linewidth=1)
ax2.set_xlabel("人口（万人）")
ax2.set_ylabel("増減率（%）")
st.pyplot(fig2)

df_pref = df[df["Prefecture"] != "Japan"].copy()

df_pref["Loss_Count"] = df_pref["Pop_2022"] - df_pref["Pop_2020"]
worst_5 = df_pref.sort_values("Loss_Count").head(5)

st.write("###  2年間で最も人が減った県 TOP5")
st.table(worst_5[["Prefecture", "Loss_Count", "Percent_Change"]])


df_clean = df[df["Prefecture"] != "Japan"].copy()
df_clean["Pop_2022_man"] = df_clean["Pop_2022"] / 10000 # 万人単位
df_clean["Pop_2020_man"] = df_clean["Pop_2020"] / 10000


st.header("自分で選ぶデータ分析")

col_settings, col_chart = st.columns([1, 2])

with col_settings:
    st.write("### 設定")
    top_n = st.slider("表示件数を選んでください (Top N)", min_value=2, max_value=20, value=10)

    sort_target = st.radio(
        "並び替えの基準",
        ["人口数 (2022年)", "人口増減率 (%)", "減少数 (実数)"]
    )
    

    if sort_target == "人口数 (2022年)":
        display_df = df_clean.sort_values("Pop_2022", ascending=False).head(top_n)
        y_axis = "Pop_2022_man"
        y_label = "人口（万人）"
    elif sort_target == "人口増減率 (%)":
        display_df = df_clean.sort_values("Percent_Change", ascending=False).head(top_n)
        y_axis = "Percent_Change"
        y_label = "増減率（%）"
    else:
       
        df_clean["Diff"] = df_clean["Pop_2022"] - df_clean["Pop_2020"]
        display_df = df_clean.sort_values("Diff", ascending=True).head(top_n)
        y_axis = "Diff"
        y_label = "減少人数（人）"

with col_chart:
    st.write(f"### {sort_target} Top {top_n}")
    
   
    fig, ax = plt.subplots(figsize=(8, 6))
    
    
    ax.scatter(display_df[y_axis], display_df["Prefecture"], s=100, color="royalblue", edgecolors="black")
    ax.hlines(y=display_df["Prefecture"], xmin=display_df[y_axis].min()*0.9, xmax=display_df[y_axis], color='gray', alpha=0.3)
    
    ax.set_xlabel(y_label)
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    st.pyplot(fig)

st.write(f"#### {sort_target} 上位{top_n}件のデータ詳細")
st.dataframe(display_df[["Prefecture", "Pop_2022", "Pop_2020", "Percent_Change"]])
 
st.subheader(" データ間の相関関係（ヒートマップ）")

df_analysis = df_pref.copy()
df_analysis["減少数"] = df_analysis["Pop_2020"] - df_analysis["Pop_2022"]
corr_df = df_analysis[["Pop_2022", "Percent_Change", "減少数"]].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_df, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
ax.set_title("人口・増減率・減少数の相関")
st.pyplot(fig)


st.subheader("日本全体の増減率の「形」を見る（バイオリン図）")

fig, ax = plt.subplots(figsize=(8, 5))
sns.violinplot(data=df_pref, x="Percent_Change", color="lightseagreen", inner="quartile", ax=ax)

ax.axvline(0, color='red', linestyle='--', label="増減なし")
ax.set_title("都道府県別 増減率の密度分布")
ax.legend()

st.pyplot(fig)

st.subheader(" 2年間で「何人」減ったかランキング")

n_val = st.slider("表示する件数を選んでください", 3, 15, 5)

df_pref["Diff_Count"] = df_pref["Pop_2020"] - df_pref["Pop_2022"]
loss_df = df_pref.sort_values("Diff_Count", ascending=False).head(n_val)

fig, ax = plt.subplots(figsize=(10, 6))
colors = sns.color_palette("Reds_r", n_val)
ax.barh(loss_df["Prefecture"], loss_df["Diff_Count"], color=colors)
ax.invert_yaxis() 

ax.set_xlabel("減少した人口（人）")
ax.set_title(f"人口減少数 ワースト {n_val}")

st.pyplot(fig)

st.header("資料の技術を活用した高度分析")
target_min_pop = st.sidebar.slider("最小人口フィルター (万人)", 0, 1000, 50)

df_filtered = df_pref[df_pref["Pop_2022"] >= target_min_pop * 10000]


st.subheader("人口増減率の密度分布（バイオリン図）")
fig_v, ax_v = plt.subplots(figsize=(8, 4))
sns.violinplot(data=df_filtered, x="Percent_Change", color="skyblue", inner="point", ax=ax_v)
ax_v.axvline(0, color='red', linestyle='--')
st.pyplot(fig_v)

st.subheader("人口規模と減少率の相関（回帰分析）")
fig_s, ax_s = plt.subplots(figsize=(8, 6))
sns.regplot(data=df_filtered, x=df_filtered["Pop_2022"]/10000, y="Percent_Change", 
            scatter_kws={'alpha':0.5}, line_kws={'color':'orange'}, ax=ax_s)
ax_s.set_xlabel("2022年人口（万人）")
ax_s.set_ylabel("増減率（%）")
st.pyplot(fig_s)

df_pref = df[df["Prefecture"] != "Japan"].copy()

st.header(" データ間の相関関係（ヒートマップ）")
st.write("どの要素が人口増減に影響を与えているか、関連性の強さを可視化します。")

corr = df_pref[["Pop_2022", "Pop_2020", "Percent_Change"]].corr()
fig_heat, ax_heat = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='RdYlBu', fmt=".2f", ax=ax_heat)
st.pyplot(fig_heat)

import plotly.express as px
st.header("人口規模・増減率のバブルチャート")
st.write("マウスを乗せると詳細が表示されます。円の大きさは人口規模を表します。")

fig_plotly = px.scatter(
    df_pref, 
    x="Pop_2022", 
    y="Percent_Change",
    size="Pop_2022", 
    color="Percent_Change",
    hover_name="Prefecture",
    labels={"Pop_2022": "2022年人口", "Percent_Change": "増減率(%)"},
    color_continuous_scale="RdBu_r"
)
st.plotly_chart(fig_plotly)

st.header("注目すべき自治体の抽出（行政データ分析）")
top_n = st.number_input("表示する件数を入力してください", min_value=2, max_value=20, value=7)

sort_col = st.selectbox("並び替えの基準を選んでください", ["Pop_2022", "Percent_Change"])
display_df = df_pref.sort_values(sort_col, ascending=False).head(top_n)

fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
ax_bar.barh(display_df["Prefecture"], display_df[sort_col], color="teal")
ax_bar.invert_yaxis()
ax_bar.set_title(f"{sort_col} ランキング Top {top_n}")
st.pyplot(fig_bar)

st.header(" 人口規模の類似性分析（重要地点ラベル）")

fig_cat, ax_cat = plt.subplots(figsize=(10, 6))


sns.scatterplot(data=df_pref, x="Percent_Change", y="Pop_2022", 
                hue="Pop_2022", size="Pop_2022", palette="viridis", ax=ax_cat, legend=False)

targets = pd.concat([
    df_pref.nlargest(5, "Pop_2022"), 
    df_pref.nlargest(3, "Percent_Change"),
    df_pref.nsmallest(3, "Percent_Change")
]).drop_duplicates()

for i, row in targets.iterrows():
    ax_cat.text(row["Percent_Change"], row["Pop_2022"], row["Prefecture"], fontsize=9)

ax_cat.axvline(0, color='red', linestyle='--', alpha=0.5)
ax_cat.set_ylabel("人口規模")
ax_cat.set_xlabel("増減率 (%)")
st.pyplot(fig_cat)


import plotly.express as px

st.header(" Plotlyによるクリーンな分析")

fig_plotly = px.scatter(
    df_pref, x="Percent_Change", y="Pop_2022",
    color="Pop_2022", size="Pop_2022",
    hover_name="Prefecture", 
    log_y=True, 
    title="人口規模と増減率の分布（マウスホバーで県名表示）",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig_plotly)
region_mapping = {
    'Hokkaido': '北海道',
    'Aomori-ken': '東北', 'Iwate-ken': '東北', 'Miyagi-ken': '東北', 'Akita-ken': '東北', 'Yamagata-ken': '東北', 'Fukushima-ken': '東北',
    'Ibaraki-ken': '関東', 'Tochigi-ken': '関東', 'Gunma-ken': '関東', 'Saitama-ken': '関東', 'Chiba-ken': '関東', 'Tokyo-to': '関東', 'Kanagawa-ken': '関東',
    'Niigata-ken': '中部', 'Toyama-ken': '中部', 'Ishikawa-ken': '中部', 'Fukui-ken': '中部', 'Yamanashi-ken': '中部', 'Nagano-ken': '中部', 'Gifu-ken': '中部', 'Shizuoka-ken': '中部', 'Aichi-ken': '中部',
    'Mie-ken': '近畿', 'Shiga-ken': '近畿', 'Kyoto-fu': '近畿', 'Osaka-fu': '近畿', 'Hyogo-ken': '近畿', 'Nara-ken': '近畿', 'Wakayama-ken': '近畿',
    'Tottori-ken': '中国', 'Shimane-ken': '中国', 'Okayama-ken': '中国', 'Hiroshima-ken': '中国', 'Yamaguchi-ken': '中国',
    'Tokushima-ken': '四国', 'Kagawa-ken': '四_国', 'Ehime-ken': '四国', 'Kochi-ken': '四国',
    'Fukuoka-ken': '九州', 'Saga-ken': '九州', 'Nagasaki-ken': '九州', 'Kumamoto-ken': '九州', 'Oita-ken': '九州', 'Miyazaki-ken': '九州', 'Kagoshima-ken': '九州', 'Okinawa-ken': '九州'
}


temp_pref = df_pref["Prefecture"].str.replace(r'[都道府県]$', '', regex=True)

df_pref['Region'] = temp_pref.map(region_mapping)

import unicodedata

def normalize_prefecture_name(name):
    return ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )

df_pref = df[df["Prefecture"] != "Japan"].copy() # 日本全体の行を除外
df_pref['Prefecture_Clean'] = df_pref['Prefecture'].apply(normalize_prefecture_name)

region_mapping = {
    'Hokkaido': '北海道',
    'Aomori-ken': '東北', 'Iwate-ken': '東北', 'Miyagi-ken': '東北', 'Akita-ken': '東北', 'Yamagata-ken': '東北', 'Fukushima-ken': '東北',
    'Ibaraki-ken': '関東', 'Tochigi-ken': '関東', 'Gunma-ken': '関東', 'Saitama-ken': '関東', 'Chiba-ken': '関東', 'Tokyo-to': '関東', 'Kanagawa-ken': '関東',
    'Niigata-ken': '中部', 'Toyama-ken': '中部', 'Ishikawa-ken': '中部', 'Fukui-ken': '中部', 'Yamanashi-ken': '中部', 'Nagano-ken': '中部', 'Gifu-ken': '中部', 'Shizuoka-ken': '中部', 'Aichi-ken': '中部',
    'Mie-ken': '近畿', 'Shiga-ken': '近畿', 'Kyoto-fu': '近畿', 'Osaka-fu': '近畿', 'Hyogo-ken': '近畿', 'Nara-ken': '近畿', 'Wakayama-ken': '近畿',
    'Tottori-ken': '中国', 'Shimane-ken': '中国', 'Okayama-ken': '中国', 'Hiroshima-ken': '中国', 'Yamaguchi-ken': '中国',
    'Tokushima-ken': '四国', 'Kagawa-ken': '四_国', 'Ehime-ken': '四国', 'Kochi-ken': '四国',
    'Fukuoka-ken': '九州', 'Saga-ken': '九州', 'Nagasaki-ken': '九州', 'Kumamoto-ken': '九州', 'Oita-ken': '九州', 'Miyazaki-ken': '九州', 'Kagoshima-ken': '九州', 'Okinawa-ken': '九州'
}

df_pref['Region'] = df_pref['Prefecture_Clean'].map(region_mapping)

df_clean = df_pref.dropna(subset=['Region'])
missing_count = len(df_pref) - len(df_clean)

if missing_count > 0:
    st.warning(f"{missing_count}件の地方区分に失敗しました。名前を確認してください。")
    st.write(df_pref[df_pref['Region'].isnull()]['Prefecture_Clean'].unique())
else:
    st.success("すべての都道府県を地方区分に割り当てました！")

def normalize_name(name):
    return ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )

df_pref = df[df["Prefecture"] != "Japan"].copy()
df_pref['Prefecture_Clean'] = df_pref['Prefecture'].apply(normalize_name)


df_pref['Region'] = df_pref['Prefecture_Clean'].map(region_mapping)
df_clean = df_pref.dropna(subset=['Region'])



def normalize_wikipedia_name(name):
    return ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
df_pref = df[df["Prefecture"] != "Japan"].copy()
df_pref['Prefecture_Clean'] = df_pref['Prefecture'].apply(normalize_wikipedia_name)


df_pref['Region'] = df_pref['Prefecture_Clean'].map(region_mapping)
df_clean = df_pref.dropna(subset=['Region']) # これで Kanagawa-ken も残ります！


st.header("地方別の人口増減トレンド（修正済）")
if not df_clean.empty:
    fig_v, ax_v = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=df_clean, x="Percent_Change", y="Region", 
                   palette="coolwarm", inner="point", ax=ax_v)
    ax_v.axvline(0, color='red', linestyle='--', alpha=0.5)
    st.pyplot(fig_v)
    st.write("図：地方別の人口増減率分布。バイオリンの膨らみはデータの密度を表す。")
 
    st.header(" 地方別の平均増減率（ヒートマップ）")
    region_stats = df_clean.groupby("Region")[["Percent_Change"]].mean(numeric_only=True)
    
    fig_h, ax_h = plt.subplots(figsize=(10, 4))
    sns.heatmap(region_stats.T, annot=True, cmap="RdYlBu", center=0, fmt=".2f", ax=ax_h)
    ax_h.set_title("地方別の平均人口増減率 (%)")
    st.pyplot(fig_h)
    st.write("図：地方ごとの人口増減率の平均。青が増加、赤が減少を示す（資料第5回流の配色）。")
    

else:
    st.error("地方区分に失敗しました。以下の県名を確認してください。")
    st.write(df_pref['Prefecture_Clean'].unique())

    st.header("指標間の相関分析")
corr = df_filtered[["Pop_2022", "Pop_2020", "Percent_Change"]].corr()
fig_h, ax_h = plt.subplots(figsize=(6, 4))
sns.heatmap(corr, annot=True, cmap='RdYlBu', center=0, ax=ax_h)
st.pyplot(fig_h)

st.header("インタラクティブ・バブルチャート")


if "Region" not in df_filtered.columns:

    df_filtered['Prefecture_Clean'] = df_filtered['Prefecture'].apply(normalize_name)
    df_filtered['Region'] = df_filtered['Prefecture_Clean'].map(region_mapping)

if not df_filtered.empty and "Region" in df_filtered.columns:
    import plotly.express as px
    
    fig_px = px.scatter(
        df_filtered, 
        x="Pop_2022", 
        y="Percent_Change",
        color="Region",  
        size="Pop_2022",
        hover_name="Prefecture",
        labels={"Pop_2022": "2022年人口", "Percent_Change": "増減率(%)", "Region": "地方"},
        title="人口規模 vs 増減率（地方別色分け）",
        template="plotly_white"
    )
    
    st.plotly_chart(fig_px)
    
    st.write("図：人口規模（円の大きさ）と増減率の相関。地方ごとに色分けされている（資料第6回参照）。")
    

else:
    st.warning("Region列の作成に失敗したか、データが空です。地方区分の設定を確認してください。")
st.header(" 散布図行列による多角的な相関確認")


fig_pair = sns.pairplot(df_clean[["Pop_2022", "Percent_Change", "Region"]], 
                        hue="Region", corner=True, palette="viridis")
st.pyplot(fig_pair)


import networkx as nx 

st.header(" 県同士の「類似性」ネットワーク分析")
st.write("図：人口増減率が近い（差が0.1%以内）県同士を線で結んだ図。中心にあるほど、平均的な動きをしている県です。")

G = nx.Graph()

for i, row in df_clean.iterrows():
    G.add_node(row['Prefecture'], region=row['Region'], change=row['Percent_Change'])

prefs = df_clean['Prefecture'].tolist()
changes = df_clean['Percent_Change'].tolist()

for i in range(len(prefs)):
    for j in range(i + 1, len(prefs)):
        if abs(changes[i] - changes[j]) < 0.1: 
            G.add_edge(prefs[i], prefs[j])

fig_nx, ax_nx = plt.subplots(figsize=(12, 10))
pos = nx.spring_layout(G, k=0.3, seed=42) 

centrality = nx.betweenness_centrality(G)
node_size = [v * 5000 + 100 for v in centrality.values()]


nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color=list(centrality.values()), 
                       cmap=plt.cm.plasma, alpha=0.8, ax=ax_nx)
nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color='gray', ax=ax_nx)
nx.draw_networkx_labels(G, pos, font_family='IPAexGothic', font_size=9, ax=ax_nx)

ax_nx.set_title("人口増減率の類似性ネットワーク")
plt.axis('off')
st.pyplot(fig_nx)
st.write("図：ネットワーク図。ノードの大きさは「橋渡し」の重要度（中心性）を示します。")



st.header(" 地方別の減少フェーズ比較（リッジライン）")


plt.figure(figsize=(10, 6))
sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})


g = sns.FacetGrid(df_clean, row="Region", hue="Region", aspect=9, height=1.2, palette="coolwarm")
g.map(sns.kdeplot, "Percent_Change", bw_adjust=.5, clip_on=False, fill=True, alpha=1, linewidth=1.5)
g.map(plt.axhline, y=0, lw=2, clip_on=False)


def label(x, color, label):
    ax = plt.gca()
    ax.text(0, .2, label, fontweight="bold", color=color, ha="left", va="center", transform=ax.transAxes)

g.map(label, "Percent_Change")
g.figure.subplots_adjust(hspace=-.25)
g.set_titles("")
g.set(yticks=[], ylabel="")
g.despine(bottom=True, left=True)

st.pyplot(plt.gcf())
st.write("図：地方別の人口増減率の密度。山の位置が左にあるほど、その地方全体で減少が進行しています。")


import networkx as nx

st.header("人口動態の「似たもの同士」ネットワーク")

G = nx.Graph()

thresh = 0.05
for i, row_i in df_clean.iterrows():
    for j, row_j in df_clean.iterrows():
        if i < j:
            diff = abs(row_i['Percent_Change'] - row_j['Percent_Change'])
            if diff < thresh:
                G.add_edge(row_i['Prefecture'], row_j['Prefecture'], weight=1-diff)

pos = nx.spring_layout(G, k=0.5, seed=42)
fig_net, ax_net = plt.subplots(figsize=(10, 10))



d = dict(G.degree)
nx.draw(G, pos, with_labels=True, 
        node_size=[v * 100 for v in d.values()], 
        node_color=list(d.values()), 
        cmap=plt.cm.Blues, 
        font_family='Japanize-matplotlib', 
        font_size=8, ax=ax_net, edge_color="gray", alpha=0.6)

st.pyplot(fig_net)
st.write("図：増減率が近い県同士のネットワーク。大きな円は『日本の平均的な増減傾向』を持つ県です。")



st.divider() 
st.header("地方別ディープ・ダイブ分析")
st.write("特定の地方に絞って、県ごとの増減率の違いを精密に比較します（資料第10回：属性の階層化）")


target_region = st.selectbox("分析したい地方を選択してください", df_clean["Region"].unique())


df_region = df_clean[df_clean["Region"] == target_region].sort_values("Percent_Change", ascending=False)

fig_reg, ax_reg = plt.subplots(figsize=(10, len(df_region) * 0.6))


colors = ["#00c0f2" if x > 0 else "#ff4b4b" for x in df_region["Percent_Change"]]

bars = ax_reg.barh(df_region["Prefecture"], df_region["Percent_Change"], color=colors)
ax_reg.axvline(0, color='black', linewidth=1) 

for bar in bars:
    width = bar.get_width()
    ax_reg.text(width, bar.get_y() + bar.get_height()/2, 
                f' {width:.2f}%', va='center', 
                ha='left' if width > 0 else 'right',
                fontweight='bold', color='black')

ax_reg.set_title(f"【{target_region}地方】県別 人口増減率の詳細比較", fontsize=14)
ax_reg.set_xlabel("増減率 (%)")
ax_reg.grid(axis='x', linestyle='--', alpha=0.5)

st.pyplot(fig_reg)
st.write(f"図：{target_region}地方における各県の増減率。同じ地方内でも、中心県と周辺県で差があるかを確認できます。")

st.subheader(" 全地方の減少フェーズ分布（比較図）")

fig_ridge, ax_ridge = plt.subplots(figsize=(10, 6))


for i, region in enumerate(df_clean["Region"].unique()):
    subset = df_clean[df_clean["Region"] == region]
    sns.kdeplot(subset["Percent_Change"], label=region, fill=True, alpha=0.5, ax=ax_ridge)

ax_ridge.axvline(0, color='red', linestyle='--', alpha=0.6, label="増減なし")
ax_ridge.set_title("地方別：増減率の『山の位置』比較", fontsize=14)
ax_ridge.set_xlabel("人口増減率 (%)")
ax_ridge.set_ylabel("分布密度")
ax_ridge.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

st.pyplot(fig_ridge)
st.write("図：各地方の増減率分布。山のピークが左（マイナス側）にあるほど、その地方全体で減少傾向が強いことを示します。")


st.header("全国平均からの乖離（偏差分析）")
st.write("全国平均を0としたとき、各県がどれだけ「特殊な動き」をしているかを可視化します。")


mean_val = df_clean["Percent_Change"].mean()
std_val = df_clean["Percent_Change"].std()
df_clean["Z_Score"] = (df_clean["Percent_Change"] - mean_val) / std_val


df_extreme = pd.concat([
    df_clean.sort_values("Z_Score").head(5),
    df_clean.sort_values("Z_Score").tail(5)
])

fig_z, ax_z = plt.subplots(figsize=(10, 6))
colors = ["#ff4b4b" if x < 0 else "#00c0f2" for x in df_extreme["Z_Score"]]
ax_z.barh(df_extreme["Prefecture"], df_extreme["Z_Score"], color=colors)
ax_z.axvline(0, color='black', linewidth=1)
ax_z.set_title("人口増減率の偏差（全国平均からの離れ具合）", fontsize=14)
ax_z.set_xlabel("標準偏差 (σ)")

st.pyplot(fig_z)
st.write("図：偏差グラフ。±2σ（標準偏差）を超える県は、日本全体の中でも極めて特殊な人口動態を持っていることを示唆します。")


st.header("都道府県の「立ち位置」分類（4象限分析）")

fig_quad, ax_quad = plt.subplots(figsize=(10, 8))
sns.scatterplot(data=df_clean, x="Pop_2022", y="Percent_Change", 
                hue="Region", size="Pop_2022", sizes=(50, 500), alpha=0.6, ax=ax_quad)


med_pop = df_clean["Pop_2022"].median()
med_change = df_clean["Percent_Change"].median()
ax_quad.axvline(med_pop, color='gray', linestyle='--', alpha=0.5)
ax_quad.axhline(med_change, color='gray', linestyle='--', alpha=0.5)

ax_quad.text(df_clean["Pop_2022"].max(), df_clean["Percent_Change"].max(), "成長・大規模", fontsize=10, alpha=0.7, ha='right')
ax_quad.text(df_clean["Pop_2022"].min(), df_clean["Percent_Change"].min(), "衰退・小規模", fontsize=10, alpha=0.7)

ax_quad.set_title("人口規模 × 増減率の4象限マトリックス", fontsize=14)
ax_quad.set_xscale('log') 
st.pyplot(fig_quad)
st.write("図：4象限プロット。右上のエリアに近いほど人口基盤が強く成長しており、左下に近いほど対策が急務な地域と言えます。")



sns.set_context("talk") 
plt.rcParams['font.family'] = 'Japanize-matplotlib' 

plt.rcParams['axes.spines.top'] = False 

plt.rcParams['axes.spines.right'] = False 


