###############################################################
# Customer Segmentation with RFM
###############################################################

###############################################################
# Business Problem
###############################################################
# FLO an online shoe store segmenting and marketing it's Customers and according to these segments
# wants to define strategies. For this purpose behavior of customers will be defined and these groups will be formed according to clusters in behavior

###############################################################
# Data set
###############################################################

# The data set is based on the past shopping behavior of customers who made their last purchases as OmniChannel (both online and offline shopper) in 2020 - 2021.
# consists of the information obtained.

# master_id Unique customer id
# order_channel Shopping Channel (Android, ios, Desktop, Mobile)
# last_order_channel lastly used channel to order
# first_order_date Date when customer ordered for the first time
# last_order_date Date when customer ordered lastly
# last_order_date_online Date when customer ordered lastly on the online platform
# last_order_date_offline Date when customer ordered lastly as offline
# order_num_total_ever_online
# order_num_total_ever_offline
# customer_value_total_ever_offline Amount of money that customer paid ever to buy as offline
# customer_value_total_ever_online Amount of money that customer paid ever to buy as online
# interested_in_categories_12 categories in which customer has bought for last 12 monthes

###############################################################
# Tasks
###############################################################

# Task 1: Data Understanding and Preparation
           # 1. read flo_data_20K.csv.
           # 2.
                     # a. First 10 observation in the data set,
                     # b. Variable names,
                     # c. Descriptive statistics,
                     # d. null values,
                     # e. variable types
           # 3. Create new varible for total customer value and number of order by using online anf offline data
           # 4.Change varible types which stands for date from object to date
           # 5. Check number of customers in order channels, average number of products and distribution of average expenditure
           # 6. List 10 customers who brings atmost value
           # 7. List 10 customers who ordered atmost
           # 8. Create a function for data prepareation

# Task 2: Calculate RFM Metrics

# Task 3: Calculate RF ve RFM Scores

# Task 4: Define RF Scores as Segment

# Task 5: Time to take actions!
           # 1. Calculate the recency, frequency and monetary averages of the segments
           # 2. With the help of RFM analysis, find the customers in the relevant profile for 2 cases and save the customer IDs to csv.
                   # a. FLO includes a new women's shoe brand.
                   # The product prices of the brand it includes are above the general customer preferences.
                   # For this reason, customers in the profile who will be interested in the promotion of the brand and product sales are requested to be contacted privately.
                   #Those who shop from their loyal customers (champions, loyal_customers), on average over 250 TL and from the women category, are the customers
                   # to contact privately. Save the id numbers of these customers in the csv file as new_brand_target_customer_id.cvs.
                   # b. Up to 40% discount is planned for Men's and Children's products. It is aimed to specifically target customers who are good customers in the past,
                   # but who have not shopped for a long time,
                   # who are interested in the categories related to this discount,
                    # who should not be lost, those who are asleep and new customers.
                    # Save the ids of the customers in the appropriate profile to the csv file as discount_target_customer_ids.csv.


###############################################################
#  Task 1: Data Understanding and Preparation
###############################################################
import pandas as pd
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width',1000)

# 1.1
df_ = pd.read_csv("/Dataset/flo_data_20K.csv")
df = df_.copy()
df.head()

# 1.2
df.head(10)
df.columns
df.shape
df.describe().T
df.isnull().sum()
df.info()

# 1.3
df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

# 1.4
date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.info()

# 1.5
df.groupby("order_channel").agg({"master_id":"count",
                                 "order_num_total":"sum",
                                 "customer_value_total":"sum"})

# 1.6
df.sort_values("customer_value_total", ascending=False)[:10]

# 1.7
df.sort_values("order_num_total", ascending=False)[:10]

# 1.8
def data_prep(dataframe):
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)
    return df

###############################################################
# Task 2: Calculate RFM Metrics
###############################################################

# Analysis date 2 days after the last purchase in the data set
df["last_order_date"].max() # 2021-05-30
analysis_date = dt.datetime(2021,6,1)


# A new rfm dataframe with customer_id, recency, frequnecy and monetary values
rfm = pd.DataFrame()
rfm["customer_id"] = df["master_id"]
rfm["recency"] = (analysis_date - df["last_order_date"]).astype('timedelta64[D]')
rfm["frequency"] = df["order_num_total"]
rfm["monetary"] = df["customer_value_total"]

rfm.head()

###############################################################
# Task 3: Calculate RF ve RFM Scores
###############################################################

# Converting Recency, Frequency and Monetary metrics to scores between 1-5 with the help of qcut and
# Saving these scores as recency_score, frequency_score and monetary_score
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm.head()

# Expressing recency_score and frequency_score as a single variable and saving it as RF_SCORE
rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))


# Expressing recency_score and frequency_score and monetary_score as a single variable and saving it as RFM_SCORE
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))

rfm.head()

###############################################################
# Task 4: Define RF Scores as Segment
###############################################################

# Segment definition and converting RF_SCORE to segments
# with the help of defined seg_map so that the generated RFM scores can be explained more clearly.
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

rfm.head()

###############################################################
# Time to take actions!
###############################################################

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#                          recency       frequency       monetary
#                        mean count      mean count     mean count
# segment
# about_to_sleep       113.79  1629      2.40  1629   359.01  1629
# at_Risk              241.61  3131      4.47  3131   646.61  3131
# cant_loose           235.44  1200     10.70  1200  1474.47  1200
# champions             17.11  1932      8.93  1932  1406.63  1932
# hibernating          247.95  3604      2.39  3604   366.27  3604
# loyal_customers       82.59  3361      8.37  3361  1216.82  3361
# need_attention       113.83   823      3.73   823   562.14   823
# new_customers         17.92   680      2.00   680   339.96   680
# potential_loyalists   37.16  2938      3.30  2938   533.18  2938
# promising             58.92   647      2.00   647   335.67   647

# a. FLO includes a new women's shoe brand.
# The product prices of the brand it includes are above the general customer preferences.
# For this reason, customers in the profile who will be interested in the promotion of the brand and product sales are requested to be contacted privately.
#Those who shop from their loyal customers (champions, loyal_customers), on average over 250 TL and from the women category, are the customers
# to contact privately. Save the id numbers of these customers in the csv file as new_brand_target_customer_id.cvs.

target_segments_customer_ids = rfm[rfm["segment"].isin(["champions","loyal_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) &(df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
cust_ids.to_csv("yeni_marka_hedef_müşteri_id.csv", index=False)
cust_ids.shape

rfm.head()

# b. Up to 40% discount is planned for Men's and Children's products. It is aimed to specifically target customers who are good customers in the past,
# but who have not shopped for a long time,
# who are interested in the categories related to this discount,
# who should not be lost, those who are asleep and new customers.
# Save the ids of the customers in the appropriate profile to the csv file as discount_target_customer_ids.csv.

target_segments_customer_ids = rfm[rfm["segment"].isin(["cant_loose","hibernating","new_customers"])]["customer_id"]
cust_ids = df[(df["master_id"].isin(target_segments_customer_ids)) & ((df["interested_in_categories_12"].str.contains("ERKEK"))|(df["interested_in_categories_12"].str.contains("COCUK")))]["master_id"]
cust_ids.to_csv("indirim_hedef_müşteri_ids.csv", index=False)
