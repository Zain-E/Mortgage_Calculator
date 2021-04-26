
import streamlit as st
import pandas as pd
from datetime import date
import numpy_financial as np

#---------------------MORTGAGE CALCULATOR PROJECT (NUMBER 2)-------------------------------------------------------------------------------------

payments_per_year = 12
#no_of_years = 40
Early_payment_percentage = 0.1
start_date = date.today()
start_date = start_date.strftime("%d/%m/%Y")


#-------------------------------STREAM LIT APP----------------------------------------------------------------------------------------------------
st.title('Mortgage Calculator')

st.sidebar.subheader('House Price')
house_price = st.sidebar.number_input(label=f'Please enter the house price here (£):',value=550000, step=50000)
st.sidebar.subheader('Deposit')
deposit = st.sidebar.number_input(label=f'Please enter deposit size here (£):',value=200000, step=10000)
st.sidebar.subheader('Interest Rate')
Interest_rate_text = st.sidebar.number_input(label=f'Interest Rate (%):',value=1.31, step=0.1)
st.sidebar.subheader('Term')
no_of_years = st.sidebar.number_input(label=f'Mortgage Term (years):',value=40, step=1)
st.sidebar.subheader('Early Payment (Optional)')
Early_payment = st.sidebar.number_input(label=f'Monthly Early payment amount (£):',value=0, step=100)

Interest_rate = Interest_rate_text/100
Loan_amount = house_price - deposit
Early_payment_limit = (Loan_amount*Early_payment_percentage)/payments_per_year

i = Interest_rate/payments_per_year
n = payments_per_year * no_of_years

Discount_factor = ((1 + i)**n -1) / (i * (1 + i)**n)

# Loan_payment = Loan_amount / Discount_factor
Interest_payment = (Interest_rate/12)*Loan_amount
# Principal_payment = Loan_payment - Interest_payment

#-------------------------------- INPUT TO DF ----------------------------------------------------------------------------------



#List of dates to df
date_range = pd.date_range(start=start_date, periods=no_of_years*12, freq='M')
df = pd.DataFrame(date_range, columns=['date_range'])

#Date
df['date_range'] = df['date_range'].dt.date
df['date_range'] = pd.to_datetime(df["date_range"]).dt.strftime('%m/%Y')

#Extract year from the dates
df['year'] = pd.DatetimeIndex(df['date_range']).year

#Interest
df["interest_payment"] = abs(np.ipmt(Interest_rate/payments_per_year, df.index, no_of_years*payments_per_year, Loan_amount))
df['interest_payment'] = round(df['interest_payment'],0)

#Principal
Loan_payment = Loan_amount / Discount_factor
Principal_payment = Loan_payment - Interest_payment
df['Principle_payment'] = abs(np.ppmt(Interest_rate/payments_per_year, df.index, no_of_years*payments_per_year, Loan_amount))
df['Principle_payment'] = round(df['Principle_payment'],0)

#Early Payment
df['Early payment'] = round(Early_payment,0)

#Total Payment
df['Loan_payment'] = df["interest_payment"] + df['Principle_payment'] + df['Early payment']

#Loan
Loan_list = [Loan_amount]
for i in range(len(df)-1):
    Loan_list.append(Loan_list[-1] - df['Loan_payment'].values[i+1])

df['Loan_amount'] = Loan_list
df['Loan_amount'] = round(df['Loan_amount'],0)

#https://pbpython.com/amortization-model.html

#Truncate the table when balance reaches zero
last_payment = df.query("Loan_amount <= 0")["Loan_amount"].idxmax(axis=1, skipna=True)
df = df.loc[0:last_payment]

df['Loan_amount'] = df['Loan_amount'].apply(lambda x : "{:,}".format(x))

#Df aggregated for visualisation

dfgroup = df.groupby(['year'], as_index=True)[
            'interest_payment'].sum()

df_total = Loan_amount + df['interest_payment'].sum()
extra = df['interest_payment'].sum()
df_total = df_total.astype(int)
extra = extra.astype(int)

#------------------------------- PRESENTATION -----------------------------------------------------------------------------------
st.subheader('Summary of Calculations')
st.markdown(f'With an interest rate of **{round(Interest_rate_text,2)}%** and a house price of **£{round(house_price,0):,}**...')
#st.markdown(f'Monthly payments will be **£{round(Loan_payment,2):,}**.')
st.markdown(f'Monthly payments will be **£{round(Loan_payment,2):,}**.')
st.markdown(f'Of that, interest payments will be **£{round(Interest_payment,2):,}**.')
st.markdown(f'And principal payments will be **£{round(Principal_payment,2):,}**.')
st.markdown(f'The monthly early payment limit is **£{round(Early_payment_limit,2):,}** based on a **{round(100*Early_payment_percentage,0):}%** allowance.')
st.markdown(f'With a loan of **£{round(Loan_amount,2):,}** you will pay **£{df_total:,}**, which is an extra **£{extra:,}**.')

st.subheader('Graph')
st.bar_chart(dfgroup)

st.subheader('Amortization Schedule')
st.dataframe(df)


