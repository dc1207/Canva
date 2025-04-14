"""
日幣匯率boken互動統計圖
"""
#ie11andabove > div > table
import pandas as pd

url="https://rate.bot.com.tw/xrt/quote/ltm/JPY/cash"
df=pd.read_html(url)
print(df)
len(df) #表格個數
df1=df[0] #使用 df1 = df[0] 確保df1是從df中提取的第一個 DataFrame。這樣就可以使用 iloc 方法來選擇行和列。

df2=df1.iloc[0:30,[0,1,2,3,4,5]]  #多選需兩個[[]]，分別(欄,列)，全選 : 即可
df2.columns=["日期","幣別","現金匯率_本行買入","現金匯率_本行賣出","即期買入","即期賣出"]
df2['日期'] = pd.to_datetime(df2['日期'])
# 只保留月份和日期
df2['日期'] = df2['日期'].dt.strftime('%m/%d')
#df2.to_csv("travelrate.csv",encoding="utf-8-sig",index=False) #匯出csv可修改內容
# 反轉日期順序，重置索引，確保新的順序有正確的索引號
df2 = df2.iloc[::-1].reset_index(drop=True)


from bokeh.plotting import figure,output_file,show
from bokeh.layouts import row,column
from bokeh.models.widgets import Panel,Tabs
from bokeh.palettes import Spectral4

output_file("row-JPrate.html")

#建立圖形物件
bH1=figure(width=1200, height=600,title="日幣現金匯率",x_axis_label="日期",y_axis_label="匯率",x_range=df2["日期"],y_range=(0.2,0.25))
bH2=figure(width=1200, height=600,title="日幣即期匯率",x_axis_label="日期",y_axis_label="匯率",x_range=df2["日期"],y_range=(0.2,0.25))
#在圖形物件加入繪圖指示
bH1.line(df2["日期"],df2["現金匯率_本行賣出"],line_width=5,color="orange",muted_color="green",muted_alpha=0.2,legend="現金賣出")
bH1.diamond(df2["日期"],df2["現金匯率_本行賣出"],size=10,color="green")
bH1.line(df2["日期"],df2["現金匯率_本行買入"],line_width=5,color="blue",muted_color="blue",muted_alpha=0.2,legend="現金買入")
bH1.triangle(df2["日期"],df2["現金匯率_本行買入"],size=10,color="red")

bH2.line(df2["日期"],df2["即期賣出"],line_width=5,color="orange",legend="即期賣出")
bH2.diamond(df2["日期"],df2["即期賣出"],size=10,color="green",legend="即期賣出")
bH2.line(df2["日期"],df2["即期買入"],line_width=5,color="blue",legend="即期買入")
bH2.triangle(df2["日期"],df2["即期買入"],size=10,color="red",legend="即期買入")
#隱藏圖例
bH1.legend.location = "top_left"
bH1.legend.click_policy="mute" #淡化
bH2.legend.click_policy="hide"
#分頁模式
taB1 = Panel(child=bH1, title="現金")
taB2 = Panel(child=bH2, title="即期")
bH = Tabs(tabs=[taB1,taB2])

show(bH)