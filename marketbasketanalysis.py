# -*- coding: utf-8 -*-
"""MarketBasketAnalysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1t8xuE06QK2H8Isll3y4PRrtSEC1zSpjD
"""

!pip install -q pyspark

!wget -q 'https://drive.google.com/uc?export=download&id=19xz2KPlbhVgIXDjyKNPebVbv15iIRdx4' -O "groceries - groceries.csv"
!wget -q 'https://drive.google.com/uc?export=download&id=1plfOaSkWbtoVjENyylRKcmj3UNaapbUq' -O "tesecase1.csv"
!wget -q 'https://drive.google.com/uc?export=download&id=1QBtVe81S6ZjNmTfgLQWaY0J17RwtyiEX' -O "testcase2.csv"
!wget -q 'https://drive.google.com/uc?export=download&id=1_SxuZPZl5yWkpb9ty9c4mQbwWatq4h1L' -O "Testcase3.csv"
!wget -q 'https://drive.google.com/uc?export=download&id=16DFgtsIN91UirfGUKRPZKp2gmtPP7ZQ_' -O "Testcase4.csv"

from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession

conf = SparkConf().setAppName('apriori-fp growth')
sc = SparkContext.getOrCreate(conf = conf)

sqlContext = SparkSession.builder\
        .master("local")\
        .appName("Colab")\
        .config('spark.ui.port', '4050')\
        .getOrCreate()

"""**Converting the input data into required format**"""

from pyspark.sql.functions import concat_ws, array, row_number, lit, split, count, expr, desc, explode, col, concat, round, collect_list
from pyspark.sql.window import Window
from itertools import combinations
from os import truncate


df = sqlContext.read.option("header", "false").csv("groceries - groceries.csv")
# df = sqlContext.read.option("header", "false").csv("testcase1.csv")
# df = sqlContext.read.option("header", "false").csv("testcase2.csv")
item_columns = [col for col in df.columns[1:]]
item_array = df.select(array(*item_columns).alias("Items"))
df_single_column = item_array.withColumn("All_Items", concat_ws(", ", "Items"))
df_single_column = df_single_column.select("All_Items")
window_spec = Window.orderBy(lit(1))
df_with_row_number = df_single_column.withColumn("row_number", row_number().over(window_spec))
df_without_count = df_with_row_number.filter("row_number > 1").drop("row_number")
df_with_list = df_without_count.withColumn("Item_List", split("All_Items", ", "))
formated_input = df_with_list.select("Item_List")
formated_input.show(truncate=False)

"""**Obtaining the Single item count**"""

df_exploded = formated_input.withColumn("Item", explode(col("Item_List")))
df_items = df_exploded.withColumn("Item", explode(split(col("Item"), ", ")))
single_item_count = df_items.groupBy("Item").count()
single_item_count.show()

"""**Creating all possible pairs and its count**"""

minimum_support = 120

from itertools import combinations
from pyspark.sql import Row

list_of_item = formated_input.rdd.map(lambda row: row.Item_List)
pairs = list_of_item.flatMap(lambda item_list: combinations(sorted(item_list), 2))
pair_counting = pairs.map(lambda pair: (pair, 1))
count_pair = pair_counting.reduceByKey(lambda x, y: x + y)
filtered_pairs = count_pair.filter(lambda x: x[1] >= minimum_support)

def join_counts(row):
    pair = row[0]
    support = row[1]
    item1, item2 = pair
    return [(pair, support), ((item2, item1), support)]

all_pairs_count = filtered_pairs.flatMap(join_counts).map(lambda x: Row(pairs=",".join(x[0]), support=x[1])).toDF()
all_pairs_count.show(truncate=False)

"""**Find Confidence of each pair and filter on support threshold**"""

word_counts_dict = dict(single_item_count.collect())

def join_with_single_item_count(row):
    pair = row["pairs"]
    item1, item2 = pair.split(',')
    support = row["support"]
    count1 = word_counts_dict.get(item1, 0)
    return (pair, support, count1)

joined_pair_count = all_pairs_count.rdd.map(join_with_single_item_count).toDF(["pairs", "Pairs_support", "item_support"])
association_rule_df = joined_pair_count.withColumn(
    "confidence",
    round((col("Pairs_support") / col("item_support")),3)
)
association_rule_df.show(truncate=False)

minimum_confidence = 0.4
filtered_association_rules = association_rule_df.filter(col("confidence") >= minimum_confidence)
sorted_rules=filtered_association_rules.orderBy(desc("confidence"))
split_on_pair = sorted_rules.withColumn("pair_items", split(col("pairs"), ","))
item_extract = split_on_pair.withColumn("x", col("pair_items").getItem(0))
items_extract = item_extract.withColumn("y", col("pair_items").getItem(1))
df = items_extract.select("x", "y","Pairs_support","item_support","confidence")
formated_rdd = df.rdd.map(lambda row: (f"{row['x']}->{row['y']}",row['Pairs_support'],row['item_support'],row['confidence']))
formated_output = formated_rdd.toDF(["association rule: (I->j)","support(I U j)","support(I)","confidence=support(I U j)/support(I)"])
formated_output.write.csv("apriori_association_rules.csv", mode="overwrite")
formated_output.show(truncate=False)

"""### **FP-Growth Implementation Begins Here**:

### **Cleaning the dataset**
"""

from pyspark.ml.fpm import FPGrowth

# Read the CSV file into a DataFrame
# Please change the dataset to Testcase3 or Testcase4. Groceries dataset sometimes error out due to memory constraint.
df = sqlContext.read.option("header", "true").csv("groceries - groceries.csv")

# Concatenate all columns except the first one with comma-separated values
concatenated_df = df.withColumn("Items", concat_ws(",", *[col for col in df.columns[1:]]))

# Select both the first column and the concatenated column
result_df = concatenated_df.select(col("Item(s)"), col("Items"))

result_df.show(20)

"""### **Splitting the "Items" in the DataFrame and creating an "Item_Array**"
"""

split_items = result_df.withColumn("Item_Array", split(result_df["Items"], ","))
array_df = split_items.drop('Items')
array_df.show(20)

"""**frequent pattern mining to identify frequently occurring combinations of items in a dataset**"""

# Create an instance of FPGrowth
fp_growth = FPGrowth(itemsCol="Item_Array", minSupport=0.01, minConfidence=0.01)

# Fit the model on your DataFrame
fp_model = fp_growth.fit(split_items)

# Display frequent itemsets
frequent_itemsets = fp_model.freqItemsets

# Find frequent itemsets and export to file for checking
freq_itemsets_pandas = fp_model.freqItemsets.toPandas()
freq_itemsets_pandas.to_csv("Frequent Items.csv", index=False)

frequent_itemsets.show(20)

"""**Association Rules:**"""

# Display association rules
association_rules = fp_model.associationRules
association_rules.show(20)

# Find frequent itemsets and export to file for checking
association_rules_pandas = association_rules.toPandas()
association_rules_pandas.to_csv("FP_AssociationRules.csv", index=False)

# transform examines the input items against all the association rules and summarize the consequents as prediction
transformed_df = fp_model.transform(split_items)

transformed_df.show(20)

"""**Creating and saving final output csv:**"""

from pyspark.sql.functions import array_join

# Convert the array column "Item_Array" to a string representation
transformed_df = transformed_df.withColumn("Item_List", array_join("Item_Array", ", "))

# Convert the "prediction" column to a string representation
transformed_df = transformed_df.withColumn("Prediction_String", array_join("prediction", ", "))

# Select only the necessary columns
selected_df = transformed_df.select("Item_List", "Prediction_String")

# Write the selected DataFrame to a CSV file
selected_df.write.mode("overwrite").csv("FP Growth output", header=True)