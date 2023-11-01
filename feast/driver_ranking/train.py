import feast
from joblib import dump
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from feast import FeatureStore

# Load driver order data
orders = pd.read_csv("driver_orders.csv", sep="\t")
orders["event_timestamp"] = pd.to_datetime(orders["event_timestamp"])

fs = feast.FeatureStore(repo_path="feature_repo")

# entity_df = pd.DataFrame.from_dict(
#     {
#         # entity's join key -> entity values
#         "driver_id": [1001, 1002, 1003],
#         # "event_timestamp" (reserved key) -> timestamps
#         "event_timestamp": [
#             datetime(2021, 4, 12, 10, 59, 42),
#             datetime(2021, 4, 12, 8, 12, 10),
#             datetime(2021, 4, 12, 16, 40, 26),
#         ],
#         # (optional) label name -> label values. Feast does not process these
#         "trip_completed": [1, 0, 1],
#     }
# )
#
# training_df = fs.get_historical_features(
#     entity_df=entity_df,
#     features=[
#         "driver_hourly_stats:conv_rate",
#         "driver_hourly_stats:acc_rate",
#         "driver_hourly_stats:avg_daily_trips",
#     ],
# ).to_df()
# print(training_df)


training_df = fs.get_historical_features(
    entity_df=orders,
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
).to_df()

print("Training dataset:")
print(training_df)
print()

# Train model
target = "trip_completed"

reg = LinearRegression()
train_X = training_df[training_df.columns.drop(target).drop("event_timestamp")]
train_Y = training_df.loc[:, target]
reg.fit(train_X[sorted(train_X)], train_Y)

# Save model
dump(reg, "driver_model.bin")