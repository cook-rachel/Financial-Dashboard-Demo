# Personal Finance Dashboard

An interactive personal finance dashboard built with **Python**, **Dash**, and **Plotly**. This dashboard connects directly to exported YNAB (You Need A Budget) financial data to provide comprehensive insights into cash flow, savings rates, debt-to-income (DTI) metrics, and cumulative progress toward long-term financial milestones. 

For the purposes of this demo, an excel document, "ynab_dashboard_data.xlsx", has been provided that contains mock data used to populate the visuals for the dashboard.


---

### How to Use

1. Download or clone the repository.
2. Open the project folder in your preferred IDE.
3. Open Personal_Finance.py and set up your environment with the required dependencies:

	```python
	pip install -r requirements.txt
	```

4. Launch the dashboard application locally:

	```python
	Python Personal_Finance.Dashboard.py
	```

5. Open your web browser and paste the provided URL printed in the terminal.

---

### Key Features

- **Dynamic Date Filtering**: 
	- Interactive calendar that allows for specific date range selection.
 	- Quick-select preset buttons (**6 Months**, **12 Months**, **Current Year**, **All Dates**).

- **Dynamic Summary Banner**:
  	- **Total Income**: Aggregate inflow across all tracked net income sources for the selected date range.
  	- **Total Expenses**: Aggregate spending for the selected date range.
  	- **Net Savings Rate**: Percentage of income retained after expenses for the selected date range.
  	- **Debt-to-Income (DTI)**: Percentage of gross monthly income dedicated to paying off debt for the selected date range.

- **Dynamic Visualizations**:
  	- **Monthly Income vs. Expenses**: Grouped bar chart comparing inflows against outflows month-over-month for the selected date range.
  	- **Net Monthly Savings**: Monthly net balance of savings for the selected date range.

- **Current Financial Progress**:
  	- **Savings Goal**: Current progress towards savings goal calculated by the amount of money currently saved compared to the goal amount.
  	- **Investments Portfolio**: Cumulative portfolio progress toward targeted net worth goal.
  	- **Debt Annihilation**: Amount of debt that has been paid down again the total starting debt balance.
  
	*Gray shaded regions represent visual benchmarks at 25%, 50%, and 75% intervals.*

---

### Included Files

```text
├── Personal_Finance_Dashboard.py       # Main Dash application, UI layout, and reactive callbacks
├── ynab_dashboard_data.xlsx      	# Source data workbook (Accounts, Summaries, Transactions, Goals)
├── requirements.txt              	# Python package dependencies
└── README.md                     	# Project documentation and setup guide
```

---

### Required Dependencies:

Framework: Dash

Data Visualization: Plotly

Data Analysis: Pandas

Excel Reader: openpyxl

---

### Data Structure:

The dashboard expects the workbook to include the following sheets and columns:

*Accounts*: id, name, type, balance_amount, closed, deleted

*Monthly_Summaries*: month (YYYY-MM-DD), income_amount, activity_amount

*Transactions*: date (YYYY-MM-DD), account_id, account_name, transaction_amount

*Category_Goals*: category_group_name, balance_amount, goal_target_amount

This is the format that can be downloaded via the YNAB API with your personal YNAB token. Mock data has been provided via the ynab_dashboard_data.xlsx file.

---

### Calculations:

Net Savings Calculation:
$$\text{Savings Amount} = \text{Net Income} - \text{Expenses}$$

Net Savings Rate (%):

$$\text{Savings Rate} = \left( \frac{\sum \text{Net Income} - \sum \text{Expenses}}{\sum \text{Net Income}} \right) \times 100$$

Debt-to-Income (DTI) Ratio (%):

$$\text{DTI} = \left( \frac{\sum \text{Debt Payments}}{\sum \text{Net Income}} \right) \times 100$$

Total Starting Debt:

$$\text{Total Starting Debt} = \text{Cumulative Debt Principal Paid} + \text{Current Outstanding Balance}$$

