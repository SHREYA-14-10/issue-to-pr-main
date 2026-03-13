from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
from scan_repo import scan_repository

builder = SparkSession.builder \
    .appName("RepoAnalyzer") \
    .master("local[*]") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

repo = "../../flask"

files = scan_repository(repo)

df = spark.createDataFrame(files)

df.show(100, truncate=False)

# Save metadata in Delta Lake
df.write.format("delta").mode("overwrite").save("repo_metadata")

spark.stop()