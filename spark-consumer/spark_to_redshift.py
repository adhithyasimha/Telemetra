from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, window, expr, sum as _sum, 
    collect_list, when, size, sort_array, struct,
    first, last, max as spark_max, coalesce
)
from pyspark.sql.types import StructType, StringType, BooleanType, TimestampType, IntegerType, DoubleType

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("F1LapTimingPipeline") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define schema
schema = StructType() \
    .add("SessionKey", StringType()) \
    .add("timestamp", StringType()) \
    .add("DriverNo", StringType()) \
    .add("LapNumber", IntegerType()) \
    .add("Sectors_0_Value", StringType()) \
    .add("Sectors_1_Value", StringType()) \
    .add("Sectors_2_Value", StringType())

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "pkc-p11xm.us-east-1.aws.confluent.cloud:9092") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanisms", "PLAIN") \
    .option("kafka.sasl.username", "nah") \
    .option("kafka.sasl.password", "nah") \
    .option("kafka.session.timeout.ms", "45000") \
    .option("kafka.client.id", "ccloud-python-client-3a0fabd2-56c6-4ba1-b185-4ac8f686dd2a") \
    .option("subscribe", "timing_data_f1") \
    .option("startingOffsets", "latest") \
    .load()

# Parse and transform
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.*")

# Convert and clean data
converted_df = parsed_df \
    .withColumn("timestamp", col("timestamp").cast(TimestampType())) \
    .withColumn("S1", when(col("Sectors_0_Value") != "", col("Sectors_0_Value").cast("double")).otherwise(None)) \
    .withColumn("S2", when(col("Sectors_1_Value") != "", col("Sectors_1_Value").cast("double")).otherwise(None)) \
    .withColumn("S3", when(col("Sectors_2_Value") != "", col("Sectors_2_Value").cast("double")).otherwise(None)) \
    .filter(col("DriverNo").isNotNull() & col("LapNumber").isNotNull())

# Create sector records - one row per sector completion
sector_df = converted_df.select(
    col("DriverNo"),
    col("LapNumber"), 
    col("timestamp"),

    expr("array(struct(1 as sector_num, S1 as sector_time, timestamp), " +
         "struct(2 as sector_num, S2 as sector_time, timestamp), " +
         "struct(3 as sector_num, S3 as sector_time, timestamp)) as sectors")
).select(
    col("DriverNo"),
    col("LapNumber"),
    col("timestamp"),
    expr("explode(sectors) as sector_data")
).select(
    col("DriverNo"),
    col("LapNumber"),
    col("timestamp"),
    col("sector_data.sector_num").alias("SectorNum"),
    col("sector_data.sector_time").alias("SectorTime")
).filter(col("SectorTime").isNotNull())

# Use watermarking and windowing optimized for F1 racing conditions
# Window: 60s to capture all drivers + weather delays
# Watermark: 50s to handle rain conditions but prevent memory bloat
windowed_df = sector_df \
    .withWatermark("timestamp", "50 seconds") \
    .groupBy(
        window(col("timestamp"), "60 seconds", "20 seconds"),  # 60s window, slide every 20s
        col("DriverNo"), 
        col("LapNumber")
    ) \
    .agg(
        collect_list(
            struct(col("SectorNum"), col("SectorTime"), col("timestamp"))
        ).alias("sector_list"),
        spark_max(col("timestamp")).alias("last_sector_time"),
        expr("size(collect_list(struct(SectorNum, SectorTime, timestamp)))").alias("sector_count")
    )

# Filter only complete laps (all 3 sectors received)
# Also handle timeout cases for incomplete laps
complete_laps_df = windowed_df \
    .filter(size(col("sector_list")) >= 3) \
    .select(
        col("DriverNo"),
        col("LapNumber"),
        col("last_sector_time").alias("LapCompletionTime"),
        sort_array(col("sector_list")).alias("sorted_sectors"),
        col("sector_count")
    ) \
    .select(
        col("DriverNo"),
        col("LapNumber"),
        col("LapCompletionTime"),
        col("sorted_sectors")[0]["SectorTime"].alias("S1"),
        col("sorted_sectors")[1]["SectorTime"].alias("S2"), 
        col("sorted_sectors")[2]["SectorTime"].alias("S3"),
        (col("sorted_sectors")[0]["SectorTime"] + 
         col("sorted_sectors")[1]["SectorTime"] + 
         col("sorted_sectors")[2]["SectorTime"]).alias("TotalLapTime"),
        col("sector_count")
    )

# Optional: Handle incomplete laps for monitoring
incomplete_laps_df = windowed_df \
    .filter((size(col("sector_list")) < 3) & (size(col("sector_list")) > 0)) \
    .select(
        col("DriverNo"),
        col("LapNumber"), 
        col("sector_count"),
        col("last_sector_time"),
        expr("'INCOMPLETE'").alias("status")
    )

# Final output with proper primary key structure
final_df = complete_laps_df.select(
    col("LapNumber"),           # Primary key part 
    col("DriverNo"),             
    col("S1"),
    col("S2"),
    col("S3"),
    col("TotalLapTime"),
    col("LapCompletionTime")
)

# Write to Redshift function with proper error handling
def write_to_redshift(batch_df, batch_id):
    try:
        print(f"Processing batch {batch_id} with {batch_df.count()} records")
        batch_df.show(5, truncate=False)
        batch_df.write \
            .format("jdbc") \
            .option("url", "jdbc:redshift://your-redshift-cluster:5439/yourdb") \
            .option("dbtable", "lap_times") \
            .option("user", "your_user") \
            .option("password", "your_password") \
            .option("driver", "com.amazon.redshift.jdbc.Driver") \
            .option("stringtype", "unspecified") \
            .mode("append") \
            .save()
            
        print(f"Successfully wrote batch {batch_id}")
    except Exception as e:
        print(f"Error writing batch {batch_id}: {str(e)}")

        
# Start streaming query with optimized trigger interval
query = final_df.writeStream \
    .foreachBatch(write_to_redshift) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/f1_lap_timing_checkpoint") \
    .trigger(processingTime='20 seconds') \
    .start()

incomplete_query = incomplete_laps_df.writeStream \
    .foreachBatch(lambda df, batch_id: df.show(truncate=False)) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/f1_incomplete_checkpoint") \
    .trigger(processingTime='30 seconds') \
    .start()

query.awaitTermination()