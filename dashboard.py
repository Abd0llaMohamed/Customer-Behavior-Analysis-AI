import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import joblib

# تحميل البيانات والنموذج
df = pd.read_excel('customers_churn.xlsx')
model = joblib.load('best_churn_model.pkl')

# إنشاء التطبيق
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("📊 نظام تحليل سلوك العملاء - لوحة تحكم متقدمة", 
                style={'textAlign': 'center', 'color': '#1f77b4', 'marginBottom': 30}),
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'marginBottom': '20px'}),
    
    html.Div([
        # الإحصائيات العامة
        html.Div([
            html.Div([
                html.H3(f"👥 {len(df)}", style={'color': '#1f77b4'}),
                html.P("إجمالي العملاء")
            ], className='stat-box'),
            
            html.Div([
                html.H3(f"⚠️ {len(df[df['Churn_Probability'] > 70])}", style={'color': '#ff7f0e'}),
                html.P("معرضون للرحيل")
            ], className='stat-box'),
            
            html.Div([
                html.H3(f"✅ {len(df[df['Churn_Probability'] <= 30])}", style={'color': '#2ca02c'}),
                html.P("عملاء مخلصون")
            ], className='stat-box'),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '30px'}),
        
        # الرسوم البيانية
        html.Div([
            html.Div([
                dcc.Graph(id='churn-distribution')
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
            
            html.Div([
                dcc.Graph(id='features-correlation')
            ], style={'width': '48%', 'display': 'inline-block'}),
        ]),
        
        # جدول البيانات
        html.Div([
            html.H3("📋 البيانات التفصيلية"),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th('الاسم'),
                        html.Th('المشتريات'),
                        html.Th('القيمة'),
                        html.Th('الزيارات'),
                        html.Th('احتمال الرحيل %'),
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(row['Name']),
                        html.Td(f"{row['Purchases']}"),
                        html.Td(f"{row['Total_Value']:.0f}"),
                        html.Td(f"{row['Visits']}"),
                        html.Td(f"{row['Churn_Probability']:.1f}%", 
                               style={'color': 'red' if row['Churn_Probability'] > 70 else 'green'}),
                    ]) for _, row in df.head(20).iterrows()
                ])
            ], style={'width': '100%', 'border': '1px solid #ddd'})
        ], style={'marginTop': '20px'}),
        
    ], style={'padding': '20px'}),
], style={'fontFamily': 'Arial', 'maxWidth': '1400px', 'margin': '0 auto'})

@app.callback(
    Output('churn-distribution', 'figure'),
    Input('churn-distribution', 'id')
)
def update_churn_distribution(_):
    fig = px.histogram(df, x='Churn_Probability', nbins=20, 
                       title='توزيع احتمالية الرحيل',
                       color_discrete_sequence=['#1f77b4'])
    return fig

@app.callback(
    Output('features-correlation', 'figure'),
    Input('features-correlation', 'id')
)
def update_correlation(_):
    corr = df[['Purchases', 'Total_Value', 'Visits', 'Churn_Probability']].corr()
    fig = go.Figure(data=go.Heatmap(z=corr.values, 
                                     x=corr.columns, 
                                     y=corr.columns,
                                     colorscale='RdBu'))
    fig.update_layout(title='مصفوفة الارتباط')
    return fig

if __name__ == '__main__':
    print("🚀 Dash App running on http://localhost:8050")
    app.run_server(debug=True, port=8050)
