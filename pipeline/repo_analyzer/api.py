from fastapi import FastAPI
from pyspark.sql import SparkSession

app = FastAPI()

spark = SparkSession.builder \
    .appName("RepoAnalyzerAPI") \
    .config("spark.jars.packages", "io.delta:delta-spark_2.13:4.1.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()


@app.get("/")
def home():
    return {"message": "Repo Analyzer API running"}


@app.get("/files")
def get_files():
    df = spark.read.format("delta").load("../../repo_metadata")

    rows = df.limit(20).collect()

    files = []
    for r in rows:
        files.append({
            "filename": r["filename"],
            "path": r["path"]
        })

    return {"files": files}


@app.get("/search")
def search_files(keyword: str):
    df = spark.read.format("delta").load("../../repo_metadata")

    rows = df.filter(df.filename.contains(keyword)).limit(20).collect()

    results = []
    for r in rows:
        results.append({
            "filename": r["filename"],
            "path": r["path"]
        })

    return {"results": results}