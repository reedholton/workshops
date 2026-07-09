#!/usr/bin/env python3
# pip install oracledb
# Enables minimal + primary-key supplemental logging on an RDS Oracle instance
# ahead of a DMS CDC task, and verifies ARCHIVELOG / supplemental logging status.

import getpass
import oracledb

# Copy the endpoint from RDS console: your instance -> Connectivity & security
HOST = input("RDS Oracle endpoint (e.g. hr-db-<U>.xxxxx.us-west-2.rds.amazonaws.com): ").strip()
PORT = 1521
SERVICE_NAME = "ORCL"
USERNAME = "admin"

password = getpass.getpass(f"Password for {USERNAME}@{HOST}: ")

dsn = oracledb.makedsn(HOST, PORT, service_name=SERVICE_NAME)

with oracledb.connect(user=USERNAME, password=password, dsn=dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT log_mode FROM v$database")
        print("log_mode:", cur.fetchone()[0])

        cur.execute("SELECT supplemental_log_data_min FROM v$database")
        print("supplemental_log_data_min (before):", cur.fetchone()[0])

        print("Enabling minimal supplemental logging...")
        cur.execute("BEGIN rdsadmin.rdsadmin_util.alter_supplemental_logging('ADD'); END;")

        print("Enabling primary-key supplemental logging...")
        cur.execute(
            "BEGIN rdsadmin.rdsadmin_util.alter_supplemental_logging('ADD','PRIMARY KEY'); END;"
        )
        conn.commit()

        cur.execute("SELECT supplemental_log_data_min FROM v$database")
        print("supplemental_log_data_min (after):", cur.fetchone()[0])

print("Done.")
