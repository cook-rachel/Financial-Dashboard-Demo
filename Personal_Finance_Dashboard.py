import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, ctx
from datetime import datetime

pio.renderers.default='notebook_connected'
pio.templates.default = 'simple_white' 

## set defaults for outputs
pd.set_option('display.max_columns', None)				# Shows all columns
pd.set_option('display.max_colwidth', None)				# Show full column width
pd.set_option('display.width', 1000)        			# Keeps columns on a single line
pd.set_option('display.expand_frame_repr', False) 		# Prevents wrapping

pio.renderers.default='notebook'

#########################
#		Data Prep		#
#########################
## read data
account_data = pd.read_excel('ynab_dashboard_data.xlsx', sheet_name= 'Accounts')
monthly_summaries_data = pd.read_excel('ynab_dashboard_data.xlsx', sheet_name= 'Monthly_Summaries')
transactions_data = pd.read_excel('ynab_dashboard_data.xlsx', sheet_name= 'Transactions')
category_goals_data = pd.read_excel('ynab_dashboard_data.xlsx', sheet_name= 'Category_Goals')

# dashboard title
title_text = '## Personal Finance Dashboard'

# rename columns
monthly_summaries_data = monthly_summaries_data.rename(
	columns={
		'income_amount': 'Net Income',
		'activity_amount': 'Expenses'}
	)

# convert date column to datetime object
monthly_summaries_data['month'] = pd.to_datetime(monthly_summaries_data['month'], format="%Y-%m-%d")
transactions_data['date'] = pd.to_datetime(transactions_data['date'], format="%Y-%m-%d")

transactions_data['month'] = transactions_data['date'].dt.to_period('M').dt.to_timestamp()

# create savings column
monthly_summaries_data['savings_amount'] = (monthly_summaries_data['Net Income'] - monthly_summaries_data['Expenses'])	

# calculate time frames 
today = datetime.now()

min_date = transactions_data['date'].min()
max_date = today
last_12_months = today - pd.DateOffset(months=12)


# --------------------------------- #
# 		calculate dti ratio			#
# --------------------------------- #
debt_types = ['creditCard', 'mortgage', 'autoLoan', 'medicalDebt', 'personalLoan', 'lineOfCredit', 'otherDebt']
debt_account_ids = account_data[account_data['type'].isin(debt_types)]['id'].tolist()

monthly_debt = (
	transactions_data[
		transactions_data['account_id'].isin(debt_account_ids) &
		(
			(transactions_data['transaction_amount'] < 0) & (~transactions_data['account_name'].str.contains('Visa|Card', case=False, na=False)) |	# loan payments
			(transactions_data['transaction_amount'] > 0) & (transactions_data['account_name'].str.contains('Visa|Card', case=False, na=False))	# credit card payments
		)
	]
	.assign(transaction_amount=lambda df: df['transaction_amount'].abs())
	.groupby('month')['transaction_amount']
	.sum()
	.reset_index(name='debt_payments')
)

# merge debt transactions with income from monthly_summaries_data
dti_df = pd.merge(
	monthly_summaries_data[['month', 'Net Income']],
	monthly_debt,
	on='month',
	how='left'
).fillna(0)


date_button_style = {
	'padding': '3px 8px',
	'backgroundColor': '#f8f9fa',
	'border': '1px solid #ccc',
	'borderRadius': '4px',
	'cursor': 'pointer',
	'whiteSpace': 'nowrap',
	'fontSize': '12px',
	'marginBottom': '4px',
	'width': '100%'
	}


banner_style={
	'backgroundColor': '#F9FAF8',
	'border': '1px solid #E5E7EB',
	'borderRadius': '8px',
	'padding': '16px 24px',
	'marginBottom': '20px',
	'width': '220px',
	'boxShadow': '0 1px 3px rgba(0,0,0,0.05)',
	'textAlign': 'center'
	}




#########################
#		UI Layout		#
#########################
app = Dash(__name__)

app.layout = html.Div([ 
	# ------------------------------------- # 
	# 			 HEADER ROW BLOCK 			#
	# ------------------------------------- # 
	html.Div([
		# TITLE BLOCK                                                                                       
		html.Div(
			[dcc.Markdown(children=title_text)],
			style={
				'display': 'inline-block',
				'backgroundColor': 'white', 
				'font': '15px Arial, sans-serif', 
				'color': 'black', 
				'font-weight': '400'
			}
		),

			# ------------------------------------- # 
			#			 DATE RANGE BLOCK			#
			# ------------------------------------- # 
		html.Div([
			html.Label(
				"Select Date Range: ", 
				style={
					'marginRight': '12px',
					'whiteSpace': 'nowrap'
				}
			),
			dcc.DatePickerRange(
				id='date-picker-range',
				min_date_allowed=min_date,
				max_date_allowed=max_date,
				initial_visible_month=max_date,
				start_date = (last_12_months).strftime('%Y-%m-%d'),
				end_date = max_date.strftime("%Y-%m-%d")
			),

			# ------------------------------------- # 
			#			DATE BUTTONS COLUMN			#
			# ------------------------------------- # 
			html.Div([
				html.Div([
					html.Button(
						'6 Months',
						id='six-months-button',
						n_clicks=0,
						style = date_button_style
					),

					html.Button(
						'12 Months',
						id='twelve-months-button',
						n_clicks=0,
						style = date_button_style
					)
				], style={
					'display': 'flex',
					'flexDirection': 'column',
					'marginLeft': '12px'
				}),

				html.Div([
					html.Button(
						'Current Year',
						id='current-year-button',
						n_clicks=0,
						style = date_button_style
					),
					html.Button(
						'All Dates',
						id='reset-date-button',
						n_clicks=0,
						style = date_button_style
					)
				], style={
					'display': 'flex',
					'flexDirection': 'column',
					'marginLeft': '12px'
				})

			# date buttons style
			], style={
				'display': 'flex',
				'flexDirection': 'row',
				'marginLeft': '12px'})
		# ------------------------------------- # 
		#			Date Block Style			#
		# ------------------------------------- # 
		], style={
			'display': 'flex',
			'alignItems': 'center',
			'backgroundColor': 'white',
			'font': '15px Arial, sans-serif',
			'color': 'black',
			'marginLeft': 'auto'
		})
	], 

	# ------------------------------------- # 
	# 			Header row style			#
	# ------------------------------------- # 
	style={                     
		'display': 'flex',
		'justifyContent': 'space-between',
		'alignItems': 'center',
		'padding': '15px 25px',
		'backgroundColor': 'white',
		'borderBottom': '1px solid #E5E7EB'
	}),

	# ------------------------------------- # 
	# 			 MAIN CONTAINER 			#
	# ------------------------------------- # 
	html.Div([

		# ------------------------------------- # 
		# 				Banner Summary			#
		# ------------------------------------- # 
		html.Div([

			# total income
            html.Div([
                html.Div([
                    html.Span("Total Income", style={'marginRight': '4px'}),
                    html.Details([
                        html.Summary(
                            "ⓘ", 
                            style={
                                'cursor': 'pointer',
                                'fontSize': '12px',
                                'color': '#9CA3AF',
                                'listStyle': 'none',
                                'outline': 'none',
                                'userSelect': 'none'
                            }
                        ),
                        html.Div(
                            "Total Net Income received across all accounts during the selected date range.",
                            style={
                                'position': 'absolute',
                                'zIndex': 1000,
                                'width': '190px',
                                'padding': '8px 10px',
                                'backgroundColor': '#1F2937',
                                'color': '#FFFFFF',
                                'fontSize': '11px',
                                'borderRadius': '6px',
                                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.15)',
                                'left': '50%',
                                'transform': 'translateX(-50%)',
                                'marginTop': '6px',
                                'lineHeight': '1.4',
                                'textAlign': 'left'
                            }
                        )
                    ], style={'display': 'inline-block', 'position': 'relative'})
                ], style={'fontSize': '14px', 'color': '#6B7280', 'fontWeight': '500', 'marginBottom': '4px', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
                html.Div(id='total-income-banner', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#11CACA'}),
            ], style=banner_style),

            # total expenses
            html.Div([
                html.Div([
                    html.Span("Total Expenses", style={'marginRight': '4px'}),
                    html.Details([
                        html.Summary(
                            "ⓘ", 
                            style={
                                'cursor': 'pointer',
                                'fontSize': '12px',
                                'color': '#9CA3AF',
                                'listStyle': 'none',
                                'outline': 'none',
                                'userSelect': 'none'
                            }
                        ),
                        html.Div(
                            "Total spending and outflows across all budget categories during the selected period.",
                            style={
                                'position': 'absolute',
                                'zIndex': 1000,
                                'width': '190px',
                                'padding': '8px 10px',
                                'backgroundColor': '#1F2937',
                                'color': '#FFFFFF',
                                'fontSize': '11px',
                                'borderRadius': '6px',
                                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.15)',
                                'left': '50%',
                                'transform': 'translateX(-50%)',
                                'marginTop': '6px',
                                'lineHeight': '1.4',
                                'textAlign': 'left'
                            }
                        )
                    ], style={'display': 'inline-block', 'position': 'relative'})
                ], style={'fontSize': '14px', 'color': '#6B7280', 'fontWeight': '500', 'marginBottom': '4px', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
                html.Div(id='total-expenses-banner', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#CA2D3A'}),
            ], style=banner_style),

            # net savings rate
            html.Div([
                html.Div([
                    html.Span("Net Savings Rate", style={'marginRight': '4px'}),
                    html.Details([
                        html.Summary(
                            "ⓘ", 
                            style={
                                'cursor': 'pointer',
                                'fontSize': '12px',
                                'color': '#9CA3AF',
                                'listStyle': 'none',
                                'outline': 'none',
                                'userSelect': 'none'
                            }
                        ),
                        html.Div(
                            "Percentage of income saved: ((Total Income - Total Expenses) / Total Income) × 100.",
                            style={
                                'position': 'absolute',
                                'zIndex': 1000,
                                'width': '190px',
                                'padding': '8px 10px',
                                'backgroundColor': '#1F2937',
                                'color': '#FFFFFF',
                                'fontSize': '11px',
                                'borderRadius': '6px',
                                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.15)',
                                'left': '50%',
                                'transform': 'translateX(-50%)',
                                'marginTop': '6px',
                                'lineHeight': '1.4',
                                'textAlign': 'left'
                            }
                        )
                    ], style={'display': 'inline-block', 'position': 'relative'})
                ], style={'fontSize': '14px', 'color': '#6B7280', 'fontWeight': '500', 'marginBottom': '4px', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
                html.Div(id='net-savings-rate-banner', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': "#2DCA79"}),
            ], style=banner_style),

            # debt to income ratio
            html.Div([
                html.Div([
                    html.Span("Debt-to-Income (DTI)", style={'marginRight': '4px'}),
                    html.Details([
                        html.Summary(
                            "ⓘ", 
                            style={
                                'cursor': 'pointer',
                                'fontSize': '12px',
                                'color': '#9CA3AF',
                                'listStyle': 'none',
                                'outline': 'none',
                                'userSelect': 'none'
                            }
                        ),
                        html.Div(
                            "Debt-to-Income Ratio: (Total Debt Payments / Total Net Income) × 100.",
                            style={
                                'position': 'absolute',
                                'zIndex': 1000,
                                'width': '190px',
                                'padding': '8px 10px',
                                'backgroundColor': '#1F2937',
                                'color': '#FFFFFF',
                                'fontSize': '11px',
                                'borderRadius': '6px',
                                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.15)',
                                'left': '50%',
                                'transform': 'translateX(-50%)',
                                'marginTop': '6px',
                                'lineHeight': '1.4',
                                'textAlign': 'left'
                            }
                        )
                    ], style={'display': 'inline-block', 'position': 'relative'})
                ], style={'fontSize': '14px', 'color': '#6B7280', 'fontWeight': '500', 'marginBottom': '4px', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
                html.Div(id='dti-banner', style={'fontSize': '28px', 'fontWeight': 'bold', 'color': "#932DCA"}),
            ], style=banner_style),

        # style for banner
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'justifyContent': 'center',
            'gap': '16px',
            'marginBottom': '20px'
        }),

		# --------------------------------------------- # 
		# 					PLOTS: Row 1				#
		# --------------------------------------------- # 
		html.Div([
			dcc.Graph(
				id='income_v_expense_bar',
				style={
					'flex': '5.5',
		   			# 'border': '1px solid #E5E7EB'
				}
			),

			dcc.Graph(
				id='net_savings_bar',
				style={
					'flex': '4.5',
					# 'border': '1px solid #E5E7EB'
				}
			)

		# style for Plots: Row 1
		], style = {
		'display': 'flex',
		'flexDirection': 'row',
		'width': '100%',
		'gap': '20px',
		'marginBottom': '10px'
		}),

		# --------------------------------------------- # 
		# 				Current Status: Row 2			#
		# --------------------------------------------- # 

		# Current financial status banner
		html.Div([
            html.Div([
                html.Span(
                    "Current Financial Progress", 
                    style={'marginRight': '8px'}
                ),
                html.Details([
                    html.Summary(
                        "ⓘ", 
                        style={
                            'cursor': 'pointer',
                            'fontSize': '16px',
                            'color': '#9CA3AF',
                            'listStyle': 'none',
                            'outline': 'none',
                            'userSelect': 'none'
                        }
                    ),
                    html.Div(
                        "Cumulative progress toward goal targets to date. Shaded gauge segments represent 25%, 50%, and 75% benchmarks toward each goal.",
                        style={
                            'position': 'absolute',
                            'zIndex': 1000,
                            'width': '260px',
                            'padding': '8px 12px',
                            'backgroundColor': '#1F2937',
                            'color': '#FFFFFF',
                            'fontSize': '12px',
                            'fontWeight': 'normal',
                            'borderRadius': '6px',
                            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.15)',
                            'left': '50%',
                            'transform': 'translateX(-50%)',
                            'marginTop': '6px',
                            'lineHeight': '1.4',
                            'textAlign': 'left'
                        }
                    )
                ], style={'display': 'inline-block', 'position': 'relative'})
            ], style={
                'fontSize': '26px', 
                'color': '#6B7280', 
                'fontWeight': '500', 
                'marginTop': '4px', 
                'marginBottom': '4px',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center'
            }),
        ], style={
            'backgroundColor': '#F9FAF8',
            'border': '1px solid #E5E7EB',
            'borderRadius': '15px',
            'padding': '8px 0',
            'marginTop': '60px',
            'width': '100%',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.05)',
            'textAlign': 'center'
        }),



		# --------------------------------------------- # 
		# 					PLOTS: Row 3				#
		# --------------------------------------------- # 
		html.Div([
			# --------------------------------------------- # 
			# 				Savings Progress				#
			# --------------------------------------------- # 
			html.Div([
				dcc.Graph(
					id="savings-goal-gauge",
					style={
						# 'padding': '10px 40px'
						}
				)

			# style for savings container
			], style={
			'display': 'flex',
			'flexDirection': 'column',
			'width': '33%',
			'marginBottom': '10px'
			}),
			

			# --------------------------------------------- # 
			# 					Investments					#
			# --------------------------------------------- # 
			html.Div([
				dcc.Graph(
					id="investments-gauge",
					style={
						# 'padding': '40px 40px'
						}
				)

			# style for investments container
			], style={
			'display': 'flex',
			'flexDirection': 'column',
			'width': '33%',
			'marginBottom': '10px'
		}),

			# --------------------------------------------- # 
			# 						Debt					#
			# --------------------------------------------- # 
			html.Div([
				dcc.Graph(
					id="debt-gauge",
					style={
						# 'padding': '40px 40px'
						}
				)

			# style for debt container
			], style={
			'display': 'flex',
			'flexDirection': 'column',
			'width': '33%',
			'marginBottom': '10px'
		})


		# style for Plot: Row 3
		], style={
			'display': 'flex',
			'flexDirection': 'row',
			'width': '100%',
			'marginBottom': '10px'
		})

	

	# style for main container
	], style={
		'display': 'flex',
		'flexDirection': 'column',
		'padding': '10px'
		})





]) # end of container



# #################################
# #	      Server Callbacks		#
# #################################

@app.callback(		
	Output('date-picker-range', 'start_date'),
	Output('date-picker-range', 'end_date'),

	Output('total-income-banner', 'children'),			
	Output('total-expenses-banner', 'children'),		
	Output('net-savings-rate-banner', 'children'),	
	Output('dti-banner', 'children'),	

	Output('income_v_expense_bar', 'figure'),	
	Output('net_savings_bar', 'figure'),

	Output('savings-goal-gauge', 'figure'),
	Output('investments-gauge', 'figure'),
	Output('debt-gauge', 'figure'),

	Input('date-picker-range', 'start_date'),
	Input('date-picker-range', 'end_date'),
	Input('six-months-button', 'n_clicks'),
	Input('twelve-months-button', 'n_clicks'),
	Input('current-year-button', 'n_clicks'),
	Input('reset-date-button', 'n_clicks')

)													

def update_dashboard(start_date, end_date, six_months_clicks, twelve_months_clicks, current_year_clicks, reset_clicks):
	# ------------------------------------- # 
	# 			activate date buttons		#
	# ------------------------------------- # 
	triggered_id = ctx.triggered_id

	if triggered_id == 'six-months-button':
		start_date = (today - pd.DateOffset(months=6)).strftime('%Y-%m-%d')
		end_date = today.strftime('%Y-%m-%d')

	if triggered_id == 'twelve-months-button':
		start_date = (today - pd.DateOffset(months=12)).strftime('%Y-%m-%d')
		end_date = today.strftime('%Y-%m-%d')
	
	if triggered_id == 'reset-date-button':
		start_date = min_date.strftime('%Y-%m-%d')
		end_date = max_date.strftime('%Y-%m-%d')

	if triggered_id == 'current-year-button':
		start_date = f'{today.year}-01-01'
		end_date = today.strftime('%Y-%m-%d')

	# --------------------------------------------- # 
	# 	filter data based on date range selected	#
	# --------------------------------------------- # 
	filtered_transactions = transactions_data.copy()
	filtered_monthly = monthly_summaries_data.copy()
	filtered_debt = dti_df.copy()

	if start_date:
		filtered_transactions = filtered_transactions[filtered_transactions['date'] >= pd.to_datetime(start_date)]
		filtered_monthly = filtered_monthly[filtered_monthly['month'] >= pd.to_datetime(start_date)]
		filtered_debt = filtered_debt[filtered_debt['month'] >= pd.to_datetime(start_date)]
	if end_date:
		filtered_transactions = filtered_transactions[filtered_transactions['date'] <= pd.to_datetime(end_date)]
		filtered_monthly = filtered_monthly[filtered_monthly['month'] <= pd.to_datetime(end_date)]
		filtered_debt = filtered_debt[filtered_debt['month'] <= pd.to_datetime(end_date)]

	is_long_range = len(filtered_monthly) > 12

	# ------------------------------------- # 
	# 		summarize data for banner		#
	# ------------------------------------- # 
	total_income = filtered_monthly['Net Income'].sum() if 'Net Income' in filtered_monthly.columns else 0
	formatted_total_income = f"${total_income:,.0f}"

	total_expenses = filtered_monthly['Expenses'].sum() if 'Expenses' in filtered_monthly.columns else 0
	formatted_total_expenses = f"${total_expenses:,.0f}"

	net_savings_rate = (																			# (net income - total expenses) / net income
		(filtered_monthly['Net Income'].sum() - filtered_monthly['Expenses'].sum())		
		/ filtered_monthly['Net Income'].sum()												
		) * 100 if 'Net Income' and 'Expenses' in filtered_monthly.columns else 0

	formatted_net_savings_rate = f"{net_savings_rate:,.0f}%"

	dti_ratio = (filtered_debt['debt_payments'].sum() / filtered_debt['Net Income'].sum()) * 100
	formatted_dti_ratio = f"{dti_ratio:,.0f}%"




	# ------------------------------------- # 
	# 		income vs expenses bar plot 	#
	# ------------------------------------- # 
	# plot
	income_v_expenses_bar = px.bar(
		filtered_monthly,
		x='month',
		y=['Net Income', 'Expenses'],
		barmode='group',
		title='<b>Monthly Income vs Expenses</b>',
		color_discrete_map={
			'Net Income': "#11CACA",
			'Expenses': "#CA2D3A"
		},
		text_auto=',.0f'					# format value of each bar
		)

	# update y axis
	income_v_expenses_bar.update_yaxes(
		title= None,
		showline=False,
		showticklabels=False,
		ticks='',
		showgrid=True
	)

	# update x-axis depending on which date range selected
	if is_long_range:
		# months > 12
		income_v_expenses_bar.update_xaxes(
			title= None,
			ticks='outside',
			tickson='boundaries',
			ticklen=10,
			type='date',
			tickformat='%b %Y',
			dtick='M6'
		)

		income_v_expenses_bar.update_traces(
			text=None,
			texttemplate='',
			customdata=filtered_monthly['month'].dt.strftime("%B %Y"),
			hovertemplate=(
				"<b>Month</b>: %{customdata}<br>"
				"<b>%{fullData.name}</b>: $%{y:,.0f}"
				"<extra></extra>"
				)
		)
	else:
		# months <= 12
		income_v_expenses_bar.update_xaxes(
			title= None,
			ticks='outside',
			tickson='boundaries',
			ticklen=10,
			type='category',
			tickvals=filtered_monthly['month'],
			ticktext=filtered_monthly['month'].dt.strftime('%b')
		)

		
		income_v_expenses_bar.update_traces(
			customdata=filtered_monthly['month'].dt.strftime("%B %Y"),
			hovertemplate=(
				"<b>Month</b>: %{customdata}<br>"
				"<b>%{fullData.name}</b>: $%{y:,.0f}"
				"<extra></extra>"
				),
			textangle=-90,
			textposition='inside',
			insidetextanchor='end'
		)



	# title, legend, margins
	income_v_expenses_bar.update_layout(
		margin=dict(l=30, r=30, t=80, b=30),			# adjust plot margins within container
		title={
			'x': 0.5,
			'xanchor': 'center',
			'font': {
				'color': "#000000",
				'size': 20
			}
		},
		legend=dict(
			orientation='h',
			yanchor='top',
			y=1.1,
			xanchor='center',
			x=0.70,
			title_text=''
		)
	)


	# ------------------------------------- # 
	# 		monthly net savings bar plot 	#
	# ------------------------------------- # 
	net_savings_bar = px.bar(
		filtered_monthly,
		x='month',
		y='savings_amount',
		barmode='group',
		title='<b> Net Monthly Savings</b>',
		color_discrete_map={
			'savings_amount': "#2DCA79"
		},
		text_auto=',.0f',
	)

	# adjust y-axis
	net_savings_bar.update_yaxes(
		title= None,
		showline=False,
		showticklabels=False,
		ticks='',
		showgrid=True
	)

	# update x-axis depending on which date range selected
	if is_long_range:
		# months > 12
		net_savings_bar.update_xaxes(
			title= None,
			ticks='outside',
			tickson='boundaries',
			ticklen=10,
			type='date',
			tickformat='%b %Y',
			dtick='M6'
		)

		net_savings_bar.update_traces(
			text=None,
			texttemplate='',
			marker_color="#2DCA79",
			customdata=filtered_monthly['month'].dt.strftime("%B %Y"),
			hovertemplate=(
				"<b>Month</b>: %{customdata}<br>"
				"<b>Net Savings</b>: $%{y:,.0f}"
				"<extra></extra>"
			)
		)
	else:
		# months <= 12
		net_savings_bar.update_xaxes(
			title= None,
			ticks='outside',
			tickson='boundaries',
			ticklen=10,
			type='category',
			tickvals=filtered_monthly['month'],
			ticktext=filtered_monthly['month'].dt.strftime('%b')
		)

		net_savings_bar.update_traces(
			marker_color="#2DCA79",
			customdata=filtered_monthly['month'].dt.strftime("%B %Y"),
			hovertemplate=(
				"<b>Month</b>: %{customdata}<br>"
				"<b>Net Savings</b>: $%{y:,.0f}"
				"<extra></extra>"
			),
			textangle=-90,
			textposition='inside',
			insidetextanchor='end'
		)

	# update layout
	net_savings_bar.update_layout(
		margin=dict(l=30, r=30, t=80, b=30),
		title={
			'x': 0.5,
			'xanchor': 'center',
			'font': {
				'color': "#000000",
				'size': 20
			}
		},
		legend=dict(
			orientation='h',
			yanchor='top',
			y=1.2,
			xanchor='center',
			x=0.90,
			title_text=''
		)
	)






	# ------------------------------------- # 
	# 			gauge plot function		 	#
	# ------------------------------------- # 
	def create_gauge_plot(metric_value, goal_value, plt_title, color_pal):
		sections = goal_value / 4

		percent_complete = (
			(metric_value / goal_value * 100) if goal_value > 0 else 0.0
		)

		remaining_value = goal_value - metric_value

		remaining_percent = 100 - percent_complete 
		

		fig = go.Figure(go.Indicator(
			mode="gauge+number",
			value=metric_value,
			number={
				'font': {'size': 36, 'color': "black", 'family': 'Arial'},
				'valueformat': "$,.0f"
			},
			gauge={
				'shape': "angular",
				'axis': {
					'range': [0, goal_value],
					'tickvals': [0, goal_value],          			# lab min and max goal
					'ticktext': ['$0', f'${goal_value}'],   		# format labels
					'tickwidth': 1,
					'tickcolor': "gray",
					'tickfont': {'size': 12, 'color': "black"},
					'showticklabels': False,
					'ticks':''
				},
				'bar': {'color': color_pal[0], 'thickness': 1},		# hide line within bar
				'threshold':{										# add line at metric_value
					'line': {'color': color_pal[1], 'width': 5},
					'thickness': 1,
					'value': metric_value
				},
				'bgcolor': "white",
				'borderwidth': 0,
				'steps': [
					{'range': [0, sections], 'color': 'rgba(0, 0, 0, 0.1)'},    
					{'range': [sections, sections*2], 'color': 'rgba(0, 0, 0, 0.15)'},    
					{'range': [sections*2, sections*3], 'color': 'rgba(0, 0, 0, 0.20)'},
					{'range': [sections*3, goal_value], 'color': 'rgba(0, 0, 0, 0.25)'}      
				],
			},
		))

		# title
		fig.add_annotation(
			text=f"<b>{plt_title}</b>",
			x=0.5,
			y=1.1,
			xref='paper',
			yref='paper',
			showarrow=False,
			font=dict(size=18, color='black', family='Arial'),
			xanchor='center',
			yanchor='top'
		)

		# axis labels
		fig.add_annotation(
			text=f'$0',
			x=0.05,
			y=-0.05,
			xref='paper',
			yref='paper',
			showarrow=False,
			font=dict(size=14, color='black', family='Arial'),
			xanchor='center'
		)

		fig.add_annotation(
			text=f'${goal_value:,.0f}',
			x=0.92,
			y=-0.05,
			xref='paper',
			yref='paper',
			showarrow=False,
			font=dict(size=14, color='black', family='Arial'),
			xanchor='center'
		)

		fig.add_annotation(
			text=(f'<b>Completed: </b>{percent_complete:,.1f}%<br><b>Remaining:</b> ${remaining_value: ,.0f} ({remaining_percent:.1f}%)'),
			x=0.5,
			y=-0.15,
			xref='paper',
			yref='paper',
			showarrow=False,
			font=dict(size=14, color='black', family='Arial'),
			xanchor='center'
		)

		fig.update_layout(
			height=320,
			margin=dict(l=30, r=30, t=40, b=40),
			paper_bgcolor='white',
			font={'family': 'Arial'}
		)

		

		return fig

	# ------------------------------------- # 
	# 				gauge plots			 	#
	# ------------------------------------- # 


	# calculate savings goal and currently saved
	savings_goal = category_goals_data[category_goals_data['category_group_name'] == "Long Term Savings & Sinking Funds"]
	current_saved = savings_goal['balance_amount'].sum()
	total_savings_goal = savings_goal['goal_target_amount'].sum()
		

	# calculate investments goal and currently investments
	investment_goal = category_goals_data[category_goals_data['category_group_name'] == "Investments & Net Worth"]
	current_invested = investment_goal['balance_amount'].sum()
	total_investment_goal = investment_goal['goal_target_amount'].sum()


	# calculate debt starting balance and currently paid off
	debt_accounts = account_data[
		(account_data['type'].isin(debt_types)) & 
		(~account_data['closed']) & 
		(~account_data['deleted'])
	]

	current_debt_owed = debt_accounts['balance_amount'].abs().sum()

	all_time_debt_paid = transactions_data[
		transactions_data['account_id'].isin(debt_accounts['id']) &
		((transactions_data['transaction_amount'] < 0) & (~transactions_data['account_name'].str.contains('Visa|Card', case=False, na=False)) |
		(transactions_data['transaction_amount'] > 0) & (transactions_data['account_name'].str.contains('Visa|Card', case=False, na=False)))
	]['transaction_amount'].abs().sum()

	total_starting_debt = all_time_debt_paid + current_debt_owed
	
	# plot gauge plots 
	savings_gauge = create_gauge_plot(metric_value=current_saved, goal_value=total_savings_goal, plt_title = "Savings Goal", color_pal = ["#3B8E1A", "#184506"])
	investments_gauge = create_gauge_plot(metric_value=current_invested, goal_value=total_investment_goal, plt_title = "Investments Portfolio", color_pal = ["#B91C7F", "#691149"])
	debt_gauge = create_gauge_plot(metric_value=all_time_debt_paid, goal_value=total_starting_debt, plt_title = "Debt Annihilation", color_pal = ["#932DCA", "#51186F"])


	# return outputs
	return (
		start_date, end_date, 
		formatted_total_income, formatted_total_expenses, formatted_net_savings_rate, formatted_dti_ratio,
		income_v_expenses_bar, net_savings_bar, savings_gauge, investments_gauge, debt_gauge
	)






if __name__ == '__main__':
	app.run(jupyter_mode="external")