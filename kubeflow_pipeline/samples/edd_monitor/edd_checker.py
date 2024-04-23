"""
This is pipeline to monitor whether edd data loading is successful.
    $ python edd_checker.py

    * create and upload edd_checker.yaml(pipeline) to kubeflow.
    * check ede_monitor at kubeflow.
"""
import kfp.compiler
from kfp.components import create_component_from_func
import kfp

def kfp_client():
    """
    Kubeflow pipelines client inside cluster.
    """
    end_point="http://ml-pipeline.kubeflow.svc.cluster.local:8888"
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    client = kfp.Client(host=end_point, credentials=credentials)

    return client

def base_image() -> str:
    import os
    import re

    iam = os.environ.get("AWS_ROLE_ARN")
    account = re.findall("arn:aws:iam::(.*):role*", iam)[0]
    region = os.environ.get("AWS_REGION")
    # base_image = "{}.dkr.ecr.{}.amazonaws.com/aladin-runtime:anaconda-cpu".format(account, region)
    base_image = "{}.dkr.ecr.{}.amazonaws.com/aladin:runtime-common-cpu-202404r1".format(account, region)
    print("base_image = {}".format(base_image))
    return base_image

def apollo(cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("cur_date = {}, debug={}, args = {}".format(cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "apollo"
    def apollo_helper(cur_date: str, args: str):
        table_name = "luna_user"
        query = f"SELECT count(*) as cnt FROM {catalog_name}.{schema_name}.{table_name} t "
        r1 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["cnt"])

        table_name = "luna_id_apollo_sub"
        query = f"SELECT dt as p_dt FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc"
        r2 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_dt"])
        check_last_data(r2, cur_date, -2)

        table_name = "luna_comm_log"
        query = f"SELECT dt as p_dt FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc"
        r3 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_dt"])
        check_last_data(r3, cur_date, -2)

        table_name = "user_context_log"
        query = f"SELECT dt as p_dt, hh as p_hh FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc, hh desc"
        r4 = edd_util.fetchmany(conn, query=query, size=5, column_name=["p_dt", "p_hh"])
        check_last_data(r4, cur_date, -2)

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        apollo_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise

    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

def cpm(previous:str, cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("previous={}, cur_date = {}, debug={}, args = {}".format(previous, cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "cpm"

    def cpm_helper(cur_date: str, args: str):
        table_name = "life_locationfeature_monthly"
        query = f"SELECT ym as p_ym FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by ym desc"
        r1 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_ym"])
        check_last_data(r1, cur_date, -60)

        table_name = "life_visit_poi_monthly"
        query = f"SELECT ym as p_ym FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by ym desc"
        r2 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_ym"])
        check_last_data(r2, cur_date, -60)

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        cpm_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise

    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

def di_cpm(previous:str, cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("previous={}, cur_date = {}, debug={}, args = {}".format(previous, cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "di_cpm"

    def di_cpm_helper(cur_date: str, args: str):
        table_name = "base_tasa_rel_pred_monthly"
        query = f"SELECT ym as p_ym FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by ym desc"
        r1 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_ym"])
        check_last_data(r1, cur_date, -60)
        r2 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_ym"])

        table_name = "fmly_hhld_pf_svc_monthly"
        query = f"SELECT ym as p_ym FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by ym desc"
        r2 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_ym"])
        check_last_data(r2, cur_date, -60)

        table_name = "fmly_pf_edge_monthly"
        query = f"SELECT ym as p_ym FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by ym desc"
        r3 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_ym"])
        check_last_data(r3, cur_date, -60)

        table_name = "general_pf_svc_monthly"
        query = f"SELECT * FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by ym desc"
        r4 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["ym", "cat1", "cat2"])
        check_last_data(r4, cur_date, -60)

        table_name = "seg_profile_inference_svc_monthly"
        query = f"SELECT * FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by ym desc"
        r5 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["ym", "age_group_cd"])
        check_last_data(r5, cur_date, -60)

        table_name = "seg_profile_seg_meta"
        query = f"SELECT count(*) as cnt FROM {catalog_name}.{schema_name}.{table_name}"
        r6 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["cnt"])

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        di_cpm_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise

    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

def ict_11st_11st(previous:str, cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("previous={}, cur_date = {}, debug={}, args = {}".format(previous, cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "ict_11st_11st"

    def ict_11st_11st_helper(cur_date: str, args: str):
        table_name = "tlounge_itg_agr_st11_dealings"
        query = f"SELECT part_date FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by part_date desc"
        r1 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["part_date"])
        check_last_data(r1, cur_date, -3)

        table_name = "tlounge_itg_agr_st11_member"
        query = f"SELECT part_date FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by part_date desc"
        r2 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["part_date"])
        check_last_data(r2, cur_date, -3)

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        ict_11st_11st_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise
    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

def ict_skb_acc(previous:str, cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("previous={}, cur_date = {}, debug={}, args = {}".format(previous, cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "ict_skb_acc"

    def ict_skb_acc_helper(cur_date: str, args: str):
        table_name = "cc_svc_prst_month"
        query = f"SELECT ym as p_ym FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by ym desc"
        r1 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_ym"])
        check_last_data(r1, cur_date, -60)

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        ict_skb_acc_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise
    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

def ict_skt_common(previous:str, cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("previous={}, cur_date = {}, debug={}, args = {}".format(previous, cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "ict_skt_common"

    def ict_skt_common_helper(cur_date: str, args: str):
        table_name = "ci_mst_u14"
        query = f"SELECT svc_name FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" "
        edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["svc_name"])
        query = f"SELECT count(*) as cnt FROM {catalog_name}.{schema_name}.{table_name} where svc_name='mobile'"
        edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["cnt"])

        table_name = "ict_key_mst"
        query = f"SELECT site FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" "
        edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["site"])
        query = f"SELECT count(*) as cnt FROM {catalog_name}.{schema_name}.{table_name} where site='11st'"
        edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["cnt"])

        table_name = "ict_key_mst_tmm"
        query = f"SELECT site FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" "
        edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["site"])
        query = f"SELECT count(*) as cnt FROM {catalog_name}.{schema_name}.{table_name} where site='11st'"
        edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["cnt"])

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        ict_skt_common_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise
    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

def ict_tmm_tmap(previous:str, cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("previous={}, cur_date = {}, debug={}, args = {}".format(previous, cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "ict_tmm_tmap"

    def ict_tmm_tmap_helper(cur_date: str, args: str):
        table_name = "tmap_favorate"
        query = f"SELECT dt as p_dt FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc"
        r1 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_dt"])
        check_last_data(r1, cur_date, -2)

        table_name = "tmap_poimeta"
        query = f"SELECT dt as p_dt FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc"
        r2 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_dt"])
        check_last_data(r2, cur_date, -2)

        table_name = "tmap_routehistory"
        query = f"SELECT dt as p_dt, hh as p_hh FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc"
        r3 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_dt", "p_hh"])
        check_last_data(r3, cur_date, -2)

        table_name = "tmap_rprsd"
        query = f"SELECT dt as p_dt, hh as p_hh FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc"
        r4 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_dt", "p_hh"])
        check_last_data(r4, cur_date, -2)

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        ict_tmm_tmap_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise
    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

def litmus(previous:str, cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("previous={}, cur_date = {}, debug={}, args = {}".format(previous, cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "litmus"

    def litmus_helper(cur_date: str, args: str):
        table_name = "litmus_trip"
        query = f"SELECT dt as p_dt FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc"
        r1 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_dt"])
        check_last_data(r1, cur_date, -5)

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        litmus_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise
    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

def loc_meta_raw(previous:str, cur_date: str, debug:bool, args: str) -> str:
    from aladin import trino
    from aladin import edd_util
    from datetime import datetime

    if cur_date is None or cur_date == "":
        cur_date = datetime.today().strftime("%Y%m%d")
    print("previous={}, cur_date = {}, debug={}, args = {}".format(previous, cur_date, debug, args))

    def check_last_data(last_date: str, cur_date: str, days: int):
        if debug:
            return
        if last_date < edd_util.date_add(cur_date, days).strftime("%Y%m%d"):
            raise Exception("cur_date = {}, last_date = {}. expected last_date = {} ".format(cur_date, last_date, edd_util.date_add(cur_date, days).strftime("%Y%m%d")))

    catalog_name = "edd_hive"
    schema_name = "loc_meta_raw"

    def loc_meta_raw_helper(cur_date: str, args: str):
        table_name = "enb_base"
        query = f"SELECT dt as p_dt FROM {catalog_name}.{schema_name}.\"{table_name}$partitions\" order by dt desc"
        r1 = edd_util.fetchmany(conn=conn, query=query, size=5, column_name=["p_dt"])
        check_last_data(r1, cur_date, -2)

    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    try:
        loc_meta_raw_helper(cur_date, args)
    except Exception as error:
        print("-- Exception --", error)
        raise
    # Close trino connection
    conn.close()
    print("Finish {}".format(schema_name))
    return "ok"

base_image = base_image()
apollo_op = create_component_from_func(apollo, base_image=base_image)
cpm_op = create_component_from_func(cpm, base_image=base_image)
di_cpm_op = create_component_from_func(di_cpm, base_image=base_image)
ict_11st_11st_op = create_component_from_func(ict_11st_11st, base_image=base_image)
ict_skb_acc_op = create_component_from_func(ict_skb_acc, base_image=base_image)
ict_skt_common_op = create_component_from_func(ict_skt_common, base_image=base_image)
ict_tmm_tmap_op = create_component_from_func(ict_tmm_tmap, base_image=base_image)
litmus_op = create_component_from_func(litmus, base_image=base_image)
loc_meta_raw_op = create_component_from_func(loc_meta_raw, base_image=base_image)

import kfp.dsl as dsl
@dsl.pipeline(name='edd_checker_pipeline', description='EDD data loading monitor')
def my_pipeline(cur_date: str, debug: bool, args: str):
    print("my_pipeline: cur_date={}, debug={}, args={}".format(cur_date, debug, args))
    data_op = dsl.VolumeOp(name="data-pvc",
                           resource_name="data-volume",
                           generate_unique_name=False,
                           action='apply',
                           size="10Gi",
                           modes=dsl.VOLUME_MODE_RWO)
    task_1 = apollo_op(cur_date=cur_date, debug=debug, args=args).add_pvolumes({"/data": data_op.volume})
    task_2 = cpm_op(previous=task_1.output, cur_date=cur_date, debug=debug, args=args)
    task_3 = di_cpm_op(task_2.output, cur_date=cur_date, debug=debug, args=args)
    task_4 = ict_11st_11st_op(task_3.output, cur_date=cur_date, debug=debug, args=args)
    task_5 = ict_skb_acc_op(task_4.output, cur_date=cur_date, debug=debug, args=args)
    task_6 = ict_skt_common_op(task_5.output, cur_date=cur_date, debug=debug, args=args)
    task_7 = ict_tmm_tmap_op(task_6.output, cur_date=cur_date, debug=debug, args=args)
    task_8 = litmus_op(task_7.output, cur_date=cur_date, debug=debug, args=args)
    task_9 = loc_meta_raw_op(task_8.output, cur_date=cur_date, debug=debug, args=args)

if __name__ == "__main__":
    kfp.compiler.Compiler(mode=kfp.dsl.PipelineExecutionMode.V1_LEGACY).compile(my_pipeline, "./edd_checker.yaml")
    client = kfp_client()
    client.upload_pipeline(pipeline_package_path="./edd_checker.yaml", pipeline_name="edd_checker", description="EDD Checker pipeline")

