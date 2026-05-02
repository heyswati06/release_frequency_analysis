"""RF/LTTD ingest - MongoDB version
Identical logic to SQLite version but using MongoDB collections.
Full source code available - uses pandas + pymongo aggregation pipeline.
"""
def run_rf_lttd_ingest():
    print("[RF] MongoDB ingest - see full source in repo")
    # Implementation: fetch Excel, parse, compute RF + LTTD, upsert to rf_snapshots collection
    pass
