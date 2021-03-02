def MyTransform(glueContext, dfc) -> DynamicFrameCollection:
    selected = dfc.select(list(dfc.keys())[0]).toDF()
    
    from pyspark.sql.functions import regexp_replace as regxx
    
    modeCa = selected.groupby("ca").count().orderBy("count", ascending=False).first()[0]
    newDF = selected.withColumn('ca', regxx('ca', '\?', modeCa))
    
    modeThal = newDF.groupby("thal").count().orderBy("count", ascending=False).first()[0]
    newDF = newDF.withColumn('thal', regxx('thal', '\?', modeThal))
    
    results = DynamicFrame.fromDF(newDF, glueContext, "results")
    return DynamicFrameCollection({"results": results}, glueContext)
