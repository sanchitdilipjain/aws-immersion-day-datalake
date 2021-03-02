import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame

def MyTransform(glueContext, dfc) -> DynamicFrameCollection:
    selected = dfc.select(list(dfc.keys())[0]).toDF()
    
    from pyspark.sql.functions import regexp_replace as regxx
    
    modeCa = selected.groupby("ca").count().orderBy("count", ascending=False).first()[0]
    newDF = selected.withColumn('ca', regxx('ca', '\?', modeCa))
    
    modeThal = newDF.groupby("thal").count().orderBy("count", ascending=False).first()[0]
    newDF = newDF.withColumn('thal', regxx('thal', '\?', modeThal))
    
    results = DynamicFrame.fromDF(newDF, glueContext, "results")
    return DynamicFrameCollection({"results": results}, glueContext)

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
## @type: DataSource
## @args: [format_options = {"withHeader":True,"separator":",","quoteChar":"\""}, connection_type = "s3", format = "csv", connection_options = {"paths": ["s3://aws-glue-lab-src-header/processed.cleveland_withheader.csv"]}, transformation_ctx = "DataSource0"]
## @return: DataSource0
## @inputs: []
DataSource0 = glueContext.create_dynamic_frame.from_options(format_options = {"withHeader":True,"separator":",","quoteChar":"\""}, connection_type = "s3", format = "csv", connection_options = {"paths": ["s3://aws-glue-lab-src-header/processed.cleveland_withheader.csv"]}, transformation_ctx = "DataSource0")
## @type: CustomCode
## @args: [dynamicFrameConstruction = DynamicFrameCollection({"DataSource0": DataSource0}, glueContext), className = MyTransform, transformation_ctx = "Transform0"]
## @return: Transform0
## @inputs: [dfc = DataSource0]
Transform0 = MyTransform(glueContext, DynamicFrameCollection({"DataSource0": DataSource0}, glueContext))
## @type: SelectFromCollection
## @args: [key = list(Transform0.keys())[0], transformation_ctx = "Transform1"]
## @return: Transform1
## @inputs: [dfc = Transform0]
Transform1 = SelectFromCollection.apply(dfc = Transform0, key = list(Transform0.keys())[0], transformation_ctx = "Transform1")
## @type: DataSink
## @args: [connection_type = "s3", format = "parquet", connection_options = {"path": "s3://aws-glue-lab-tgt/", "compression": "gzip", "partitionKeys": []}, transformation_ctx = "DataSink0"]
## @return: DataSink0
## @inputs: [frame = Transform1]
DataSink0 = glueContext.write_dynamic_frame.from_options(frame = Transform1, connection_type = "s3", format = "parquet", connection_options = {"path": "s3://aws-glue-lab-tgt/", "compression": "gzip", "partitionKeys": []}, transformation_ctx = "DataSink0")
job.commit()