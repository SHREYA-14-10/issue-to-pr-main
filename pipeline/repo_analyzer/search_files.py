from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = SparkSession.builder \
    .appName("SearchFiles") \
    .master("local[*]") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Load Delta table
df = spark.read.format("delta").load("repo_metadata")

# Filter Python files
python_files = df.filter(df.filename.endswith(".py"))

python_files.show(100, truncate=False)

spark.stop()